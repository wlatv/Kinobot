# Python 3.9 asosida
FROM python:3.9

# Ishchi katalog yaratamiz
WORKDIR /app

# requirements.txt faylni ko‘chirib olib, kutubxonalarni o‘rnatamiz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Barcha fayllarni konteynerga ko‘chiramiz
COPY . .

# Botni ishga tushiramiz
CMD ["python", "bot.py"]
