from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Item
from .serializers import ItemSerializer


class AuthenticatedMixin:
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]


class ReadItem(AuthenticatedMixin, generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class UpdateItem(AuthenticatedMixin, generics.RetrieveUpdateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class CreateItem(AuthenticatedMixin, generics.CreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class DeleteItem(AuthenticatedMixin, generics.DestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class ReadItemByID(AuthenticatedMixin, generics.RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'pk'


@login_required(login_url='/login/')
def items_page_view(request):
    items = Item.objects.select_related('category', 'business').all()
    return render(
        request,
        'item_management/items.html',
        {
            'items': items,
            'user': request.user,
        },
    )
