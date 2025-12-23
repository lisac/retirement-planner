"""
Custom middleware for retirement_planner project.
"""

from django.conf import settings


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to all responses.

    Adds Content Security Policy (CSP) and other security headers
    to protect against XSS, clickjacking, and other attacks.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add Content Security Policy header
        if hasattr(settings, 'SECURE_CONTENT_SECURITY_POLICY'):
            csp_dict = settings.SECURE_CONTENT_SECURITY_POLICY
            csp_parts = []
            for directive, sources in csp_dict.items():
                sources_str = ' '.join(sources)
                csp_parts.append(f"{directive} {sources_str}")
            response['Content-Security-Policy'] = '; '.join(csp_parts)

        return response
