from app import app
from flask import render_template

@app.route('/admin/admin_dashboard')
def admin_dashboard():
    return render_template("/admin/dashboard.html")

@app.route('/admin/admin_profile')
def admin_profile():
    return render_template("admin/profile.html")
