-- Sample seed data (demo users + a few tags)
-- Passwords are placeholders; use API registration for real users.

INSERT INTO users(email, password_hash, role)
VALUES
  ('admin@example.com', 'pbkdf2_sha256$200000$00000000000000000000000000000000$0000000000000000000000000000000000000000000000000000000000000000', 'Admin'),
  ('user@example.com',  'pbkdf2_sha256$200000$00000000000000000000000000000000$0000000000000000000000000000000000000000000000000000000000000000', 'User')
ON CONFLICT (email) DO NOTHING;

INSERT INTO tags(name)
VALUES
  ('invoice'),
  ('receipt'),
  ('contract'),
  ('screenshot'),
  ('logo'),
  ('report')
ON CONFLICT (name) DO NOTHING;

