import pandas as pd
from sdv.single_table import CTGANSynthesizer
# Charger le fichier Excel
data = pd.read_excel("balanced_dataset.xlsx")

# Supprimer les colonnes d'identification
data = data.drop(columns=[
    "enregistrer par le nom",
    "identification"
])

print("\nDataset utilisé pour CTGAN :")
print(data.head())

print("\nDimensions :", data.shape)

print("\nColonnes :")
print(data.columns)

from sdv.metadata import SingleTableMetadata

# ==========================================
# Création des métadonnées
# ==========================================

metadata = SingleTableMetadata()

metadata.detect_from_dataframe(data)

print("\n========== METADATA ==========\n")

print(metadata.to_dict())
synthesizer = CTGANSynthesizer(
    metadata,
    epochs=300
)
# ==========================================
# Entraînement du modèle CTGAN
# ==========================================

print("\nDébut de l'entraînement CTGAN...")

synthesizer.fit(data)

print("\nEntraînement terminé avec succès !")
# ==========================================
# Génération des données synthétiques
# ==========================================

print("\nGénération des données...")


synthetic_data = synthesizer.sample(
    num_rows=10000
)


print("\nDataset généré :")
print(synthetic_data.head())


print("\nDimensions :")
print(synthetic_data.shape)


print("\nRépartition Pass / Fail :")
print(synthetic_data["statut_reel"].value_counts())


# Sauvegarde Excel

synthetic_data.to_excel(
    "dataset_CTGAN_10000.xlsx",
    index=False
)


print("\nFichier créé : dataset_CTGAN_10000.xlsx")