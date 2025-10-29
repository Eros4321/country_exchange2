from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    capital = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    population = models.BigIntegerField()
    currency_code = models.CharField(max_length=10, null=True, blank=True, db_index=True)
    exchange_rate = models.FloatField(null=True, blank=True)  # rate relative to USD
    estimated_gdp = models.FloatField(null=True, blank=True)
    flag_url = models.TextField(null=True, blank=True)
    last_refreshed_at = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return self.name

class AppMeta(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key} -> {self.value}"
