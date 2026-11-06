
from flask import (
    Flask, request, redirect, url_for,
    session, render_template_string
)
import sqlite3
import os
import hmac
from datetime import date

app = Flask(__name__)

# Change these before publishing!
app.secret_key = os.environ.get(
    "SECRET_KEY", "change-this-secret-before-publishing"
)
ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD", "change-this-password"
)

DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "wedding_rsvps.db"
)

WEDDING_DATE = "2027-12-04"

def connect_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with connect_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS rsvps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                attendance TEXT NOT NULL,
                guests INTEGER NOT NULL,
                message TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

init_db()

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#526449">
<title>Aldré & Lee | Our Wedding</title>
<meta name="description"
content="Join Aldré and Lee to celebrate their garden wedding on 4 December 2027.">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Cormorant+Garamond:wght@400;500;600&family=Montserrat:wght@300;400;500&display=swap"
rel="stylesheet">

<style>
:root {
 --olive:#626b43;
 --sage:#829078;
 --emerald:#365844;
 --plum:#633b52;
 --mauve:#b28a9e;
 --ivory:#faf6ed;
 --champagne:#d8c39b;
 --ink:#403c37;
}
* { box-sizing:border-box; }
html { scroll-behavior:smooth; }
body {
 margin:0;
 background:var(--ivory);
 color:var(--ink);
 font-family:Montserrat,sans-serif;
 font-size:14px;
}
a { color:var(--plum); }
button,input,select,textarea { font:inherit; }
.hero {
 min-height:94vh;
 padding:65px 22px;
 display:flex;
 flex-direction:column;
 justify-content:center;
 align-items:center;
 text-align:center;
 position:relative;
 overflow:hidden;
 background:
 linear-gradient(#f8f3e7b8,#f8f3e7df),
 url("https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=1800&q=85")
 center/cover;
}
.hero:before {
 content:"";
 position:absolute;
 inset:14px;
 border:1px solid var(--champagne);
 pointer-events:none;
}
.hero-content { max-width:750px; position:relative; }
.eyebrow {
 text-transform:uppercase;
 letter-spacing:4px;
 font-size:10px;
 line-height:2;
}
.script {
 font-family:"Great Vibes",cursive;
 color:var(--plum);
 font-weight:400;
}
h1 {
 font-size:clamp(64px,12vw,112px);
 line-height:1.12;
 margin:22px 0;
}
.amp {
 color:var(--olive);
 font-size:.68em;
}
.subtitle {
 font-family:"Cormorant Garamond",serif;
 font-size:25px;
}
.rule {
 width:76px;
 height:1px;
 background:var(--champagne);
 margin:24px auto;
}
.date {
 letter-spacing:3px;
 font-size:12px;
}
.btn {
 display:inline-block;
 border:1px solid var(--olive);
 background:var(--olive);
 color:#fffdf7;
 padding:15px 24px;
 text-decoration:none;
 letter-spacing:2px;
 font-size:10px;
 cursor:pointer;
 margin-top:15px;
}
.btn:hover { background:var(--plum); }
nav {
 display:flex;
 justify-content:center;
 gap:22px;
 flex-wrap:wrap;
 padding:19px 10px;
 background:var(--emerald);
}
nav a {
 color:#fffaf0;
 text-decoration:none;
 font-size:10px;
 letter-spacing:1px;
}
section {
 padding:72px 20px;
 text-align:center;
 scroll-margin-top:20px;
}
.section-inner { max-width:720px; margin:auto; }
.section-title {
 font:400 48px "Great Vibes",cursive;
 color:var(--plum);
 margin:12px 0;
}
.lead {
 font:400 21px "Cormorant Garamond",serif;
 line-height:1.7;
}
p { line-height:1.9; }
.small {
 font-size:10px;
 text-transform:uppercase;
 letter-spacing:3px;
 color:var(--olive);
}
.paper {
 max-width:540px;
 margin:25px auto 0;
 padding:32px 25px;
 background:#fffdf8;
 border:1px solid #e5d9c4;
 box-shadow:0 8px 25px #4b39240c;
}
.countdown {
 display:flex;
 justify-content:center;
 gap:18px;
 flex-wrap:wrap;
 margin:25px 0;
}
.time { min-width:65px; }
.time strong {
 display:block;
 color:var(--emerald);
 font:500 34px "Cormorant Garamond",serif;
}
.time span {
 font-size:9px;
 letter-spacing:1px;
 text-transform:uppercase;
}
.details {
 background:#eeeadf;
}
.detail-label {
 color:var(--olive);
 font-size:10px;
 letter-spacing:3px;
 margin-top:25px;
}
form { text-align:left; }
label {
 display:block;
 font-size:11px;
 margin:16px 0 7px;
 color:var(--emerald);
}
input,select,textarea {
 width:100%;
 padding:13px;
 border:1px solid #d9cfbd;
 background:#fffefa;
 color:var(--ink);
 border-radius:0;
}
textarea { min-height:90px; resize:vertical; }
form .btn { width:100%; }
.notice {
 padding:12px;
 background:#eeeadf;
 text-align:center;
 margin-bottom:15px;
}
footer {
 text-align:center;
 background:var(--emerald);
 color:#fff8e9;
 padding:35px 20px;
}
footer .script { color:#e4c9d6; font-size:37px; }
.admin-table {
 overflow-x:auto;
 max-width:100%;
}
table { border-collapse:collapse; width:100%; font-size:12px; }
td,th { border-bottom:1px solid #ddd; padding:10px; text-align:left; }
@media(max-width:480px) {
 section { padding:55px 17px; }
 .paper { padding:25px 18px; }
 nav { gap:13px; }
}
</style>
</head>

<body>
<nav>
<a href="#home">HOME</a>
<a href="#our-day">OUR DAY</a>
<a href="#details">THE DETAILS</a>
<a href="#rsvp">RSVP</a>
</nav>

<header class="hero" id="home">
<div class="hero-content">
<p class="eyebrow">Together with our families</p>
<p class="script" style="font-size:37px;margin-bottom:0">
With love and joy
</p>
<h1 class="script">
Aldré <span class="amp">&</span> Lee
</h1>
<div class="rule"></div>
<p class="eyebrow">Invite you to celebrate their wedding</p>
<p class="subtitle">A day of love, laughter and forever</p>
<p class="date">SATURDAY · 4 DECEMBER 2027</p>
<a class="btn" href="#rsvp">KINDLY RSVP ♡</a>
</div>
</header>

<section id="our-day">
<div class="section-inner">
<p class="small">Our forever begins</p>
<h2 class="section-title">Counting down to I do</h2>
<p class="lead">
Two hearts, one beautiful adventure, and a lifetime
of memories waiting to be made.
</p>
<div class="paper">
<p class="small">Our wedding day</p>
<div class="countdown">
<div class="time"><strong id="days">--</strong><span>Days</span></div>
<div class="time"><strong id="hours">--</strong><span>Hours</span></div>
<div class="time"><strong id="minutes">--</strong><span>Minutes</span></div>
<div class="time"><strong id="seconds">--</strong><span>Seconds</span></div>
</div>
<p>We cannot wait to celebrate with you.</p>
</div>
</div>
</section>

<section class="details" id="details">
<div class="section-inner">
<p class="small">The celebration</p>
<h2 class="section-title">The Wedding Details</h2>
<div class="paper">
<p class="detail-label">THE DATE</p>
<p class="lead">Saturday, 4 December 2027</p>

<div class="rule"></div>
<p class="detail-label">THE VENUE</p>
<p class="lead">MoyaWaaihoek</p>
<p>Venue address and directions will be added here.</p>

<div class="rule"></div>
<p class="detail-label">THE TIME</p>
<p>Please check back for ceremony time.</p>

<div class="rule"></div>
<p class="detail-label">DRESS CODE</p>
<p>Garden wedding elegance</p>

<p style="font-size:12px">
More details will be shared as the day approaches.
</p>
</div>
</div>
</section>

<section id="rsvp">
<div class="section-inner">
<p class="small">We saved you a seat</p>
<h2 class="section-title">Kindly RSVP</h2>
<p class="lead">
Your presence would mean the world to us.
Please let us know if you can join our celebration.
</p>

<div class="paper">
{% if message %}
<div class="notice">{{ message }}</div>
{% endif %}

<form method="POST" action="/rsvp">
<label for="name">Your full name *</label>
<input id="name" name="name" maxlength="100"
autocomplete="name" required placeholder="Enter your full name">

<label for="email">Email address (optional)</label>
<input id="email" name="email" type="email"
maxlength="150" placeholder="you@example.com">

<label for="attendance">Will you be joining us? *</label>
<select id="attendance" name="attendance" required>
<option value="">Please choose</option>
<option value="Yes">Joyfully accepts ♡</option>
<option value="No">Regretfully declines</option>
</select>

<label for="guests">Number of people in your party *</label>
<select id="guests" name="guests" required>
<option value="1">1 person</option>
<option value="2">2 people</option>
<option value="3">3 people</option>
<option value="4">4 people</option>
<option value="5">5 people</option>
</select>

<label for="message">A little message for the couple (optional)</label>
<textarea id="message" name="message" maxlength="500"
placeholder="Leave us a note..."></textarea>

<button class="btn" type="submit">SEND OUR RSVP ♡</button>
</form>

<p style="font-size:11px">
Please submit one response per household.
Only include guests who have been invited.
</p>
</div>
</div>
</section>

<footer>
<p class="script">Aldré & Lee</p>
<p>4 December 2027 · MoyaWaaihoek</p>
<p>Made with love, for our favourite people.</p>
</footer>

<script>
const target = new Date("2027-12-04T14:00:00");

function updateCountdown() {
  let diff = target.getTime() - Date.now();

  if (diff <= 0) {
    document.getElementById("days").textContent = "♡";
    document.getElementById("hours").textContent = "♡";
    document.getElementById("minutes").textContent = "♡";
    document.getElementById("seconds").textContent = "♡";
    return;
  }

  const d = Math.floor(diff / 86400000);
  const h = Math.floor((diff % 86400000) / 3600000);
  const m = Math.floor((diff % 3600000) / 60000);
  const s = Math.floor((diff % 60000) / 1000);

  document.getElementById("days").textContent = d;
  document.getElementById("hours").textContent = h;
  document.getElementById("minutes").textContent = m;
  document.getElementById("seconds").textContent = s;
}
updateCountdown();
setInterval(updateCountdown, 1000);
</script>
</body>
</html>
"""

@app.route("/")
def home():
    message = request.args.get("message", "")
    return render_template_string(PAGE, message=message)

@app.route("/rsvp", methods=["POST"])
def rsvp():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    attendance = request.form.get("attendance", "")
    guests = request.form.get("guests", "")
    note = request.form.get("message", "").strip()

    if (
        not name or len(name) > 100
        or len(email) > 150
        or attendance not in ("Yes", "No")
        or guests not in ("1", "2", "3", "4", "5")
        or len(note) > 500
    ):
        return redirect(url_for(
            "home", message="Please check your details and try again."
        ))

    with connect_db() as db:
        db.execute("""
            INSERT INTO rsvps
            (name, email, attendance, guests, message)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, attendance, int(guests), note))

    return redirect(url_for(
        "home", message="Thank you! Your RSVP has been received ♡"
    ))

ADMIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wedding RSVPs</title>
<style>
body {font-family:Arial;background:#faf6ed;color:#403c37;
padding:20px;max-width:1000px;margin:auto}
input,button {padding:12px;margin:6px 0}
table {border-collapse:collapse;width:100%;font-size:12px}
td,th {padding:9px;border-bottom:1px solid #ccc;text-align:left}
.wrap {overflow-x:auto}
</style>
</head>
<body>
<h1>Aldré & Lee — RSVP Dashboard</h1>

{% if not logged_in %}
<form method="POST" action="/admin">
<label>Admin password</label><br>
<input name="password" type="password" required>
<button type="submit">Log in</button>
</form>
{% else %}
<p><b>Total responses:</b> {{ rows|length }}</p>
<p><b>Acceptances:</b> {{ accepted }}</p>
<p><b>Declines:</b> {{ declined }}</p>
<p><a href="/admin/logout">Log out</a></p>
<div class="wrap">
<table>
<tr><th>Name</th><th>Email</th><th>Attendance</th>
<th>Party size</th><th>Message</th><th>Submitted</th></tr>
{% for r in rows %}
<tr>
<td>{{ r['name'] }}</td>
<td>{{ r['email'] }}</td>
<td>{{ r['attendance'] }}</td>
<td>{{ r['guests'] }}</td>
<td>{{ r['message'] }}</td>
<td>{{ r['submitted_at'] }}</td>
</tr>
{% endfor %}
</table>
</div>
{% endif %}
</body>
</html>
"""

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password", "")
        if hmac.compare_digest(password, ADMIN_PASSWORD):
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))

    if not session.get("admin_logged_in"):
        return render_template_string(
            ADMIN_PAGE, logged_in=False
        )

    with connect_db() as db:
        rows = db.execute(
            "SELECT * FROM rsvps ORDER BY submitted_at DESC"
        ).fetchall()

    accepted = sum(r["attendance"] == "Yes" for r in rows)
    declined = sum(r["attendance"] == "No" for r in rows)

    return render_template_string(
        ADMIN_PAGE, logged_in=True, rows=rows,
        accepted=accepted, declined=declined
    )

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)