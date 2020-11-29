FROM python:3.7

LABEL description "Renderable core library."
LABEL version "1.0.0"
LABEL maintainer "Danilo Peixoto <danilo@therenderable.com>"

WORKDIR /usr/src/renderable-core/
COPY . .

RUN pip3 install --upgrade pip
RUN pip3 install .
