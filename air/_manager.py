from flask import (
    Blueprint,
    render_template
)
from air.auth import manager_required
from air.db import Room


bp = Blueprint("manager", __name__, url_prefix="/manager")


@bp.route('/report')
@manager_required
def report():
    rooms = Room.query.all()

    return render_template('manager/report.html', rooms=rooms)