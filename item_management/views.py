from django.shortcuts import render
from rest_framework import generics
from .models import Item
from .serializers import ItemSerializer


class ReadItem(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class UpdateItem(generics.RetrieveUpdateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class CreateItem(generics.CreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class DeleteItem(generics.DestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class ReadItemByID(generics.RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'pk'


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
