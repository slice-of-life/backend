"""
    :module_name: sliceoflife_webservice
    :module_summary: entry point for the slice of life backend
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""
from flask import Flask

from .api import hello

app = Flask(__name__)

app.add_url_rule('/api/v1/greet', endpoint='index', view_func=hello)
