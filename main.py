import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def run_pipeline():
  print("=" * 65)
  print("NOVABANK STRATEGIC ANALYTICS PIPELINE")
  print("=" * 65)

  # Detect the data file location
  candidate_paths = [
      os.path.join("data", "bank-additional-full.csv"),
      os.path.join("bank-additional", "bank-additional-full.csv"),
      "bank-additional-full.csv",
      "bank-full.csv",
  ]
  data_path = next((p for p in candidate_paths if os.path.exists(p)), None)

  if not data_path:
    print(
        "Error: Could not locate data file. Please ensure"
        " 'bank-additional-full.csv' is in your project folder."
    )
    return

  print(f"\n[1/5] Loading: {data_path}...")
  df = pd.read_csv(data_path, sep=";")
  df["target"] = (df["y"].str.strip().str.lower() == "yes").astype(int)

  # Drop 'duration' to eliminate data leakage
  if "duration" in df.columns:
    df = df.drop(columns=["duration"])
  df = df.drop(columns=["y"])

  if "pdays" in df.columns:
    df["previously_contacted"] = (df["pdays"] != 999).astype(int)

  # Categorical encoding
  cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
  df_encoded = pd.get_dummies(df, columns=cat_cols, drop_first=True)

  X = df_encoded.drop(columns=["target"])
  y = df_encoded["target"]

  X_train, X_test, y_train, y_test = train_test_split(
      X, y, test_size=0.20, random_state=42, stratify=y
  )

  # Scale numeric features for the linear model
  numeric_cols = [c for c in X.columns if X[c].dtype in ["int64", "float64"]]
  scaler = StandardScaler()
  X_train_scaled = X_train.copy()
  X_test_scaled = X_test.copy()
  X_train_scaled[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
  X_test_scaled[numeric_cols] = scaler.transform(X_test[numeric_cols])

  # Train models
  print("\n[2/5] Training Baseline (Logistic Regression)...")
  lr = LogisticRegression(max_iter=1000, C=1.0, random_state=42)
  lr.fit(X_train_scaled, y_train)

  print("[3/5] Training Improved Model (Gradient Boosting)...")
  gb = HistGradientBoostingClassifier(
      learning_rate=0.08, max_iter=200, random_state=42
  )
  gb.fit(X_train, y_train)

  # Evaluate
  print("\n[4/5] Evaluating Diagnostics & Top 20% Decile Lift...")
  prob_lr = lr.predict_proba(X_test_scaled)[:, 1]
  prob_gb = gb.predict_proba(X_test)[:, 1]

  eval_df = pd.DataFrame(
      {"actual": y_test.values, "lr": prob_lr, "gb": prob_gb}
  )
  n_top20 = int(0.20 * len(eval_df))
  top20_lr = eval_df.sort_values("lr", ascending=False).iloc[:n_top20]
  top20_gb = eval_df.sort_values("gb", ascending=False).iloc[:n_top20]

  summary = pd.DataFrame([
      {
          "Model": "Baseline (Logistic Regression)",
          "ROC-AUC": f"{roc_auc_score(y_test, prob_lr):.4f}",
          "Brier Score": f"{brier_score_loss(y_test, prob_lr):.4f}",
          "Precision@Top20%": f"{top20_lr['actual'].mean():.2%}",
          "Recall@Top20%": (
              f"{top20_lr['actual'].sum() / eval_df['actual'].sum():.2%}"
          ),
          "Lift": (
              f"{top20_lr['actual'].mean() / eval_df['actual'].mean():.2f}x"
          ),
      },
      {
          "Model": "Improved (Gradient Boosting)",
          "ROC-AUC": f"{roc_auc_score(y_test, prob_gb):.4f}",
          "Brier Score": f"{brier_score_loss(y_test, prob_gb):.4f}",
          "Precision@Top20%": f"{top20_gb['actual'].mean():.2%}",
          "Recall@Top20%": (
              f"{top20_gb['actual'].sum() / eval_df['actual'].sum():.2%}"
          ),
          "Lift": (
              f"{top20_gb['actual'].mean() / eval_df['actual'].mean():.2f}x"
          ),
      },
  ])
  print("\n" + summary.to_string(index=False))

  # Economic calculations
  print("\n[5/5] Translating Probabilities to Campaign P&L...")
  cost_call = 15.0
  deposit_clv = 250.0

  policy_cost = n_top20 * cost_call
  policy_rev = top20_gb["actual"].sum() * deposit_clv
  policy_net = policy_rev - policy_cost

  mass_cost = len(eval_df) * cost_call
  mass_rev = eval_df["actual"].sum() * deposit_clv
  mass_net = mass_rev - mass_cost

  scale = 41188 / len(eval_df)
  print(
      f"  Net Profit Gain (Top 20% vs Mass):"
      f" +€{(policy_net - mass_net) * scale:,.0f}"
  )
  print(
      f"  Operational Call Expense Saved:"
      f" -€{(mass_cost - policy_cost) * scale:,.0f} (-80.0%)"
  )

  # Chart output
  os.makedirs("outputs", exist_ok=True)
  sorted_eval = eval_df.sort_values("gb", ascending=False)
  cum_gain = (sorted_eval["actual"].cumsum() / sorted_eval["actual"].sum()) * 100
  pop_pct = np.linspace(0, 100, len(sorted_eval))

  plt.figure(figsize=(7, 5))
  plt.plot(pop_pct, cum_gain, color="#1a365d", lw=2.5, label="Ensemble Model")
  plt.plot(
      [0, 100], [0, 100], color="#cbd5e0", linestyle="--", label="Mass Calling"
  )
  plt.axvline(20, color="#e53e3e", linestyle=":", label="Top 20% Cutoff")
  plt.title("Cumulative Conversion Lift (NovaBank)", fontweight="bold")
  plt.xlabel("% Database Contacted")
  plt.ylabel("% Conversions Captured")
  plt.legend()
  plt.grid(True, alpha=0.3)
  plt.savefig("outputs/diagnostic_chart.png", dpi=300)
  plt.close()
  print("\nDiagnostic chart saved to: outputs/diagnostic_chart.png")
  print("=" * 65)


if __name__ == "__main__":
  run_pipeline()