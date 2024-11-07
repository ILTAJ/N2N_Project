FROM tensorflow/tensorflow:2.6.0

WORKDIR /app
COPY . /app

RUN pip --trusted-host files.pythonhosted.org --trusted-host pypi.org --trusted-host pypi.python.org install --timeout=60 -r requirements.txt

CMD ["python", "app.py"]