from django.shortcuts import redirect



#condition for token to give 400 response 
# api response limit is exauhsted 
# page token is invalid 
# user token is invalid or expired (middleware only apply to this )

#renew the page token if expired 
#redirect to token_expired page if User token is expired (critical)
class TokenExpiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # print("from custom middleware",response.status_code)
        if response.status_code == 500:
            # if request.path.startswith('/api/'):
                # Redirect to a custom page
            return redirect('token_expired')  # Replace with your URL name
        return response