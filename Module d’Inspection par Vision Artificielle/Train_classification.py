import os
import sys
import argparse
import torch
import torch.nn.functional as F
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from ultralytics import YOLO


class WeightedClassificationLoss:
    """Perte Cross-Entropy pondérée avec Label Smoothing."""
    def __init__(self, weight, label_smoothing=0.1):
        self.weight = weight
        self.label_smoothing = label_smoothing

    def __call__(self, preds, batch):
        preds = preds[1] if isinstance(preds, (list, tuple)) else preds
        w = self.weight.to(preds.device)
        loss = F.cross_entropy(
            preds, batch["cls"], weight=w,
            label_smoothing=self.label_smoothing, reduction="mean"
        )
        return loss, loss.detach()


def _appliquer_ponderation_classe(model, poids_par_nom_classe, label_smoothing=0.1):
    def on_train_start(trainer):
        names = trainer.data["names"]
        poids = torch.ones(len(names))
        for idx, nom in names.items():
            if nom in poids_par_nom_classe:
                poids[idx] = poids_par_nom_classe[nom]
        print(f"Pondération de classe appliquée : {{{', '.join(f'{names[i]}={poids[i]:.1f}' for i in names)}}}")
        print(f"Label smoothing appliqué : {label_smoothing}")
        trainer.model.criterion = WeightedClassificationLoss(poids, label_smoothing)

    model.add_callback("on_train_start", on_train_start)


def _generer_graphiques_metrics(dossier_resultats):
    """Génère un graphique propre des pertes et métriques à partir de results.csv."""
    csv_path = os.path.join(dossier_resultats, "results.csv")
    if not os.path.exists(csv_path):
        return

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    fig, axs = plt.subplots(2, 2, figsize=(10, 8), dpi=150)
    
    # Train Loss
    if "train/loss" in df.columns:
        axs[0, 0].plot(df["epoch"], df["train/loss"], "o-", label="train/loss")
        axs[0, 0].set_title("Train Loss")
        axs[0, 0].grid(True, linestyle="--", alpha=0.5)

    # Val Loss
    if "val/loss" in df.columns:
        axs[1, 0].plot(df["epoch"], df["val/loss"], "o-", color="red", label="val/loss")
        axs[1, 0].set_title("Validation Loss")
        axs[1, 0].grid(True, linestyle="--", alpha=0.5)

    # Accuracy
    acc_col = [c for c in df.columns if "accuracy" in c or "top1" in c]
    if acc_col:
        axs[0, 1].plot(df["epoch"], df[acc_col[0]], "o-", color="green", label="Accuracy")
        axs[0, 1].set_title("Accuracy Top-1")
        axs[0, 1].grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    chart_path = os.path.join(dossier_resultats, "courbes_propres.png")
    plt.savefig(chart_path)
    plt.close()
    print(f"Courbes sauvegardées -> {chart_path}")


def _imprimer_metriques_defaut(cm, classes, split):
    """Affiche Accuracy / Précision / Rappel / F1 pour la classe 'defaut', dans le
    même format que le tableau 3.5 du rapport, pour comparaison directe avec les
    métriques de validation obtenues au sprint précédent."""
    if "defaut" not in classes:
        return
    idx = classes.index("defaut")
    vp = int(cm[idx, idx])
    fn = int(cm[idx, :].sum() - vp)
    fp = int(cm[:, idx].sum() - vp)
    vn = int(cm.sum() - vp - fn - fp)

    total = cm.sum()
    accuracy = (vp + vn) / total if total else 0.0
    precision = vp / (vp + fp) if (vp + fp) else 0.0
    rappel = vp / (vp + fn) if (vp + fn) else 0.0
    f1 = 2 * precision * rappel / (precision + rappel) if (precision + rappel) else 0.0

    print(f"\n=== Métriques sur le jeu de '{split}' (classe 'defaut') ===")
    print(f"  Accuracy globale : {accuracy:.4f}")
    print(f"  Précision        : {precision:.4f}")
    print(f"  Rappel           : {rappel:.4f}  ({fn} faux négatifs sur {vp + fn} cartes réellement défectueuses)")
    print(f"  F1-Score         : {f1:.4f}")


def _generer_matrice_confusion(model, dataset_dir, dossier_resultats, split="test"):
    best_path = os.path.join(dossier_resultats, "weights", "best.pt")
    modele_best = YOLO(best_path)

    split_dir = os.path.join(dataset_dir, split)
    if not os.path.isdir(split_dir):
        print(f"[AVERTISSEMENT] Dossier '{split}' introuvable dans {dataset_dir}.")
        print("  -> Repli sur 'val' : ces métriques ne sont alors PAS indépendantes du "
              "choix du meilleur checkpoint (limite méthodologique, section 3.3.4 du rapport).")
        print("  Lance Split_dataset.py (version à jour) pour générer un dossier 'test'.")
        split = "val"
        split_dir = os.path.join(dataset_dir, split)

    classes = sorted(os.listdir(split_dir))

    # Métriques officielles Ultralytics (top1/top5), calculées sur ce split précis.
    modele_best.val(data=dataset_dir, split=split)

    y_true, y_pred = [], []
    for classe in classes:
        dossier_classe = os.path.join(split_dir, classe)
        for fichier in os.listdir(dossier_classe):
            chemin_img = os.path.join(dossier_classe, fichier)
            resultat = modele_best.predict(chemin_img, verbose=False)[0]
            classe_predite = resultat.names[resultat.probs.top1]
            y_true.append(classe)
            y_pred.append(classe_predite)

    cm = confusion_matrix(y_true, y_pred, labels=classes)
    # Correction : normalize='true' pour afficher le Recall direct sur la matrice
    cm_norm = confusion_matrix(y_true, y_pred, labels=classes, normalize="true")

    for matrice, titre, nom_fichier, fmt in [
        (cm, f"Confusion Matrix ({split}, brute)", f"confusion_matrix_best_{split}.png", "d"),
        (cm_norm, f"Confusion Matrix ({split}, Normalized/Recall)", f"confusion_matrix_best_{split}_normalized.png", ".2f"),
    ]:
        plt.figure(figsize=(6, 5))
        sns.heatmap(matrice, annot=True, fmt=fmt, cmap="Blues",
                    xticklabels=classes, yticklabels=classes)
        plt.title(titre)
        plt.xlabel("Prédit")
        plt.ylabel("Réel")
        plt.tight_layout()
        plt.savefig(os.path.join(dossier_resultats, nom_fichier), dpi=150)
        plt.close()

    _imprimer_metriques_defaut(cm, classes, split)

    return cm, cm_norm


def _verifier_taille_dataset(dataset_dir, seuil_alerte_par_classe=200):
    """Piste 2 du rapport : une partie de l'instabilité des métriques de validation
    d'une epoch à l'autre vient probablement d'un jeu de train/val trop petit.
    On ne peut pas fabriquer des images automatiquement ici, mais on peut au moins
    rendre le problème visible AVANT de lancer un entraînement coûteux plutôt que
    de le découvrir après coup dans les courbes."""
    print("\n=== Vérification de la taille du dataset (piste 2 du rapport) ===")
    extensions = (".jpg", ".jpeg", ".png", ".bmp")
    trop_petit = False

    for split in ("train", "val", "test"):
        dossier_split = os.path.join(dataset_dir, split)
        if not os.path.isdir(dossier_split):
            continue
        for classe in sorted(os.listdir(dossier_split)):
            dossier_classe = os.path.join(dossier_split, classe)
            if not os.path.isdir(dossier_classe):
                continue
            n = len([f for f in os.listdir(dossier_classe) if f.lower().endswith(extensions)])
            marqueur = "  <-- ATTENTION : sous le seuil recommandé" if n < seuil_alerte_par_classe else ""
            if marqueur:
                trop_petit = True
            print(f"  {split}/{classe} : {n} images{marqueur}")

    if trop_petit:
        print(
            f"\n[AVERTISSEMENT] Au moins une classe a moins de {seuil_alerte_par_classe} images.\n"
            "Les métriques de validation (accuracy, recall) risquent d'être instables d'une\n"
            "epoch à l'autre simplement à cause du peu d'échantillons. Pour réduire cette\n"
            "variance : collecter davantage d'images (en priorité côté 'defaut', la classe la\n"
            "plus critique métier), puis relancer Split_dataset.py avant de ré-entraîner.\n"
        )


def entrainer(dataset_dir, epochs=60, imgsz=224, modele_base="yolov8s-cls.pt",
              patience=40, dropout=0.3, batch=32, lr0=0.0005, lrf=0.05,
              warmup_epochs=3, cos_lr=True, momentum=0.937, poids_defaut=2.0,
              weight_decay=0.0025, label_smoothing=0.1, mixup=0.0, freeze=9,
              fliplr=0.0, flipud=0.0, mosaic=0.0, seed=0,
              seuil_alerte_par_classe=200, split_evaluation="test"):

    dataset_dir = os.path.abspath(dataset_dir)
    _verifier_taille_dataset(dataset_dir, seuil_alerte_par_classe)

    model = YOLO(modele_base)

    if poids_defaut != 1.0:
        _appliquer_ponderation_classe(model, {"defaut": poids_defaut}, label_smoothing)

    results = model.train(
        data=dataset_dir,
        epochs=epochs,
        imgsz=imgsz,
        patience=patience,
        dropout=dropout,
        batch=batch,
        lr0=lr0,
        lrf=lrf,
        warmup_epochs=warmup_epochs,
        cos_lr=cos_lr,
        momentum=momentum,
        weight_decay=weight_decay,
        freeze=freeze,
        plots=True,
        seed=seed,
        deterministic=True,
        optimizer="auto",
        # --- Configuration d'augmentation reproduisant la section 3.2 (args.yaml réel) ---
        hsv_h=0.015, hsv_s=0.3, hsv_v=0.4,
        degrees=5.0, translate=0.05, scale=0.1,
        erasing=0.2,
        # Flip horizontal/vertical désactivés : l'orientation de la carte sur le support de
        # test est fixe et connue, un retournement produirait des images physiquement
        # invalides (sérigraphie inversée, polarité des composants faussée). Ne pas réactiver.
        fliplr=fliplr,
        flipud=flipud,
        # Mosaic désactivé : ne correspond à aucune configuration réelle observable par la
        # caméra du poste d'inspection (une seule carte par image, jamais 4 assemblées).
        mosaic=mosaic,
        # Mixup non documenté dans args.yaml / section 3.2 -> supposé non utilisé (0.0).
        # A vérifier dans ton args.yaml si tu veux être certain à 100%.
        mixup=mixup,
        # --- Piste 3 (rapport) : LR initial plus faible + décroissance cosine moins agressive ---
        # Baseline réelle : lr0=0.001, lrf=0.01 (LR final = 1% du LR initial -> chute abrupte).
        # On adoucit : lr0=0.0005, lrf=0.05 (LR final = 5% du LR initial).
    )

    dossier_resultats = results.save_dir
    print(f"\n=== Entraînement terminé ===")
    print(f"Meilleur modèle : {os.path.join(dossier_resultats, 'weights', 'best.pt')}")
    print(f"Évaluation finale sur le split '{split_evaluation}' (indépendant du choix du checkpoint)")

    _generer_matrice_confusion(model, dataset_dir, dossier_resultats, split=split_evaluation)
    _generer_graphiques_metrics(dossier_resultats)

    return dossier_resultats

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="dataset_classification")
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--modele", default="yolov8s-cls.pt")
    parser.add_argument("--lr0", type=float, default=0.0005, help="Taux d'apprentissage initial (piste 3 ; baseline réelle = 0.001)")
    parser.add_argument("--lrf", type=float, default=0.05, help="Fraction du LR final, cosine decay (piste 3 ; baseline réelle = 0.01)")
    parser.add_argument("--mixup", type=float, default=0.0, help="Intensité du mixup (non utilisé dans la config baseline)")
    parser.add_argument("--split_evaluation", default="test",
                         help="Split utilisé pour l'évaluation finale, indépendant du choix du checkpoint (défaut : test)")
    args = parser.parse_args()

    entrainer(
        args.data, epochs=args.epochs, modele_base=args.modele,
        lr0=args.lr0, lrf=args.lrf, mixup=args.mixup,
        split_evaluation=args.split_evaluation,
    )