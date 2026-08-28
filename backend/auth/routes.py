import hashlib
import logging
import os
import secrets
import smtplib
import threading
from datetime import datetime, timedelta
from email.message import EmailMessage

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

from models import PasswordResetToken, User, db

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

# Reset tokens live for 60 minutes and can only be used once.
RESET_TOKEN_TTL_MINUTES = 60


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _build_reset_link(token: str) -> str:
    """Build the URL a user visits to complete their reset.

    Falls back to the request origin when APP_BASE_URL isn't set, so this
    works out-of-the-box in development without any extra configuration.
    """
    base = os.environ.get("APP_BASE_URL", "").rstrip("/")
    if not base:
        base = request.host_url.rstrip("/")
    return f"{base}/reset-password?token={token}"


def _smtp_configured() -> bool:
    """Whether the environment has enough variables to attempt an SMTP send."""
    return all(
        os.environ.get(k)
        for k in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD")
    )


def _send_reset_email_sync(email: str, link: str) -> bool:
    """Blocking SMTP send. Called from a background thread so the HTTP
    request thread never waits on Gmail. Returns True on success."""
    host = os.environ.get("SMTP_HOST")
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASSWORD")
    port = int(os.environ.get("SMTP_PORT", "587"))
    sender = os.environ.get("SMTP_FROM", user)

    msg = EmailMessage()
    msg["Subject"] = "Reset your LinguaDepth password"
    msg["From"] = sender
    msg["To"] = email
    msg.set_content(
        "You (or someone using your email) asked to reset your LinguaDepth "
        "password.\n\n"
        f"Follow this link within {RESET_TOKEN_TTL_MINUTES} minutes to set a "
        f"new one:\n{link}\n\n"
        "If you didn't ask for this, you can safely ignore this email — "
        "your current password stays active."
    )

    try:
        # Short timeout: a slow SMTP server should fail fast so the log tells
        # the operator immediately rather than tying up a worker thread.
        with smtplib.SMTP(host, port, timeout=5) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(msg)
        logger.info("[password-reset] email sent to %s", email)
        return True
    except Exception as exc:
        logger.warning(
            "[password-reset] SMTP send failed for %s: %s — "
            "recover with this link: %s",
            email,
            exc,
            link,
        )
        return False


def _dispatch_reset_email(email: str, link: str) -> None:
    """Fire an SMTP send on a background thread — the HTTP response returns
    immediately regardless of whether the send succeeds, times out, or is
    blocked by the platform's outbound-mail policy.
    """
    if not _smtp_configured():
        # No SMTP wired up — log the link so an operator can hand it off.
        logger.warning(
            "[password-reset] SMTP not configured — reset link for %s: %s",
            email,
            link,
        )
        return

    threading.Thread(
        target=_send_reset_email_sync,
        args=(email, link),
        name=f"reset-email-{email}",
        daemon=True,
    ).start()


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists"}), 409

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return (
        jsonify(
            {
                "token": token,
                "user": user.to_dict(),
                "needs_placement": True,
            }
        ),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))
    # A user who has never completed a session and is still at the default
    # level with zero XP is treated as needing the placement quiz.
    needs_placement = user.xp == 0 and not user.sessions
    return jsonify(
        {
            "token": token,
            "user": user.to_dict(),
            "needs_placement": needs_placement,
        }
    )


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()})


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """Start a password-reset flow for the account with the given email.

    Always returns the same success payload — no matter whether the address
    exists — so an attacker can't use this endpoint to enumerate accounts.
    When SMTP is configured the reset link is emailed; otherwise the link is
    written to the server log for the operator to hand off manually. In
    development (DEBUG=True) the link is also returned in the JSON response
    so a single-machine dev doesn't need email at all.
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    generic_response = {
        "message": (
            "If an account exists for that email, a password reset link is "
            "on its way. Check your inbox (and spam folder) in a few minutes."
        )
    }

    if not email:
        return jsonify(generic_response)

    user = User.query.filter_by(email=email).first()
    if not user:
        # Don't leak whether the account exists — respond identically.
        return jsonify(generic_response)

    # Invalidate any live tokens this user still has so only the newest one
    # works. Keeps `used_at` history intact.
    now = datetime.utcnow()
    PasswordResetToken.query.filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used_at.is_(None),
        PasswordResetToken.expires_at > now,
    ).update({PasswordResetToken.expires_at: now}, synchronize_session=False)

    token = secrets.token_urlsafe(32)
    db.session.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=_hash_token(token),
            expires_at=now + timedelta(minutes=RESET_TOKEN_TTL_MINUTES),
        )
    )
    db.session.commit()

    link = _build_reset_link(token)
    # Fire-and-forget: SMTP happens on a background thread so a slow or
    # broken mail server can never stall the HTTP response.
    _dispatch_reset_email(user.email, link)

    payload = dict(generic_response)
    if current_app.config.get("DEBUG"):
        # Development convenience only. Never returned in production.
        payload["debug_reset_link"] = link
    return jsonify(payload)


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """Consume a reset token and set a new password."""
    data = request.get_json(silent=True) or {}
    token = (data.get("token") or "").strip()
    new_password = data.get("password") or ""

    if not token or not new_password:
        return jsonify({"error": "Token and new password are required"}), 400
    if len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    record = PasswordResetToken.query.filter_by(token_hash=_hash_token(token)).first()
    now = datetime.utcnow()
    if not record or record.used_at is not None or record.expires_at <= now:
        return (
            jsonify(
                {
                    "error": (
                        "This reset link has expired or already been used. "
                        "Please request a new one."
                    )
                }
            ),
            400,
        )

    user = User.query.get(record.user_id)
    if not user:
        return jsonify({"error": "Account no longer exists."}), 404

    user.password_hash = generate_password_hash(new_password)
    record.used_at = now
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify(
        {
            "message": "Password updated. You are now signed in.",
            "token": token,
            "user": user.to_dict(),
        }
    )
