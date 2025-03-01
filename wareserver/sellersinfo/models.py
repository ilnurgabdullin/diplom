from django.db import models
from accounts.models import CustomUser

class Sellers(models.Model):
    name = models.CharField(max_length=255)
    sid = models.CharField(unique=True, max_length=36)
    trademark = models.CharField(max_length=255, blank=True, null=True)
    api_token = models.CharField(max_length=1000, blank=True, null=True)

class InfoModel(models.Model):
    userId = models.ForeignKey(CustomUser, to_field='id', on_delete=models.CASCADE, related_name='info')  # Связь один-ко-многим
    sellerId = models.ForeignKey(Sellers, to_field='sid', on_delete=models.CASCADE, related_name='info')  # Один пользователь - много продавцов

class Cards(models.Model):
    seller = models.ForeignKey(Sellers, to_field='sid', blank=True, null=True, on_delete=models.CASCADE)
    nmid = models.IntegerField()
    imtid = models.IntegerField(blank=True, null=True)
    nmuuid = models.CharField(max_length=36, blank=True, null=True)
    subjectid = models.IntegerField(blank=True, null=True)
    subjectname = models.CharField(max_length=255, blank=True, null=True)
    vendorcode = models.CharField(max_length=255, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    needkiz = models.BooleanField(blank=True, null=True)
    createdat = models.DateTimeField(blank=True, null=True)
    updatedat = models.DateTimeField(blank=True, null=True)


class Warehouse(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    location_id = models.IntegerField(unique=True, verbose_name="ID локации")
    office_id = models.IntegerField( verbose_name="ID офиса")
    cargo_type = models.IntegerField(verbose_name="Тип груза")
    delivery_type = models.IntegerField(verbose_name="Тип доставки")
   

