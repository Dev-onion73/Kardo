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
            if role == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("dashboard"))
        else:
            flash(resp.json().get("error", "Login failed"))

    return render_template("login.html")


# -------- DASHBOARD ROUTE --------
@app.route("/admin")
def admin_dashboard():
    return render_template("dashboard/admin.html")

@app.route("/admin/users")
def admin_users():
    token = session.get("token")
    role = session.get("role")
    if not token:
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}
    users = requests.get(API_URL + "/admin/users", headers=headers).json()
    return render_template("admin/users.html",users=users)


@app.route('/admin/users/add', methods=["POST"])
def add_user():
    form_data = {
        "full_name": request.form.get('full_name', '').strip(),
        "email": request.form.get('email', '').strip(),
        "password": request.form.get('password', '').strip(),
        "role": request.form.get('role', 'customer').strip()
    }

    for value in form_data.values():
        if not value:
            flash("Input Error: All fields are required.", "info")
            return redirect(url_for("admin_users")) # Assuming the users page route is 'admin_users'


    # Prepare API call
    api_url = f"{API_URL}/admin/users" # Replace API_URL with your actual base URL
    token = session.get("token")
    role = session.get("role")
    if not token:
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(api_url, json=form_data, headers=headers)
        response_data = response.json()

        if response.status_code == 201:
            flash(f"User {form_data['full_name']} added successfully!", "success")
        elif response.status_code == 409:
            flash(f"Error: {response_data.get('error', 'User already exists.')}", "error")
        elif response.status_code == 400:
            flash(f"Error: {response_data.get('error', 'Invalid data provided.')}", "error")
        else:
            flash(f"Failed to add user. API returned status {response.status_code}.", "error")

    except requests.exceptions.RequestException as e:
        flash(f"An error occurred while contacting the API: {str(e)}", "error")

    return redirect(url_for("admin_users"))


@app.route('/admin/users/delete', methods=["POST"])
def handle_delete_user_admin():
    """
    Handles the form submission from the admin users page to delete a user.
    Makes an API call to the backend.
    """
    user_id_str = request.form.get('user_id') # Gets the ID from the select dropdown

    if not user_id_str:
        flash("Error: No user selected for deletion.", "error")
        return redirect(url_for("admin_users")) # Redirect back to the users list page

    try:
        user_id = int(user_id_str) # Ensure it's an integer
    except ValueError:
        flash("Error: Invalid user ID format.", "error")
        return redirect(url_for("admin_users"))
    
    api_url = f"{API_URL}/admin/users/delete"
    token = session.get("token")
    role = session.get("role")
    if not token:
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}

    # Prepare the JSON payload containing the user_id
    json_payload = {
        "user_id": user_id
    }

    try:
        # Make the POST request to the backend API
        response = requests.post(api_url, json=json_payload, headers=headers)
        print(response)

        # Check the response status code from the API
        if response.status_code == 200:
            # Assuming the API returns 200 on successful deletion
            flash("User deleted successfully!", "success")
        elif response.status_code == 404:
            # Handle user not found error from the API
            api_error = response.json().get('error', 'User not found.')
            flash(f"Error: {api_error}", "error")
        elif response.status_code == 403:
            # Handle permission error (e.g., trying to delete an admin) from the API
            api_error = response.json().get('error', 'Cannot delete user.')
            flash(f"Error: {api_error}", "error")
        else:
            # Handle other potential errors from the API
            # Attempt to get error message from response body
            try:
                api_error_detail = response.json().get('error', 'Unknown error from API.')
            except ValueError: # If response is not JSON
                api_error_detail = f"Non-JSON response: {response.text[:100]}..." # Log first 100 chars
            flash(f"Failed to delete user. API Error: {api_error_detail}", "error")

    except requests.exceptions.RequestException as e:
        # Handle potential network errors during the API call
        flash(f"An error occurred while contacting the API: {str(e)}", "error")

    # Redirect back to the users list page after attempting the deletion
    return redirect(url_for("admin_users"))


@app.route("/admin/businesses")
def admin_businesses():
    token = session.get("token")
    role = session.get("role")
    if not token:
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}
    businesses = requests.get(API_URL + "/admin/businesses", headers=headers).json()
    return render_template("admin/business.html",businesses=businesses)

@app.route('/admin/businesses/add', methods=["POST"])
def handle_add_business_admin():
    """
    Handles the form submission from the admin businesses page to add a business.
    Makes an API call to the backend.
    """
    form_data = {
        "name": request.form.get('name', '').strip(),
        "category": request.form.get('category', '').strip(), # Optional field
        "contact_email": request.form.get('contact_email', '').strip(),
        "contact_phone": request.form.get('contact_phone', '').strip(), # Optional field
        "password": request.form.get('password', '').strip(),
    }

    # Validate required fields
    if not form_data["name"] or not form_data["contact_email"] or not form_data["password"]:
        flash("Input Error: Name, Contact Email, and Password are required.", "info")
        return redirect(url_for("admin_businesses")) # Assuming this route calls render_admin_businesses_page

    api_url = f"{API_URL}/admin/businesses" # Use the API endpoint that handles POST for adding
    token = session.get("token")
    role = session.get("role")
    if not token:
        return redirect(url_for("login"))

    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {token}"
    }

    json_payload = form_data

    try:
        response = requests.post(api_url, json=json_payload, headers=headers)

        if response.status_code == 201:
            flash(f"Business '{form_data['name']}' added successfully!", "success")
        elif response.status_code == 409:
            api_error = response.json().get('error', 'Business already exists.')
            flash(f"Error: {api_error}", "error")
        elif response.status_code == 400:
            api_error = response.json().get('error', 'Invalid data provided.')
            flash(f"Error: {api_error}", "error")
        else:
            try:
                api_error_detail = response.json().get('error', 'Unknown error from API.')
            except ValueError:
                api_error_detail = f"Non-JSON response: {response.text[:100]}..."
            flash(f"Failed to add business. API Error: {api_error_detail}", "error")

    except requests.exceptions.RequestException as e:
        flash(f"An error occurred while contacting the API: {str(e)}", "error")

    return redirect(url_for("admin_businesses"))



# --- Frontend Handler for Deleting Business ---

@app.route('/admin/businesses/delete', methods=["POST"])
def handle_delete_business_admin():
    """
    Handles the form submission from the admin businesses page to delete a business.
    Makes an API call to the backend.
    """
    business_id_str = request.form.get('business_id')

    if not business_id_str:
        flash("Error: No business selected for deletion.", "error")
        return redirect(url_for("admin_businesses"))

    try:
        business_id = int(business_id_str)
    except ValueError:
        flash("Error: Invalid business ID format.", "error")
        return redirect(url_for("admin_businesses"))

    api_url = f"{API_URL}/admin/businesses/delete" # Use the API endpoint that handles POST for deletion
    token = session.get("token")
    role = session.get("role")
    if not token:
        return redirect(url_for("login"))

    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {token}"
    }

    json_payload = {"business_id": business_id}

    try:
        response = requests.post(api_url, json=json_payload, headers=headers)

        if response.status_code == 200:
            flash("Business deleted successfully!", "success")
        elif response.status_code == 404:
            api_error = response.json().get('error', 'Business not found.')
            flash(f"Error: {api_error}", "error")
        else:
            try:
                api_error_detail = response.json().get('error', 'Unknown error from API.')
            except ValueError:
                api_error_detail = f"Non-JSON response: {response.text[:100]}..."
            flash(f"Failed to delete business. API Error: {api_error_detail}", "error")

    except requests.exceptions.RequestException as e:
        flash(f"An error occurred while contacting the API: {str(e)}", "error")

    return redirect(url_for("admin_businesses"))


@app.route("/admin/transactions")
def admin_transactions():
    token = session.get("token")
    role = session.get("role")
    if not token:
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}
    transactions = requests.get(API_URL + "/admin/transactions", headers=headers).json()
    return render_template("admin/transactions.html",transactions=transactions)

@app.route("/dashboard")
def dashboard():
    token = session.get("token")
    role = session.get("role")
    if not token:
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}

    if role == "business":
        memberships = requests.get(API_URL + "/business/memberships", headers=headers).json()
        transactions = requests.get(API_URL + "/business/transactions", headers=headers).json()
        return render_template("dashboard/business.html", memberships=memberships, transactions=transactions)

    elif role == "customer":
        memberships = requests.get(API_URL + "/customer/memberships", headers=headers).json()
        transactions = requests.get(API_URL + "/customer/transactions", headers=headers).json()
        return render_template("dashboard/customer.html", memberships=memberships, transactions=transactions)

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
    return render_template("register/customer.html")


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
    return render_template("register/business.html")


# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Frontend runs on 5001
