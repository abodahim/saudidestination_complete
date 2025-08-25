import os
import csv
import smtplib
from io import StringIO, BytesIO
from datetime import datetime, timedelta
from email.message import EmailMessage

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, send_from_directory, Response
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-in-production")

# قاعدة البيانات
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL or "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# بيانات الشركة / التواصل
COMPANY = {
    "name": os.getenv("COMPANY_NAME", "وجهة السعودية"),
    "email": os.getenv("COMPANY_EMAIL", "info@example.com"),
    "phone": os.getenv("COMPANY_PHONE", "+9665xxxxxxx"),
    "address": os.getenv("COMPANY_ADDRESS", "المملكة العربية السعودية"),
    "whatsapp": os.getenv("COMPANY_WHATSAPP", ""),  # مثال: 9665xxxxxxx
}

# إعدادات البريد (SMTP)
SMTP = {
    "host": os.getenv("SMTP_HOST", ""),
    "port": int(os.getenv("SMTP_PORT", "587")),
    "user": os.getenv("SMTP_USER", ""),
    "password": os.getenv("SMTP_PASS", ""),
    "from_email": os.getenv("FROM_EMAIL", os.getenv("SMTP_USER", "noreply@example.com")),
}

# -------------------- نموذج الحجز --------------------
class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    trip_id = db.Column(db.Integer, nullable=False)
    days = db.Column(db.Integer, nullable=False, default=1)
    total = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="pending")  # pending/paid
    paid_at = db.Column(db.DateTime, nullable=True)
    invoice_number = db.Column(db.String(32), unique=True, nullable=True) # INV-YYYY-0001

def _safe_upgrade_table():
    insp = inspect(db.engine)
    cols = {c["name"] for c in insp.get_columns("bookings")}
    with db.engine.begin() as conn:
        if "status" not in cols:
            conn.execute(text("ALTER TABLE bookings ADD COLUMN status VARCHAR(20) DEFAULT 'pending'"))
        if "paid_at" not in cols:
            conn.execute(text("ALTER TABLE bookings ADD COLUMN paid_at TIMESTAMP"))
        if "invoice_number" not in cols:
            conn.execute(text("ALTER TABLE bookings ADD COLUMN invoice_number VARCHAR(32)"))

# -------------------- بيانات ثابتة --------------------
TRIPS = [
    {
        "id": 1, "slug": "jeddah", "name": "رحلة جدة", "city": "جدة",
        "days": 1, "price": 299,
        "images": ["jeddah_1.JPG", "jeddah_2.JPG", "jeddah_3.JPG", "jeddah_4.JPG"],
        "desc": "اكتشف سحر مدينة جدة مع جولة تشمل المعالم التراثية والكورنيش."
    },
    {
        "id": 2, "slug": "riyadh", "name": "رحلة الرياض", "city": "الرياض",
        "days": 1, "price": 399,
        "images": ["riyadh_1.JPG", "riyadh_2.JPG", "riyadh_3.JPG", "riyadh_4.JPG"],
        "desc": "جولة مميزة لاستكشاف معالم العاصمة السعودية بين التراث والحداثة."
    },
    {
        "id": 3, "slug": "yanbu", "name": "رحلة ينبع", "city": "ينبع",
        "days": 1, "price": 399,
        "images": ["yanbu_1.JPG", "yanbu_2.JPG", "yanbu_3.JPG", "yanbu_4.JPG"],
        "desc": "استمتع بجمال الشواطئ والأنشطة البحرية في مدينة ينبع."
    },
    {
        "id": 4, "slug": "ala", "name": "رحلة العلا", "city": "العلا",
        "days": 1, "price": 499,
        "images": ["ala_1.JPG", "ala_2.JPG", "ala_3.JPG", "ala_4.JPG"],
        "desc": "رحلة لاكتشاف العلا التاريخية وجبالها الساحرة ومناظرها الفريدة."
    },
]
TRIP_MAP = {t["id"]: t for t in TRIPS}

GUIDES = [
    {"id": 1, "name": "سامي الحربي",    "city": "الرياض", "years": 7, "photo": "guide1.JPG"},
    {"id": 2, "name": "خالد الفيفي",    "city": "جدة",   "years": 5, "photo": "guide2.JPG"},
    {"id": 3, "name": "عبدالله الشهري", "city": "ينبع",  "years": 6, "photo": "guide3.JPG"},
    {"id": 4, "name": "ماجد القحطاني",  "city": "العلا", "years": 8, "photo": "guide4.JPG"},
]

REVIEWS = [
    {"name": "أحمد علي",     "city": "جدة",   "rating": 5, "text": "تجربة رائعة والتنظيم ممتاز. المرشد متعاون جدًا."},
    {"name": "سالم القحطاني","city": "الرياض","rating": 4, "text": "رحلة ممتعة وأسعار مناسبة. أنصح بها."},
    {"name": "ناصر الدوسري","city": "الدمام","rating": 5, "text": "العلا كانت مبهرة! شكرًا على الاحترافية."},
    {"name": "عبدالإله",     "city": "مكة",   "rating": 4, "text": "ينبع جميلة والأنشطة البحرية ممتعة."},
    {"name": "تركي الحربي",  "city": "المدينة","rating": 5, "text": "أفضل جولة قمت بها داخل المملكة."},
]

FAQS = [
    {"q": "كيف يمكنني حجز رحله؟", "a": "من صفحة الرحلات اختر الباقة واضغط \"احجز الآن\" ثم املأ النموذج."},
    {"q": "هل يوجد استرداد للمبلغ؟", "a": "نعم، حسب سياسة الإلغاء الموضحة في صفحة السياسة."},
    {"q": "هل الرحلات مناسبة للعائلات؟", "a": "نعم، نوفر باقات خاصة للعائلات والمدارس والشركات."},
    {"q": "هل السعر يشمل النقل؟", "a": "يعتمد على الباقة. راجع تفاصيل كل رحلة."},
    {"q": "كيف أتواصل معكم؟", "a": "عبر صفحة التواصل أو البريد الذي يصلك بعد تأكيد الحجز."},
    {"q": "هل يمكن تخصيص البرنامج؟", "a": "نعم، بالتنسيق مع المرشد قبل الموعد."},
]

# -------------------- أدوات مساعدة --------------------
def parse_date_or_none(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        return None

def next_invoice_number():
    year = datetime.utcnow().year
    prefix = f"INV-{year}-"
    last = (
        db.session.query(Booking)
        .filter(Booking.invoice_number.like(f"{prefix}%"))
        .order_by(Booking.invoice_number.desc())
        .first()
    )
    if last and last.invoice_number:
        try:
            n = int(last.invoice_number.split("-")[-1])
        except Exception:
            n = 0
    else:
        n = 0
    return f"{prefix}{n+1:04d}"

def send_email(to_email: str, subject: str, html: str):
    """إرسال بريد عبر SMTP (TLS). يتجاهل الإرسال لو لم تُضبط الإعدادات."""
    if not (SMTP["host"] and SMTP["user"] and SMTP["password"] and SMTP["from_email"]):
        return False
    msg = EmailMessage()
    msg["From"] = SMTP["from_email"]
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content("هذا بريد HTML، الرجاء عرضه بصيغة HTML.")
    msg.add_alternative(html, subtype="html")
    try:
        with smtplib.SMTP(SMTP["host"], SMTP["port"]) as s:
            s.starttls()
            s.login(SMTP["user"], SMTP["password"])
            s.send_message(msg)
        return True
    except Exception:
        return False

# -------------------- الصفحات العامة --------------------
@app.route("/")
def home():
    bookings_count = db.session.query(Booking).count()
    return render_template("home.html",
        trips=TRIPS, guides=GUIDES, reviews=REVIEWS[:6],
        bookings_count=bookings_count
    )

@app.route("/trips")
def trips():
    return render_template("trips.html", trips=TRIPS)

@app.route("/trips/<int:trip_id>")
def trip_details(trip_id):
    trip = TRIP_MAP.get(trip_id)
    if not trip:
        flash("الرحلة غير موجودة", "danger")
        return redirect(url_for("trips"))
    return render_template("trip_details.html", trip=trip)

@app.route("/guides")
def guides():
    return render_template("guides.html", guides=GUIDES)

# -------------------- إنشاء الحجز + بريد تأكيد --------------------
@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        trip_id = request.form.get("trip_id", "").strip()
        days = int(request.form.get("days", 1))
        total = int(request.form.get("total_amount", 0))

        trip = TRIP_MAP.get(int(trip_id)) if trip_id.isdigit() else None
        if not (name and email and phone and trip):
            flash("الرجاء تعبئة جميع الحقول واختيار رحلة صحيحة.", "danger")
            return redirect(url_for("book"))

        booking = Booking(
            name=name, email=email, phone=phone,
            trip_id=trip["id"], days=days, total=total,
            status="pending", invoice_number=next_invoice_number()
        )
        db.session.add(booking)
        db.session.commit()

        # بريد تأكيد إنشاء الحجز
        detail_url = url_for("booking_detail", booking_id=booking.id, _external=True)
        inv_url = url_for("booking_invoice_html", booking_id=booking.id, _external=True)
        email_html = render_template(
            "email_booking_created.html",
            booking=booking, trip=trip, company=COMPANY,
            detail_url=detail_url, inv_url=inv_url
        )
        send_email(booking.email, f"تأكيد حجزك — {COMPANY['name']}", email_html)

        flash(f"تم إرسال طلب الحجز بنجاح. رقم الفاتورة: {booking.invoice_number}", "success")
        return redirect(url_for("booking_detail", booking_id=booking.id))

    pre = request.args.get("trip_id", type=int)
    return render_template("booking.html", trips=TRIPS, preselect=pre or TRIPS[0]["id"])

# -------------------- صفحة تفاصيل الحجز (تبين التواصل بعد الدفع) --------------------
@app.route("/booking/<int:booking_id>")
def booking_detail(booking_id):
    b = Booking.query.get_or_404(booking_id)
    trip = TRIP_MAP.get(b.trip_id, {"name": str(b.trip_id), "price": 0, "images": []})
    return render_template("booking_detail.html", b=b, trip=trip, company=COMPANY)

# -------------------- بوابة دفع تجريبية --------------------
@app.route("/pay/<int:booking_id>", methods=["GET", "POST"])
def pay(booking_id):
    b = Booking.query.get_or_404(booking_id)
    trip = TRIP_MAP.get(b.trip_id, {"name": str(b.trip_id), "price": 0})
    if request.method == "POST":
        # هنا مكان ربط بوابة دفع حقيقية (تحقق التوقيع/المرجع، ثم وضع الحالة مدفوعة)
        b.status, b.paid_at = "paid", datetime.utcnow()
        if not b.invoice_number:
            b.invoice_number = next_invoice_number()
        db.session.commit()

        # بريد تأكيد الدفع
        detail_url = url_for("booking_detail", booking_id=b.id, _external=True)
        pdf_url = url_for("booking_invoice_pdf", booking_id=b.id, _external=True)
        email_html = render_template(
            "email_payment_paid.html",
            booking=b, trip=trip, company=COMPANY,
            detail_url=detail_url, pdf_url=pdf_url
        )
        send_email(b.email, f"تم استلام الدفع — {COMPANY['name']}", email_html)

        flash("تم الدفع بنجاح. شكرًا لك!", "success")
        return redirect(url_for("booking_detail", booking_id=b.id))
    return render_template("payment.html", b=b, trip=trip, company=COMPANY)

# -------------------- فواتير (عرض للمستخدم) --------------------
@app.route("/booking/<int:booking_id>/invoice")
def booking_invoice_html(booking_id):
    b = Booking.query.get_or_404(booking_id)
    trip = TRIP_MAP.get(b.trip_id, {"name": str(b.trip_id), "price": 0})
    return render_template("invoice.html", b=b, trip=trip, company=COMPANY)

@app.route("/booking/<int:booking_id>/invoice.pdf")
def booking_invoice_pdf(booking_id):
    b = Booking.query.get_or_404(booking_id)
    trip = TRIP_MAP.get(b.trip_id, {"name": str(b.trip_id), "price": 0})
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 18 * mm
    x = margin; y = height - margin

    c.setFont("Helvetica-Bold", 18)
    c.drawString(x, y, "فاتورة حجز — وجهة السعودية")
    y -= 8 * mm
    c.setFont("Helvetica", 11)
    c.drawString(x, y, f"رقم الفاتورة: {b.invoice_number or '-'}"); y -= 6 * mm
    c.drawString(x, y, f"تاريخ الإنشاء: {b.created_at.strftime('%Y-%m-%d %H:%M')}"); y -= 10 * mm

    c.setFont("Helvetica-Bold", 12); c.drawString(x, y, "بيانات العميل"); y -= 6 * mm
    c.setFont("Helvetica", 11)
    c.drawString(x, y, f"الاسم: {b.name}"); y -= 6 * mm
    c.drawString(x, y, f"البريد: {b.email}"); y -= 6 * mm
    c.drawString(x, y, f"الجوال: {b.phone}"); y -= 10 * mm

    c.setFont("Helvetica-Bold", 12); c.drawString(x, y, "تفاصيل الحجز"); y -= 6 * mm
    c.setFont("Helvetica", 11)
    c.drawString(x, y, f"الرحلة: {trip['name']}"); y -= 6 * mm
    c.drawString(x, y, f"سعر اليوم: {trip.get('price',0)} ر.س"); y -= 6 * mm
    c.drawString(x, y, f"عدد الأيام: {b.days}"); y -= 6 * mm
    c.drawString(x, y, f"الإجمالي: {b.total} ر.س"); y -= 12 * mm

    if b.status == "paid":
        c.setFont("Helvetica-Bold", 28); c.setFillColor(colors.green)
        c.drawString(width - 90*mm, height - 40*mm, "مدفوع")
        c.setFillColor(colors.black)
        if b.paid_at:
            c.setFont("Helvetica", 11)
            c.drawString(x, y, f"تاريخ الدفع: {b.paid_at.strftime('%Y-%m-%d %H:%M')}"); y -= 10 * mm

    c.setStrokeColor(colors.lightgrey); c.line(x, y, width - margin, y); y -= 8 * mm
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(x, y, "هذه الفاتورة صادرة آليًا. لأي استفسار الرجاء التواصل معنا.")
    c.showPage(); c.save()
    pdf = buffer.getvalue(); buffer.close()
    filename = f"invoice_{b.id}.pdf"
    return Response(pdf, mimetype="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )

# -------------------- صفحات إضافية قديمة/ثابتة --------------------
@app.route("/faq")     def faq():          return render_template("faq.html", faqs=FAQS)
@app.route("/policy")  def policy():       return render_template("policy.html")
@app.route("/reviews") def reviews_page(): return render_template("reviews.html", reviews=REVIEWS)

# -------------------- لوحة الإدارة (بدون تغيير كبير) --------------------
def parse_date_or_none_local(s):
    return parse_date_or_none(s)

def build_admin_query():
    q    = request.args.get("q", "").strip()
    sort = request.args.get("sort", "created_desc")
    start_str = request.args.get("start", "").strip()
    end_str   = request.args.get("end", "").strip()
    start_dt  = parse_date_or_none_local(start_str)
    end_dt    = parse_date_or_none_local(end_str)
    if end_dt: end_dt = end_dt + timedelta(days=1)

    query = Booking.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Booking.name.ilike(like)) |
            (Booking.email.ilike(like)) |
            (Booking.phone.ilike(like)) |
            (Booking.invoice_number.ilike(like))
        )
    if start_dt: query = query.filter(Booking.created_at >= start_dt)
    if end_dt:   query = query.filter(Booking.created_at < end_dt)

    sort_map = {
        "created_desc": Booking.created_at.desc(),
        "created_asc":  Booking.created_at.asc(),
        "total_desc":   Booking.total.desc(),
        "total_asc":    Booking.total.asc(),
        "days_desc":    Booking.days.desc(),
        "days_asc":     Booking.days.asc(),
        "name_asc":     Booking.name.asc(),
        "name_desc":    Booking.name.desc(),
    }
    return query.order_by(sort_map.get(sort, Booking.created_at.desc())), q, sort, (start_str or ""), (end_str or "")

@app.route("/admin")
def admin_dashboard():
    page = request.args.get("page", 1, type=int)
    per_page = 10
    query, q, sort, start_str, end_str = build_admin_query()
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    bookings = pagination.items
    return render_template(
        "admin_dashboard.html",
        bookings=bookings, trips=TRIPS, trip_map=TRIP_MAP,
        q=q, sort=sort, start=start_str, end=end_str,
        page=page, pages=pagination.pages, total=pagination.total,
        has_prev=pagination.has_prev, has_next=pagination.has_next
    )

@app.route("/admin/export.csv")
def admin_export_csv():
    query, *_ = build_admin_query()
    rows = query.all()
    si = StringIO(); w = csv.writer(si)
    w.writerow(["id","invoice_number","status","paid_at","name","email","phone","trip_id","trip_name","days","total","created_at"])
    for b in rows:
        trip_name = TRIP_MAP.get(b.trip_id, {}).get("name", b.trip_id)
        w.writerow([
            b.id, b.invoice_number or "", b.status or "", b.paid_at.strftime("%Y-%m-%d %H:%M") if b.paid_at else "",
            b.name, b.email, b.phone, b.trip_id, trip_name, b.days, b.total,
            b.created_at.strftime("%Y-%m-%d %H:%M")
        ])
    out = si.getvalue()
    fname = f"bookings_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(out, mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={fname}"}
    )

@app.route("/admin/export.xlsx")
def admin_export_xlsx():
    query, *_ = build_admin_query()
    rows = query.all()
    wb = Workbook(); ws = wb.active; ws.title = "Bookings"
    headers = ["ID","Invoice","Status","Paid At","Name","Email","Phone","Trip ID","Trip Name","Days","Total (SAR)","Created At"]
    ws.append(headers)
    for b in rows:
        trip_name = TRIP_MAP.get(b.trip_id, {}).get("name", b.trip_id)
        ws.append([
            b.id, b.invoice_number or "", b.status or "", b.paid_at.strftime("%Y-%m-%d %H:%M") if b.paid_at else "",
            b.name, b.email, b.phone, b.trip_id, trip_name, b.days, b.total,
            b.created_at.strftime("%Y-%m-%d %H:%M")
        ])
    bio = BytesIO(); wb.save(bio); bio.seek(0)
    fname = f"bookings_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return Response(
        bio.read(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={fname}"}
    )

@app.route("/admin/booking/<int:booking_id>/delete", methods=["POST"])
def admin_delete_booking(booking_id):
    b = Booking.query.get_or_404(booking_id)
    db.session.delete(b); db.session.commit()
    flash("تم حذف الحجز بنجاح.", "success")
    return redirect(url_for("admin_dashboard", **{k: v for k,v in request.args.items()}))

@app.route("/admin/booking/<int:booking_id>/edit", methods=["GET","POST"])
def admin_edit_booking(booking_id):
    b = Booking.query.get_or_404(booking_id)
    if request.method == "POST":
        name   = request.form.get("name","").strip()
        email  = request.form.get("email","").strip()
        phone  = request.form.get("phone","").strip()
        trip_id= request.form.get("trip_id","").strip()
        days   = int(request.form.get("days", b.days) or b.days)
        total  = int(request.form.get("total", b.total) or b.total)
        status = request.form.get("status", b.status or "pending").strip()

        if not (name and email and phone and trip_id.isdigit() and int(trip_id) in TRIP_MAP):
            flash("الرجاء تعبئة جميع الحقول بشكل صحيح.", "danger")
            return redirect(url_for("admin_edit_booking", booking_id=booking_id))

        b.name, b.email, b.phone = name, email, phone
        b.trip_id, b.days, b.total = int(trip_id), days, total

        if status not in ("pending","paid"):
            status = "pending"
        if status == "paid" and b.status != "paid":
            b.status, b.paid_at = "paid", datetime.utcnow()
            if not b.invoice_number:
                b.invoice_number = next_invoice_number()
        elif status == "pending" and b.status != "pending":
            b.status, b.paid_at = "pending", None

        db.session.commit()
        flash("تم تعديل الحجز بنجاح.", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_edit_booking.html", b=b, trips=TRIPS, trip_map=TRIP_MAP)

@app.route("/admin/booking/<int:booking_id>/mark_paid", methods=["POST"])
def admin_mark_paid(booking_id):
    b = Booking.query.get_or_404(booking_id)
    b.status, b.paid_at = "paid", datetime.utcnow()
    if not b.invoice_number:
        b.invoice_number = next_invoice_number()
    db.session.commit()

    # بريد: إشعار دفع
    trip = TRIP_MAP.get(b.trip_id, {"name": str(b.trip_id), "price": 0})
    detail_url = url_for("booking_detail", booking_id=b.id, _external=True)
    pdf_url = url_for("booking_invoice_pdf", booking_id=b.id, _external=True)
    email_html = render_template(
        "email_payment_paid.html",
        booking=b, trip=trip, company=COMPANY,
        detail_url=detail_url, pdf_url=pdf_url
    )
    send_email(b.email, f"تم استلام الدفع — {COMPANY['name']}", email_html)

    flash("تم تعليم الحجز كمدفوع.", "success")
    return redirect(url_for("admin_dashboard", **{k: v for k,v in request.args.items()}))

@app.route("/admin/booking/<int:booking_id>/mark_pending", methods=["POST"])
def admin_mark_pending(booking_id):
    b = Booking.query.get_or_404(booking_id)
    b.status, b.paid_at = "pending", None
    db.session.commit()
    flash("تم إرجاع الحجز إلى حالة الانتظار.", "success")
    return redirect(url_for("admin_dashboard", **{k: v for k,v in request.args.items()}))

# ----- ملفات PWA ثابتة -----
@app.route("/service-worker.js")
def sw():
    return send_from_directory("static", "service-worker.js", mimetype="application/javascript")

@app.route("/manifest.webmanifest")
def manifest():
    return send_from_directory("static", "manifest.webmanifest", mimetype="application/manifest+json")

@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt")

with app.app_context():
    db.create_all()
    try:
        _safe_upgrade_table()
    except Exception:
        pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))