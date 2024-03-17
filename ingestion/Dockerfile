FROM python:3.9  
WORKDIR /app

COPY . .
COPY requirements.txt ./
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "main.py"]