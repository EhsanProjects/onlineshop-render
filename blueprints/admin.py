from flask import Blueprint, render_template, request, session, redirect, abort

import config

app = Blueprint("admin", __name__)


@app.route('/admin/login', methods=["POST", "GET"])
def admin():  # put application's code here
    if request.method == "POST":
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            # This shows what session is active now. By checking its value
            session['admin_login'] = username
            return redirect("/admin/dashboard")
        else:
            redirect("/admin/login")
    else:

        return render_template("/admin/login.html")


@app.route('/admin/dashboard', methods=["GET"])
def dashboard():
    if session.get('admin_login', None) == None:
        return "Error: Not logged in yet"
        # abort(403)

    return "dashboard"
