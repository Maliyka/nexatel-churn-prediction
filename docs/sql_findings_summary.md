# SQL Findings Summary — NexaTel Churn Analysis

*Findings below come directly from `database/queries.sql` run against the normalized PostgreSQL schema. Numbers are real query outputs, not estimates.*

- **Overall churn rate is 26.54%** (1,869 of 7,043 customers) — confirms the VP's ~26.6% figure.
- **Contract type is the single strongest churn driver we can query directly:** Month-to-month customers churn at **42.71%**, vs. 11.27% for one-year contracts and just 2.83% for two-year contracts.
- **Fiber optic internet customers churn at 41.89%**, more than double DSL (18.96%) and nearly 6x customers with no internet service (7.40%) — despite fiber being the premium product. Likely price-sensitivity or service-quality related; worth a product-side follow-up.
- **No tech support = 41.64% churn vs. 15.17% with tech support** — a ~2.7x difference, and tech support is something the company can actively offer.
- **Churned customers have far shorter tenure** (avg. 18.0 months) than retained customers (avg. 37.6 months), and pay more per month on average ($74.44 vs. $61.27) — consistent with newer customers on pricier plans being the most flight-risk.
- **The single highest-risk identifiable segment: Month-to-month + Electronic check payment** — 1,850 customers, 53.7% churn rate. This segment alone should be a standing retention-campaign target.
- **A very narrow, very high-risk segment: tenure < 6 months AND no tech support** — 908 customers, **66.52% churn rate**. This is the sharpest, most actionable segment found in the whole analysis.
- **Electronic check payers churn at 45.29%**, roughly 3x the rate of automatic payment methods (15–17%). Manual payment friction (a customer has to actively pay each month, giving them a natural monthly "should I cancel" decision point) appears to be a real retention lever — nudging customers to autopay is a low-cost intervention.
- **Add-on services show a non-obvious pattern:** churn is *not* lowest at zero add-ons (21.41%) — it actually peaks at exactly 1 add-on service (45.76%) before falling steadily as services stack up, bottoming out at 5.28% for customers with all 6 add-ons. Read together with the fiber-optic finding, this suggests it's not "having services" that retains customers, it's being a *fully invested, bundled* customer — a customer with just one service may be actively trialing/downgrading on their way out.
- **Senior citizens churn nearly twice as often** as non-seniors (41.68% vs. 23.61%) — a demographic segment worth a tailored retention approach (e.g., simplified plans, phone support).
- **Paperless billing customers churn more** (33.57% vs. 16.33%) — likely a proxy for the same "less friction to leave" pattern as electronic check payment, rather than a causal driver on its own.
- **Household stability correlates with retention:** customers with both a partner and dependents churn at just 14.24%, less than half the rate of customers with neither (34.24%).
- **Revenue at risk today: $139,130.85/month, or ~$1.67M annualized** — this is the number the retention program is being built to reduce.

## What this means for the model and the app

These SQL findings directly motivated three of the engineered features built in Phase 3: `tenure_group`, `total_services`, and a combined `high_risk_flag` (short tenure + month-to-month + no tech support) — because the SQL layer already shows that exact combination is the sharpest risk signal in the data (66.5% churn). They also motivated a `payment_risk_flag` for manual/electronic-check payers.
