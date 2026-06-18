from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = [
            'id', 'name', 'price', 'description', 'category',
            'business', 'created_on', 'updated_on',
        ]
        