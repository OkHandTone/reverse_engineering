from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.http import urlencode
from rest_framework.authentication import TokenAuthentication


class APIAuthenticationMiddleware:
    """Exige une authentification (token ou session) sur toutes les routes protégées."""

    PUBLIC_PATHS = frozenset({
        '/',
        '/login/',
        '/logout/',
        '/api/v1/users/login/',
    })

    EXCLUDED_PREFIXES = (
        '/admin/',
        '/static/',
    )

    API_PREFIX = '/api/v1/'

    def __init__(self, get_response):
        self.get_response = get_response
        self.token_auth = TokenAuthentication()

    def __call__(self, request):
        if not self._requires_auth(request):
            return self.get_response(request)

        user = self._resolve_user(request)
        if user is None:
            return self._unauthenticated_response(request)

        if not user.is_active:
            return self._inactive_response(request)

        request.user = user
        return self.get_response(request)

    def _requires_auth(self, request):
        for prefix in self.EXCLUDED_PREFIXES:
            if request.path.startswith(prefix):
                return False

        path = self._normalize_path(request.path)
        return path not in self.PUBLIC_PATHS

    def _resolve_user(self, request):
        if request.user.is_authenticated:
            return request.user

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Token '):
            return self._authenticate_token(request)

        return None

    def _authenticate_token(self, request):
        try:
            result = self.token_auth.authenticate(request)
        except Exception:
            return None
        if result is None:
            return None
        return result[0]

    def _is_api_request(self, request):
        if request.path.startswith(self.API_PREFIX):
            return True
        accept = request.META.get('HTTP_ACCEPT', '')
        return 'application/json' in accept and 'text/html' not in accept

    def _unauthenticated_response(self, request):
        if self._is_api_request(request):
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Token '):
                return JsonResponse({'detail': 'Invalid token.'}, status=401)
            return JsonResponse(
                {'detail': 'Authentication credentials were not provided.'},
                status=401,
            )

        login_url = settings.LOGIN_URL
        next_param = urlencode({'next': request.get_full_path()})
        return redirect(f'{login_url}?{next_param}')

    def _inactive_response(self, request):
        if self._is_api_request(request):
            return JsonResponse({'detail': 'User account is disabled.'}, status=403)
        return redirect(settings.LOGIN_URL)

    @staticmethod
    def _normalize_path(path):
        return path if path.endswith('/') else f'{path}/'
