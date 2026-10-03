"""
split_dataset_classification.py
--------------------------------
Organise deux dossiers d'images (cartes correctes / cartes défectueuses)
en structure de classification directement utilisable par YOLO.

Répartition :
    Train : 70 %
    Val   : 15 %
    Test  : 15 %

Structure créée :

    dataset_classification/
    ├── train/
    │   ├── correct/
    │   └── defaut/
    ├── val/
    │   ├── correct/
    │   └── defaut/
    └── test/
        ├── correct/
        └── defaut/

Le découpage est effectué par IMAGE.
"""

import os
import shutil
import random
import argparse
import sys


# ============================================================
# 1. LISTER LES IMAGES
# ============================================================

def lister_images(dossier):
    """
    Cherche les images récursivement.

    Retourne une liste de chemins relatifs.
    """

    extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    )

    if not os.path.isdir(dossier):
        return []

    resultats = []

    for racine, _dirs, fichiers in os.walk(dossier):

        for f in fichiers:

            if f.lower().endswith(extensions):

                chemin_relatif = os.path.relpath(
                    os.path.join(racine, f),
                    dossier
                )

                resultats.append(chemin_relatif)

    return resultats


# ============================================================
# 2. REPARTITION 70 % / 15 % / 15 %
# ============================================================

def repartir_70_15_15(images, seed=42):
    """
    Répartit les images en :

        70 % -> train
        15 % -> val
        15 % -> test

    Le découpage est aléatoire mais reproductible grâce au seed.
    """

    images = list(images)

    # Mélange aléatoire
    random.Random(seed).shuffle(images)

    total = len(images)

    # Calcul des tailles
    n_train = int(total * 0.70)
    n_val = int(total * 0.15)

    # Le reste va dans test
    # Cela garantit que train + val + test = 100 %
    n_test = total - n_train - n_val

    train = images[:n_train]

    val = images[
        n_train:n_train + n_val
    ]

    test = images[
        n_train + n_val:
    ]

    return train, val, test


# ============================================================
# 3. NOM DE FICHIER UNIQUE
# ============================================================

def nom_aplati(chemin_relatif):
    """
    Transforme un chemin relatif potentiellement dans un
    sous-dossier en un nom de fichier plat unique.

    Exemple :

        source1/photo01.jpg

    devient :

        source1__photo01.jpg
    """

    return chemin_relatif.replace(
        os.sep,
        "__"
    ).replace(
        "/",
        "__"
    )


# ============================================================
# 4. COPIER LES IMAGES
# ============================================================

def copier_images(
    images,
    dossier_source,
    dossier_destination
):
    """
    Copie les images vers le dossier correspondant.
    """

    os.makedirs(
        dossier_destination,
        exist_ok=True
    )

    for img in images:

        source = os.path.join(
            dossier_source,
            img
        )

        destination = os.path.join(
            dossier_destination,
            nom_aplati(img)
        )

        shutil.copy2(
            source,
            destination
        )


# ============================================================
# 5. ORGANISER LE DATASET
# ============================================================

def organiser_classification(
    dossier_correct,
    dossier_defaut,
    sortie,
    seed=42
):

    # --------------------------------------------------------
    # Création des dossiers
    # --------------------------------------------------------

    for split in ["train", "val", "test"]:

        for classe in ["correct", "defaut"]:

            os.makedirs(
                os.path.join(
                    sortie,
                    split,
                    classe
                ),
                exist_ok=True
            )

    # --------------------------------------------------------
    # Récupération des images
    # --------------------------------------------------------

    images_correct = lister_images(
        dossier_correct
    )

    images_defaut = lister_images(
        dossier_defaut
    )

    print(
        f"Cartes correctes trouvées   : "
        f"{len(images_correct)}"
    )

    print(
        f"Cartes défectueuses trouvées : "
        f"{len(images_defaut)}"
    )

    # Vérification
    if not images_correct or not images_defaut:

        raise ValueError(
            "Il faut des images dans LES DEUX dossiers "
            "(correct ET défaut)."
        )

    # ========================================================
    # REPARTITION DES IMAGES CORRECTES
    # ========================================================

    print("\nRépartition des cartes correctes :")

    train_c, val_c, test_c = repartir_70_15_15(
        images_correct,
        seed
    )

    print(
        f"  Train : {len(train_c)} images"
    )

    print(
        f"  Val   : {len(val_c)} images"
    )

    print(
        f"  Test  : {len(test_c)} images"
    )

    # ========================================================
    # REPARTITION DES IMAGES DEFAUT
    # ========================================================

    print("\nRépartition des cartes défectueuses :")

    train_d, val_d, test_d = repartir_70_15_15(
        images_defaut,
        seed + 1
    )

    print(
        f"  Train : {len(train_d)} images"
    )

    print(
        f"  Val   : {len(val_d)} images"
    )

    print(
        f"  Test  : {len(test_d)} images"
    )

    # ========================================================
    # COPIE DES IMAGES
    # ========================================================

    print("\nCopie des images...\n")

    # --------------------------------------------------------
    # CORRECT
    # --------------------------------------------------------

    copier_images(
        train_c,
        dossier_correct,
        os.path.join(
            sortie,
            "train",
            "correct"
        )
    )

    copier_images(
        val_c,
        dossier_correct,
        os.path.join(
            sortie,
            "val",
            "correct"
        )
    )

    copier_images(
        test_c,
        dossier_correct,
        os.path.join(
            sortie,
            "test",
            "correct"
        )
    )

    # --------------------------------------------------------
    # DEFAUT
    # --------------------------------------------------------

    copier_images(
        train_d,
        dossier_defaut,
        os.path.join(
            sortie,
            "train",
            "defaut"
        )
    )

    copier_images(
        val_d,
        dossier_defaut,
        os.path.join(
            sortie,
            "val",
            "defaut"
        )
    )

    copier_images(
        test_d,
        dossier_defaut,
        os.path.join(
            sortie,
            "test",
            "defaut"
        )
    )

    # ========================================================
    # CALCUL DES TOTAUX
    # ========================================================

    total_train = (
        len(train_c) +
        len(train_d)
    )

    total_val = (
        len(val_c) +
        len(val_d)
    )

    total_test = (
        len(test_c) +
        len(test_d)
    )

    total = (
        total_train +
        total_val +
        total_test
    )

    # ========================================================
    # AFFICHAGE FINAL
    # ========================================================

    print("\n==============================================")
    print("             DATASET FINAL")
    print("==============================================")

    print(
        f"\nTRAIN : {len(train_c)} correct + "
        f"{len(train_d)} défaut "
        f"= {total_train} images"
    )

    print(
        f"        Proportion : "
        f"{total_train / total * 100:.2f} %"
    )

    print(
        f"\nVAL   : {len(val_c)} correct + "
        f"{len(val_d)} défaut "
        f"= {total_val} images"
    )

    print(
        f"        Proportion : "
        f"{total_val / total * 100:.2f} %"
    )

    print(
        f"\nTEST  : {len(test_c)} correct + "
        f"{len(test_d)} défaut "
        f"= {total_test} images"
    )

    print(
        f"        Proportion : "
        f"{total_test / total * 100:.2f} %"
    )

    print(
        f"\nTOTAL : {total} images"
    )

    print("\n==============================================")
    print("Proportions demandées")
    print("==============================================")
    print("Entraînement : 70 %")
    print("Validation   : 15 %")
    print("Test         : 15 %")
    print("Total        : 100 %")
    print("==============================================")

    print(
        f"\nDataset créé dans : '{sortie}'"
    )

    print(
        "\nLe dossier TEST est indépendant et ne doit pas "
        "être utilisé pendant l'entraînement ni pour "
        "choisir le meilleur checkpoint."
    )


# ============================================================
# 6. MODE INTERACTIF
# ============================================================

def mode_interactif():

    print(
        "=== Organisation du dataset "
        "CORRECT / DEFAUT ===\n"
    )

    dossier_correct = input(
        "Dossier des cartes correctes "
        "[dataset_augmente] : "
    ).strip()

    if not dossier_correct:
        dossier_correct = "dataset_augmente"

    dossier_defaut = input(
        "Dossier des cartes défectueuses : "
    ).strip()

    sortie = input(
        "Dossier de sortie "
        "[dataset_classification] : "
    ).strip()

    if not sortie:
        sortie = "dataset_classification"

    organiser_classification(
        dossier_correct,
        dossier_defaut,
        sortie
    )


# ============================================================
# 7. PROGRAMME PRINCIPAL
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) == 1:

        mode_interactif()

    else:

        parser = argparse.ArgumentParser(
            description=(
                "Organisation d'un dataset de classification "
                "avec Train 70 %, Val 15 %, Test 15 %"
            )
        )

        parser.add_argument(
            "--correct",
            default="dataset_augmente",
            help="Dossier des cartes correctes"
        )

        parser.add_argument(
            "--defaut",
            required=True,
            help="Dossier des cartes défectueuses"
        )

        parser.add_argument(
            "--output",
            default="dataset_classification",
            help="Dossier de sortie"
        )

        parser.add_argument(
            "--seed",
            type=int,
            default=42,
            help="Seed aléatoire"
        )

        args = parser.parse_args()

        organiser_classification(
            args.correct,
            args.defaut,
            args.output,
            args.seed
        )