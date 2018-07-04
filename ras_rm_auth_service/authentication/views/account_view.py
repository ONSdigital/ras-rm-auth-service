from distutils.util import strtobool

from django.http import JsonResponse, QueryDict
from django.views import View
from ..models import User
import logging


stdlogger = logging.getLogger(__name__)


class AccountView(View):
    # Create a users account
    def post(self, request):
        stdlogger.debug("Create account")
        user = User.objects.create_user(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        user.save()

        return JsonResponse(data={"account": user.username, "created": "success"}, status=201)

    # Update a users account
    def put(self, request):
        put_params = QueryDict(request.body)
        users = User.objects.filter(username=put_params.get('username'))

        if len(users) < 1:
            return JsonResponse(
                data={"detail": "Unknown user credentials. This user does not exist on the OAuth2 server"},
                status=401,
            )

        user = users[0]
        try:
            user.is_verified = strtobool(put_params.get('account_verified'))
        except ValueError as e:
            return JsonResponse(data={"detail": "account_verified status is invalid"}, status=400)

        user.save()

        return JsonResponse(data={"account": user.username, "updated": "success"}, status=201)
