from rest_framework import serializers
from .models import Country

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            "id", "name", "capital", "region", "population",
            "currency_code", "exchange_rate", "estimated_gdp",
            "flag_url", "last_refreshed_at"
        ]

    def validate(self, data):
        # name and population are required by spec — serializer used for responses,
        # but do validation for any create APIs (we don't expose create manually).
        if "name" in data and (data.get("name") is None or str(data.get("name")).strip() == ""):
            raise serializers.ValidationError({"name": "is required"})
        if "population" in data and data.get("population") is None:
            raise serializers.ValidationError({"population": "is required"})
        # currency_code required in general, but per spec: when currencies empty, currency_code must be null.
        # We'll not block when currency_code is None because spec allows it.
        return data
