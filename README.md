# 🌍 Country Exchange API

A Django REST API that provides country data, exchange rates, and generates a summary image displaying total countries, top 5 countries by estimated GDP, and the last refresh timestamp.

---

## 🚀 Features

- Fetch and refresh countries with population, currency, and GDP estimates  
- Retrieve details for a specific country (case-insensitive)  
- Sort countries by GDP  
- Generate a summary image with top GDP countries  
- Serve the summary image from the `/countries/image` endpoint  
- View refresh status and total countries stored  

---

## 🧩 API Endpoints

| Method | Endpoint | Description |
|--------|-----------|--------------|
| **POST** | `/countries/refresh` | Fetches data from external APIs and updates the database |
| **GET** | `/countries` | Lists all countries (supports filters: `region`, `currency`, `sort`) |
| **GET** | `/countries/<name>` | Retrieves details of a specific country (case-insensitive) |
| **DELETE** | `/countries/<name>` | Deletes a specific country (case-insensitive) |
| **GET** | `/countries/image` | Serves the generated summary image |
| **GET** | `/status` | Returns total countries and last refresh timestamp |

---

## ⚙️ Tech Stack

- **Backend:** Django 5.x, Django REST Framework  
- **Database:** SQLite (default) or PostgreSQL for production  
- **External APIs:**  
  - [REST Countries](https://restcountries.com/v2/all)  
  - [Open Exchange Rates API](https://open.er-api.com/v6/latest/USD)

---

## 🧠 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/country_exchange2.git
cd country_exchange2
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Start the development server
```bash
python manage.py runserver
```

Then open:  
👉 **http://127.0.0.1:8000/countries**

---

## ☁️ Deployment (Railway)

1. Push your project to GitHub.
2. Go to [Railway.app](https://railway.app).
3. Create a **New Project → Deploy from GitHub Repo**.
4. Add environment variables:
   - `DJANGO_SETTINGS_MODULE=country_exchange2.settings`
   - `PORT=8000`
   - `PYTHONUNBUFFERED=1`
5. Railway will automatically detect your `Procfile` and build your app.

---

## ⚙️ Procfile

```
web: gunicorn country_exchange2.wsgi
```

---

## 🧾 requirements.txt

```
Django>=5.0
djangorestframework>=3.15
gunicorn
requests
pillow
```

---

## 🖼️ Summary Image Generation

After running:
```bash
POST /countries/refresh
```
A new image will be created at:
```
cache/summary.png
```
You can access it directly via:
```
GET /countries/image
```

---

## 📄 License

MIT License © 2025  
Developed by Benjamin Eromosele Odion-Owase
