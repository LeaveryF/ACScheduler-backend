from flask import (
    Blueprint,
    render_template
)
from air.auth import acadmin_required
from air.db import Room


bp = Blueprint("acadmin", __name__, url_prefix="/acadmin")


@bp.route('/rooms')
@acadmin_required
def rooms():
    rooms = Room.query.all()

    return render_template('acadmin/rooms.html', rooms=rooms)
