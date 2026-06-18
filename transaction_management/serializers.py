from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'item', 'quantity',
            'totalPrice', 'date', 'created_on', 'updated_on',
        ]
        