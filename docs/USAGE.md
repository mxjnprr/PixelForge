# 📖 Guide d'Utilisation de PixelForge Studio

## Table des Matières

1. [Configuration Initiale](#configuration-initiale)
2. [Onglet Édition (Traitement en Masse)](#onglet-édition-traitement-en-masse)
3. [Onglet Génération](#onglet-génération)
4. [Onglet Édition Ciblée](#onglet-édition-ciblée)
5. [Paramètres](#paramètres)

---

## Configuration Initiale

### 1. Obtenir une clé API Gemini

1. Rendez-vous sur [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Connectez-vous avec votre compte Google
3. Cliquez sur **"Create API Key"**
4. Copiez la clé générée

### 2. Configurer PixelForge

1. Lancez l'application
2. Allez dans l'onglet **⚙️ Paramètres**
3. Collez votre clé API dans le champ prévu
4. Cliquez sur **Tester** pour vérifier la connexion
5. Cliquez sur **Sauvegarder**

> 💡 La clé est stockée de manière sécurisée dans le trousseau de votre système.

---

## Onglet Édition (Traitement en Masse)

Cet onglet permet d'appliquer le même prompt à plusieurs images.

### Comment utiliser

1. **Ajouter des images** :
   - Cliquez sur **"➕ Ajouter des images"**
   - Ou glissez-déposez directement des images

2. **Écrire le prompt** :
   - Décrivez la transformation souhaitée
   - Ou utilisez un **style prédéfini** dans le menu déroulant

3. **Lancer le traitement** :
   - Cliquez sur **"🚀 Lancer le traitement"**
   - Suivez la progression dans la barre

### Exemples de prompts

| Catégorie | Prompt |
|-----------|--------|
| Style artistique | `Transforme en style aquarelle avec des tons pastel` |
| Fond | `Supprime l'arrière-plan et remplace par un fond blanc` |
| Ambiance | `Ajoute une ambiance coucher de soleil avec des couleurs chaudes` |
| Cartoon | `Transforme en illustration cartoon colorée` |

---

## Onglet Génération

Cet onglet permet de créer des images à partir de zéro.

### Comment utiliser

1. **Écrire la description** :
   - Décrivez l'image que vous voulez générer
   - Soyez précis (style, couleurs, éléments, ambiance)

2. **Configurer** :
   - **Nombre d'images** : 1 à 10
   - **Modèle** : Nano Banana (rapide) ou Pro (haute qualité)
   - **Ratio** : 1:1, 16:9, 9:16, 4:3, 3:4

3. **Générer** :
   - Cliquez sur **"✨ Générer"**
   - Les images apparaissent dans la grille d'aperçu

### Conseils pour de bons prompts

- ✅ `Un chat roux assis sur un coussin bleu, éclairage doux, style photo réaliste`
- ❌ `un chat` (trop vague)

---

## Onglet Édition Ciblée

Cet onglet permet de **modifier une zone spécifique** d'une image en dessinant dessus.

### Outils disponibles

| Outil | Description |
|-------|-------------|
| 🖌️ **Pinceau** | Dessin libre avec couleur et taille ajustable |
| ▢ **Rectangle** | Sélection rectangulaire |
| ○ **Ellipse** | Sélection elliptique |
| ✏️ **Sélection libre** | Tracé fermé à main levée |

### Comment utiliser

1. **Charger une image** :
   - Cliquez sur **"📂 Charger une image"**
   - Ou cliquez directement sur le canvas

2. **Dessiner la zone à modifier** :
   - Sélectionnez l'outil **🖌️ Pinceau** (recommandé)
   - Choisissez une couleur
   - Ajustez la taille du pinceau
   - **Dessinez sur la zone** que vous voulez modifier

3. **Écrire le prompt** :
   - Décrivez ce que vous voulez faire dans cette zone
   - Exemple : `Ajoute des papillons` ou `Remplace par un ciel bleu`

4. **Appliquer** :
   - Cliquez sur **"🎯 Appliquer la modification"**
   - L'IA modifiera uniquement la zone dessinée

### Exemples d'utilisation

| Vous dessinez sur... | Prompt | Résultat |
|---------------------|--------|----------|
| Le ciel | `Remplace par un coucher de soleil` | Le ciel devient un coucher de soleil |
| Un objet | `Supprime cet élément` | L'objet disparaît |
| Une zone vide | `Ajoute des fleurs` | Des fleurs apparaissent |

### Conseils

- ✅ **Dessinez clairement** la zone avec des traits visibles
- ✅ Utilisez une **couleur contrastante** avec l'image
- ✅ Soyez **précis dans le prompt** (ce que vous voulez, pas ce que vous ne voulez pas)

---

## Onglet Transfert de Style

Cet onglet permet d'**appliquer le style d'une image sur une autre**.

### Comment utiliser

1. **Charger l'image source** :
   - C'est l'image que vous voulez transformer
   - Cliquez sur **"📂 Charger l'image source"**

2. **Charger l'image de style** :
   - C'est l'image dont vous voulez copier le style
   - Cliquez sur **"📂 Charger l'image de style"**

3. **Choisir l'intensité** :
   - **Subtil** : Légère influence du style
   - **Modéré** : Équilibre entre source et style
   - **Fort** : Le style domine fortement

4. **Appliquer** :
   - Cliquez sur **"🎨 Appliquer le style"**

### Exemples

| Image Source | Image Style | Résultat |
|--------------|-------------|----------|
| Photo de paysage | Tableau de Van Gogh | Paysage en style impressionniste |
| Portrait | Photo vintage | Portrait avec tons sépia |
| Architecture | Aquarelle | Bâtiment en style aquarelle |

---

## Paramètres

### Options disponibles

| Paramètre | Description |
|-----------|-------------|
| **Clé API** | Votre clé Gemini API |
| **Dossier de sortie** | Où sauvegarder les images générées |
| **Modèle** | Nano Banana (rapide) ou Pro (qualité) |
| **Ratio d'aspect** | Format de sortie (1:1, 16:9, etc.) |
| **Qualité** | Standard, 2K ou 4K |

### Stockage de la configuration

- **Linux** : `~/.config/pixelforge-studio/`
- **Windows** : `%APPDATA%\pixelforge-studio\`

---

## Raccourcis et astuces

| Astuce | Description |
|--------|-------------|
| Double-clic sur aperçu | Ouvre l'image dans la visionneuse système |
| Glisser-déposer | Ajoutez des images rapidement |
| Styles prédéfinis | Gagnez du temps avec les prompts préconçus |

---

## Support

En cas de problème :
1. Vérifiez votre connexion internet
2. Testez votre clé API dans les paramètres
3. Reformulez votre prompt si l'API refuse de générer
