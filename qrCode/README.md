# QR Code (site)

Génère un QR Code à partir d'une URL de site web, avec l'URL écrite en clair
sous le code — une solution de secours si le QR ne peut pas être scanné
(papier abîmé, mauvaise lumière, etc.).

---

## Fonctionnalités

- Normalise l'URL (ajoute `https://` si le protocole est absent).
- Valide le format (rejette les espaces et les domaines sans point).
- Vérifie que le site répond réellement (HTTP `200` ou `403`).
- Génère le PNG : QR Code en haut, URL en texte en bas.

---

## Choix des bibliothèques

| Bibliothèque | Type | Rôle | Pourquoi celle-ci |
|--------------|------|------|-------------------|
| `argparse` | standard | Lire les arguments en ligne de commande | Gère `--help`, les erreurs d'usage et le typage automatiquement. Plus robuste que `sys.argv` brut. |
| `urllib.parse` | standard | Décomposer et analyser une URL | Fournit `urlparse` qui isole le schéma (`https`) et le domaine. Rien à installer. |
| `requests` | tierce | Faire la requête HTTP de vérification | API bien plus lisible que `urllib.request` (stdlib) pour un simple `GET`. |
| `qrcode` | tierce | Générer le QR Code | La référence Python pour les QR, simple et bien documentée. |
| `Pillow` | tierce | Composer l'image finale (texte sous le QR) | Le standard de fait pour manipuler des images en Python. |

> **Règle de choix retenue** : bibliothèque standard quand elle suffit (`argparse`,
> `urllib.parse`), bibliothèque tierce quand elle simplifie nettement le code
> (`requests`, `qrcode`, `Pillow`).

---

## Explication du code

### `normaliser_url(url)`

```python
def normaliser_url(url: str) -> str:
    if not urlparse(url).scheme:
        return "https://" + url
    return url
```

`urlparse("lamizana.github.io/ZehdBox").scheme` vaut `""` (pas de `https://`).
Dans ce cas on ajoute le préfixe. Si l'utilisateur a déjà écrit `https://...`,
on renvoie l'URL telle quelle.

### `est_url_valide(url)`

```python
def est_url_valide(url: str) -> bool:
    if " " in url:
        return False
    resultat = urlparse(url)
    return resultat.scheme in ("http", "https") and "." in resultat.netloc
```

Deux vérifications : **pas d'espace** (`urlparse` tolère `pas une url`, pas nous)
et **un point dans le domaine** (donc un vrai TLD : `exemple.com`, pas `a`).
On accepte uniquement `http` et `https`.

> ⚠️ Limite assumée : `https://localhost` est rejeté (pas de point). C'est un
> compromis volontaire — une règle simple et lisible plutôt qu'une regex complexe.

### `url_existe(url)`

```python
def url_existe(url: str) -> bool:
    try:
        reponse = requests.get(url, timeout=10)
        return reponse.status_code in (200, 403)
    except requests.exceptions.RequestException:
        return False
```

Envoie une requête et regarde le code HTTP : `200` = OK, `403` = le site existe
mais refuse les robots (on le considère comme existant). Un `timeout` de 10 s
évite de bloquer indéfiniment. Si quoi que ce soit échoue (DNS, réseau coupé,
timeout), on retourne `False`.

### `generer_qrcode(donnees, texte_visible, fichier_sortie)`

```python
qr = qrcode.QRCode(
    error_correction=qrcode.constants.ERROR_CORRECT_H,  # 30% de correction
    box_size=10,                                        # taille d'un module
    border=4,                                           # marge blanche
)
qr.add_data(donnees)
qr.make(fit=True)                                       # ajuste la taille auto
img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")
```

Le QR est généré puis **composé** avec Pillow : on crée une image blanche plus
haute (hauteur du QR + 60 px), on colle le QR en haut, on écrit l'URL centrée en
bas (`dessin.textlength` sert à mesurer le texte pour le centrer).

### `main()`

```
normaliser → valider le format → vérifier l'existence → générer
```

Le flux est volontairement **séquentiel** : chaque étape peut arrêter le script
avec un message clair et un code de retour. `sys.exit(main())` permet de
propager ce code à l'appelant.

---

## Gestion des erreurs

Trois niveaux de contrôle, du plus simple au plus coûteux :

| Étape | Nature | Style |
|-------|--------|-------|
| `est_url_valide` | Erreur **prévisible** (format) | `if` → LBYL (Look Before You Leap) |
| `url_existe` | Erreur **imprévisible** (réseau) | `try/except` → EAFP (Easier to Ask Forgiveness) |
| `main` | Comportement d'arrêt | codes de retour `0` / `1` |

Pourquoi cette distinction ? Un format invalide se vérifie **avant** d'agir avec
un simple `if`. En revanche, la réponse d'un serveur (hors ligne, DNS absent,
timeout) est **impossible à prévoir** : on tente la requête et on attrape
l'exception — c'est le cas d'école du `try/except`.

### Codes de retour

| Code | Signification |
|------|---------------|
| `0` | Succès |
| `1` | Échec (format invalide **ou** URL injoignable) |

Chaque échec affiche un message `ERREUR : ...` qui indique **laquelle** des deux
vérifications a échoué — c'est ce qui rend le débogage rapide.

---

## Installation

```bash
# Depuis la racine du dépôt (là où se trouvent .venv et requirements.txt)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

```bash
# Depuis la racine du dépôt
python qrCode/qrcode_site.py lamizana.github.io/ZehdBox
# → génère qrcode_site.png dans le dossier courant
```

```bash
python qrCode/qrcode_site.py "pas une url"
# → ERREUR : L'URL https://pas une url n'est pas valide
```
