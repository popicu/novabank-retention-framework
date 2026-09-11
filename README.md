# NovaBank: Predictive Retention & Margin Optimization Framework

This repository contains the analytical pipeline, baseline vs. ensemble predictive models, and business decision framework for the **Quantic MSBA Analytics Methods and Frameworks Project**.

---

## 📌 Executive Summary

NovaBank's core operating margins are under pressure from deposit run-off and escalating telemarketing costs[cite: 1, 5]. Legacy mass outreach contacted 100% of candidate profiles (41,188 contacts), yielding an 11.27% conversion rate at an unsustainable operational expense of €617,820[cite: 5].

**Strategic Recommendation:** Deploy an algorithmic decision rule targeting the **top 20% highest-propensity customers ($P \ge 0.18$)** using our calibrated Gradient Boosting decision model[cite: 1].

### Key Financial & Operational Results
* **Direct Cost Reduction:** **-80.0%** (€494,301 direct operational expense saved)[cite: 5]
* **Conversion Capture Rate:** **66.8%** of all available deposit conversions captured in the top quintile[cite: 5]
* **Precision Acceleration:** Precision jumps from **11.27% to 37.64%** (3.34x baseline lift)[cite: 5]
* **Net Profit Expansion:** **+€105,570 net campaign profit** compared to mass calling[cite: 5]

---

## ⚖️ Analytical Hygiene & The `duration` Leakage Trap

The raw telemarketing dataset contains a `duration` attribute (call duration in seconds)[cite: 5]. In telemarketing operations:
1. `duration` is completely unknown **prior** to placing an outbound call[cite: 5].
2. `duration = 0` guarantees `y = no`[cite: 5].

Including `duration` introduces severe **look-ahead data leakage**, producing an artificially inflated AUC (~0.94) that is useless for pre-call batch targeting[cite: 1, 5]. In compliance with rigorous predictive governance, **`duration` was dropped** during preprocessing, yielding an auditable and defensible test **ROC-AUC of 0.8120**[cite: 1, 5].

---

## 📊 Comparative Performance Benchmark

| Modeling Paradigm | Algorithm | Test ROC-AUC | Brier Score | Precision @ Top 20% | Recall @ Top 20% | Lift @ Top 20% |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline Benchmark**[cite: 1] | L2 Logistic Regression[cite: 1] | 0.8005 | 0.0769 | 36.55% | 64.87% | 3.24x |
| **Improved Policy**[cite: 1] | HistGradientBoosting[cite: 1] | **0.8120** | **0.0745** | **37.64%** | **66.81%** | **3.34x** |

---

## 🤖 AI Usage & Governance Attribution

In accordance with Quantic project guidelines[cite: 1]:
* **AI Assistance:** AI copilots assisted with boilerplate syntax for scikit-learn parameter definitions and Matplotlib formatting[cite: 1].
* **Human Validation:** All analytical premises, leakage detection (`duration` removal), cost-benefit objective functions, and macro sensitivity evaluations were formulated, verified, and audited by the project author[cite: 1, 5].
