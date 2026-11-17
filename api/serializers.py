"""Serializers de DRF que validan los bodies/query de api/api.yaml."""

from rest_framework import serializers


class LoginRequestSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)


class WithdrawQuerySerializer(serializers.Serializer):
    amount = serializers.FloatField(required=True, min_value=0.01)


class ProductSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    name = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1)
    unit_price = serializers.FloatField(min_value=0)


class PaymentDataSerializer(serializers.Serializer):
    card_number = serializers.CharField(required=False, allow_blank=True)
    expiry = serializers.CharField(required=False, allow_blank=True)
    cvv = serializers.CharField(required=False, allow_blank=True)
    holder = serializers.CharField(required=False, allow_blank=True)
    iban = serializers.CharField(required=False, allow_blank=True)


class PaymentRequestSerializer(serializers.Serializer):
    total_amount = serializers.FloatField(min_value=0)
    payment_method = serializers.ChoiceField(choices=["card", "cash", "transfer"])
    products = ProductSerializer(many=True)
    payment_data = PaymentDataSerializer()

    def validate_products(self, value):
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un producto.")
        return value


class TicketRequestSerializer(serializers.Serializer):
    company_id = serializers.CharField(required=False, allow_blank=True)
    total = serializers.FloatField(min_value=0)
    products = ProductSerializer(many=True)
    issued_at = serializers.CharField(required=False, allow_blank=True)

    def validate_products(self, value):
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un producto.")
        return value
