from flask import (
    Blueprint,
    render_template
)
from air.auth import reception_required
from air.db import Room


bp = Blueprint("reception", __name__, url_prefix="/reception")


@bp.route('/getinvoice')
@reception_required
def getinvoice():
    rooms = Room.query.all()

    return render_template('reception/getinvoice.html', rooms=rooms)
