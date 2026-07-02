# Public Dashboard Access Overview

Use

```python
AUTH_ROLE_PUBLIC = "Public"
PUBLIC_ROLE_LIKE = "Gamma"
```

Result:

- anonymous users map to `Public`
- `Public` inherits working read permissions from `Gamma`
- with `DASHBOARD_RBAC = True`, only dashboards explicitly assigned to `Public` remain visible

## Required Dashboard Settings

- dashboard must be published
- dashboard must have `Public` role assigned in Superset UI

## Public URL Arguments

- `standalone=1` hide top nav
- `standalone=2` hide top nav + title
- `standalone=3` hide top nav + title + tabs
- `show_filters=0` hide filter bar
- `expand_filters=0` keep filter bar collapsed
- `permalink_key=<key>` restore saved dashboard state

Example:

```text
/superset/dashboard/<id>/?standalone=3&show_filters=0&expand_filters=0
```

## Future Options

If direct public link still shows too much Superset UI:

- iframe: wrap public dashboard URL in custom page
- Superset Embedded SDK: use `hideTitle`, `hideTab`, `hideChartControls`, `filters.visible`, `filters.expanded`, `urlParams.permalink_key`


# Public role permissions

- can read Chart
- can read Dataset
- can read Dashboard
- can read Database
- can explore json Superset
- can dashboard Superset
