FROM python:3.10.8

RUN apt-get update && \
    apt-get install -y locales && \
    sed -i '/ru_RU.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen && \
    update-locale LANG=ru_RU.UTF-8 \
    apt-get clean && rm -rf /var/lib/apt/lists/* 

ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["sh", "-c", "python manage.py init_db --config=Test && python manage.py runserver --config=Test 0.0.0.0:8000"]
