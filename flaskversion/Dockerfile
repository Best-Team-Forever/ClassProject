FROM python:3.12.4-bookworm

WORKDIR /python-docker

CMD ["apt-get", "update"]
CMD ["apt-get", "-y", "install", "pkg-config"]

COPY ./index.html index.html
COPY ./app.py app.py
COPY ./result.html result.html
COPY ./breast_cancer_model.h5 breast_cancer_model.h5
COPY ./requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

CMD [ "python3", "app.py"]
