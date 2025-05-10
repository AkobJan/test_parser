from django.db import models

class info(models.Model):
    title = models.CharField(max_length = 100)
    price = models.CharField(max_length = 20)
    address = models.CharField(max_length = 255)
    square = models.CharField(max_length = 10)
    link = models.URLField(unique = True)
    date = models.CharField(max_length = 100)