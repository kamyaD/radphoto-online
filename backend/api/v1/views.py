from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import HealthCheckSerializer


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
       
        data = {
                "status": "ok",
                "service": "RADPHOTO ONLINE API",
                "version": "v1",
            }

        serializer = HealthCheckSerializer(data=data)

        return Response(serializer.data)