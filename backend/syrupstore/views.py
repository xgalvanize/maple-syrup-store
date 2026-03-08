"""
Custom views with security enhancements for the Maple Syrup Store
"""
from graphene_django.views import GraphQLView
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


class RateLimitedGraphQLView(GraphQLView):
    """
    GraphQL view with rate limiting protection.
    
    Limits:
    - 100 requests per minute per IP for anonymous users
    - 300 requests per minute per user for authenticated users
    """
    
    @method_decorator(csrf_exempt)
    @method_decorator(ratelimit(key='ip', rate='100/m', method='POST'))
    @method_decorator(ratelimit(key='user', rate='300/m', method='POST'))
    def dispatch(self, request, *args, **kwargs):
        # Check if request was rate limited
        if getattr(request, 'limited', False):
            return JsonResponse(
                {
                    "errors": [{
                        "message": "Rate limit exceeded. Please try again later.",
                        "extensions": {
                            "code": "RATE_LIMITED"
                        }
                    }]
                },
                status=429
            )
        return super().dispatch(request, *args, **kwargs)


@ratelimit(key='ip', rate='10/h', method='POST')
def health_check(request):
    """Simple health check endpoint"""
    if getattr(request, 'limited', False):
        return JsonResponse({"status": "rate_limited"}, status=429)
    return JsonResponse({"status": "healthy"})
