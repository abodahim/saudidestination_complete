import os, uuid, smtplib
from email.message import EmailMessage
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_from_directory, session,
    abort, make_response
)

# (اختياري) دعم PDF عبر WeasyPrint
WEASYPRINT_AVAILABLE = False
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except Exception:
    WEASYPRINT_AVAILABLE = False

# -----------------------------------
# إعداد التطبيق
# -----------------------------------
app = Flask(__name__, static_url_path="/static", static_folder="static", template_folder="templates")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret")

# إعدادات البريد
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USER)
EMAIL_BCC  = os.getenv("EMAIL_BCC")
BASE_URL   = os.getenv("BASE_URL")

# بيانات الشركة
COMPANY_NAME     = os.getenv("COMPANY_NAME", "وجهة السعودية")
COMPANY_TAX_ID   = os.getenv("COMPANY_TAX_ID", "3100000000")
COMPANY_VAT_RATE = float(os.getenv("COMPANY_VAT_RATE", "15"))
COMPANY_ADDRESS  = os.getenv("COMPANY_ADDRESS", "المملكة العربية السعودية")
COMPANY_PHONE    = os.getenv("COMPANY_PHONE", "+9665XXXXXXX")
COMPANY_EMAIL    = os.getenv("COMPANY_EMAIL", "info@example.com")
COMPANY_WEBSITE  = os.getenv("COMPANY_WEBSITE", "https://saudidestination.com")

CURRENCY = "ر.س"

# -----------------------------------
# إرسال البريد
# -----------------------------------
def send_email(to_email, subject, html_body, text_body=None, bcc=None, attachments=None):
    if not all([EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, EMAIL_FROM]):
        print("Email settings missing; skipping send.")
        return False
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = EMAIL_FROM
    msg["To"]      = to_email
    if bcc:
        msg["Bcc"] = bcc
    msg.set_content(text_body or "تم تأكيد حجزك.")
    msg.add_alternative(html_body, subtype="html")
    if attachments:
        for att in attachments:
            fname = att["filename"]; data = att["data"]; mime = att["mime"]
            maintype, _, subtype = mime.partition("/")
            msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=fname)
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls(); smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print("Email send error:", e)
        return False

# -----------------------------------
# بيانات الرحلات والمرشدين
# -----------------------------------
TRIPS = [
    {"id":1, "name":"رحلة جدة","default_guide_id":1,"price":299,
     "description":"جولة بحرية وثقافية في جدة.",
     "itinerary":{1:"الاستقبال وزيارة الكورنيش",2:"البلد التاريخية",3:"أنشطة اختيارية"}},
    {"id":2, "name":"رحلة الرياض","default_guide_id":2,"price":349,
     "description":"اكتشاف الرياض: المتحف والدرعية.",
     "itinerary":{1:"زيارة المتحف الوطني",2:"الدرعية التاريخية",3:"أنشطة ترفيهية"}},
    {"id":3, "name":"رحلة ينبع","default_guide_id":3,"price":399,
     "description":"رحلة ساحلية في ينبع.",
     "itinerary":{1:"شواطئ وأنشطة",2:"الواجهة البحرية",3:"رحلة بحرية"}},
]
GUIDES = [
    {"id":1,"name":"أحمد السبيعي","city":"جدة","phone":"+966500000001","whatsapp":"+966500000001","img":"images/guide1.PNG","bio":"خبير بجدة."},
    {"id":2,"name":"سارة العتيبي","city":"الرياض","phone":"+966500000002","whatsapp":"+966500000002","img":"images/guide1.PNG","bio":"خبيرة بالرياض."},
    {"id":3,"name":"خالد الزهراني","city":"ينبع","phone":"+966500000003","whatsapp":"+966500000003","img":"images/guide1.PNG","bio":"متخصص بالأنشطة البحرية."},
]

def get_trip(trip_id): return next((t for t in TRIPS if t["id"]==int(trip_id)), None)
def get_guide(guide_id): return next((g for g in GUIDES if g["id"]==int(guide_id)), None)
def calc_totals(price, vat): subtotal=price; vat_amt=round(price*vat/100,2); return subtotal,vat_amt,subtotal+vat_amt

def get_pending(): return session.setdefault("pending_bookings",{})
def get_confirmed(): return session.setdefault("confirmed_bookings",{})

# -----------------------------------
# الصفحات العامة
# -----------------------------------
@app.route("/")
def home(): return render_template("home.html",active="home",trips=TRIPS,guides=GUIDES,currency=CURRENCY)
@app.route("/trips")
def trips(): return render_template("trips.html",active="trips",trips=TRIPS,currency=CURRENCY)
@app.route("/trips/<int:trip_id>")
def trip_details(trip_id):
    trip = next((t for t in TRIPS if t["id"] == trip_id), None)
    if not trip:
        abort(404)
    return render_template("trip_details.html", trip=trip, currency=CURRENCY, active="trips")
@app.route("/guides")
def guides(): return render_template("guides.html",active="guides",guides=GUIDES)
@app.route("/gallery")
def gallery(): return render_template("gallery.html",active="gallery")
@app.route("/reviews")
def reviews(): return render_template("reviews.html",active="reviews")
@app.route("/contact",methods=["GET","POST"])
def contact():
    if request.method=="POST":
        flash("تم استلام رسالتك.","success"); return redirect(url_for("thank_you"))
    return render_template("contact.html",active="contact")

# -----------------------------------
# الحجز والدفع
# -----------------------------------
@app.route("/booking",methods=["GET","POST"])
def booking():
    if request.method=="POST":
        name,email,phone=request.form.get("name"),request.form.get("email"),request.form.get("phone")
        trip_id,guide_id=request.form.get("trip_id"),request.form.get("guide_id")
        if not all([name,email,phone,trip_id]): flash("أكمل البيانات","danger"); return redirect(url_for("booking"))
        trip=get_trip(trip_id); guide=get_guide(guide_id or trip["default_guide_id"])
        booking_id=uuid.uuid4().hex[:8].upper()
        get_pending()[booking_id]={"booking_id":booking_id,"name":name,"email":email,"phone":phone,"trip_id":trip["id"],"trip_name":trip["name"],"guide_id":guide["id"]}
        session.modified=True; return redirect(url_for("payment",booking_id=booking_id))
    return render_template("booking.html",active="booking",trips=TRIPS,guides=GUIDES,vat_rate=COMPANY_VAT_RATE,currency=CURRENCY)

@app.route("/payment",methods=["GET","POST"])
def payment():
    booking_id=request.args.get("booking_id") or request.form.get("booking_id")
    booking=get_pending().get(booking_id)
    if not booking: flash("لا يوجد حجز","danger"); return redirect(url_for("booking"))
    trip=get_trip(booking["trip_id"]); subtotal,vat_amt,total=calc_totals(trip["price"],COMPANY_VAT_RATE)
    if request.method=="POST":
        get_confirmed()[booking_id]={**booking,"price":trip["price"],"subtotal":subtotal,"vat_amount":vat_amt,"total":total}
        get_pending().pop(booking_id,None); session.modified=True
        flash("تم الدفع","success"); return redirect(url_for("receipt",booking_id=booking_id))
    return render_template("payment.html",booking=booking,trip=trip,subtotal=subtotal,vat_amount=vat_amt,total=total,vat_rate=COMPANY_VAT_RATE,currency=CURRENCY)

@app.route("/receipt/<booking_id>")
def receipt(booking_id):
    booking=get_confirmed().get(booking_id)
    if not booking: return render_template("receipt_locked.html",booking_id=booking_id)
    trip=get_trip(booking["trip_id"]); guide=get_guide(booking["guide_id"])
    return render_template("receipt.html",booking=booking,trip=trip,guide=guide,currency=CURRENCY,company=dict(name=COMPANY_NAME,tax_id=COMPANY_TAX_ID,address=COMPANY_ADDRESS,phone=COMPANY_PHONE,email=COMPANY_EMAIL,website=COMPANY_WEBSITE))

@app.route("/thank-you")
def thank_you(): return render_template("thank_you.html")

# -----------------------------------
# إدارة (مبدئي)
# -----------------------------------
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        if request.form.get("username")=="admin" and request.form.get("password")=="admin":
            flash("تم الدخول","success"); return redirect(url_for("admin_dashboard"))
        flash("خطأ في البيانات","danger")
    return render_template("login.html")
@app.route("/admin")
def admin_dashboard(): return render_template("admin_dashboard.html")

# -----------------------------------
# ملفات ثابتة
# -----------------------------------
@app.route("/service-worker.js")
def service_worker(): return send_from_directory("static","service-worker.js")
@app.route("/manifest.webmanifest")
def manifest(): return send_from_directory("static","manifest.webmanifest")
@app.route("/robots.txt")
def robots(): return send_from_directory("static","robots.txt")

# -----------------------------------
if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT",5000)))