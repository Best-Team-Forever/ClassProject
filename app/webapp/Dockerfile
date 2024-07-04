FROM openjdk:24-slim-bullseye
COPY --from=python:3.9.6-slim-bullseye / /

WORKDIR /python-docker

CMD ["apt-get", "update"]
CMD ["apt-get", "-y", "install", "pkg-config"]

COPY ./ai/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install pillow

COPY ./ai/breast_cancer_model.h5 breast_cancer_model.h5
COPY ./ai/predict.py predict.py

WORKDIR /java-docker

COPY ./webapp/DeepScan/target/DeepScan-1.0.jar /application/deepscan.jar
ENTRYPOINT ["java","-jar","/application/deepscan.jar"]
