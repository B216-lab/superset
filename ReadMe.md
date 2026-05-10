# 🐳 Apache Superset
B216 Superset docker image with PostgreSQL driver and SSO support.

# 📖 Resources

- _Superset's metadata database_ - database to store the information it manages, like the definitions of charts, dashboards, and many other things

> Don't forget to check version of documentation

- [Building your own production Docker image](https://superset.apache.org/docs/installation/docker-builds#building-your-own-production-docker-image)
- [Configuring Superset](https://superset.apache.org/docs/configuration/configuring-superset)
- [Connecting Superset to your local database instance](https://superset.apache.org/docs/installation/docker-compose/#4-connecting-superset-to-your-local-database-instance)

# Local dev without Authentik

Run:

`just local-dev`

Then open `http://localhost:8088` and log in with `admin` / `admin` unless `ADMIN_PASSWORD` changed.
Recipe writes `docker/.env-local` with local auth/example-data overrides before startup.

Local profile also loads:

- disposable Postgres datasource `Local Test Postgres`
- seeded table `public.sales_orders`
- Superset example charts and dashboards
