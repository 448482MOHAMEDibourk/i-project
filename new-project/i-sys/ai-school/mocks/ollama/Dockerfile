FROM python:3.12-slim
WORKDIR /app
COPY app.py /app/app.py
RUN pip install flask
EXPOSE 11434
CMD ["python", "app.py"]
