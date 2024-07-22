# syntax=docker/dockerfile:1

FROM python:3.12.4

ARG DEEPFACE_WEIGHTS_DIR="/root/.deepface/weights"
RUN mkdir -p ${DEEPFACE_WEIGHTS_DIR} && \
    wget https://github.com/Star-Clouds/CenterFace/raw/master/models/onnx/centerface.onnx -O ${DEEPFACE_WEIGHTS_DIR}/centerface.onnx && \
    wget https://drive.google.com/uc?id=1qcr9DbgsX3ryrz2uU8w4Xm3cOrRywXqb -O ${DEEPFACE_WEIGHTS_DIR}/yolov8n-face.pt && \
    wget https://github.com/serengil/deepface_models/releases/download/v1.0/vgg_face_weights.h5 -O ${DEEPFACE_WEIGHTS_DIR}/vgg_face_weights.h5
# RUN curl https://github.com/Star-Clouds/CenterFace/raw/master/models/onnx/centerface.onnx -o ${DEEPFACE_WEIGHTS_DIR}/centerface.onnx

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6

COPY ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# RUN rm -r $HOME/.cache

ARG APP_DIR="/app/deepface"
RUN mkdir -p ${APP_DIR}
WORKDIR ${APP_DIR}
