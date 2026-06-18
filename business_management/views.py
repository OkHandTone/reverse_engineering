from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Business
from .serializers import BusinessSerializer, BusinessCreateSerializer
from auth_management.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


def _business_queryset_for_user(user):
    if user.user_type == user.UserType.CLIENT:
        return Business.objects.filter(owner=user), None

    if user.user_type == user.UserType.WORKER:
        if not user.business:
            error = Response(
                {"error": "Worker has no associated business."},
                status=status.HTTP_403_FORBIDDEN,
            )
            return None, error
        return Business.objects.filter(pk=user.business.pk), None

    return Business.objects.all(), None


def _list_businesses(business_qs, pk):
    if not pk:
        serializer = BusinessSerializer(business_qs, many=True)
        return Response(serializer.data)

    try:
        business = business_qs.get(pk=pk)
    except Business.DoesNotExist:
        return Response(
            {"error": "Business not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(BusinessSerializer(business).data)


def _get_businesses(request):
    business_qs, error_response = _business_queryset_for_user(request.user)
    if error_response:
        return error_response

    pk = request.query_params.get("pk")
    return _list_businesses(business_qs, pk)


def _create_business(request):
    user = request.user
    if user.user_type == user.UserType.WORKER:
        return Response(
            {"error": "Workers cannot create businesses."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = BusinessCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save(owner=user)
    return Response(
        {
            "data": serializer.data,
            "user": UserSerializer(instance=user).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def business_view(request):
    if request.method == "GET":
        return _get_businesses(request)

    return _create_business(request)
