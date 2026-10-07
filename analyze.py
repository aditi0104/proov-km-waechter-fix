# analyze.py
#
# Which factors predict a breakdown?  Uses fleet_history.csv (120 labelled cars).
# Every number and conclusion printed below is computed from the data -- nothing
# is typed in by hand -- so the output cannot drift away from the CSV.
#
# Run from anywhere:  python analyze.py

from pathlib import Path

import numpy as np
import pandas as pd

from km_wachter import SERVICE_INTERVAL_KM, WARN_AT_PERCENT

HERE = Path(__file__).resolve().parent
PREDICTORS = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]
MIN_ABS_R = 0.15     # a column must correlate at least this much with breakdown to be used
FOLDS = 5
SEED = 42


def correlations(df: pd.DataFrame) -> dict[str, float]:
    """Point-biserial correlation (= Pearson r with a 0/1 label) of each predictor."""
    return {col: float(df[col].corr(df["broke_down"])) for col in PREDICTORS}


def fit(train: pd.DataFrame) -> dict:
    """Pick the separating columns on `train` and store their weights and ranges."""
    corr = correlations(train)
    cols = {c: abs(r) for c, r in corr.items() if abs(r) >= MIN_ABS_R}
    ranges = {c: (train[c].min(), train[c].max()) for c in cols}
    return {"weights": cols, "ranges": ranges}


def score(model: dict, df: pd.DataFrame) -> pd.Series:
    """Risk score 0-100: |r|-weighted mean of min-max scaled useful columns."""
    total = sum(model["weights"].values())
    acc = pd.Series(0.0, index=df.index)
    for col, weight in model["weights"].items():
        lo, hi = model["ranges"][col]
        scaled = ((df[col] - lo) / (hi - lo)).clip(0, 1) if hi > lo else 0.0
        acc = acc + scaled * weight
    return acc / total * 100


def auc(scores: pd.Series, labels: pd.Series) -> float:
    """Probability that a random broken-down car outscores a random intact one."""
    ranks = scores.rank()
    n1 = int(labels.sum())
    n0 = len(labels) - n1
    return float((ranks[labels == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def out_of_fold_scores(df: pd.DataFrame) -> pd.Series:
    """Score every car with a model that never saw that car (k-fold)."""
    order = np.random.default_rng(SEED).permutation(len(df))
    result = pd.Series(0.0, index=df.index)
    for fold in np.array_split(order, FOLDS):
        test_idx = df.index[fold]
        model = fit(df.drop(test_idx))
        result[test_idx] = score(model, df.loc[test_idx])
    return result


def main() -> None:
    df = pd.read_csv(HERE / "fleet_history.csv")
    broke, intact = df[df["broke_down"] == 1], df[df["broke_down"] == 0]
    corr = correlations(df)

    print("=" * 72)
    print("Step 1 -- which columns separate cars that broke down from those that did not?")
    print(f"  broke_down = 1 : {len(broke):>3} cars")
    print(f"  broke_down = 0 : {len(intact):>3} cars\n")
    print(f"  {'column':<18} {'mean(broke)':>12} {'mean(intact)':>13} {'%diff':>7} {'r':>7}  separates?")
    print("  " + "-" * 68)
    for col in PREDICTORS:
        m1, m0 = broke[col].mean(), intact[col].mean()
        pct = (m1 - m0) / m0 * 100 if m0 else 0.0
        verdict = "YES" if abs(corr[col]) >= MIN_ABS_R else "no"
        print(f"  {col:<18} {m1:>12.2f} {m0:>13.2f} {pct:>6.1f}% {corr[col]:>7.3f}  {verdict}")

    model = fit(df)
    used = sorted(model["weights"], key=model["weights"].get, reverse=True)
    ignored = [c for c in PREDICTORS if c not in used]
    print(f"\n  Used (|r| >= {MIN_ABS_R}): {', '.join(used)}")
    print(f"  Ignored (no separation):  {', '.join(ignored)}")
    if {"odometer_km", "age_years"} <= set(ignored):
        print("  'Older / higher-mileage cars break down' is NOT supported by this data:")
        print("  total mileage and age look the same in both groups.")
    print("=" * 72)

    # ---- Step 2: risk score and ranking --------------------------------------
    df["risk_score"] = score(model, df).round(1)
    ranked = df.sort_values("risk_score", ascending=False)
    shown = ["car_id", "risk_score", "km_since_service", "avg_daily_km", "load_factor", "broke_down"]

    print("\nStep 2 -- top 10 cars by breakdown risk (0-100, higher = more urgent)\n")
    print(f"  {'rank':<5} {'car_id':<10} {'risk':>6} {'km_since_svc':>13} {'daily_km':>9} {'load':>6} {'broke?':>7}")
    print("  " + "-" * 62)
    for rank, row in enumerate(ranked.head(10)[shown].itertuples(index=False), start=1):
        flag = "YES" if row.broke_down else "-"
        print(f"  {rank:<5} {row.car_id:<10} {row.risk_score:>6.1f} {row.km_since_service:>13.0f} "
              f"{row.avg_daily_km:>9.0f} {row.load_factor:>6.2f} {flag:>7}")
    ranked[shown].to_csv(HERE / "risk_ranking.csv", index=False)
    print("\n  Full ranking saved to risk_ranking.csv")

    # ---- Step 3: honest check, and comparison with the 80 % rule -------------
    oof = out_of_fold_scores(df)
    rule_km = SERVICE_INTERVAL_KM * WARN_AT_PERCENT / 100
    rule_flag = df["km_since_service"] >= rule_km
    n_rule = int(rule_flag.sum())
    caught_rule = int(df.loc[rule_flag, "broke_down"].sum())
    top_n = oof.sort_values(ascending=False).index[:n_rule]
    caught_model = int(df.loc[top_n, "broke_down"].sum())
    total_broke = int(df["broke_down"].sum())

    print("\n" + "=" * 72)
    print(f"Step 3 -- does the score work on cars it has not seen? ({FOLDS}-fold check)")
    print(f"  AUC out-of-fold : {auc(oof, df['broke_down']):.2f}  (0.50 = coin flip, 1.00 = perfect)")
    print(f"  AUC in-sample   : {auc(df['risk_score'], df['broke_down']):.2f}  (optimistic: it saw these cars)")
    print(f"\n  The {WARN_AT_PERCENT}% rule (>= {rule_km:.0f} km since service) flags {n_rule} cars "
          f"and catches {caught_rule} of {total_broke} breakdowns.")
    print(f"  The same number of cars chosen by the out-of-fold risk score catches {caught_model}.")
    missed = total_broke - caught_rule
    print(f"  {missed} breakdowns happened on cars the {WARN_AT_PERCENT}% rule would NOT have flagged.")
    print("  Caveat: 120 cars only -- treat the weights as a guide, not a guarantee.")
    print("=" * 72)


if __name__ == "__main__":
    main()
