"""
    :module_name: test_options_response
    :module_summary: tests for OPTIONS response
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

from sliceoflife_webservice.api.options import SliceOfLifeApiOptionsResponse
from sliceoflife_webservice import app

def test_preflight_reponses():
    with app.test_request_context('/', method='OPTIONS'):
        assert SliceOfLifeApiOptionsResponse().preflight_request().get_data() == b''
        assert SliceOfLifeApiOptionsResponse().preflight_request().status == '204 NO CONTENT'
