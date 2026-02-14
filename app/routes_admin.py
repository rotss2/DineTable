from __future__ import annotations
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .extensions import db, limiter
from .models import Reservation, User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def _is_admin() -> bool:
    return getattr(current_user, "role", "") in {"ADMIN","MANAGER"}

def _is_staff() -> bool:
    return getattr(current_user, "role", "") in {"ADMIN","MANAGER","HOST","CASHIER"}

@admin_bp.get("/")
@login_required
def dashboard():
    if not _is_staff():
        flash("Not authorized.", "danger")
        return redirect(url_for("public.home"))

    waiting = Reservation.query.filter_by(status="WAITING").count()
    ready = Reservation.query.filter_by(status="READY").count()
    seated = Reservation.query.filter_by(status="SEATED").count()
    total = Reservation.query.count()

    rows = Reservation.query.order_by(Reservation.created_at.desc()).limit(200).all()
    return render_template("admin_dashboard.html", rows=rows, waiting=waiting, ready=ready, seated=seated, total=total)

@admin_bp.post("/reservation/<int:rid>/status")
@login_required
@limiter.limit("60/minute")
def set_status(rid: int):
    if not _is_staff():
        flash("Not authorized.", "danger")
        return redirect(url_for("admin.dashboard"))

    status = (request.form.get("status") or "").strip().upper()
    if status not in {"WAITING","READY","SEATED","DONE","CANCELLED"}:
        flash("Invalid status.", "danger")
        return redirect(url_for("admin.dashboard"))

    r = db.session.get(Reservation, rid)
    if not r:
        flash("Reservation not found.", "danger")
        return redirect(url_for("admin.dashboard"))

    r.status = status
    db.session.commit()
    flash("Status updated.", "success")
    return redirect(url_for("admin.dashboard"))

@admin_bp.get("/users")
@login_required
def users():
    if not _is_admin():
        flash("Admins only.", "danger")
        return redirect(url_for("admin.dashboard"))
    rows = User.query.order_by(User.created_at.desc()).limit(200).all()
    return render_template("admin_users.html", rows=rows)

@admin_bp.post("/users/<int:uid>/approve")
@login_required
def approve_user(uid: int):
    if not _is_admin():
        flash("Admins only.", "danger")
        return redirect(url_for("admin.users"))
    u = db.session.get(User, uid)
    if not u:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users"))
    u.is_approved = True
    db.session.commit()
    flash("User approved.", "success")
    return redirect(url_for("admin.users"))
