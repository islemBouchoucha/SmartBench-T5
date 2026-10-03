import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler

# ==============================================================================
# 1. CHARGEMENT DES DONNÉES DEPUIS TON FICHIER EXCEL
# ==============================================================================
# Ton chemin d'accès exact avec le préfixe 'r' pour éviter les erreurs de chemin Windows
chemin_excel = r"C:\Users\ejlas\OneDrive\Bureau\Sagemcom\synthetic_data.xlsx"

try:
    df = pd.read_excel(chemin_excel)
    print("✅ Fichier Excel chargé avec succès !")
    print(f"Nombre de lignes (cartes) : {len(df)}")
    print("\n--- Liste des colonnes détectées dans ton fichier ---")
    print(list(df.columns))
    print("----------------------------------------------------\n")
except Exception as e:
    print(f"❌ Erreur lors de l'ouverture du fichier : {e}")

# ==============================================================================
# 2. ADAPTATION DES COLONNES (À VÉRIFIER AVEC LES NOMS EXACTS DE TON EXCEL)
# ==============================================================================
# Si tes colonnes s'appellent différemment dans synthetic_data.xlsx,
# modifie simplement les noms ci-dessous :

colonnes_mesures = [
    "tension_repos",
    "courant_ligne",
    "tension_sonnerie",
    "transmission_audio",
    "consommation",
]

colonne_statut_reel = "statut_reel"  # Nom de la colonne avec PASS/FAIL ou 0/1

# Extraction des variables
X = df[colonnes_mesures]
y_true = df[colonne_statut_reel]

# Uniformisation du résultat réel : 0 = PASS (Normal), 1 = FAIL (Anomalie)
if y_true.dtype == object:
    y_true_binary = y_true.apply(
        lambda val: 0 if str(val).strip().upper() == "PASS" else 1
    )
else:
    y_true_binary = y_true

# ==============================================================================
# 3. NORMALISATION & ENTRAÎNEMENT DE L'ISOLATION FOREST
# ==============================================================================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Calcul automatique du taux d'anomalies réel dans ton dataset
taux_anomalies_estime = (y_true_binary == 1).sum() / len(y_true_binary)
if taux_anomalies_estime == 0:
    taux_anomalies_estime = 0.05

# Entraînement du modèle
model = IsolationForest(
    n_estimators=100, contamination=taux_anomalies_estime, random_state=42
)
model.fit(X_scaled)

# ==============================================================================
# 4. PREDICTION & MAPPING
# ==============================================================================
# Isolation Forest renvoie :  1 = Conforme (PASS) / -1 = Anomalie (FAIL)
y_pred_raw = model.predict(X_scaled)

# Conversion vers 0 = PASS et 1 = FAIL
y_pred_binary = np.where(y_pred_raw == 1, 0, 1)

# ==============================================================================
# 5. AFFICHAGE DES RÉSULTATS (ACCURACY + MATRICE DE CONFUSION)
# ==============================================================================
acc = accuracy_score(y_true_binary, y_pred_binary)
cm = confusion_matrix(y_true_binary, y_pred_binary)

print("==================================================")
print(" RÉSULTATS DU MODÈLE DE DÉTECTION D'ANOMALIES")
print("==================================================")
print(f"📊 Précision Globale (Accuracy) : {acc * 100:.2f}%\n")

print("📋 Rapport de Classification Détaillé :")
print(
    classification_report(
        y_true_binary,
        y_pred_binary,
        target_names=["Conforme (PASS)", "Anomalie (FAIL)"],
    )
)

# Affichage graphique de la Matrice de Confusion
plt.figure(figsize=(7, 5))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["Prédit PASS", "Prédit FAIL"],
    yticklabels=["Réel PASS", "Réel FAIL"],
)
plt.title(
    f"Matrice de Confusion - Isolation Forest (Accuracy: {acc * 100:.2f}%)"
)
plt.xlabel("Prédiction de l'IA")
plt.ylabel("Réalité Terrain")
plt.tight_layout()
plt.show()