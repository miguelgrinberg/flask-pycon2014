from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.moment import Moment
from flask.ext.pagedown import PageDown
from flask.ext.mail import Mail
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
pagedown = PageDown()
mail = Mail()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    if not app.config['DEBUG'] and not app.config['TESTING']:
        # configure logging for production

        # email errors to the administrators
        if app.config.get('MAIL_ERROR_RECIPIENT') is not None:
            import logging
            from logging.handlers import SMTPHandler
            credentials = None
            secure = None
            if app.config.get('MAIL_USERNAME') is not None:
                credentials = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
                if app.config['MAIL_USE_TLS'] is not None:
                    secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=app.config['MAIL_DEFAULT_SENDER'],
                toaddrs=[app.config['MAIL_ERROR_RECIPIENT']],
                subject='[Talks] Application Error',
                credentials=credentials,
                secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # send standard logs to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    from .talks import talks as talks_blueprint
    app.register_blueprint(talks_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api_1_0 import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/1.0')

    from app.emails import start_email_thread
    @app.before_first_request
    def before_first_request():
        start_email_thread()

    return app
