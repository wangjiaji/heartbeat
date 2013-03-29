from django.http import HttpResponse
from django.utils import simplejson as json

class HttpResponseJSON(HttpResponse):
    mimetype = 'application/json'

    def __init__(self, content='', need_dump=True, *args, **kwargs):
        if need_dump:
            content = json.dumps(content)
        super(HttpResponseJSON, self).__init__(content, *args, **kwargs)

class HttpResponseOK(HttpResponseJSON):
    status_code = 200

class HttpResponseCreated(HttpResponseJSON):
    status_code = 201

class HttpResponseAccepted(HttpResponseJSON):
    status_code = 202

class HttpResponseForbidden(HttpResponseJSON):
    status = 403

class HttpResponseNoContent(HttpResponseJSON):
    status_code = 204

class HttpResponseBadRequest(HttpResponseJSON):
    status_code = 400
