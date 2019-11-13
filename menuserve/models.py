from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

# Create your models here.

class Item(models.Model):
    category = models.CharField(max_length=50)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=250)
    price = models.CharField(max_length=20)
    image = models.FileField(null=True, blank=True)
    class Meta:
        verbose_name = ("Item")
        verbose_name_plural = ("Items")
    def __str__(self):
        return self.name #name to be shown when called

class OrderedItem(models.Model):
    item = models.ForeignKey(Item, default=None, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    class Meta:
        verbose_name = ("OrderedItem")
        verbose_name_plural = ("OrderedItems")
    def __str__(self):
        return self.item.name #name to be shown when called


class Location(models.Model):
    name = models.CharField(max_length=20)
    active = models.BooleanField(default=False)
    class Meta:
        verbose_name = ("Location")
        verbose_name_plural = ("Locations")
    def __str__(self):
        return self.name #name to be shown when called

class Order(models.Model):
    items = models.ManyToManyField(OrderedItem)
    location = models.ForeignKey(Location, default=None, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, default="")
    delivery = models.CharField(max_length=150, default="")
    submitted = models.BooleanField(default=False)
    total_items = models.IntegerField(default=0)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, default=None)
    fulfilled = models.BooleanField(default=False)

    class Meta:
        verbose_name = ("Order")
        verbose_name_plural = ("Orders")
    def __str__(self):
        return self.name + " : Order"

class Employee(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, primary_key=True, default=None)
    name = models.CharField(max_length=30)
    image = models.FileField(null=True, blank=True)
    is_manager = models.BooleanField(default=False)
    locations = models.ManyToManyField(Location)

    class Meta:
        verbose_name = ("Employee")
        verbose_name_plural = ("Employees")
    def __str__(self):
        return self.name #name to be shown when called
