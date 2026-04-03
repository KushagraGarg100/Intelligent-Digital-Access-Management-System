import os

from app.db.session import init_engine, init_session_factory, db_session, create_all
from app.models.user import User, UserRole
from app.utils.security import hash_password


def main() -> None:
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://dam_user:dam_pass@localhost:5432/dam",
    )
    init_engine(database_url)
    init_session_factory()
    create_all()

    with db_session() as db:
        for (email, role) in [
            ("admin@example.com", UserRole.ADMIN),
            ("user@example.com", UserRole.USER),
        ]:
            u = db.query(User).filter(User.email == email).one_or_none()
            if not u:
                u = User(email=email, role=role, password_hash=hash_password("Password123!"))
                db.add(u)

    print("Seeded demo users:")
    print("- admin@example.com / Password123! (Admin)")
    print("- user@example.com / Password123! (User)")


if __name__ == "__main__":
    main()

