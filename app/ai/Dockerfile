FROM tensorflow/tensorflow

WORKDIR /python-docker

COPY ./ai/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --ignore-installed embedchain

COPY ./ai/breast_cancer_model.h5 breast_cancer_model.h5
COPY ./ai/predict.py predict.py
COPY ./ai/server.py server.py

CMD [ "python3", "server.py"]
