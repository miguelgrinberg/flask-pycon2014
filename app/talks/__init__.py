from flask import Blueprint

talks = Blueprint('talks', __name__)

from . import routes

