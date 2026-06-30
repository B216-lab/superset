ARG SUPERSET_VERSION=6.0.0

FROM node:20-bookworm-slim AS ru-language-pack

ARG SUPERSET_VERSION

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates curl && \
    rm -rf /var/lib/apt/lists/* && \
    npm install --global po2json@0.4.5

RUN mkdir -p /out/ru/LC_MESSAGES && \
    curl -fsSL \
        "https://raw.githubusercontent.com/apache/superset/${SUPERSET_VERSION}/superset/translations/ru/LC_MESSAGES/messages.po" \
        -o /out/ru/LC_MESSAGES/messages.po && \
    po2json \
        --domain superset \
        --format jed1.x \
        --fuzzy \
        /out/ru/LC_MESSAGES/messages.po \
        /out/ru/LC_MESSAGES/messages.json

FROM apache/superset:${SUPERSET_VERSION}

USER root

COPY --from=ru-language-pack /out/ru /app/superset/translations/ru

RUN /app/.venv/bin/pybabel compile -d /app/superset/translations -l ru; \
    test -f /app/superset/translations/ru/LC_MESSAGES/messages.mo && \
    rm -f /app/superset/translations/ru/LC_MESSAGES/messages.po

# Install packages using uv into the virtual environment
# hadolint ignore=SC1091
RUN . /app/.venv/bin/activate && \
    uv pip install \
    # https://superset.apache.org/docs/configuration/databases/
    # install psycopg2 for using PostgreSQL metadata store and connection
    psycopg2-binary \
    # 
    # https://superset.apache.org/docs/configuration/configuring-superset/#custom-oauth2-configuration
    # package needed for using single-sign on authentication:
    Authlib \
    #
    # openpyxl to be able to upload Excel files
    openpyxl \
    #
    # Pillow for Alerts & Reports to generate PDFs of dashboards
    Pillow


# Switch back to the superset user
USER superset

CMD ["/app/docker/entrypoints/run-server.sh"]
