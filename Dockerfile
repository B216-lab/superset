# or master for the latest
FROM apache/superset:5.0.0

USER root

# Install packages using uv into the virtual environment
RUN . /app/.venv/bin/activate && \
    uv pip install \
    # https://superset.apache.org/docs/configuration/databases/
    # install psycopg2 for using PostgreSQL metadata store and connection
    psycopg2-binary \
    # 
    # https://superset.apache.org/docs/configuration/configuring-superset/#custom-oauth2-configuration
    # package needed for using single-sign on authentication:
    # Authlib \
    #
    # openpyxl to be able to upload Excel files
    openpyxl \
    
    # Pillow for Alerts & Reports to generate PDFs of dashboards
    Pillow


# Switch back to the superset user
USER superset

CMD ["/app/docker/entrypoints/run-server.sh"]