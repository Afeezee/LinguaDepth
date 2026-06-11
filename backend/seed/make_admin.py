"""Grant (or revoke) admin access for a user by email.

Run from the backend/ directory:
    python seed/make_admin.py user@example.com          # grant
    python seed/make_admin.py user@example.com --revoke # revoke
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from models import User, db


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    email = sys.argv[1].strip().lower()
    revoke = "--revoke" in sys.argv

    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"No user found with email: {email}")
            sys.exit(1)
        user.is_admin = not revoke
        db.session.commit()
        print(f"{'Revoked admin from' if revoke else 'Granted admin to'} {email}")


if __name__ == "__main__":
    main()
