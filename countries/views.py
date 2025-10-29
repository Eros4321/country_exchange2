import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Country, AppMeta
from .serializers import CountrySerializer
from .utils import generate_summary_image
from random import randint
from django.db.models import Q
from django.http import FileResponse, JsonResponse
import os

EXTERNAL_TIMEOUT = getattr(settings, "EXTERNAL_API_TIMEOUT", 10)
SUMMARY_IMAGE_PATH = getattr(settings, "SUMMARY_IMAGE_PATH")

# Helper error responses
def external_error(api_name):
    return Response(
        {"error": "External data source unavailable", "details": f"Could not fetch data from {api_name}"},
        status=status.HTTP_503_SERVICE_UNAVAILABLE
    )

@api_view(["POST"])
def refresh_countries(request):
    """
    POST /countries/refresh
    Transactional: if external fails, DO NOT modify DB.
    """
    # 1. fetch countries
    try:
        r_c = requests.get('https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies', timeout=EXTERNAL_TIMEOUT)
        if r_c.status_code != 200:
            return external_error("Countries API")
        countries_data = r_c.json()
    except Exception:
        return external_error("Countries API")

    # 2. fetch exchange rates
    try:
        r_e = requests.get('https://open.er-api.com/v6/latest/USD', timeout=EXTERNAL_TIMEOUT)
        if r_e.status_code != 200:
            return external_error("Exchange rates API")
        exchange_data = r_e.json()
        rates = exchange_data.get("rates", {})
    except Exception:
        return external_error("Exchange rates API")

    sanitized = []
    for c in countries_data:
        name = c.get("name")
        population = c.get("population")
        capital = c.get("capital")
        region = c.get("region")
        flag = c.get("flag")
        currencies = c.get("currencies") or []

        currency_code = None
        exchange_rate = None
        estimated_gdp = None

        if currencies and isinstance(currencies, list) and len(currencies) > 0:
            first = currencies[0]
            if isinstance(first, dict):
                currency_code = first.get("code")
            else:
                currency_code = first
            if currency_code and currency_code in rates:
                try:
                    exchange_rate = float(rates.get(currency_code))
                except Exception:
                    exchange_rate = None
            else:
                exchange_rate = None
                estimated_gdp = None
        else:
            # empty currencies array per spec
            currency_code = None
            exchange_rate = None
            estimated_gdp = 0

        if exchange_rate is not None and estimated_gdp is None:
            multiplier = randint(1000, 2000)
            try:
                estimated_gdp = (int(population) * multiplier) / exchange_rate if population is not None else None
            except Exception:
                estimated_gdp = None

        sanitized.append({
            "name": name,
            "capital": capital,
            "region": region,
            "population": population,
            "currency_code": currency_code,
            "exchange_rate": exchange_rate,
            "estimated_gdp": estimated_gdp,
            "flag_url": flag
        })

    # 3. Persist in DB within transaction
    try:
        with transaction.atomic():
            now = timezone.now()
            for row in sanitized:
                name = row.get("name")
                population = row.get("population")
                # Validate required fields
                if not name or population is None:
                    # According to spec: return 400 for invalid/missing data
                    return Response(
                        {"error": "Validation failed", "details": {"name_or_population": "required"}},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Case-insensitive match
                existing = Country.objects.filter(name__iexact=name).first()
                if existing:
                    existing.capital = row.get("capital")
                    existing.region = row.get("region")
                    existing.population = row.get("population")
                    existing.currency_code = row.get("currency_code")
                    existing.exchange_rate = row.get("exchange_rate")
                    existing.estimated_gdp = row.get("estimated_gdp")
                    existing.flag_url = row.get("flag_url")
                    existing.last_refreshed_at = now
                    existing.save()
                else:
                    Country.objects.create(
                        name=row.get("name"),
                        capital=row.get("capital"),
                        region=row.get("region"),
                        population=row.get("population"),
                        currency_code=row.get("currency_code"),
                        exchange_rate=row.get("exchange_rate"),
                        estimated_gdp=row.get("estimated_gdp"),
                        flag_url=row.get("flag_url"),
                    )
            # update app meta
            AppMeta.objects.update_or_create(key="last_refreshed_at", defaults={"value": now.isoformat()})
    except Exception as e:
        # transaction will rollback automatically
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 4. generate summary image (best-effort; don't fail the endpoint if image generation fails)
    try:
        total = Country.objects.count()
        top5_qs = Country.objects.filter(estimated_gdp__isnull=False).order_by("-estimated_gdp")[:5]
        top5 = [{"name": c.name, "estimated_gdp": c.estimated_gdp} for c in top5_qs]
        last_ref = timezone.now()
        generate_summary_image(SUMMARY_IMAGE_PATH, total, top5, last_ref)
    except Exception:
        # swallow but log if available
        import logging; logging.exception("Failed to generate summary image")

    return Response({"status": "success", "total_countries": len(sanitized), "refreshed_at": timezone.now().isoformat()}, status=status.HTTP_200_OK)
generate_summary_image()

@api_view(["GET"])
def list_countries(request):
    """
    GET /countries?region=Africa&currency=NGN&sort=gdp_desc
    """
    region = request.GET.get("region")
    currency = request.GET.get("currency")
    sort = request.GET.get("sort")
    qs = Country.objects.all()
    if region:
        qs = qs.filter(region=region)
    if currency:
        qs = qs.filter(currency_code=currency)
    if sort == "gdp_desc":
        qs = qs.order_by("-estimated_gdp")
    elif sort == "gdp_asc":
        qs = qs.order_by("estimated_gdp")

    serializer = CountrySerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["GET", "DELETE"])
def country_detail(request, name):
    """
    GET or DELETE /countries/<name> (case-insensitive)
    """
    country = Country.objects.filter(name__iexact=name).first()
    if not country:
        return Response({"error": "Country not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = CountrySerializer(country)
        return Response(serializer.data)
    elif request.method == "DELETE":
        country.delete()
        return Response({"status": "deleted"}, status=status.HTTP_200_OK)

@api_view(["GET"])
def status_view(request):
    total = Country.objects.count()
    meta = AppMeta.objects.filter(key="last_refreshed_at").first()
    last_ref = meta.value if meta else None
    return Response({"total_countries": total, "last_refreshed_at": last_ref})


@api_view(['GET'])
def serve_image(request):
    image_path = "cache/summary.png"
    if not os.path.exists(image_path):
        return JsonResponse({"error": "Summary image not found"}, status=404)
    return FileResponse(open(image_path, "rb"), content_type="image/png")


