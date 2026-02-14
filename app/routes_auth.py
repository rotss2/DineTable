from __future__ import annotations
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from .extensions import db, limiter
from .models import User

auth_bp = Blueprint("auth", __name__, url_prefix="")

@auth_bp.get("/login")
def login():
    return render_template("auth_login.html")

@auth_bp.post("/login")
@limiter.limit("10/minute")
def login_post():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    if not username or not password:
        flash("Missing username/password.", "danger")
        return redirect(url_for("auth.login"))

    u = User.query.filter_by(username=username).first()
    if not u or not u.check_password(password):
        flash("Invalid login.", "danger")
        return redirect(url_for("auth.login"))
    if not u.is_active:
        flash("Account disabled.", "danger")
        return redirect(url_for("auth.login"))
    if not u.is_approved:
        flash("Account pending approval.", "warning")
        return redirect(url_for("auth.login"))

    login_user(u)
    flash("Welcome!", "success")
    return redirect(url_for("admin.dashboard"))

@auth_bp.get("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("public.home"))

@auth_bp.get("/signup")
def signup():
    return render_template("auth_signup.html")

@auth_bp.post("/signup")
@limiter.limit("5/minute")
def signup_post():
    username = (request.form.get("username") or "").strip()
    phone = (request.form.get("phone") or "").strip()
    password = request.form.get("password") or ""
    if not username or not password:
        flash("Missing username/password.", "danger")
        return redirect(url_for("auth.signup"))

    if User.query.filter_by(username=username).first():
        flash("Username already exists.", "warning")
        return redirect(url_for("auth.signup"))

    require_approval = bool(current_app.config.get("REQUIRE_APPROVAL", False))
    u = User(
        username=username,
        phone=phone or None,
        password_hash=generate_password_hash(password),
        role="HOST",
        is_active=True,
        is_approved=(not require_approval),
    )
    db.session.add(u)
    db.session.commit()

    flash("Account created. Please login." if not require_approval else "Signup submitted. Wait for approval.", "success")
    return redirect(url_for("auth.login"))
