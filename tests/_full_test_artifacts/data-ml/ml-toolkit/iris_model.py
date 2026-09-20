import sys
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

def main():
    X, y = load_iris(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    m = LogisticRegression(max_iter=2000, random_state=42).fit(Xtr, ytr)
    acc = accuracy_score(yte, m.predict(Xte))
    print(f"n_train={len(Xtr)} n_test={len(Xte)} accuracy={acc:.3f}")
    return 0 if acc >= 0.9 else 1

if __name__ == "__main__":
    sys.exit(main())
