# syntax=docker/dockerfile:1
# Sandboxed SLM inference. Build from slm/ so model.py is in the context:
#   docker build -f serve/Dockerfile -t topak-slm-serve .
# serve/Dockerfile.dockerignore keeps data/ and runs/ out of the context.
# The base is pinned by its multi-arch index digest, so the same line builds linux/arm64 on an
# M-series Mac and linux/amd64 elsewhere.
ARG PYTHON=python:3.12-slim@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f

FROM ${PYTHON} AS build
COPY serve/requirements.txt /tmp/requirements.txt
# Behind a TLS-intercepting proxy, pass its CA as a build secret (never stored in a layer):
#   docker build --secret id=pip_ca,src=/path/to/ca.pem ...
RUN --mount=type=secret,id=pip_ca,required=false \
    if [ -s /run/secrets/pip_ca ]; then export PIP_CERT=/run/secrets/pip_ca; fi \
 && python -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir --require-hashes --only-binary=:all: -r /tmp/requirements.txt \
 && /opt/venv/bin/pip uninstall -y pip \
 && find /opt/venv -name __pycache__ -prune -exec rm -rf {} +

FROM ${PYTHON}
RUN useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin slm \
 && rm -rf /usr/local/lib/python3.12/site-packages/pip* /usr/local/bin/pip*
COPY --from=build /opt/venv /opt/venv
COPY model.py serve/serve.py /opt/slm/
ENV PATH=/opt/venv/bin:$PATH \
    SLM_BUNDLE=/model \
    HF_HUB_OFFLINE=1
USER 10001:10001
WORKDIR /opt/slm
ENTRYPOINT ["python", "-I", "-B", "/opt/slm/serve.py"]
