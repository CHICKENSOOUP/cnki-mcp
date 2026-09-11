ARG CNKI_COMMIT=f7f423c9962c2cfcde8b31086bdb3e1099c46888

FROM golang:1.26-bookworm AS cnki-builder
ARG CNKI_COMMIT
RUN mkdir -p /out \
 && GOBIN=/out go install github.com/ExquisiteCore/cnki-search/cmd/cnki@${CNKI_COMMIT}

FROM python:3.12-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml README.md LICENSE THIRD_PARTY_NOTICES.md ./
COPY cnki_chatgpt ./cnki_chatgpt
RUN pip install --no-cache-dir .
COPY --from=cnki-builder /out/cnki /usr/local/bin/cnki
RUN useradd --create-home --uid 10001 appuser
USER appuser
ENV CNKI_BIN=/usr/local/bin/cnki \
    HOST=0.0.0.0 \
    PORT=8000 \
    PYTHONUNBUFFERED=1
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).read()" || exit 1
CMD ["cnki-chatgpt-mcp"]
