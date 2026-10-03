import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# ==============================================================================
# 1. CHARGEMENT ET SÉLECTION STRICTE DES COLONNES
# ==============================================================================
chemin_entree = (
    r"C:\Users\ejlas\OneDrive\Bureau\Sagemcom\balanced_dataset.xlsx"
)

print("⏳ Chargement du fichier Excel équilibré...")
df = pd.read_excel(chemin_entree)
print(f"✅ Fichier chargé avec succès ! Total de cartes : {len(df)}")

# Liste stricte des 8 colonnes (élimine la colonne parasite Unnamed: 11)
colonnes_mesures = [
    "Tension (V)",
    "Courant (mA)",
    "Gain mes1 (dB)",
    "Gain mes2 (dB)",
    "Gain mes3 (dB)",
    "Puissance (W)",
    "RMS (Vrms)",
    "Température('C)",
]

# Vrai nom de la colonne dans ton fichier Excel
colonne_statut_reel = "Test"

# On conserve UNIQUEMENT les 8 colonnes de mesures
X = df[colonnes_mesures]

# Conversion : PASS/OK/0 -> 0, sinon -> 1
y = df[colonne_statut_reel].apply(
    lambda v: 0 if str(v).strip().upper() in ["PASS", "OK", "0"] else 1
)

# ==============================================================================
# 2. SÉPARATION DES DONNÉES ET NORMALISATION
# ==============================================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ==============================================================================
# 3. ENTRAÎNEMENT DU MODÈLE RANDOM FOREST
# ==============================================================================
print("⚙️ Entraînement du modèle Random Forest...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# ==============================================================================
# 4. ÉVALUATION ET AFFICHAGE DES RÉSULTATS
# ==============================================================================
y_pred = model.predict(X_test_scaled)
acc = accuracy_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

print("\n==================================================")
print("📊 RÉSULTATS SUR LES DONNÉES DE TEST (Inconnues du modèle)")
print("==================================================")
print(f"Précision Globale (Accuracy) : {acc * 100:.2f}%\n")
print("📑 Rapport de Classification Détaillé :")
print(
    classification_report(
        y_test, y_pred, target_names=["Conforme (PASS)", "Anomalie (FAIL)"]
    )
)

# Matrice de confusion visuelle
plt.figure(figsize=(7, 5))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["Prédit PASS", "Prédit FAIL"],
    yticklabels=["Réel PASS", "Réel FAIL"],
)
plt.title(f"Matrice de Confusion (Données de test) - Accuracy: {acc * 100:.2f}%")
plt.xlabel("Prédiction IA")
plt.ylabel("Réalité Terrain")
plt.tight_layout()
plt.show()

# =============================================================detectio =================
# 5. SAUVEGARDE DES ARTEFACTS NETTOYÉS
# ==============================================================================
joblib.dump(model, "modele_isolation_forest.pkl")
joblib.dump(scaler, "scaler_donnees.pkl")
print("💾 Modèle et Scaler mis à jour sous .pkl avec succès (structure 8 colonnes) !")