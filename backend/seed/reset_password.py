"""Emergency password reset for a single user, run from the server.

Use this when a user (in particular the super admin) is locked out and the
forgot-password email flow isn't reachable — for example when SMTP isn't
configured yet, or when the account is the sole admin and no one else can
approve the reset in the UI.

Run from the backend/ directory. Two ways to provide the new password:

  Interactive (recommended — the password stays out of shell history):
      python seed/reset_password.py olagunjuafeez@gmail.com

  Non-interactive (needed when running through a pipe or on Windows
  consoles that don't support hidden input):
      python seed/reset_password.py olagunjuafeez@gmail.com --password NewPass99

On Windows PowerShell the interactive prompt uses hidden input when the
console supports it, and falls back to visible input (with a warning)
when it doesn't.
"""
import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from werkzeug.security import generate_password_hash

from app import create_app
from models import User, db


def _prompt_password(prompt: str) -> str:
    """Read a password from the console, hiding input when possible."""
    try:
        return getpass.getpass(prompt)
    except (getpass.GetPassWarning, EOFError, OSError):
        # Some Windows consoles / piped stdin can't hide input. Fall back to
        # visible input so the script doesn't hang forever waiting.
        print("(input will be VISIBLE — no console echo suppression here)")
        return input(prompt)


def main():
    parser = argparse.ArgumentParser(description="Reset a user's password.")
    parser.add_argument("email", help="Email of the account to reset.")
    parser.add_argument(
        "--password",
        help=(
            "New password. If omitted, you'll be prompted. "
            "WARNING: passing --password puts the value in your shell history."
        ),
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the confirmation prompt (useful for automation).",
    )
    args = parser.parse_args()

    email = args.email.strip().lower()
    app = create_app()

    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"No user with email {email!r}")
            sys.exit(1)

        print(
            f"Resetting password for: {user.name} <{user.email}> "
            f"(admin={bool(user.is_admin)})"
        )

        if args.password is not None:
            new_password = args.password
        else:
            new_password = _prompt_password("New password (min 6 chars): ")
            if not args.yes:
                confirm = _prompt_password("Confirm new password:          ")
                if new_password != confirm:
                    print("Passwords do not match. Aborting.")
                    sys.exit(1)

        if len(new_password) < 6:
            print("Password too short (need at least 6 characters). Aborting.")
            sys.exit(1)

        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        print(
            f"OK — password reset for {user.email}. "
            "You can now sign in with the new password."
        )


if __name__ == "__main__":
    main()
