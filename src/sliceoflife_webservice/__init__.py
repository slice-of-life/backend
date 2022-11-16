"""
    :module_name: sliceoflife_webservice
    :module_summary: entry point for the slice of life backend
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""
from flask import Flask

from .api import hello

def app():
    """
        declares an instance of the sliceoflife api
        :returns: API instance
        :rtype: FlaskApp
    """
    api = Flask(__name__)
    api.add_url_rule('/api/v1/greet', endpoint='index', view_func=hello)

    return api
