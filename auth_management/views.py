from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from . import serializers
from .models import AuthUser as User
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


def _register_permission_error(requesting_user, data):
    if requesting_user.user_type == User.UserType.WORKER:
        return Response({"error": "Workers cannot register new users."}, status=403)

    is_client = requesting_user.user_type == User.UserType.CLIENT
    if is_client and data.get("user_type") != User.UserType.WORKER:
        return Response({"error": "Clients can only register workers."}, status=403)

    if is_client:
        data["client"] = requesting_user.id

    return None


@api_view(['POST'])
def login_view(request):
    serializer = serializers.LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=400)

    user = authenticate(
        request,
        username=serializer.validated_data['username'],
        password=serializer.validated_data['password'],
    )
    if user is None:
        return Response({'error': 'Invalid credentials'}, status=401)

    if not user.is_active:
        return Response({'error': 'User account is disabled.'}, status=403)

    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            'token': token.key,
            'user': serializers.UserSerializer(user).data,
        },
        status=200,
    )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def register_view(request):
    data = request.data.copy()
    permission_error = _register_permission_error(request.user, data)
    if permission_error:
        return permission_error

    serializer = serializers.RegisterSerializer(data=data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=400)

    user = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            'message': 'User registered successfully!',
            'token': token.key,
            'user': serializers.UserSerializer(user).data,
        },
        status=201,
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def my_profile_view(request):
    user = request.user
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            'user': serializers.UserSerializer(instance=user).data,
            'token': token.key,
        },
    )
