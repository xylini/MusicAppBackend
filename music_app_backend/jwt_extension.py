from datetime import datetime, timezone
from rest_framework_jwt.settings import api_settings


def read_jwt_cookie_when_refresh():
    from rest_framework_jwt.views import RefreshJSONWebToken

    class ReadCookieWhenRefreshJSONWebToken(RefreshJSONWebToken):
        def post(self, request, *args, **kwargs):
            if api_settings.JWT_AUTH_COOKIE:
                request.data['token'] = request.COOKIES.get(api_settings.JWT_AUTH_COOKIE)
            if 'Authorization' in request.headers:
                bearer, token = request.headers['Authorization'].split(' ')
                if bearer == 'Bearer':
                    request.data['token'] = token
            return super(ReadCookieWhenRefreshJSONWebToken, self).post(request, args, kwargs)

    return ReadCookieWhenRefreshJSONWebToken.as_view()


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        "token": token,
        "expiration": (datetime.now(timezone.utc) + api_settings.JWT_EXPIRATION_DELTA).isoformat()
    }
