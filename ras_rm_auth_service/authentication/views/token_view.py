from django.http import JsonResponse
from django.views import View
from django.contrib.auth import authenticate

from ..encryption import pwd_context
from ..models import User


class TokenView(View):
    def post(self, request):
        user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))

        if user is None or not user.is_verified:
            return JsonResponse(data={"detail": "User account not verified"}, status=401)

        return JsonResponse(
            data={"id": 895725, "access_token": "fakefake-4bc1-4254-b43a-f44791ecec75", "expires_in": 3600,
                  "token_type": "Bearer", "scope": "", "refresh_token": "fakefake-2151-4b11-b0d5-a9a68f2c53de"},
            status=201)
