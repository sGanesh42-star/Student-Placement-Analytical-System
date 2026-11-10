from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, get_db
from model import predict_placement

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Enter all details. Password must be at least 6 characters.", "danger")
            return redirect(url_for("signup"))
        db = get_db()
        try:
            db.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
                       (name, email, generate_password_hash(password), "student"))
            db.commit()
        except Exception:
            flash("This email may already be registered.", "danger")
            return redirect(url_for("signup"))
        flash("Account created. Please login.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            return redirect(url_for("admin" if user["role"] == "admin" else "dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")

def login_required():
    if "user_id" not in session:
        flash("Please login to continue.", "warning")
        return False
    return True

@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))
    db = get_db()
    total = db.execute("SELECT COUNT(*) n FROM predictions WHERE user_id=?", (session["user_id"],)).fetchone()["n"]
    placed = db.execute("SELECT COUNT(*) n FROM predictions WHERE user_id=? AND result='Placed'", (session["user_id"],)).fetchone()["n"]
    recent = db.execute("SELECT * FROM predictions WHERE user_id=? ORDER BY created_at DESC LIMIT 5", (session["user_id"],)).fetchall()
    return render_template("dashboard.html", total=total, placed=placed, recent=recent)

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if not login_required():
        return redirect(url_for("login"))
    result = None
    probability = None
    if request.method == "POST":
        try:
            cgpa = float(request.form["cgpa"])
            aptitude = float(request.form["aptitude"])
            communication = float(request.form["communication"])
            internships = int(request.form["internships"])
            projects = int(request.form["projects"])
            if not (0 <= cgpa <= 10 and 0 <= aptitude <= 100 and 0 <= communication <= 100
                    and 0 <= internships <= 20 and 0 <= projects <= 20):
                raise ValueError
            result, probability = predict_placement(cgpa, aptitude, communication, internships, projects)
            db = get_db()
            db.execute("""INSERT INTO predictions(user_id,cgpa,aptitude,communication,internships,projects,result,probability)
                          VALUES(?,?,?,?,?,?,?,?)""",
                       (session["user_id"], cgpa, aptitude, communication, internships, projects, result, probability))
            db.commit()
        except (ValueError, KeyError):
            flash("Please enter valid values within the given ranges.", "danger")
    return render_template("predict.html", result=result, probability=probability)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not login_required():
        return redirect(url_for("login"))
    db = get_db()
    user = db.execute("SELECT name,email FROM users WHERE id=?", (session["user_id"],)).fetchone()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name:
            db.execute("UPDATE users SET name=? WHERE id=?", (name, session["user_id"]))
            db.commit()
            session["name"] = name
            flash("Profile updated.", "success")
            return redirect(url_for("profile"))
    return render_template("profile.html", user=user)

@app.route("/admin")
def admin():
    if "user_id" not in session or session.get("role") != "admin":
        flash("Admin access required.", "warning")
        return redirect(url_for("login"))
    db = get_db()
    users = db.execute("SELECT id,name,email,role FROM users ORDER BY id DESC").fetchall()
    predictions = db.execute("SELECT p.*,u.name student FROM predictions p JOIN users u ON p.user_id=u.id ORDER BY p.created_at DESC").fetchall()
    count = db.execute("SELECT COUNT(*) n FROM predictions").fetchone()["n"]
    placed = db.execute("SELECT COUNT(*) n FROM predictions WHERE result='Placed'").fetchone()["n"]
    return render_template("admin.html", users=users, predictions=predictions, count=count, placed=placed)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out.", "info")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
