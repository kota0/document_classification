from django.db import models

# Create your models here.


class Article_data(models.Model):
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    text = models.CharField(max_length=10000)
    category = models.CharField(max_length=255)
