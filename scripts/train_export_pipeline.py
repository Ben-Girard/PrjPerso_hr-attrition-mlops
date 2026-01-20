import json

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split

from technova_attrition.config import (
    FINAL_MODEL_PARAMS,
    FINAL_MODEL_THRESHOLD,
    PATHS,
    SETTINGS,
)
from technova_attrition.evaluation import evaluate_classifier
from technova_attrition.modeling import make_logreg
from technova_attrition.preprocessing import make_feature_groups

TARGET = "a_quitte_l_entreprise"


def main():
    df = pd.read_parquet(PATHS.data_processed / "employees_features.parquet")
    X = df.drop(columns=[TARGET])
    y = df[TARGET].astype(int)

    # mentor: 90/10, stratifié
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.10,
        random_state=SETTINGS.random_state,
        stratify=y,
    )

    # 🔒 Source de vérité unique pour les groupes de features
    groups = make_feature_groups(df, target=TARGET)

    # Pipeline complet (preprocessing + modèle)
    pipeline = make_logreg(groups)

    # ✅ On applique explicitement les hyperparams du "meilleur modèle"
    pipeline.set_params(**FINAL_MODEL_PARAMS)

    pipeline.fit(X_train, y_train)

    # sanity check: métriques à threshold par défaut (0.5)
    res = evaluate_classifier(
        pipeline,
        X_train,
        y_train,
        X_test,
        y_test,
        threshold=FINAL_MODEL_THRESHOLD,
    )

    PATHS.models.mkdir(parents=True, exist_ok=True)
    PATHS.reports.mkdir(parents=True, exist_ok=True)

    # ✅ artefact principal (NON versionné en git, mais utile localement)
    joblib.dump(pipeline, PATHS.models / "pipeline.joblib")

    # ✅ liste officielle des features attendues
    expected_features = list(X_train.columns)
    (PATHS.models / "expected_features.json").write_text(
        json.dumps(expected_features, indent=2),
        encoding="utf-8",
    )

    # ✅ set de test API (complet + samples)
    api_test_dir = PATHS.data_processed / "api_test"
    api_test_dir.mkdir(parents=True, exist_ok=True)

    # (fichiers complets : probablement ignorés par git)
    X_test.to_csv(api_test_dir / "X_test.csv", index=False)
    y_test.to_csv(api_test_dir / "y_test.csv", index=False)

    # (samples : à versionner)
    X_test.head(10).to_json(api_test_dir / "X_test_sample.json", orient="records")
    y_test.head(10).to_json(api_test_dir / "y_test_sample.json", orient="records")

    # ✅ petit "model card" minimal (versionnable)
    model_card = {
        "target": TARGET,
        "model_type": "logistic_regression",
        "final_params": FINAL_MODEL_PARAMS,
        "default_threshold": FINAL_MODEL_THRESHOLD,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "train_ap": res["train_ap"],
        "test_ap": res["test_ap"],
        "expected_n_features_raw": len(expected_features),
    }
    (PATHS.models / "model_card.json").write_text(
        json.dumps(model_card, indent=2),
        encoding="utf-8",
    )

    (PATHS.reports / "api_model_metrics.json").write_text(
        json.dumps(
            {
                "train_ap": res["train_ap"],
                "test_ap": res["test_ap"],
                "threshold": FINAL_MODEL_THRESHOLD,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("✅ Export terminé")
    print(" - models/pipeline.joblib")
    print(" - models/expected_features.json")
    print(" - models/model_card.json")
    print(" - data/processed/api_test/X_test_sample.json")
    print(" - data/processed/api_test/y_test_sample.json")
    print(" - reports/api_model_metrics.json")


if __name__ == "__main__":
    main()
