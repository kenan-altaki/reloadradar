# Django Libraries
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Link(models.Model):
    link_type = models.CharField(max_length=32)
    link_url = models.URLField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.link_type}: {self.link_url[:25]}"


class Supplier(models.Model):
    name = models.CharField(max_length=128)
    urls = GenericRelation(Link)

    def __str__(self) -> str:
        return self.name


class Pricing(models.Model):
    price = models.DecimalField(decimal_places=3, max_digits=8)
    retrieved = models.DateTimeField(auto_now_add=True)
    price_url = models.URLField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="prices",
        related_query_name="price",
    )

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.content_object.name}: {self.price}"


class Manufacturer(models.Model):
    name = models.CharField(max_length=128)
    urls = GenericRelation(Link)

    def __str__(self) -> str:
        return self.name


class Propellant(models.Model):
    name = models.CharField(max_length=18)
    weight = models.DecimalField(decimal_places=2, max_digits=10)

    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.RESTRICT,
        related_name="propellants",
        related_query_name="propellant",
    )
    prices = GenericRelation(Pricing)

    def __str__(self) -> str:
        return self.name
