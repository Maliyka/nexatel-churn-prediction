# Problem Statement — NexaTel Customer Churn Prediction & Retention Intelligence System

## 1. Problem Statement (Formal)

NexaTel Communications, a regional telecom provider serving roughly 500,000 subscribers, is losing customers at a churn rate of approximately 26.5% — well above a sustainable level for a subscription-based business. Because retention offers are currently issued reactively, after a customer has already shown intent to leave or has cancelled outright, the company both overspends on customers who were never at risk and fails to intervene with customers who were genuinely about to churn. This project builds a data-driven system that scores every active customer's churn risk in advance, explains the top drivers behind that score in plain language, and surfaces that score inside a tool the retention team can use without any data science background — turning churn management from a reactive, guesswork process into a proactive, targeted one.

## 2. Target Variable & Error Cost Decision

**Target variable:** `Churn` (binary: Yes / No), 1 = customer cancelled service.

**Which error costs more?**

| Error type | What it means | Business cost |
|---|---|---|
| **False Negative** (model says "won't churn," customer churns) | An at-risk customer is missed entirely — no retention offer is sent | Full loss of that customer's recurring revenue (avg. **$74.44/month**, i.e. ~$893/year per customer) |
| **False Positive** (model says "will churn," customer stays) | A loyal customer is sent an unnecessary discount/offer | Cost of the offer only — typically a fraction of one month's revenue |

**Decision:** A missed churner (False Negative) is far more expensive than a wasted retention offer (False Positive). This means **Recall on the churn class** (and, to keep precision from collapsing, **F1-score**) is the metric this project optimizes for — not raw Accuracy. This decision is carried through Phase 5 (model selection) and Phase 7 (the risk thresholds shown in the app).

## 3. Business Questions This Analysis Answers

1. What is NexaTel's overall churn rate, and how much recurring revenue does it represent?
2. Does contract type (month-to-month vs. one-year vs. two-year) affect churn?
3. Are customers without tech support more likely to churn than those with it?
4. Does internet service type (DSL vs. Fiber optic vs. None) correlate with churn?
5. How does payment method relate to churn — are manual/check payers riskier?
6. Do customers with short tenure churn at a meaningfully higher rate than long-tenured customers?
7. Which combination of contract type × payment method produces the highest-risk segments?
8. Does the number of subscribed add-on services (security, backup, streaming, etc.) reduce churn risk?
9. Is there a relationship between monthly charges and churn — are higher bills driving cancellations?
10. What is the single highest-risk customer segment when tenure and contract type are combined?

## 4. Headline Statistic — Revenue at Risk

Using the raw extract (7,043 customers):

- **Churned customers:** 1,869 (26.54% of the customer base)
- **Average monthly charge among churned customers:** $74.44
- **Monthly recurring revenue at risk:** **$139,130.85**
- **Annualized recurring revenue at risk:** **≈ $1,669,570**

> This is the headline number this project is built to move: if the retention team can prevent even 10% of these churns with a well-targeted offer, that is roughly **$167,000/year** in protected recurring revenue.

## 5. Stakeholders & What They Care About

| Stakeholder | Cares About | How this project serves them |
|---|---|---|
| VP of Customer Retention | Lowering churn rate, protecting recurring revenue | A single dashboard number: revenue at risk, trending down |
| Retention Agents | A simple score + reason, not raw model output | The web app's risk badge (Low/Medium/High) + top-3 reasons |
| Finance Team | A defensible revenue-at-risk figure for budget planning | SQL query #7 (total monthly revenue at risk) + model output aggregated |
| IT / Engineering | Clean, documented code that could eventually be integrated | Normalized schema, documented SQL, typed API, README |

## 6. Success Criteria for This Project

- A model that achieves **meaningfully higher recall on the churn class than a naive baseline** (predicting "no churn" for everyone would score 73.5% accuracy but 0% recall — the naive floor to beat).
- A deployed tool a retention agent can use in under 30 seconds per customer.
- Every prediction accompanied by a human-readable explanation, not just a probability.
