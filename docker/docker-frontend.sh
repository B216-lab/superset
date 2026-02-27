#!/usr/bin/env bash

set -e

# Packages needed for puppeteer:
if [ "$PUPPETEER_SKIP_CHROMIUM_DOWNLOAD" = "false" ]; then
    apt update
    apt install -y chromium
fi

if [ "$BUILD_SUPERSET_FRONTEND_IN_DOCKER" = "true" ]; then
    echo "Building Superset frontend in dev mode inside docker container"
    cd /app/superset-frontend

    if [ "$NPM_RUN_PRUNE" = "true" ]; then
        echo "Running `npm run prune`"
        npm run prune
    fi

    echo "Running `npm install`"
    npm install

    echo "Start webpack dev server"
    # start the webpack dev server, serving dynamically at http://localhost:9000
    # it proxies to the backend served at http://localhost:8088
    npm run dev-server

else
    echo "Skipping frontend build steps - YOU NEED TO RUN IT MANUALLY ON THE HOST!"
    echo "https://superset.apache.org/docs/contributing/development/#webpack-dev-server"
fi
