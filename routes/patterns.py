def verify_json_header(request):
    if not request.headers['Content-Type'].startswith('application/json'):
        return {
            "error": "The content-type is not a 'application/json'"
        }

def verify_multipart_header(request):
    if not request.headers['Content-Type'].startswith('multipart/form-data'):
        return {
            "error": "The content-type is not a 'multipart/form-data'"
        }
    