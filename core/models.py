from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Document(models.Model):
    owner = models.ForeignKey(to=User, null=True, blank=True, on_delete=models.CASCADE)
    docfile = models.FileField(upload_to='documents/')
    name = models.CharField(max_length=128, null=True, blank=True)
    nbr_transactions = models.IntegerField(null=True, blank=True)
    nbr_items = models.IntegerField(null=True, blank=True)
    average_nbr_items_per_transaction = models.FloatField(null=True, blank=True)
    density_index = models.FloatField(null=True, blank=True)
