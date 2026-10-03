import cv2
import albumentations as A
import matplotlib.pyplot as plt
import os
import numpy as np

# --- Étape 1 : vérification ---
print('Toutes les bibliothèques sont installées !')

# --- Étape 2 : charger l'image ---
image_path = r"C:\Users\MSI\Downloads\ChatGPT Image 3 sept. 2026, 22_21_22.png"
image = cv2.imread(image_path)
if image is None:
    raise ValueError('Image non trouvée ! Vérifie que carte.jpg est dans le même dossier que ce script.')

image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

plt.figure(figsize=(6,6))
plt.title('Image originale')
plt.imshow(image_rgb)
plt.axis('off')
plt.show()

# --- Étape 3 : définir les transformations ---
transform = A.Compose([
    A.Rotate(limit=15, p=0.7),
    A.RandomBrightnessContrast(p=0.5),
    A.Affine(
        translate_percent=0.1,
        scale=(0.9, 1.1),
        rotate=(-10, 10),
        p=0.7
    ),
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.2),
    A.GaussNoise(std_range=(0.05, 0.15), p=0.3),
    A.Blur(blur_limit=3, p=0.2),
])

# --- Étape 4 : dossier de sortie ---
output_dir = 'dataset_TESF'
os.makedirs(output_dir, exist_ok=True)
print('Dossier créé :', output_dir)

# --- Étape 5 : générer les images ---
n_images =300 
for i in range(n_images):
    augmented = transform(image=image)['image']
    filename = os.path.join(output_dir, f'image_{i:04d}.jpg')
    cv2.imwrite(filename, augmented)
    if (i+1) % 100 == 0:
        print(f'{i+1} images générées...')
print(f'Terminé ! {n_images} images ont été générées dans {output_dir}')

# --- Étape 6 : afficher un échantillon ---
import random
def afficher_echantillon(dossier, n=8):
    images = random.sample(os.listdir(dossier), n)
    plt.figure(figsize=(12,6))
    for i, img_name in enumerate(images):
        img_path = os.path.join(dossier, img_name)
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        plt.subplot(2, 4, i+1)
        plt.imshow(img)
        plt.axis('off')
    plt.tight_layout()
    plt.show()

afficher_echantillon(output_dir, n=8)

# --- Étape 8 : vérifier le nombre total ---
n_total = len(os.listdir(output_dir))
print(f'Nombre total d\'images dans {output_dir} : {n_total}')