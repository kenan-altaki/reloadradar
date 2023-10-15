# Django Libraries
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.


class Link(models.Model):
    link_type = models.CharField(max_length=32)
    url = models.URLField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"{self.link_type}: {self.url[:25]}"

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]


class Supplier(models.Model):
    name = models.CharField(max_length=128)
    urls = GenericRelation(Link)

    def __str__(self) -> str:
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=128)
    urls = GenericRelation(Link)

    def __str__(self) -> str:
        return self.name


class Propellant(models.Model):
    name = models.CharField(max_length=18)
    weight = models.DecimalField(decimal_places=2, max_digits=10)

    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.RESTRICT)

    def __str__(self) -> str:
        return self.name


class Pricing(models.Model):
    price = models.DecimalField(decimal_places=3, max_digits=8)
    retrieved = models.DateTimeField(auto_created=True)
    urls = GenericRelation(Link)

    supplier = models.ForeignKey(
        Supplier, on_delete=models.RESTRICT, null=True, blank=True
    )
    propellant = models.ForeignKey(
        Propellant, on_delete=models.RESTRICT, null=True, blank=True
    )

    def __str__(self) -> str:
        return self.name
