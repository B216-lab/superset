CREATE TABLE IF NOT EXISTS public.sales_orders (
    order_id integer PRIMARY KEY,
    order_date date NOT NULL,
    region text NOT NULL,
    product text NOT NULL,
    sales_channel text NOT NULL,
    customer_segment text NOT NULL,
    quantity integer NOT NULL,
    unit_price numeric(10, 2) NOT NULL,
    revenue numeric(12, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

INSERT INTO public.sales_orders (
    order_id,
    order_date,
    region,
    product,
    sales_channel,
    customer_segment,
    quantity,
    unit_price
)
VALUES
    (1, '2026-01-03', 'EMEA', 'Analytics Pro', 'Partner', 'Enterprise', 12, 199.00),
    (2, '2026-01-10', 'North America', 'Analytics Pro', 'Direct', 'Mid-Market', 8, 199.00),
    (3, '2026-01-12', 'APAC', 'Viewer Seats', 'Self-Service', 'SMB', 25, 29.00),
    (4, '2026-01-18', 'EMEA', 'Embedded BI', 'Direct', 'Enterprise', 3, 1499.00),
    (5, '2026-02-02', 'North America', 'Viewer Seats', 'Partner', 'SMB', 40, 29.00),
    (6, '2026-02-11', 'LATAM', 'Analytics Pro', 'Direct', 'Mid-Market', 5, 199.00),
    (7, '2026-02-19', 'APAC', 'Embedded BI', 'Partner', 'Enterprise', 2, 1499.00),
    (8, '2026-03-01', 'North America', 'Analytics Pro', 'Self-Service', 'SMB', 10, 199.00),
    (9, '2026-03-08', 'EMEA', 'Viewer Seats', 'Direct', 'Mid-Market', 60, 29.00),
    (10, '2026-03-14', 'LATAM', 'Analytics Pro', 'Partner', 'Enterprise', 7, 199.00)
ON CONFLICT (order_id) DO NOTHING;
