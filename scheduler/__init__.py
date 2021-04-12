import os

from flask import Flask

from celery import Celery

def make_celery(app_name = __name__):
    redis_url = "redis://localhost:6379"
    return Celery(app_name, backend = redis_url, broker = redis_url)

celery = make_celery()

def create_app(test_config = None):
    app = Flask(__name__, instance_relative_config = True)
    app.config.from_mapping(
        SECRET_KEY = 'SetYourDevTestingKeyHere',
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        #loading config from external config file.
        app.config.from_pyfile('config.py', silent = True)
    else:
        #loading config from passed config object, use this only for testing.
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/test')
    def test():
        return "all_set"

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import schedule_post
    app.register_blueprint(schedule_post.bp)
    
    return app