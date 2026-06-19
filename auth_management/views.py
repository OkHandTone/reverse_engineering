from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from . import serializers
from .models import AuthUser as User


def home_view(request):
    if request.user.is_authenticated:
        return redirect('items_page')
    return redirect('login_page')


@require_http_methods(['GET', 'POST'])
@csrf_protect
def login_page_view(request):
    """Page HTML de connexion pour CLIENT, WORKER et SUPERADMIN."""
    if request.user.is_authenticated:
        return redirect('items_page')

    if request.method == 'GET':
        return render(request, 'auth_management/login.html')

    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')

    if not username or not password:
        return render(
            request,
            'auth_management/login.html',
            {'error': 'Veuillez renseigner le nom d\'utilisateur et le mot de passe.'},
        )

    user = authenticate(request, username=username, password=password)
    if user is None:
        return render(
            request,
            'auth_management/login.html',
            {'error': 'Identifiants invalides.'},
        )

    if not user.is_active:
        return render(
            request,
            'auth_management/login.html',
            {'error': 'Ce compte est désactivé.'},
        )

    auth_login(request, user)
    Token.objects.get_or_create(user=user)
    return redirect('items_page')


@require_http_methods(['GET', 'POST'])
def logout_page_view(request):
    auth_logout(request)
    return redirect('login_page')


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def login_api_view(request):
    """Endpoint JSON pour la connexion (API)."""
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
    requesting_user = request.user
    data = request.data.copy()

    if requesting_user.user_type == User.UserType.WORKER:
        return Response({'error': 'Workers cannot register new users.'}, status=403)

    if requesting_user.user_type == User.UserType.CLIENT:
        if data.get('user_type') != User.UserType.WORKER:
            return Response({'error': 'Clients can only register workers.'}, status=403)
        data['client'] = requesting_user.id

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
