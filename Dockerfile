FROM python:3.11.6-slim-bullseye
WORKDIR /senac-api
COPY requirements.txt /senac-api
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5555
ENV FLASK_APP=application.py
CMD ["python3", "./application.py"]