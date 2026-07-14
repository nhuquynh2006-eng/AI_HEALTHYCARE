"""
train_diabetes.py — Phiên bản nâng cấp
AI_HEALTHY_CARE Project
Cải tiến: chuẩn hóa dữ liệu, Dropout, so sánh nhiều model, đánh giá đa chỉ số
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report, roc_curve
)

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam

import joblib
import os

# ─────────────────────────────────────────────
# 1. ĐỌC & KHÁM PHÁ DỮ LIỆU
# ─────────────────────────────────────────────
print("=" * 55)
print("  AI_HEALTHY_CARE — Huấn luyện mô hình tiểu đường")
print("=" * 55)

df = pd.read_csv("datasets/diabetes.csv")
print(f"\n[INFO] Dataset: {df.shape[0]} mẫu, {df.shape[1]} đặc trưng")
print(f"[INFO] Phân phối nhãn:\n{df['Outcome'].value_counts()}")
print(f"[INFO] Tỷ lệ mắc bệnh: {df['Outcome'].mean()*100:.1f}%\n")

# Kiểm tra giá trị 0 bất hợp lý (Glucose, BMI, BloodPressure không thể = 0)
zero_cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
for col in zero_cols:
    n_zeros = (df[col] == 0).sum()
    if n_zeros > 0:
        print(f"[WARN] {col}: {n_zeros} giá trị = 0 → thay bằng median")
        df[col] = df[col].replace(0, df[col].median())

# ─────────────────────────────────────────────
# 2. CHUẨN BỊ DỮ LIỆU
# ─────────────────────────────────────────────
X = df.drop("Outcome", axis=1)
y = df["Outcome"]

feature_names = X.columns.tolist()

# Chia train / validation / test (70 / 15 / 15)
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.15, random_state=42, stratify=y
)
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.176, random_state=42, stratify=y_temp
)

print(f"[INFO] Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")

# Chuẩn hóa dữ liệu (fit chỉ trên train, transform trên val/test)
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_val_sc   = scaler.transform(X_val)
X_test_sc  = scaler.transform(X_test)

# Lưu scaler để dùng khi dự đoán
os.makedirs("models", exist_ok=True)
joblib.dump(scaler, "models/scaler.pkl")
print("[INFO] Đã lưu scaler → models/scaler.pkl\n")

# ─────────────────────────────────────────────
# 3. SO SÁNH NHIỀU MÔ HÌNH
# ─────────────────────────────────────────────
results = {}

# --- Model A: Logistic Regression (baseline) ---
print("▶ Huấn luyện Logistic Regression...")
lr = LogisticRegression(max_iter=1000, random_state=42)
lr.fit(X_train_sc, y_train)
lr_pred  = lr.predict(X_test_sc)
lr_proba = lr.predict_proba(X_test_sc)[:, 1]
results["Logistic Regression"] = {
    "accuracy": accuracy_score(y_test, lr_pred),
    "f1":       f1_score(y_test, lr_pred),
    "roc_auc":  roc_auc_score(y_test, lr_proba),
}
joblib.dump(lr, "models/logistic_regression.pkl")

# --- Model B: Random Forest ---
print("▶ Huấn luyện Random Forest...")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train_sc, y_train)
rf_pred  = rf.predict(X_test_sc)
rf_proba = rf.predict_proba(X_test_sc)[:, 1]
results["Random Forest"] = {
    "accuracy": accuracy_score(y_test, rf_pred),
    "f1":       f1_score(y_test, rf_pred),
    "roc_auc":  roc_auc_score(y_test, rf_proba),
}
joblib.dump(rf, "models/random_forest.pkl")

# --- Model C: Neural Network (Deep Learning) ---
print("▶ Huấn luyện Neural Network...")

def build_model(input_dim=8):
    model = Sequential([
        Dense(128, activation='relu', input_shape=(input_dim,)),
        BatchNormalization(),
        Dropout(0.3),

        Dense(64, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),

        Dense(32, activation='relu'),
        Dropout(0.2),

        Dense(1, activation='sigmoid')
    ])
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    return model

nn_model = build_model()

early_stop = EarlyStopping(
    monitor='val_loss',
    patience=15,
    restore_best_weights=True
)

history = nn_model.fit(
    X_train_sc, y_train,
    epochs=150,
    batch_size=16,
    validation_data=(X_val_sc, y_val),
    callbacks=[early_stop],
    verbose=0
)

nn_pred  = (nn_model.predict(X_test_sc) > 0.5).astype(int).flatten()
nn_proba = nn_model.predict(X_test_sc).flatten()
results["Neural Network"] = {
    "accuracy": accuracy_score(y_test, nn_pred),
    "f1":       f1_score(y_test, nn_pred),
    "roc_auc":  roc_auc_score(y_test, nn_proba),
}
nn_model.save("models/diabetes_model.keras")
print("[INFO] Đã lưu Neural Network → models/diabetes_model.keras")

# ─────────────────────────────────────────────
# 4. SO SÁNH KẾT QUẢ
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("  KẾT QUẢ SO SÁNH MÔ HÌNH")
print("=" * 55)
print(f"{'Model':<22} {'Accuracy':>10} {'F1-Score':>10} {'ROC-AUC':>10}")
print("-" * 55)

best_model_name = None
best_roc = 0
for name, metrics in results.items():
    print(f"{name:<22} {metrics['accuracy']:>9.3f}  {metrics['f1']:>9.3f}  {metrics['roc_auc']:>9.3f}")
    if metrics['roc_auc'] > best_roc:
        best_roc = metrics['roc_auc']
        best_model_name = name

print("-" * 55)
print(f"[BEST] {best_model_name} (ROC-AUC = {best_roc:.3f})\n")

# ─────────────────────────────────────────────
# 5. ĐÁNH GIÁ CHI TIẾT — NEURAL NETWORK
# ─────────────────────────────────────────────
print("=" * 55)
print("  ĐÁNH GIÁ CHI TIẾT: Neural Network")
print("=" * 55)
print(classification_report(y_test, nn_pred,
      target_names=["Không tiểu đường", "Tiểu đường"]))

# ─────────────────────────────────────────────
# 6. VISUALIZE (lưu ảnh để đưa vào tiểu luận)
# ─────────────────────────────────────────────
os.makedirs("report", exist_ok=True)
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("Đánh giá mô hình AI - Dự đoán tiểu đường", fontsize=14, fontweight='bold')

# --- 6a. Confusion Matrix ---
cm = confusion_matrix(y_test, nn_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=["Không bệnh", "Có bệnh"],
            yticklabels=["Không bệnh", "Có bệnh"], ax=axes[0])
axes[0].set_title("Confusion Matrix (Neural Network)")
axes[0].set_ylabel("Thực tế")
axes[0].set_xlabel("Dự đoán")

# --- 6b. ROC Curve (cả 3 model) ---
for name, pred, proba, color in [
    ("Logistic Regression", lr_pred, lr_proba, "blue"),
    ("Random Forest",       rf_pred, rf_proba, "green"),
    ("Neural Network",      nn_pred, nn_proba, "red"),
]:
    fpr, tpr, _ = roc_curve(y_test, proba)
    auc = roc_auc_score(y_test, proba)
    axes[1].plot(fpr, tpr, color=color, label=f"{name} (AUC={auc:.2f})")
axes[1].plot([0,1],[0,1],'k--', alpha=0.4)
axes[1].set_title("ROC Curve — So sánh 3 mô hình")
axes[1].set_xlabel("False Positive Rate")
axes[1].set_ylabel("True Positive Rate")
axes[1].legend(fontsize=9)
axes[1].grid(alpha=0.3)

# --- 6c. Training history ---
axes[2].plot(history.history['loss'],     label='Train Loss', color='blue')
axes[2].plot(history.history['val_loss'], label='Val Loss',   color='orange')
axes[2].set_title("Quá trình huấn luyện Neural Network")
axes[2].set_xlabel("Epoch")
axes[2].set_ylabel("Loss")
axes[2].legend()
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig("report/model_evaluation.png", dpi=150, bbox_inches='tight')
plt.close()
print("[INFO] Đã lưu biểu đồ → report/model_evaluation.png")

# --- Feature Importance (Random Forest) ---
importances = rf.feature_importances_
indices = np.argsort(importances)[::-1]

plt.figure(figsize=(10, 5))
plt.bar(range(len(feature_names)),
        importances[indices],
        color='steelblue', edgecolor='white')
plt.xticks(range(len(feature_names)),
           [feature_names[i] for i in indices],
           rotation=30, ha='right')
plt.title("Tầm quan trọng của các đặc trưng (Random Forest)")
plt.ylabel("Importance Score")
plt.tight_layout()
plt.savefig("report/feature_importance.png", dpi=150, bbox_inches='tight')
plt.close()
print("[INFO] Đã lưu biểu đồ → report/feature_importance.png")

print("\n✅ Hoàn tất! Models đã lưu trong thư mục models/")
print("   Biểu đồ đã lưu trong thư mục report/")