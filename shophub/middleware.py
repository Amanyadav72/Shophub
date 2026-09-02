import time


class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.client_timezone = "IST"
        start_time = time.perf_counter()

        response = self.get_response(request)

        duration = time.perf_counter() - start_time

        print(
            f"{request.method} {request.path} "
            f"-> {response.status_code} "
            f"({duration:.4f}s)"
        )

        return response