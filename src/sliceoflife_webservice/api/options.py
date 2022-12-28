"""
    :module_name: options
    :module_summary: response class for OPTIONS requests
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

from . import BaseSliceOfLifeApiResponse
from flask import request, make_response

class SliceOfLifeApiOptionsResponse(BaseSliceOfLifeApiResponse):
    """
        Response class for OPTIONS requests
    """

    def preflight_request(self):
        """
            Respond to preflight requests
            :returns: preflight response
            :rtype: Flask response
        """
        response = make_response('', 204)
        response.headers.set('Access-Control-Allow-Origin', '*')
        response.headers.set('Access-Control-Allow-Methods', 'POST, GET')
        response.headers.set('Access-Control-Allow-Headers', 'x-auth-token')
