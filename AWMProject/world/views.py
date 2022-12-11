from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken
from .serializers import UserSerializer, RegisterSerializer


# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


from django.contrib.auth import login

from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView


class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)


#
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Point
from django.http import JsonResponse


# Create your views here.
@login_required
def update_database(request):
    my_location = request.POST.get("point", None)
    if not my_location:
        return JsonResponse({"message": "No location found."}, status=400)

    try:
        my_coords = [float(coord) for coord in my_location.split(", ")]
        my_profile = request.user.profile
        my_profile.last_location = Point(my_coords)
        my_profile.save()

        message = f"Updated {request.user.username} with {f'POINT({my_location})'}"

        return JsonResponse({"message": message}, status=200)
    except:
        return JsonResponse({"message": "No profile found."}, status=400)
