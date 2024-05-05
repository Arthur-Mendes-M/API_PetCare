from werkzeug.exceptions import BadRequest

def verify_json_header(request):
    if not request.headers['Content-Type'].startswith('application/json'):
        raise BadRequest("The content-type is not a 'application/json'")

def verify_multipart_header(request):
    if not request.headers['Content-Type'].startswith('multipart/form-data'):
        return BadRequest("The content-type is not a 'multipart/form-data'")
