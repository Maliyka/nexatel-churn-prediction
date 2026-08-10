-- ============================================================================
-- NexaTel Customer Churn — Business SQL Queries
-- All queries join across customers / accounts / services / churn_status.
-- Run against the schema created by schema.sql after load_data.py has run.
-- ============================================================================


-- ----------------------------------------------------------------------------
-- Q1. What is the overall churn rate?
-- ----------------------------------------------------------------------------
SELECT
    COUNT(*) FILTER (WHERE churn) AS churned_customers,
    COUNT(*) AS total_customers,
    ROUND(100.0 * COUNT(*) FILTER (WHERE churn) / COUNT(*), 2) AS churn_rate_pct
FROM churn_status;


-- ----------------------------------------------------------------------------
-- Q2. Does contract type affect churn rate?
-- ----------------------------------------------------------------------------
SELECT
    a.contract,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE cs.churn) AS churned,
    ROUND(100.0 * COUNT(*) FILTER (WHERE cs.churn) / COUNT(*), 2) AS churn_rate_pct
FROM accounts a
JOIN churn_status cs ON cs.customer_id = a.customer_id
GROUP BY a.contract
ORDER BY churn_rate_pct DESC;


-- ----------------------------------------------------------------------------
-- Q3. Does internet service type affect churn?
-- ----------------------------------------------------------------------------
SELECT
    s.internet_service,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE cs.churn) AS churned,
    ROUND(100.0 * COUNT(*) FILTER (WHERE cs.churn) / COUNT(*), 2) AS churn_rate_pct
FROM services s
JOIN churn_status cs ON cs.customer_id = s.customer_id
GROUP BY s.internet_service
ORDER BY churn_rate_pct DESC;


-- ----------------------------------------------------------------------------
-- Q4. Are customers with tech support less likely to churn?
-- ----------------------------------------------------------------------------
SELECT
    s.tech_support,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE cs.churn) AS churned,
    ROUND(100.0 * COUNT(*) FILTER (WHERE cs.churn) / COUNT(*), 2) AS churn_rate_pct
FROM services s
JOIN churn_status cs ON cs.customer_id = s.customer_id
GROUP BY s.tech_support
ORDER BY churn_rate_pct DESC;


-- ----------------------------------------------------------------------------
-- Q5. Average tenure of churned vs. retained customers
-- ----------------------------------------------------------------------------
SELECT
    cs.churn,
    ROUND(AVG(c.tenure), 1) AS avg_tenure_months,
    ROUND(STDDEV(c.tenure), 1) AS stddev_tenure
FROM customers c
JOIN churn_status cs ON cs.customer_id = c.customer_id
GROUP BY cs.churn;


-- ----------------------------------------------------------------------------
-- Q6. Average monthly charges of churned vs. retained customers
-- ----------------------------------------------------------------------------
SELECT
    cs.churn,
    ROUND(AVG(a.monthly_charges), 2) AS avg_monthly_charges,
    ROUND(AVG(a.total_charges), 2) AS avg_total_charges
FROM accounts a
JOIN churn_status cs ON cs.customer_id = a.customer_id
GROUP BY cs.churn;


-- ----------------------------------------------------------------------------
-- Q7. Total monthly recurring revenue currently at risk (from churned customers)
-- ----------------------------------------------------------------------------
SELECT
    ROUND(SUM(a.monthly_charges), 2) AS monthly_revenue_at_risk,
    ROUND(SUM(a.monthly_charges) * 12, 2) AS annualized_revenue_at_risk
FROM accounts a
JOIN churn_status cs ON cs.customer_id = a.customer_id
WHERE cs.churn = TRUE;


-- ----------------------------------------------------------------------------
-- Q8. Top 5 customer segments (contract x payment method) with highest churn
--     (minimum 30 customers in the segment, to avoid noisy small groups)
-- ----------------------------------------------------------------------------
SELECT
    a.contract,
    a.payment_method,
    COUNT(*) AS segment_size,
    COUNT(*) FILTER (WHERE cs.churn) AS churned,
    ROUND(100.0 * COUNT(*) FILTER (WHERE cs.churn) / COUNT(*), 2) AS churn_rate_pct
FROM accounts a
JOIN churn_status cs ON cs.customer_id = a.customer_id
GROUP BY a.contract, a.payment_method
HAVING COUNT(*) >= 30
ORDER BY churn_rate_pct DESC
LIMIT 5;


-- ----------------------------------------------------------------------------
-- Q9. Churn rate for customers with tenure < 6 months AND no tech support
--     (a proxy "high risk onboarding" segment)
-- ----------------------------------------------------------------------------
SELECT
    COUNT(*) AS segment_size,
    COUNT(*) FILTER (WHERE cs.churn) AS churned,
    ROUND(100.0 * COUNT(*) FILTER (WHERE cs.churn) / COUNT(*), 2) AS churn_rate_pct
FROM customers c
JOIN services s        ON s.customer_id  = c.customer_id
JOIN churn_status cs   ON cs.customer_id = c.customer_id
WHERE c.tenure < 6
  AND s.tech_support = 'No';


-- ----------------------------------------------------------------------------
-- Q10. Correlation between number of subscribed add-on services and churn
--      (counts OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport,
--       StreamingTV, StreamingMovies where the customer actually has the add-on)
-- ----------------------------------------------------------------------------
WITH service_counts AS (
    SELECT
        s.customer_id,
        (CASE WHEN s.online_security   = 'Yes' THEN 1 ELSE 0 END +
         CASE WHEN s.online_backup     = 'Yes' THEN 1 ELSE 0 END +
         CASE WHEN s.device_protection = 'Yes' THEN 1 ELSE 0 END +
         CASE WHEN s.tech_support      = 'Yes' THEN 1 ELSE 0 END +
         CASE WHEN s.streaming_tv      = 'Yes' THEN 1 ELSE 0 END +
         CASE WHEN s.streaming_movies  = 'Yes' THEN 1 ELSE 0 END) AS num_addon_services
    FROM services s
)
SELECT
    sc.num_addon_services,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE cs.churn) AS churned,
    ROUND(100.0 * COUNT(*) FILTER (WHERE cs.churn) / COUNT(*), 2) AS churn_rate_pct
FROM service_counts sc
JOIN churn_status cs ON cs.customer_id = sc.customer_id
GROUP BY sc.num_addon_services
ORDER BY sc.num_addon_services;


-- ----------------------------------------------------------------------------
-- Q11. Does payment method correlate with churn? (manual/check vs. automatic)
-- ----------------------------------------------------------------------------
SELECT
    a.payment_method,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE cs.churn) AS churned,
    ROUND(100.0 * COUNT(*) FILTER (WHERE cs.churn) / COUNT(*), 2) AS churn_rate_pct
FROM accounts a
JOIN churn_status cs ON cs.customer_id = a.customer_id
GROUP BY a.payment_method
ORDER BY churn_rate_pct DESC;


-- ----------------------------------------------------------------------------
-- Q12. Highest-risk segment: Contract x Tenure bucket (2-way cross-tab)
-- ----------------------------------------------------------------------------
SELECT
    a.contract,
    CASE
        WHEN c.tenure <= 12 THEN '0-12 months'
        WHEN c.tenure <= 24 THEN '13-24 months'
        WHEN c.tenure <= 48 THEN '25-48 months'
        ELSE '49+ months'
    END AS tenure_bucket,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE cs.churn) AS churned,
    ROUND(100.0 * COUNT(*) FILTER (WHERE cs.churn) / COUNT(*), 2) AS churn_rate_pct
FROM customers c
JOIN accounts a       ON a.customer_id  = c.customer_id
JOIN churn_status cs  ON cs.customer_id = c.customer_id
GROUP BY a.contract, tenure_bucket
ORDER BY churn_rate_pct DESC
LIMIT 10;


-- ----------------------------------------------------------------------------
-- Q13. Senior citizens vs. non-senior citizens — churn comparison
-- ----------------------------------------------------------------------------
SELECT
    c.senior_citizen,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE cs.churn) AS churned,
    ROUND(100.0 * COUNT(*) FILTER (WHERE cs.churn) / COUNT(*), 2) AS churn_rate_pct
FROM customers c
JOIN churn_status cs ON cs.customer_id = c.customer_id
GROUP BY c.senior_citizen;


-- ----------------------------------------------------------------------------
-- Q14. Does paperless billing correlate with churn?
-- ----------------------------------------------------------------------------
SELECT
    a.paperless_billing,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE cs.churn) AS churned,
    ROUND(100.0 * COUNT(*) FILTER (WHERE cs.churn) / COUNT(*), 2) AS churn_rate_pct
FROM accounts a
JOIN churn_status cs ON cs.customer_id = a.customer_id
GROUP BY a.paperless_billing
ORDER BY churn_rate_pct DESC;


-- ----------------------------------------------------------------------------
-- Q15. Customers with Partner AND Dependents vs. neither — churn comparison
--      (family / household stability as a retention factor)
-- ----------------------------------------------------------------------------
SELECT
    CASE
        WHEN c.partner AND c.dependents THEN 'Partner + Dependents'
        WHEN c.partner AND NOT c.dependents THEN 'Partner only'
        WHEN NOT c.partner AND c.dependents THEN 'Dependents only'
        ELSE 'Neither'
    END AS household_type,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE cs.churn) AS churned,
    ROUND(100.0 * COUNT(*) FILTER (WHERE cs.churn) / COUNT(*), 2) AS churn_rate_pct
FROM customers c
JOIN churn_status cs ON cs.customer_id = c.customer_id
GROUP BY household_type
ORDER BY churn_rate_pct DESC;
