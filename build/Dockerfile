FROM alpine:3.19.1@sha256:6457d53fb065d6f250e1504b9bc42d5b6c65941d57532c072d929dd0628977d0 as base

COPY .python-version /
RUN apk add --no-cache python3~="$(cat .python-version)"

# Build dependencies
FROM base as builder

ENV POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_IN_PROJECT=1 \
  POETRY_VIRTUALENVS_CREATE=1 \
  POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apk add --no-cache poetry=1.7.1-r0

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --only main --no-root

# Build semgr8s
FROM base

ENV VIRTUAL_ENV=/app/.venv \
  PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy source code and packages
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY semgr8s/ /app/semgr8s
COPY build/harden.sh /
RUN sh /harden.sh

USER 10001:20001

LABEL org.opencontainers.image.documentation="https://sse-secure-systems.github.io/semgr8s/"
LABEL org.opencontainers.image.authors="Christoph Hamsen <christoph.hamsen@securesystems.de>"
LABEL org.opencontainers.image.vendor="Secure Systems Engineering"

CMD ["python", "-m", "semgr8s"]
