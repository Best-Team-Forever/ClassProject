FROM python:3.9.19-slim-bullseye

WORKDIR /python-docker

CMD ["apt-get", "update"]
CMD ["apt-get", "-y", "install", "pkg-config"]

COPY ./ai/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./ai/breast_cancer_model.h5 breast_cancer_model.h5
COPY ./ai/predict.py predict.py
COPY ./ai/server.py server.py

CMD [ "python3", "server.py"]
