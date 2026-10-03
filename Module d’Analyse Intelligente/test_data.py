import pandas as pd
from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer

# =====================================================
# 1. Lire le fichier Excel
# =====================================================

print("Lecture du fichier Excel...")

data = pd.read_excel("data.xlsx")

print("Dataset chargé avec succès.")
print(f"Nombre de lignes : {data.shape[0]}")
print(f"Nombre de colonnes : {data.shape[1]}")

# =====================================================
# 2. Détecter les métadonnées
# =====================================================

print("\nDétection automatique des métadonnées...")

metadata = SingleTableMetadata()
metadata.detect_from_dataframe(data)

print("Métadonnées détectées :")
print(metadata.to_dict())

# =====================================================
# 3. Créer le modèle Gaussian Copula
# =====================================================

print("\nCréation du modèle...")

model = GaussianCopulaSynthesizer(
    metadata=metadata
)

# =====================================================
# 4. Entraîner le modèle
# =====================================================

print("\nEntraînement du modèle...")

model.fit(data)

print("Entraînement terminé.")

# =====================================================
# 5. Sauvegarder le modèle
# =====================================================

model.save("gaussian_copula_model.pkl")

print("Modèle sauvegardé : gaussian_copula_model.pkl")

# =====================================================
# 6. Générer de nouvelles données
# =====================================================

print("\nGénération des données synthétiques...")

synthetic_data = model.sample(num_rows=1000)

print("1000 lignes générées.")

# =====================================================
# 7. Sauvegarder le nouveau dataset
# =====================================================

synthetic_data.to_excel("synthetic_data.xlsx", index=False)

print("Dataset sauvegardé : synthetic_data.xlsx")

# =====================================================
# 8. Afficher un aperçu
# =====================================================

print("\nAperçu des données générées :")

print(synthetic_data.head())

# =====================================================
# 9. Comparaison statistique
# =====================================================

print("\n========== STATISTIQUES ==========\n")

print("Données réelles :")
print(data.describe(include="all"))

print("\nDonnées synthétiques :")
print(synthetic_data.describe(include="all"))

print("\nLe processus est terminé avec succès.")