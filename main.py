from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# ============================================================
# NOVABANK STRATEGIC ANALYTICS PIPELINE
# Matches the final novabank_churn_retention_pipeline.ipynb
# ============================================================

TOP_FRACTION = 0.20
CALL_COST = 15.0
ASSUMED_CAMPAIGN_VALUE = 250.0
LOW_VALUE_CAMPAIGN_VALUE = 200.0
INTEREST_RATE_CONVERSION_SHOCK = 0.085
RANDOM_STATE = 42


# ============================================================
# DATA LOADING AND FEATURE PREPARATION
# ============================================================

candidate_paths = [
    Path("data") / "bank-additional-full.csv",
    Path("bank-additional") / "bank-additional-full.csv",
    Path("bank-additional-full.csv"),
]

data_path = next(
    (p for p in candidate_paths if p.exists()),
    None,
)

if data_path is None:
    raise FileNotFoundError(
        "Could not locate bank-additional-full.csv."
    )

df = pd.read_csv(data_path, sep=";")

if len(df) != 41188:
    raise ValueError(
        f"Expected 41,188 rows but found {len(df):,}."
    )

df["target"] = (
    df["y"]
    .astype(str)
    .str.strip()
    .str.lower()
    .eq("yes")
).astype(int)

print(f"Dataset: {data_path}")
print(f"Rows: {len(df):,}")
print(f"Historical conversions: {df['target'].sum():,}")
print(f"Historical conversion rate: {df['target'].mean():.2%}")

raw_for_audit = df.copy()

# Remove post-call leakage variable.
df = df.drop(columns=["duration", "y"])

df["previously_contacted"] = (
    df["pdays"] != 999
).astype(int)

categorical_cols = (
    df.select_dtypes(
        include=["object", "str"]
    )
    .columns
    .tolist()
)

df_encoded = pd.get_dummies(
    df,
    columns=categorical_cols,
    drop_first=True,
)

X = df_encoded.drop(columns=["target"])
y = df_encoded["target"]

print(f"Model features: {X.shape[1]}")


# ============================================================
# STRATIFIED TRAIN-TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=RANDOM_STATE,
)

print(f"Training observations: {len(X_train):,}")
print(f"Test observations: {len(X_test):,}")
print(f"Training conversion rate: {y_train.mean():.2%}")
print(f"Test conversion rate: {y_test.mean():.2%}")


# ============================================================
# BASELINE: LOGISTIC REGRESSION
# ============================================================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

baseline_model = LogisticRegression(
    max_iter=2000,
    random_state=RANDOM_STATE,
)

baseline_model.fit(X_train_scaled, y_train)


# ============================================================
# IMPROVED MODEL: HISTGRADIENTBOOSTING
# ============================================================

improved_model = HistGradientBoostingClassifier(
    learning_rate=0.08,
    max_iter=200,
    max_leaf_nodes=15,
    l2_regularization=1.0,
    random_state=RANDOM_STATE,
)

improved_model.fit(X_train, y_train)

print("Both models trained successfully.")


# ============================================================
# PREDICTIONS
# ============================================================

baseline_prob = baseline_model.predict_proba(
    X_test_scaled
)[:, 1]

improved_prob = improved_model.predict_proba(
    X_test
)[:, 1]

print("Predictions generated successfully.")
print(
    f"Baseline probability range: "
    f"{baseline_prob.min():.4f} - {baseline_prob.max():.4f}"
)
print(
    f"Improved probability range: "
    f"{improved_prob.min():.4f} - {improved_prob.max():.4f}"
)


# ============================================================
# MODEL PERFORMANCE
# ============================================================

baseline_auc = roc_auc_score(y_test, baseline_prob)
improved_auc = roc_auc_score(y_test, improved_prob)

baseline_brier = brier_score_loss(y_test, baseline_prob)
improved_brier = brier_score_loss(y_test, improved_prob)


def top_fraction_metrics(y_true, probabilities, fraction=0.20):
    n_top = int(len(y_true) * fraction)
    ranking = np.argsort(probabilities)[::-1]
    top_idx = ranking[:n_top]

    top_actuals = np.asarray(y_true)[top_idx]
    precision = top_actuals.mean()
    recall = top_actuals.sum() / np.asarray(y_true).sum()
    lift = precision / np.asarray(y_true).mean()

    return precision, recall, lift, top_actuals.sum()


baseline_precision, baseline_recall, baseline_lift, baseline_conversions = (
    top_fraction_metrics(
        y_test,
        baseline_prob,
        TOP_FRACTION,
    )
)

improved_precision, improved_recall, improved_lift, improved_conversions = (
    top_fraction_metrics(
        y_test,
        improved_prob,
        TOP_FRACTION,
    )
)

print("MODEL PERFORMANCE")
print(
    f"Logistic Regression | "
    f"ROC-AUC: {baseline_auc:.4f} | "
    f"Brier: {baseline_brier:.4f} | "
    f"Precision@20%: {baseline_precision:.2%} | "
    f"Recall: {baseline_recall:.2%} | "
    f"Lift: {baseline_lift:.2f}x"
)

print(
    f"Gradient Boosting | "
    f"ROC-AUC: {improved_auc:.4f} | "
    f"Brier: {improved_brier:.4f} | "
    f"Precision@20%: {improved_precision:.2%} | "
    f"Recall: {improved_recall:.2%} | "
    f"Lift: {improved_lift:.2f}x"
)


# ============================================================
# CAMPAIGN ECONOMICS
# ============================================================

n_total = len(df)
n_test = len(y_test)
scale_factor = n_total / n_test

legacy_conversions = int(
    round(y.mean() * n_total)
)

top20_contacts = int(
    round(n_total * TOP_FRACTION)
)

# Scale test-set results to the full campaign population.
gb_top20_conversions = int(
    round(improved_conversions * scale_factor)
)

lr_top20_conversions = int(
    round(baseline_conversions * scale_factor)
)

legacy_profit = (
    legacy_conversions * ASSUMED_CAMPAIGN_VALUE
    - n_total * CALL_COST
)

gb_profit = (
    gb_top20_conversions * ASSUMED_CAMPAIGN_VALUE
    - top20_contacts * CALL_COST
)

lr_profit = (
    lr_top20_conversions * ASSUMED_CAMPAIGN_VALUE
    - top20_contacts * CALL_COST
)

gb_uplift = gb_profit - legacy_profit
gb_uplift_pct = gb_uplift / legacy_profit

gb_false_positives = (
    top20_contacts - gb_top20_conversions
)

gb_false_negatives = (
    legacy_conversions - gb_top20_conversions
)

gb_precision = (
    gb_top20_conversions / top20_contacts
)

gb_recall = (
    gb_top20_conversions / legacy_conversions
)

rocs = (
    gb_top20_conversions * ASSUMED_CAMPAIGN_VALUE
) / (
    top20_contacts * CALL_COST
)

print("CAMPAIGN ECONOMICS")
print(f"Legacy mass outreach profit: €{legacy_profit:,.0f}")
print(
    f"Logistic Regression top-20% profit: "
    f"€{lr_profit:,.0f}"
)
print(
    f"Gradient Boosting top-20% profit: "
    f"€{gb_profit:,.0f}"
)
print(
    f"Profit uplift vs. legacy: "
    f"€{gb_uplift:,.0f} ({gb_uplift_pct:.1%})"
)
print(f"Top-20% contacts: {top20_contacts:,}")
print(
    f"Estimated conversions captured: "
    f"{gb_top20_conversions:,}"
)
print(
    f"Estimated false positives: "
    f"{gb_false_positives:,}"
)
print(
    f"Estimated false negatives: "
    f"{gb_false_negatives:,}"
)
print(f"Precision@20%: {gb_precision:.2%}")
print(f"Conversion capture (Recall): {gb_recall:.2%}")
print(f"Return on Campaign Spend: {rocs:.2f}x")


# ============================================================
# €200 CAMPAIGN-VALUE SCENARIO
# ============================================================

mass_profit_200 = (
    legacy_conversions * LOW_VALUE_CAMPAIGN_VALUE
    - n_total * CALL_COST
)

top20_profit_200 = (
    gb_top20_conversions * LOW_VALUE_CAMPAIGN_VALUE
    - top20_contacts * CALL_COST
)

print("€200 CAMPAIGN-VALUE SCENARIO")
print(f"Mass outreach: €{mass_profit_200:,.0f}")
print(f"Top-20% policy: €{top20_profit_200:,.0f}")
print(
    f"Top-20% advantage: "
    f"€{top20_profit_200 - mass_profit_200:,.0f}"
)


# ============================================================
# ILLUSTRATIVE INTEREST-RATE SENSITIVITY
# ============================================================

stressed_conversions = int(
    round(
        gb_top20_conversions
        * (1 - INTEREST_RATE_CONVERSION_SHOCK)
    )
)

stressed_profit = (
    stressed_conversions * ASSUMED_CAMPAIGN_VALUE
    - top20_contacts * CALL_COST
)

print("INTEREST-RATE SENSITIVITY")
print(
    "Illustrative scenario: 100 bps reduction corresponds "
    "to an 8.5% conversion reduction."
)
print(
    f"Stressed conversions: "
    f"{stressed_conversions:,}"
)
print(
    f"Stressed top-20% profit: "
    f"€{stressed_profit:,.0f}"
)


# ============================================================
# PERMUTATION IMPORTANCE
# ============================================================

output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)

perm = permutation_importance(
    improved_model,
    X_test,
    y_test,
    n_repeats=10,
    random_state=RANDOM_STATE,
    scoring="roc_auc",
)

importance_df = pd.DataFrame(
    {
        "feature": X_test.columns,
        "importance": perm.importances_mean,
    }
).sort_values(
    "importance",
    ascending=False,
)

importance_df["share"] = (
    importance_df["importance"].clip(lower=0)
    / importance_df["importance"].clip(lower=0).sum()
)

print("TOP PERMUTATION-IMPORTANCE FEATURES")
print(
    importance_df.head(15).to_string(
        index=False
    )
)


# ============================================================
# MODEL COMPARISON TABLE
# ============================================================

model_metrics = pd.DataFrame(
    {
        "Model": [
            "Logistic Regression",
            "Gradient Boosting",
        ],
        "ROC-AUC": [
            baseline_auc,
            improved_auc,
        ],
        "Brier": [
            baseline_brier,
            improved_brier,
        ],
        "Precision@20%": [
            baseline_precision,
            improved_precision,
        ],
        "Recall@20%": [
            baseline_recall,
            improved_recall,
        ],
        "Lift@20%": [
            baseline_lift,
            improved_lift,
        ],
    }
)

print(
    model_metrics.to_string(
        index=False,
        formatters={
            "ROC-AUC": lambda x: f"{x:.4f}",
            "Brier": lambda x: f"{x:.4f}",
            "Precision@20%": lambda x: f"{x:.2%}",
            "Recall@20%": lambda x: f"{x:.2%}",
            "Lift@20%": lambda x: f"{x:.2f}x",
        },
    )
)


# ============================================================
# CUMULATIVE CONVERSION GAINS
# ============================================================

def cumulative_gains(y_true, probabilities):
    order = np.argsort(probabilities)[::-1]
    y_sorted = np.asarray(y_true)[order]

    cumulative_conversions = np.cumsum(y_sorted)
    total_conversions = y_sorted.sum()

    population_fraction = (
        np.arange(1, len(y_sorted) + 1)
        / len(y_sorted)
    )

    conversion_capture = (
        cumulative_conversions
        / total_conversions
    )

    return population_fraction, conversion_capture


gb_population, gb_capture = cumulative_gains(
    y_test,
    improved_prob,
)

plt.figure(figsize=(8, 5))

plt.plot(
    gb_population,
    gb_capture,
    label="Gradient Boosting",
)

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    label="Random targeting",
)

plt.axvline(
    TOP_FRACTION,
    linestyle=":",
)

plt.xlabel("Share of customers contacted")
plt.ylabel("Share of conversions captured")
plt.title("Cumulative Conversion Gains")
plt.legend()
plt.grid(alpha=0.25)
plt.tight_layout()

chart_path = output_dir / "diagnostic_chart.png"

plt.savefig(
    chart_path,
    dpi=300,
    bbox_inches="tight",
)

plt.close()

print(f"Diagnostic chart saved to: {chart_path}")


# ============================================================
# HISTORICAL CAMPAIGN SATURATION
# ============================================================

saturation = (
    raw_for_audit
    .groupby("campaign")["target"]
    .agg(
        contacts="size",
        conversions="sum",
        conversion_rate="mean",
    )
    .reset_index()
)

print("CAMPAIGN SATURATION")
print(
    saturation.to_string(
        index=False,
        formatters={
            "conversion_rate": lambda x: f"{x:.2%}",
        },
    )
)


# ============================================================
# SUBGROUP SELECTION AUDIT
# ============================================================

audit_df = raw_for_audit.loc[
    X_test.index,
    ["age", "marital", "education", "target"],
].copy()

audit_df["predicted_probability"] = improved_prob

n_top = int(
    len(audit_df) * TOP_FRACTION
)

top_indices = (
    audit_df["predicted_probability"]
    .nlargest(n_top)
    .index
)

audit_df["selected"] = (
    audit_df.index.isin(top_indices)
)

audit_df["age_group"] = pd.cut(
    audit_df["age"],
    bins=[0, 29, 44, 59, np.inf],
    labels=["<30", "30-44", "45-59", "60+"],
)


def make_audit(data, variable):
    result = (
        data.groupby(
            variable,
            observed=True,
        )
        .agg(
            sample_size=("target", "size"),
            actual_conversion_rate=(
                "target",
                "mean",
            ),
            selection_rate=(
                "selected",
                "mean",
            ),
        )
        .reset_index()
    )

    result.insert(
        0,
        "variable",
        variable,
    )

    result = result.rename(
        columns={variable: "group"}
    )

    return result


fairness_audit = pd.concat(
    [
        make_audit(
            audit_df,
            "age_group",
        ),
        make_audit(
            audit_df,
            "marital",
        ),
        make_audit(
            audit_df,
            "education",
        ),
    ],
    ignore_index=True,
)

print("SUBGROUP SELECTION AUDIT")
print(
    fairness_audit.to_string(
        index=False,
        formatters={
            "actual_conversion_rate": (
                lambda x: f"{x:.2%}"
            ),
            "selection_rate": (
                lambda x: f"{x:.2%}"
            ),
        },
    )
)


# ============================================================
# SAVE REPRODUCIBLE OUTPUTS
# ============================================================

model_metrics.to_csv(
    output_dir / "model_metrics.csv",
    index=False,
)

importance_df.to_csv(
    output_dir / "permutation_importance.csv",
    index=False,
)

fairness_audit.to_csv(
    output_dir / "fairness_subgroup_audit.csv",
    index=False,
)

saturation.to_csv(
    output_dir / "campaign_saturation.csv",
    index=False,
)

financial_sensitivity = pd.DataFrame(
    {
        "scenario": [
            "Baseline €250",
            "Lower campaign value €200",
            "100 bps illustrative stress",
        ],
        "mass_outreach_profit": [
            legacy_profit,
            mass_profit_200,
            np.nan,
        ],
        "top20_profit": [
            gb_profit,
            top20_profit_200,
            stressed_profit,
        ],
    }
)

financial_sensitivity.to_csv(
    output_dir / "financial_sensitivity.csv",
    index=False,
)

print("OUTPUT FILES SAVED")

for file in sorted(
    output_dir.glob("*.csv")
):
    print(file)

print("PIPELINE COMPLETE")
    