from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    # Call DRF's default exception handler first to get the standard response
    response = exception_handler(exc, context)

    # If an unhandled or handled DRF exception occurs, standardize its envelope
    if response is not None:
        custom_data = {
            "status": "error",
            "status_code": response.status_code,
            "error_type": exc.__class__.__name__,
            "errors": response.data,
        }
        response.data = custom_data

    return response