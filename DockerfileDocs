FROM alpine:latest

# Install required packages
RUN apk --no-cache add \
  py2-pip \
  python-dev \
  make \
  git \
  gcc \
  alpine-sdk

RUN mkdir -p /src
WORKDIR /src
ADD . /src

RUN pip install -r docs/requirements.txt
RUN pip install sphinx-autobuild
RUN pip install -e .

EXPOSE 8050

CMD sphinx-autobuild --host 0.0.0.0 --port 8050 -z src docs docs/_build/html
