#!/usr/bin/env bash

set -e

#
# Always install local overrides first
#
/app/docker/docker-bootstrap.sh

STEP_CNT=3
if [ "${LOCAL_TEST_DATASOURCE_ENABLED:-false}" = "true" ]; then
    STEP_CNT=$((STEP_CNT + 1))
fi
if [ "$SUPERSET_LOAD_EXAMPLES" = "yes" ]; then
    STEP_CNT=$((STEP_CNT + 1))
fi

echo_step() {
cat <<EOF
######################################################################
Init Step ${1}/${STEP_CNT} [${2}] -- ${3}
######################################################################
EOF
}
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"

# Initialize the database
echo_step "1" "Starting" "Applying DB migrations"
superset db upgrade
echo_step "1" "Complete" "Applying DB migrations"

# Create an admin user
echo_step "2" "Starting" "Setting up admin user ( admin / $ADMIN_PASSWORD )"
if [ "$CYPRESS_CONFIG" == "true" ]; then
    superset load_test_users
else
    superset fab create-admin \
        --username admin \
        --email admin@superset.com \
        --password "$ADMIN_PASSWORD" \
        --firstname Superset \
        --lastname Admin
fi
echo_step "2" "Complete" "Setting up admin user"
# Create default roles and permissions
echo_step "3" "Starting" "Setting up roles and perms"
superset init
echo_step "3" "Complete" "Setting up roles and perms"

if [ "${LOCAL_TEST_DATASOURCE_ENABLED:-false}" = "true" ]; then
    echo_step "4" "Starting" "Registering local test datasource"
    python /app/docker/register_local_test_datasource.py
    echo_step "4" "Complete" "Registering local test datasource"
fi

if [ "$SUPERSET_LOAD_EXAMPLES" = "yes" ]; then
    EXAMPLES_STEP="$STEP_CNT"
    # Load some data to play with
    echo_step "$EXAMPLES_STEP" "Starting" "Loading examples"


    # If Cypress run which consumes superset_test_config – load required data for tests
    if [ "$CYPRESS_CONFIG" == "true" ]; then
        superset load_examples --load-test-data
    else
        superset load_examples
    fi
    echo_step "$EXAMPLES_STEP" "Complete" "Loading examples"
fi
