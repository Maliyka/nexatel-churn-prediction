-- ============================================================================
-- NexaTel Customer Churn Database — Schema (3rd Normal Form)
-- Target: PostgreSQL 14+ (Supabase / Neon.tech compatible)
-- ============================================================================
-- Design notes:
--   The source data arrives as one flat extract (21 columns). We normalize it
--   into 4 logical tables joined on customer_id, mirroring how a real telecom
--   billing/CRM system would actually store this data across domains:
--   customer profile, billing/account, subscribed services, and churn outcome.
-- ============================================================================

DROP TABLE IF EXISTS churn_status CASCADE;
DROP TABLE IF EXISTS services CASCADE;
DROP TABLE IF EXISTS accounts CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- ----------------------------------------------------------------------------
-- 1. customers — core demographic profile (one row per customer)
-- ----------------------------------------------------------------------------
CREATE TABLE customers (
    customer_id     VARCHAR(20)  PRIMARY KEY,
    gender          VARCHAR(10)  NOT NULL CHECK (gender IN ('Male', 'Female')),
    senior_citizen  BOOLEAN      NOT NULL DEFAULT FALSE,
    partner         BOOLEAN      NOT NULL DEFAULT FALSE,
    dependents      BOOLEAN      NOT NULL DEFAULT FALSE,
    tenure          SMALLINT     NOT NULL CHECK (tenure >= 0)
);

COMMENT ON TABLE customers IS 'One row per unique customer — demographic profile only.';

-- ----------------------------------------------------------------------------
-- 2. accounts — billing / contract details (1:1 with customers)
-- ----------------------------------------------------------------------------
CREATE TABLE accounts (
    customer_id         VARCHAR(20)     PRIMARY KEY REFERENCES customers(customer_id) ON DELETE CASCADE,
    contract             VARCHAR(20)     NOT NULL CHECK (contract IN ('Month-to-month', 'One year', 'Two year')),
    paperless_billing     BOOLEAN         NOT NULL DEFAULT FALSE,
    payment_method        VARCHAR(40)     NOT NULL,
    monthly_charges       NUMERIC(8,2)    NOT NULL CHECK (monthly_charges >= 0),
    total_charges         NUMERIC(10,2)       NULL CHECK (total_charges >= 0)  -- NULL for tenure = 0 customers
);

COMMENT ON TABLE accounts IS 'Billing and contract information — one row per customer.';
COMMENT ON COLUMN accounts.total_charges IS 'NULL for brand-new customers (tenure = 0); source data ships these as blank strings.';

-- ----------------------------------------------------------------------------
-- 3. services — subscribed product add-ons (1:1 with customers)
-- ----------------------------------------------------------------------------
CREATE TABLE services (
    customer_id        VARCHAR(20)  PRIMARY KEY REFERENCES customers(customer_id) ON DELETE CASCADE,
    phone_service       VARCHAR(20)  NOT NULL,
    multiple_lines       VARCHAR(25)  NOT NULL,
    internet_service      VARCHAR(15)  NOT NULL CHECK (internet_service IN ('DSL', 'Fiber optic', 'No')),
    online_security       VARCHAR(25)  NOT NULL,
    online_backup         VARCHAR(25)  NOT NULL,
    device_protection     VARCHAR(25)  NOT NULL,
    tech_support           VARCHAR(25)  NOT NULL,
    streaming_tv            VARCHAR(25)  NOT NULL,
    streaming_movies         VARCHAR(25)  NOT NULL
);

COMMENT ON TABLE services IS 'Subscribed phone / internet / add-on services — one row per customer.';

-- ----------------------------------------------------------------------------
-- 4. churn_status — the outcome / target variable (1:1 with customers)
-- ----------------------------------------------------------------------------
CREATE TABLE churn_status (
    customer_id  VARCHAR(20)  PRIMARY KEY REFERENCES customers(customer_id) ON DELETE CASCADE,
    churn         BOOLEAN      NOT NULL
);

COMMENT ON TABLE churn_status IS 'Target variable, kept separate from customers to guard against accidental leakage into feature tables.';

-- ----------------------------------------------------------------------------
-- Indexes for common query patterns (joins + filters used in queries.sql)
-- ----------------------------------------------------------------------------
CREATE INDEX idx_accounts_contract        ON accounts(contract);
CREATE INDEX idx_accounts_payment_method  ON accounts(payment_method);
CREATE INDEX idx_services_internet        ON services(internet_service);
CREATE INDEX idx_customers_tenure         ON customers(tenure);
CREATE INDEX idx_churn_status_churn       ON churn_status(churn);

-- ----------------------------------------------------------------------------
-- Convenience view: flattens all 4 tables back into one row per customer.
-- Used by the Python ETL / EDA layer instead of hand-writing the same join
-- everywhere.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_customer_360 AS
SELECT
    c.customer_id,
    c.gender,
    c.senior_citizen,
    c.partner,
    c.dependents,
    c.tenure,
    a.contract,
    a.paperless_billing,
    a.payment_method,
    a.monthly_charges,
    a.total_charges,
    s.phone_service,
    s.multiple_lines,
    s.internet_service,
    s.online_security,
    s.online_backup,
    s.device_protection,
    s.tech_support,
    s.streaming_tv,
    s.streaming_movies,
    cs.churn
FROM customers c
JOIN accounts a       ON a.customer_id  = c.customer_id
JOIN services s        ON s.customer_id  = c.customer_id
JOIN churn_status cs  ON cs.customer_id = c.customer_id;

COMMENT ON VIEW v_customer_360 IS 'Denormalized 360-degree view — one row per customer, all domains joined. Used for EDA / feature engineering.';
