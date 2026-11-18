"""Serializers de DRF que validan los bodies/query de api/api.yaml."""

from rest_framework import serializers


class LoginRequestSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)


class WithdrawQuerySerializer(serializers.Serializer):
    amount = serializers.FloatField(required=True, min_value=0.01)
    currency = serializers.ChoiceField(
        choices=['EUR', 'USD', 'GBP'], required=False, default='EUR'
    )


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


class TicketCreateRequestSerializer(serializers.Serializer):
    company_id = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField(required=False, allow_blank=True)
    subject = serializers.CharField(max_length=140)
    description = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(
        choices=["open", "in_progress", "closed"], required=False, default="open"
    )


class TicketMessageRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("El mensaje no puede estar vacío.")
        return value


class TicketUpdateRequestSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["open", "in_progress", "closed"], required=False)
    reply = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Debe indicar un estado o una respuesta.")
        return attrs


class TicketAssignRequestSerializer(serializers.Serializer):
    technician_id = serializers.CharField(required=False, allow_blank=True)
    assign_to_me = serializers.BooleanField(required=False, default=False)
    unassign = serializers.BooleanField(required=False, default=False)


class TechnicianCreateRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(min_length=8, write_only=True)
    force_change = serializers.BooleanField(required=False, default=True)


class ProfileUpdateRequestSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    nombre = serializers.CharField(required=False, allow_blank=True, max_length=100)
    razon_social = serializers.CharField(required=False, allow_blank=True, max_length=150)
    cif = serializers.CharField(required=False, allow_blank=True, max_length=20)
    tipo_empresa = serializers.CharField(required=False, allow_blank=True, max_length=40)
    actividad_economica = serializers.CharField(
        required=False, allow_blank=True, max_length=150
    )
    direccion = serializers.CharField(required=False, allow_blank=True, max_length=200)
    codigo_postal = serializers.CharField(required=False, allow_blank=True, max_length=10)
    ciudad = serializers.CharField(required=False, allow_blank=True, max_length=80)
    provincia = serializers.CharField(required=False, allow_blank=True, max_length=80)
    pais = serializers.CharField(required=False, allow_blank=True, max_length=80)
    telefono = serializers.CharField(required=False, allow_blank=True, max_length=30)
    web = serializers.CharField(required=False, allow_blank=True, max_length=200)


class PasswordChangeRequestSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)


class CompanyCreateRequestSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)
    razon_social = serializers.CharField(max_length=150)
    cif = serializers.CharField(max_length=20)
    tipo_empresa = serializers.CharField(max_length=40)
    actividad_economica = serializers.CharField(max_length=150)
    direccion = serializers.CharField(max_length=200)
    codigo_postal = serializers.CharField(max_length=10)
    ciudad = serializers.CharField(max_length=80)
    provincia = serializers.CharField(max_length=80)
    pais = serializers.CharField(max_length=80)
    telefono = serializers.CharField(max_length=30)
    email = serializers.EmailField()
    web = serializers.CharField(required=False, allow_blank=True, max_length=200)
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(min_length=8, write_only=True)
    force_change = serializers.BooleanField(required=False, default=True)
