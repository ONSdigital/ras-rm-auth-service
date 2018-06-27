from django.http import JsonResponse
from django.views import View
from django.contrib.auth import authenticate


class TokenView(View):

    def post(self, request):
        user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))

        if user is None or not user.is_verified:
            return JsonResponse(data={"detail": "User account not verified"}, status=401)

        return JsonResponse(data={"detail": "Success"}, status=201)
