# syntax=docker/dockerfile:1

FROM python:3

ARG APP_PATH="/app/deepface"

RUN mkdir -p ${APP_PATH}

WORKDIR ${APP_PATH}

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y

RUN pip install --upgrade pip
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

ARG DEEPFACE_WEIGHTS_DIR="/root/.deepface/weights"

RUN mkdir -p ${DEEPFACE_WEIGHTS_DIR}
RUN wget https://github.com/Star-Clouds/CenterFace/raw/master/models/onnx/centerface.onnx -O ${DEEPFACE_WEIGHTS_DIR}/centerface.onnx
RUN wget https://drive.google.com/uc?id=1qcr9DbgsX3ryrz2uU8w4Xm3cOrRywXqb -O ${DEEPFACE_WEIGHTS_DIR}/yolov8n-face.pt
RUN wget https://github.com/serengil/deepface_models/releases/download/v1.0/vgg_face_weights.h5 -O ${DEEPFACE_WEIGHTS_DIR}/vgg_face_weights.h5


# RUN curl https://github.com/Star-Clouds/CenterFace/raw/master/models/onnx/centerface.onnx -o ${DEEPFACE_WEIGHTS_DIR}/centerface.onnx
