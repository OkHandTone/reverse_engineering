from rest_framework import serializers
from .models import Business

class BusinessSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Business
        fields = ['id', 'name', 'owner', 'created_on', 'updated_on']

class BusinessCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['id', 'name', 'owner', 'created_on', 'updated_on']
        extra_kwargs = {
            'name': {'required': True, 'allow_blank': False},
            'owner': {'required': False}
        }