# TableQueue ULTRA (Enterprise)

## Features
- Public reservation booking (ticket + QR status page)
- Customer portal: search by ticket code or phone
- Live Board for TV/monitor
- Staff login (Flask-Login)
- Admin dashboard (update reservation statuses)
- Optional staff signup + approval flow
- Optional Semaphore SMS confirmation
- Rate limiting (anti spam / brute force)

## Local run
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export FLASK_SECRET_KEY=dev
python -c "from app import create_app; app=create_app(); app.run(debug=True)"
```

## Render setup (recommended)
1) Push this repo to GitHub
2) Create a Render Web Service from the repo
3) Create a Render PostgreSQL database
4) Add env vars in the Web Service:
- DATABASE_URL (from Render Postgres)
- PUBLIC_BASE_URL (your render URL)
- SEMAPHORE_API_KEY (optional)

Start command is already in Procfile/render.yaml.

## URLs
- Public home: /
- Reserve: /reserve
- Status search: /status
- Ticket page: /ticket/<CODE>
- Live board: /live
- Staff login: /login
- Admin: /admin
