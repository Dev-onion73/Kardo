from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for sessions

API_URL = "http://127.0.0.1:5000"  # Your backend URL

# -------- LOGIN --------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        # Select backend login endpoint
        endpoint = "/auth/login" if role != "business" else "/auth/login/business"
        resp = requests.post(API_URL + endpoint, json={"email": email, "password": password})

        if resp.status_code == 200:
            session["token"] = resp.json()["token"]
            session["role"] = role
            return redirect(url_for("dashboard"))
        else:
            flash(resp.json().get("error", "Login failed"))

    return render_template("login.html")


# -------- DASHBOARD ROUTE --------
@app.route("/dashboard")
def dashboard():
    token = session.get("token")
    role = session.get("role")
    if not token:
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}

    if role == "admin":
        users = requests.get(API_URL + "/admin/users", headers=headers).json()
        businesses = requests.get(API_URL + "/admin/businesses", headers=headers).json()
        transactions = requests.get(API_URL + "/admin/transactions", headers=headers).json()
        return render_template("dashboard_admin.html", users=users, businesses=businesses, transactions=transactions)

    elif role == "business":
        memberships = requests.get(API_URL + "/business/memberships", headers=headers).json()
        transactions = requests.get(API_URL + "/business/transactions", headers=headers).json()
        return render_template("dashboard_business.html", memberships=memberships, transactions=transactions)

    elif role == "customer":
        memberships = requests.get(API_URL + "/customer/memberships", headers=headers).json()
        transactions = requests.get(API_URL + "/customer/transactions", headers=headers).json()
        return render_template("dashboard_customer.html", memberships=memberships, transactions=transactions)

    else:
        flash("Invalid role")
        return redirect(url_for("login"))


# -------- REGISTRATION PAGES --------
@app.route("/register/customer", methods=["GET", "POST"])
def register_customer():
    if request.method == "POST":
        data = {
            "email": request.form["email"],
            "password": request.form["password"],
            "full_name": request.form["full_name"]
        }
        resp = requests.post(API_URL + "/auth/register/customer", json=data)
        if resp.status_code == 201:
            flash("Customer registered successfully!")
            return redirect(url_for("login"))
        else:
            flash(resp.json().get("error", "Registration failed"))
    return render_template("register_customer.html")


@app.route("/register/business", methods=["GET", "POST"])
def register_business():
    if request.method == "POST":
        data = {
            "name": request.form["name"],
            "category": request.form.get("category"),
            "contact_email": request.form["contact_email"],
            "contact_phone": request.form.get("contact_phone"),
            "password": request.form["password"]
        }
        resp = requests.post(API_URL + "/auth/register/business", json=data)
        if resp.status_code == 201:
            flash("Business registered successfully!")
            return redirect(url_for("login"))
        else:
            flash(resp.json().get("error", "Registration failed"))
    return render_template("register_business.html")


# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Frontend runs on 5001
