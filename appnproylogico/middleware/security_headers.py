from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('Referrer-Policy', getattr(settings, 'REFERRER_POLICY', 'same-origin'))
        response.headers.setdefault('Permissions-Policy', "geolocation=(), microphone=(), camera=()")
        csp = getattr(settings, 'CSP_POLICY', "default-src 'self'; base-uri 'self'; frame-ancestors 'none'; object-src 'none'; img-src 'self' data:; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' data: https://cdn.jsdelivr.net; connect-src 'self'")
        response.headers.setdefault('Content-Security-Policy', csp)
        if not settings.DEBUG:
            response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload')
        return response
