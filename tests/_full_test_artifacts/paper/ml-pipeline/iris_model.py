
import os, sys
def main():
    try:
        from sklearn.datasets import load_iris
        from sklearn.linear_model import LogisticRegression
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import cross_val_score
        from sklearn.metrics import confusion_matrix, accuracy_score
        from sklearn.model_selection import train_test_split
        import pickle
    except ModuleNotFoundError:
        print("SKLEARN_MISSING: 需要 pip install scikit-learn")
        return 1
    X, y = load_iris(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    best = None
    for name, model in [
        ("LogReg", LogisticRegression(max_iter=2000, random_state=42)),
        ("RF", RandomForestClassifier(n_estimators=200, random_state=42)),
    ]:
        cv = cross_val_score(model, Xtr, ytr, cv=5).mean()
        model.fit(Xtr, ytr)
        acc = accuracy_score(yte, model.predict(Xte))
        cm = confusion_matrix(yte, model.predict(Xte))
        print(f"{name}: cv5={cv:.3f} test_acc={acc:.3f} conf_matrix={cm.tolist()}")
        if best is None or cv > best[1]:
            best = (name, cv, model)
    n, cv, m = best
    spath = os.path.join(os.path.dirname(__file__), f"model_{n}.pkl")
    pickle.dump(m, open(spath, "wb"))
    print(f"BEST={n} cv={cv:.3f} saved={os.path.basename(spath)}")
    return 0
if __name__ == "__main__":
    sys.exit(main())
