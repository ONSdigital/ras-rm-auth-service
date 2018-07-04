from django.http import JsonResponse, QueryDict
from django.views import View
import logging

stdlogger = logging.getLogger(__name__)


class HealthView(View):
    def get(self, request):
        return JsonResponse(data={"status": "Healthy"}, status=200)
