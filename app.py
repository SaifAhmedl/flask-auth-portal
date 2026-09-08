from flask import Flask, redirect, render_template, request, session, url_for
from itsdangerous import BadTimeSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "secret_key_flask_auth_portal"

serializer = URLSafeTimedSerializer(app.secret_key)

# In-memory storage for users
users_db = {}


@app.route("/")
def index():
  if "user" in session:
    return redirect(url_for("dashboard"))
  return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
  if request.method == "POST":
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not username or not email or not password:
      return "All fields are required. <a href='/register'>Back</a>", 400

    if email in users_db:
      return "Email already registered. <a href='/register'>Back</a>", 400

    users_db[email] = {
        "username": username,
        "password": generate_password_hash(password),
        "is_verified": False,
    }

    # Generate email verification token
    token = serializer.dumps(email, salt="email-confirm")
    verify_url = url_for("verify_email", token=token, _external=True)

    return f"""
        <h3>Account registered!</h3>
        <p>Click below to verify your email address:</p>
        <p><a href="{verify_url}">{verify_url}</a></p>
        """

  return render_template("register.html")


@app.route("/verify/<token>")
def verify_email(token):
  try:
    email = serializer.loads(token, salt="email-confirm", max_age=1800)
  except (SignatureExpired, BadTimeSignature):
    return (
        "Verification link expired or invalid. <a href='/register'>Register"
        " again</a>"
    )

  if email in users_db:
    users_db[email]["is_verified"] = True
    return (
        "Email successfully verified! <a href='/login'>Click here to login</a>"
    )

  return "User not found."


@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    user = users_db.get(email)

    if not user or not check_password_hash(user["password"], password):
      return "Invalid email or password. <a href='/login'>Try again</a>", 401

    if not user["is_verified"]:
      return (
          "Please verify your email first. <a href='/login'>Back to login</a>",
          403,
      )

    session["user"] = user["username"]
    return redirect(url_for("dashboard"))

  return render_template("login.html")


@app.route("/dashboard")
def dashboard():
  if "user" not in session:
    return redirect(url_for("login"))
  return render_template("dashboard.html", username=session["user"])


@app.route("/logout")
def logout():
  session.clear()
  return redirect(url_for("login"))


if __name__ == "__main__":
  app.run(debug=True, port=5000)