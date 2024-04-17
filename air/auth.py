import functools

from flask import (
    Blueprint,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from air.db import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None
        user = User.query.filter_by(username=username).first()
        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user.id
            if username == "manager":
                return redirect(url_for("manager.report"))
            elif username == "acadmin":
                return redirect(url_for("acadmin.rooms"))
            elif username == "receptionist":
                return redirect(url_for("reception.getinvoice"))
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            User.query.filter_by(id=user_id).first()
        )


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


def manager_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or g.user.username != "manager":
            abort(403, "Permission denied.")

        return view(**kwargs)

    return wrapped_view


def acadmin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or g.user.username != "acadmin":
            abort(403, "Permission denied.")

        return view(**kwargs)

    return wrapped_view


def reception_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or g.user.username != "receptionist":
            abort(403, "Permission denied.")

        return view(**kwargs)

    return wrapped_view
