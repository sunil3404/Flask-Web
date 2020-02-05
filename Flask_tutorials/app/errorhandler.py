from app import app
from flask import render_template, request, abort


@app.errorhandler(404)
def page_not_found(error):
    return render_template("/public/404.html")

@app.errorhandler(500)
def server_error(error):
    app.logger.error(f"Internal server error {error}")
    return render_template("/public/500.html")

