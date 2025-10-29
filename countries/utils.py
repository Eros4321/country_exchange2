from PIL import Image, ImageDraw, ImageFont
from django.utils import timezone
import os
from .models import Country

def generate_summary_image():
    os.makedirs("cache", exist_ok=True)
    image_path = "cache/summary.png"

    countries = Country.objects.all().order_by('-estimated_gdp')
    total = countries.count()
    top_5 = countries[:5]

    # Create image
    img = Image.new("RGB", (600, 400), color="white")
    draw = ImageDraw.Draw(img)

    # You can customize font if you like
    # font = ImageFont.truetype("arial.ttf", 16)
    font = None  

    draw.text((20, 20), f"Total Countries: {total}", fill="black", font=font)

    draw.text((20, 60), "Top 5 by GDP:", fill="black", font=font)
    y = 90
    for c in top_5:
        draw.text((40, y), f"- {c.name}: {c.estimated_gdp}", fill="black", font=font)
        y += 25

    draw.text((20, y + 20), f"Last updated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}",
              fill="black", font=font)

    img.save(image_path)
    return image_path
