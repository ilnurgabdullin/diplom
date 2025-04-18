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


class UserSetting(models.Model):
    userId = models.ForeignKey(CustomUser, to_field='id', on_delete=models.CASCADE)
    barcodes = models.BooleanField(verbose_name="Надо ли печатать баркод", default= True)

class Cards(models.Model):
    seller = models.ForeignKey(Sellers, to_field='sid', blank=True, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, to_field='id', on_delete=models.CASCADE)
    subjectname = models.CharField(max_length=255, blank=True, null=True)
    vendorcode = models.CharField(max_length=255, blank=True, null=True)


class Warehouse(models.Model):
    owner = models.ForeignKey(Sellers, on_delete=models.CASCADE, related_name="cells", verbose_name="Склад")
    name = models.CharField(max_length=255, verbose_name="Название")
    location_id = models.IntegerField(unique=True, verbose_name="ID локации")
    office_id = models.IntegerField( verbose_name="ID офиса")
    cargo_type = models.IntegerField(verbose_name="Тип груза")
    delivery_type = models.IntegerField(verbose_name="Тип доставки")
   
   
class Storage(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="cells", verbose_name="Склад")
    address = models.CharField(max_length=255, verbose_name="Адрес склада")
    name = models.CharField(max_length=255, verbose_name="Название")


class StorageCell(models.Model):
    warehouse = models.ForeignKey(Storage, on_delete=models.CASCADE, related_name="cells", verbose_name="Склад")
    cell_code = models.CharField(max_length=50, verbose_name="Код ячейки")
    description = models.TextField(blank=True, null=True, verbose_name="Описание ячейки")


class ProductPlacement(models.Model):
    product = models.ForeignKey(Cards, on_delete=models.CASCADE, related_name="placements", verbose_name="Товар")
    cell = models.ForeignKey(StorageCell, on_delete=models.CASCADE, related_name="placements", verbose_name="Ячейка")
    quantity = models.PositiveIntegerField(verbose_name="Количество товара в ячейке")

