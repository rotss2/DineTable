from __future__ import annotations
import secrets
import string
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from .extensions import db, limiter
from .models import Reservation
from .services.sms import send_semaphore_sms, normalize_phone
from .services.qr import qr_png_base64

public_bp = Blueprint("public", __name__)

def _ticket_code(n: int = 7) -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(alphabet) for _ in range(n))

def _public_base() -> str:
    base = current_app.config.get("PUBLIC_BASE_URL", "")
    return base.rstrip("/")

@public_bp.get("/")
def home():
    # live counter
    waiting = Reservation.query.filter(Reservation.status.in_(["WAITING", "READY"])).count()
    total = Reservation.query.count()
    return render_template("public_home.html", waiting=waiting, total=total)

@public_bp.get("/reserve")
def reserve_form():
    return render_template("public_reserve.html")

@public_bp.post("/reserve")
@limiter.limit("10/minute")
def reserve_submit():
    full_name = (request.form.get("full_name") or request.form.get("name") or "").strip()
    phone_raw = (request.form.get("phone") or "").strip()
    phone = normalize_phone(phone_raw)
    guests = request.form.get("guests") or request.form.get("pax") or "2"
    date = (request.form.get("date") or "").strip()
    time = (request.form.get("time") or "").strip()
    notes = (request.form.get("notes") or "").strip()

    if not full_name or not date or not time:
        flash("Please complete name, date, and time.", "danger")
        return redirect(url_for("public.reserve_form"))

    try:
        guests_i = max(1, int(guests))
    except Exception:
        guests_i = 2

    # unique ticket loop
    for _ in range(5):
        ticket = _ticket_code()
        if not Reservation.query.filter_by(ticket_code=ticket).first():
            break
    else:
        flash("Could not generate ticket. Try again.", "danger")
        return redirect(url_for("public.reserve_form"))

    r = Reservation(
        ticket_code=ticket,
        full_name=full_name,
        phone=phone or None,
        guests=guests_i,
        reserve_date=date,
        reserve_time=time,
        status="WAITING",
        notes=notes or None,
    )
    db.session.add(r)
    db.session.commit()

    # QR + SMS link
    ticket_path = url_for("public.ticket_view", ticket_code=ticket)
    public_link = (_public_base() + ticket_path) if _public_base() else url_for("public.ticket_view", ticket_code=ticket, _external=True)
    if phone:
        ok, detail = send_semaphore_sms(
            current_app.config.get("SEMAPHORE_API_KEY",""),
            current_app.config.get("SEMAPHORE_SENDER_NAME","TableQueue"),
            phone,
            f"✅ Reservation received!\nTicket: {ticket}\nStatus: {public_link}",
        )
        # Don't scare users; just log details server-side
        current_app.logger.info("SMS send result ok=%s detail=%s", ok, detail)

    flash("Reservation confirmed! Your ticket is ready.", "success")
    return redirect(url_for("public.ticket_view", ticket_code=ticket))

@public_bp.get("/status")
def status_form():
    return render_template("public_status.html", ticket=None)

@public_bp.post("/status")
@limiter.limit("15/minute")
def status_submit():
    ticket = (request.form.get("ticket") or request.form.get("ticket_code") or "").strip().upper()
    phone = normalize_phone(request.form.get("phone") or "")

    q = Reservation.query
    r = None
    if ticket:
        r = q.filter_by(ticket_code=ticket).first()
    elif phone:
        r = q.filter_by(phone=phone).order_by(Reservation.created_at.desc()).first()

    if not r:
        flash("No active reservation found.", "warning")
        return redirect(url_for("public.status_form"))

    return redirect(url_for("public.ticket_view", ticket_code=r.ticket_code))

@public_bp.get("/ticket/<ticket_code>")
def ticket_view(ticket_code: str):
    code = (ticket_code or "").strip().upper()
    r = Reservation.query.filter_by(ticket_code=code).first()
    if not r:
        flash("Ticket not found.", "danger")
        return redirect(url_for("public.status_form"))

    ticket_path = url_for("public.ticket_view", ticket_code=code)
    public_link = (_public_base() + ticket_path) if _public_base() else url_for("public.ticket_view", ticket_code=code, _external=True)
    qr_b64 = qr_png_base64(public_link)
    return render_template("public_ticket.html", r=r, qr_b64=qr_b64, public_link=public_link)

@public_bp.get("/live")
def live_board():
    # TV/monitor friendly board
    rows = Reservation.query.filter(Reservation.status.in_(["WAITING","READY"])).order_by(Reservation.created_at.asc()).limit(30).all()
    return render_template("public_live.html", rows=rows)
