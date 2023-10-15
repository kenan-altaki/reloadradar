# Third Party Libraries
from rest_framework import serializers, viewsets

# First Party Libraries
from core.models import Link, Manufacturer, Pricing, Propellant, Supplier


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ["id", "link_url", "link_type"]


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ["id", "name"]


class SupplierSerializer(serializers.ModelSerializer):
    urls = LinkSerializer(many=True, read_only=True)

    class Meta:
        model = Supplier
        fields = ["url", "id", "name", "urls"]


class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        fields = ["id", "price", "retrieved", "supplier"]


class PropellantSerializer(serializers.ModelSerializer):
    prices = PricingSerializer(many=True, read_only=True)

    class Meta:
        model = Propellant
        fields = ["id", "name", "weight", "manufacturer", "prices"]


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer


class PricingViewSet(viewsets.ModelViewSet):
    queryset = Pricing.objects.all()
    serializer_class = PricingSerializer


class PropellantViewSet(viewsets.ModelViewSet):
    queryset = Propellant.objects.all()
    serializer_class = PropellantSerializer
