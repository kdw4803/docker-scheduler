FROM python:3.6-slim
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential libzbar-dev default-libmysqlclient-dev vim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "app.py"]