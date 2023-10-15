# Third Party Libraries
from core.models import Link, Supplier
from rest_framework import serializers, viewsets


class BaseLinkSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ["id", "url", "link_type"]


# Serializers define the API representation.
class SupplierSerializer(serializers.HyperlinkedModelSerializer):
    urls = BaseLinkSerialiser(many=True, read_only=True)

    class Meta:
        model = Supplier
        fields = ["id", "name", "urls"]


# ViewSets define the view behavior.
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
