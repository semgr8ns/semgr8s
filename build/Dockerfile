FROM python:3.12-alpine@sha256:14cfc61fc2404da8adc7b1cb1fcb299aefafab22ae571f652527184fbb21ce69 as base

# Build dependencies
FROM base as builder

RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt

RUN YARL_NO_EXTENSIONS=1 MULTIDICT_NO_EXTENSIONS=1 pip install --no-cache-dir --prefix=/install --require-hashes -r /requirements.txt

# Build semgr8s
FROM base

RUN mkdir /app \
  && chown 10001:20001 /app \
  && mkdir /.semgrep \
  && chown 10001:20001 /.semgrep \
  && mkdir /.cache \
  && chown 10001:20001 /.cache

WORKDIR /app
COPY build/harden.sh /
RUN sh /harden.sh && rm /harden.sh

# Copy source code and packages
COPY --from=builder /install /usr/local
COPY semgr8s/ /app/semgr8s

USER 10001:20001

LABEL org.opencontainers.image.documentation="https://sse-secure-systems.github.io/semgr8s/"
LABEL org.opencontainers.image.authors="Christoph Hamsen <christoph.hamsen@securesystems.de>"
LABEL org.opencontainers.image.vendor="Secure Systems Engineering"

CMD ["python", "-m", "semgr8s"]
