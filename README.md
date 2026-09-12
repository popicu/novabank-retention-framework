# NovaBank: Predictive Retention & Margin Optimization Framework

This repository contains the reproducible analytical pipeline and business decision framework for the **Quantic MSBA Analytics Methods and Frameworks Project**.

## Executive Summary

NovaBank wants to improve the economics of outbound deposit-retention outreach by prioritizing customers who are most likely to convert.

The analysis uses the UCI Bank Marketing `bank-additional-full.csv` dataset with **41,188 customer-contact records** and an observed historical conversion rate of **11.27%**.

The recommended operating policy is to **rank customers by predicted conversion probability and target the highest-scoring 20%**. No fixed probability threshold is required.

The final model is a **HistGradientBoostingClassifier**, benchmarked against Logistic Regression. The post-call `duration` variable is excluded because it is unavailable before an outbound call and would create data leakage.

## Key Results

| Metric | Logistic Regression | Gradient Boosting |
|---|---:|---:|
| Test ROC-AUC | 0.8008 | **0.8142** |
| Brier Score | 0.0769 | **0.0743** |
| Precision @ Top 20% | 36.67% | **37.77%** |
| Recall @ Top 20% | 65.09% | **67.03%** |
| Lift @ Top 20% | 3.26x | **3.35x** |

Under the illustrative campaign economics used in the analysis:

- Call cost: **€15**
- Campaign value per conversion: **€250**
- Legacy mass outreach profit: **€542,180**
- Logistic top-20% profit: **€631,430**
- Gradient Boosting top-20% profit: **€653,930**
- Improvement vs. legacy: **€111,750 (+20.6%)**
- Customers targeted: **8,238**
- Estimated conversions captured: **3,110**

The economics remain positive under an illustrative **€200 campaign-value scenario**, where the top-20% policy produces approximately **€498,430** versus **€310,180** for mass outreach.

An additional illustrative interest-rate sensitivity assumes a 100-basis-point reduction corresponds to an **8.5% conversion reduction**. Under that scenario, estimated top-20% profit remains positive at approximately **€587,930**. This is a scenario assumption, **not a causal estimate**.

## Analytical Approach

1. Load and validate `bank-additional-full.csv`.
2. Define `y = yes` as the positive outcome.
3. Remove `duration` to prevent post-call leakage.
4. Engineer a `previously_contacted` indicator from `pdays`.
5. One-hot encode categorical variables.
6. Create an 80/20 stratified train/test split.
7. Train Logistic Regression as the baseline.
8. Train HistGradientBoosting as the improved model.
9. Evaluate ROC-AUC, Brier score, Precision@20%, Recall@20%, and lift.
10. Apply a top-20% ranking policy.
11. Estimate campaign economics and sensitivity scenarios.
12. Run permutation-importance analysis.
13. Monitor selection and outcomes across age, marital-status, and education subgroups.
14. Examine campaign-contact saturation descriptively.
15. Save analytical outputs to `outputs/`.

## Governance and Interpretation

The model is intended as a **ranking aid for outreach prioritization**, not an automatic customer-decision system.

Permutation importance is used instead of SHAP. The strongest individual importance signals are concentrated in macroeconomic indicators such as `nr.employed`, `emp.var.rate`, `cons.price.idx`, and `euribor3m`, with additional contribution from contact channel, campaign activity, and relationship history.

Subgroup monitoring covers age, marital status, and education. Small subgroups should be interpreted cautiously, and selection-rate differences should be investigated rather than treated as proof of unfairness or compliance.

Campaign saturation results are descriptive associations. They should not be interpreted as causal evidence that repeated contact causes lower conversion.

## Pilot Recommendation

Before full deployment, run a randomized pilot comparing:

- **Treatment:** top-20% model-ranked outreach
- **Control:** existing/approved outreach policy

The **primary KPI should be incremental conversion lift versus the randomized control group**. Precision@20%, lift, and campaign economics are supporting measures.

Scale the policy only if the pilot demonstrates positive incremental value and acceptable governance outcomes.

## Reproducibility

The primary reproducible analytical artifact is:

`novabank_churn_retention_pipeline.ipynb`

The notebook contains the complete analysis, model training, evaluation, financial scenarios, diagnostics, subgroup monitoring, and output generation.

Required Python packages are pinned in `requirements.txt`.

### Data

The raw UCI dataset is **not included in this repository**. Place the required file at:

`data/bank-additional-full.csv`

The pipeline validates that the expected dataset contains **41,188 rows**.

### Outputs

The analysis writes the following files to `outputs/`:

- `diagnostic_chart.png`
- `model_metrics.csv`
- `financial_sensitivity.csv`
- `permutation_importance.csv`
- `permutation_feature_families.csv`
- `fairness_subgroup_audit.csv`
- `campaign_saturation.csv`

## AI Usage Disclosure

AI tools were used as coding and drafting assistance. The project author validated the analytical framing, leakage treatment, modeling choices, economic assumptions, sensitivity scenarios, governance interpretation, and final results.
