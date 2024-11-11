# middleware.py
class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the response from the view (or next middleware)
        response = self.get_response(request)

        # Add Cache-Control headers to prevent caching
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        return response
