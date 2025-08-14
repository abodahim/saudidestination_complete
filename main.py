import csv, os, smtplib, requests  # requests لإرسال webhook
from email.message import EmailMessage
from flask import Flask, render_template, abort, send_from_directory, request, redirect, url_for, flash

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")  # للـ flash

TRIPS = [
    {"slug":"jeddah","title":"رحلة جدة","desc":"جولة على شاطئ البحر الأحمر والمعالم التاريخية.","image":"jeddah_1.JPG","price":"299 ر.س","duration":"يوم واحد","category":"عائلية"},
    {"slug":"riyadh","title":"رحلة الرياض","desc":"زيارة أهم المعالم الثقافية والتراثية في العاصمة.","image":"riyadh_1.JPG","price":"549 ر.س","duration":"يومان","category":"شركات"},
    {"slug":"yanbu","title":"رحلة ينبع","desc":"استكشاف الجزر والشواطئ الرملية الساحرة.","image":"yanbu_1.JPG","price":"799 ر.س","duration":"3 أيام","category":"مدرسية"},
]

# ---------- Utilities ----------
def send_to_webhook(payload: dict) -> bool:
    url = os.environ.get("BOOKING_WEBHOOK_URL")
    if not url: return False
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.ok
    except Exception:
        return False

def send_email(payload: dict) -> bool:
    host = os.environ.get("SMTP_HOST"); port = int(os.environ.get("SMTP_PORT","0") or 0)
    user = os.environ.get("SMTP_USER"); pw = os.environ.get("SMTP_PASS")
    to  = os.environ.get("BOOKING_EMAIL_TO")
    if not all([host,port,user,pw,to]): return False
    try:
        msg = EmailMessage()
        msg["Subject"] = f"حجز جديد - {payload.get('trip_title','')}"
        msg["From"] = user
        msg["To"] = to
        body = "\n".join([f"{k}: {v}" for k,v in payload.items()])
        msg.set_content(body)
        with smtplib.SMTP_SSL(host, port) as s:
            s.login(user, pw)
            s.send_message(msg)
        return True
    except Exception:
        return False

def save_csv(payload: dict) -> bool:
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/bookings.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=sorted(payload.keys()))
            if f.tell() == 0: writer.writeheader()
            writer.writerow(payload)
        return True
    except Exception:
        return False

# ---------- Routes ----------
@app.route("/")
def home():
    return render_template("index.html", trips=TRIPS)

@app.route("/trip/<slug>")
def trip(slug):
    t = next((x for x in TRIPS if x["slug"] == slug), None)
    if not t: abort(404)
    return render_template("trip.html", trip=t)

@app.route("/booking/<slug>", methods=["GET", "POST"])
def booking(slug):
    t = next((x for x in TRIPS if x["slug"] == slug), None)
    if not t: abort(404)

    if request.method == "POST":
        data = {
            "trip_slug": slug,
            "trip_title": t["title"],
            "name": request.form.get("name","").strip(),
            "phone": request.form.get("phone","").strip(),
            "email": request.form.get("email","").strip(),
            "date": request.form.get("date","").strip(),
            "people": request.form.get("people","").strip(),
            "notes": request.form.get("notes","").strip(),
        }

        # أولوية: Webhook → Email → CSV
        ok = send_to_webhook(data) or send_email(data) or save_csv(data)
        if ok:
            return render_template("booking_success.html", trip=t, data=data)
        flash("تعذر حفظ طلب الحجز حالياً. حاول لاحقاً.", "error")
        return redirect(url_for("booking", slug=slug))

    return render_template("booking.html", trip=t)

@app.route("/robots.txt")
def robots():
    return send_from_directory(".", "robots.txt", mimetype="text/plain")

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(".", "sitemap.xml", mimetype="application/xml")

@app.route("/manifest.json")
def manifest():
    return send_from_directory(".", "manifest.json", mimetype="application/json")

@app.route("/service-worker.js")
def sw():
    return send_from_directory(".", "service-worker.js", mimetype="application/javascript")

@app.route("/health")
def health():
    return "ok", 200

# ---------- Error pages ----------
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
