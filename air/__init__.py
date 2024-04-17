import os

from flask import Flask, render_template
from air.db import db
from air.seed_data import seed_data


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///air.sqlite',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SOCK_SERVER_OPTIONS={'ping_interval': 25}
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_data()

    @app.route('/', endpoint='index')
    def index():
        return render_template('index.html')

    from . import auth
    app.register_blueprint(auth.bp)

    from . import _manager
    app.register_blueprint(_manager.bp)

    from . import _acadmin
    app.register_blueprint(_acadmin.bp)

    from . import _reception
    app.register_blueprint(_reception.bp)

    from . import _dispatch
    app.register_blueprint(_dispatch.bp)

    return app
