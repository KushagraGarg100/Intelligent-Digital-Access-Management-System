from __future__ import annotations

import os

from flask import Blueprint, jsonify, redirect, request, send_file
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.core.rbac import require_roles
from app.db.session import db_session
from app.models.asset import Asset, AssetTag, AssetType, AssetVersion, Tag
from app.services.ai_pipeline import ai_pipeline
from app.services.storage import storage_service
from app.utils.security import sha256_bytes


assets_bp = Blueprint("assets", __name__)


def _infer_asset_type(content_type: str) -> AssetType:
    ct = (content_type or "").lower()
    if ct.startswith("image/"):
        return AssetType.IMAGE
    if ct.startswith("video/"):
        return AssetType.VIDEO
    return AssetType.DOCUMENT


@assets_bp.post("/upload")
@jwt_required()
def upload_asset():
    user_id = int(get_jwt_identity())

    if "file" not in request.files:
        return jsonify({"error": "file_required"}), 400
    f = request.files["file"]
    if not f or not f.filename:
        return jsonify({"error": "invalid_file"}), 400

    content = f.read()
    content_type = f.mimetype or "application/octet-stream"
    asset_type = _infer_asset_type(content_type)
    sha256 = sha256_bytes(content)
    size_bytes = len(content)

    stored = storage_service.put_bytes(content=content, original_filename=f.filename, content_type=content_type)

    with db_session() as db:
        # Exact duplicate (same owner+sha)
        existing = (
            db.query(Asset)
            .filter(Asset.owner_user_id == user_id)
            .filter(Asset.sha256 == sha256)
            .one_or_none()
        )
        if existing:
            return jsonify({"error": "exact_duplicate", "asset_id": existing.id}), 409

        asset = Asset(
            owner_user_id=user_id,
            original_filename=f.filename,
            content_type=content_type,
            asset_type=asset_type,
            sha256=sha256,
            size_bytes=size_bytes,
            storage_provider=stored.provider,
            storage_bucket=stored.bucket,
            storage_object_key=stored.object_key,
            storage_url=stored.url,
            latest_version=1,
        )
        db.add(asset)
        db.flush()

        v1 = AssetVersion(
            asset_id=asset.id,
            version=1,
            storage_provider=stored.provider,
            storage_bucket=stored.bucket,
            storage_object_key=stored.object_key,
            storage_url=stored.url,
            sha256=sha256,
            size_bytes=size_bytes,
            note="Initial upload",
        )
        db.add(v1)

        ai = ai_pipeline.process_asset(asset_id=asset.id, bytes_=content, content_type=content_type)

        # Persist tags
        created_tags: list[dict] = []
        for t in ai.tags:
            name = (t.get("name") or "").strip().lower()
            if not name:
                continue
            tag = db.query(Tag).filter(Tag.name == name).one_or_none()
            if not tag:
                tag = Tag(name=name)
                db.add(tag)
                db.flush()
            at = db.query(AssetTag).filter(AssetTag.asset_id == asset.id, AssetTag.tag_id == tag.id).one_or_none()
            if not at:
                at = AssetTag(asset_id=asset.id, tag_id=tag.id, source=t.get("source") or "ai", confidence=str(t.get("confidence") or ""))
                db.add(at)
            created_tags.append({"name": tag.name, "source": at.source, "confidence": at.confidence})

        return jsonify(
            {
                "asset": {
                    "id": asset.id,
                    "original_filename": asset.original_filename,
                    "content_type": asset.content_type,
                    "asset_type": asset.asset_type.value,
                    "sha256": asset.sha256,
                    "size_bytes": asset.size_bytes,
                    "storage_provider": asset.storage_provider,
                    "storage_object_key": asset.storage_object_key,
                    "storage_url": asset.storage_url,
                    "latest_version": asset.latest_version,
                    "created_at": asset.created_at.isoformat() if asset.created_at else None,
                },
                "tags": created_tags,
                "near_duplicate": ai.duplicate,
            }
        )


@assets_bp.get("")
@jwt_required()
def list_assets():
    claims = get_jwt()
    role = claims.get("role")
    user_id = int(get_jwt_identity())

    q = (request.args.get("q") or "").strip().lower()
    tag = (request.args.get("tag") or "").strip().lower()
    type_ = (request.args.get("type") or "").strip().lower()

    with db_session() as db:
        query = db.query(Asset)
        if role != "Admin":
            query = query.filter(Asset.owner_user_id == user_id)
        if q:
            query = query.filter(Asset.original_filename.ilike(f"%{q}%"))
        if type_:
            try:
                asset_type = AssetType(type_)
                query = query.filter(Asset.asset_type == asset_type)
            except ValueError:
                pass
        if tag:
            query = (
                query.join(AssetTag, AssetTag.asset_id == Asset.id)
                .join(Tag, Tag.id == AssetTag.tag_id)
                .filter(Tag.name == tag)
            )

        items = query.order_by(Asset.created_at.desc()).limit(200).all()
        return jsonify(
            [
                {
                    "id": a.id,
                    "original_filename": a.original_filename,
                    "content_type": a.content_type,
                    "asset_type": a.asset_type.value,
                    "size_bytes": a.size_bytes,
                    "storage_url": a.storage_url,
                    "latest_version": a.latest_version,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in items
            ]
        )


@assets_bp.get("/<int:asset_id>")
@jwt_required()
def get_asset(asset_id: int):
    claims = get_jwt()
    role = claims.get("role")
    user_id = int(get_jwt_identity())
    with db_session() as db:
        asset = db.query(Asset).filter(Asset.id == asset_id).one_or_none()
        if not asset:
            return jsonify({"error": "not_found"}), 404
        if role != "Admin" and asset.owner_user_id != user_id:
            return jsonify({"error": "forbidden"}), 403

        tag_rows = (
            db.query(AssetTag, Tag)
            .join(Tag, Tag.id == AssetTag.tag_id)
            .filter(AssetTag.asset_id == asset.id)
            .all()
        )
        return jsonify(
            {
                "id": asset.id,
                "original_filename": asset.original_filename,
                "content_type": asset.content_type,
                "asset_type": asset.asset_type.value,
                "size_bytes": asset.size_bytes,
                "storage_provider": asset.storage_provider,
                "storage_bucket": asset.storage_bucket,
                "storage_object_key": asset.storage_object_key,
                "storage_url": asset.storage_url,
                "download_url": f"/api/assets/{asset.id}/download",
                "latest_version": asset.latest_version,
                "created_at": asset.created_at.isoformat() if asset.created_at else None,
                "tags": [
                    {"name": t.name, "source": at.source, "confidence": at.confidence} for (at, t) in tag_rows
                ],
            }
        )


@assets_bp.get("/<int:asset_id>/download")
@jwt_required()
def download_asset(asset_id: int):
    claims = get_jwt()
    role = claims.get("role")
    user_id = int(get_jwt_identity())
    with db_session() as db:
        asset = db.query(Asset).filter(Asset.id == asset_id).one_or_none()
        if not asset:
            return jsonify({"error": "not_found"}), 404
        if role != "Admin" and asset.owner_user_id != user_id:
            return jsonify({"error": "forbidden"}), 403

        if asset.storage_provider == "gcs":
            signed = storage_service.get_gcs_signed_url(object_key=asset.storage_object_key)
            if signed:
                # UX: make downloads work via normal browser navigation
                return redirect(signed, code=302)
            if asset.storage_url:
                return redirect(asset.storage_url, code=302)
            return jsonify({"error": "gcs_url_unavailable"}), 503

        # local
        path = storage_service.resolve_local_path(asset.storage_object_key)
        if not os.path.exists(path):
            return jsonify({"error": "file_missing"}), 404
        return send_file(path, as_attachment=True, download_name=asset.original_filename, mimetype=asset.content_type)


@assets_bp.post("/<int:asset_id>/version")
@jwt_required()
def create_new_version(asset_id: int):
    user_id = int(get_jwt_identity())
    if "file" not in request.files:
        return jsonify({"error": "file_required"}), 400
    f = request.files["file"]
    if not f or not f.filename:
        return jsonify({"error": "invalid_file"}), 400

    note = (request.form.get("note") or "").strip()

    content = f.read()
    content_type = f.mimetype or "application/octet-stream"
    sha256 = sha256_bytes(content)
    size_bytes = len(content)

    stored = storage_service.put_bytes(content=content, original_filename=f.filename, content_type=content_type)

    with db_session() as db:
        asset = db.query(Asset).filter(Asset.id == asset_id).one_or_none()
        if not asset:
            return jsonify({"error": "not_found"}), 404
        if asset.owner_user_id != user_id:
            return jsonify({"error": "forbidden"}), 403

        new_version = asset.latest_version + 1

        v = AssetVersion(
            asset_id=asset.id,
            version=new_version,
            storage_provider=stored.provider,
            storage_bucket=stored.bucket,
            storage_object_key=stored.object_key,
            storage_url=stored.url,
            sha256=sha256,
            size_bytes=size_bytes,
            note=note or f"Version {new_version}",
        )
        db.add(v)

        asset.latest_version = new_version
        asset.sha256 = sha256
        asset.size_bytes = size_bytes
        asset.content_type = content_type
        asset.original_filename = f.filename
        asset.storage_provider = stored.provider
        asset.storage_bucket = stored.bucket
        asset.storage_object_key = stored.object_key
        asset.storage_url = stored.url

        ai = ai_pipeline.process_asset(asset_id=asset.id, bytes_=content, content_type=content_type)

        return jsonify({"asset_id": asset.id, "version": new_version, "near_duplicate": ai.duplicate})


@assets_bp.get("/<int:asset_id>/versions")
@jwt_required()
def list_versions(asset_id: int):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    with db_session() as db:
        asset = db.query(Asset).filter(Asset.id == asset_id).one_or_none()
        if not asset:
            return jsonify({"error": "not_found"}), 404
        if role != "Admin" and asset.owner_user_id != user_id:
            return jsonify({"error": "forbidden"}), 403

        versions = (
            db.query(AssetVersion)
            .filter(AssetVersion.asset_id == asset.id)
            .order_by(AssetVersion.version.desc())
            .all()
        )
        return jsonify(
            [
                {
                    "version": v.version,
                    "sha256": v.sha256,
                    "size_bytes": v.size_bytes,
                    "storage_url": v.storage_url,
                    "note": v.note,
                    "created_at": v.created_at.isoformat() if v.created_at else None,
                }
                for v in versions
            ]
        )


@assets_bp.post("/<int:asset_id>/tags")
@jwt_required()
def add_user_tag(asset_id: int):
    user_id = int(get_jwt_identity())
    payload = request.get_json(force=True, silent=True) or {}
    name = (payload.get("name") or "").strip().lower()
    if not name:
        return jsonify({"error": "name_required"}), 400

    with db_session() as db:
        asset = db.query(Asset).filter(Asset.id == asset_id).one_or_none()
        if not asset:
            return jsonify({"error": "not_found"}), 404
        if asset.owner_user_id != user_id:
            return jsonify({"error": "forbidden"}), 403

        tag = db.query(Tag).filter(Tag.name == name).one_or_none()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()

        at = db.query(AssetTag).filter(AssetTag.asset_id == asset.id, AssetTag.tag_id == tag.id).one_or_none()
        if not at:
            at = AssetTag(asset_id=asset.id, tag_id=tag.id, source="user", confidence="")
            db.add(at)

        return jsonify({"ok": True, "tag": {"name": tag.name}})


@assets_bp.delete("/<int:asset_id>")
@jwt_required()
def delete_asset(asset_id: int):
    claims = get_jwt()
    role = claims.get("role")
    user_id = int(get_jwt_identity())

    with db_session() as db:
        asset = db.query(Asset).filter(Asset.id == asset_id).one_or_none()
        if not asset:
            return jsonify({"error": "not_found"}), 404
        if role != "Admin" and asset.owner_user_id != user_id:
            return jsonify({"error": "forbidden"}), 403

        # Collect all versions to delete their files
        versions = db.query(AssetVersion).filter(AssetVersion.asset_id == asset.id).all()
        for v in versions:
            storage_service.delete_object(provider=v.storage_provider, object_key=v.storage_object_key)

        # AI cleanup
        ai_pipeline.delete_asset(asset_id=asset.id)

        db.delete(asset)
        return jsonify({"ok": True})


@assets_bp.get("/admin/all")
@require_roles("Admin")
def admin_list_all_assets():
    with db_session() as db:
        items = db.query(Asset).order_by(Asset.created_at.desc()).limit(500).all()
        return jsonify(
            [
                {
                    "id": a.id,
                    "owner_user_id": a.owner_user_id,
                    "original_filename": a.original_filename,
                    "asset_type": a.asset_type.value,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in items
            ]
        )

