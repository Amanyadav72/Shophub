import uuid 

class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = str(uuid.uuid4())
        print(f"Request ID: {request.request_id}")  # Log the request ID
        response = self.get_response(request)
        print(f"Response for Request ID: {request.request_id}")  # Log the response for the request ID
        response['X-Request-ID'] = request.request_id
        return response