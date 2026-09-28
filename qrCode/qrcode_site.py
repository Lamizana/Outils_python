import sys
import qrcode
import argparse
import requests
from urllib.parse import urlparse
from PIL import Image, ImageDraw, ImageFont


# -----------------------------------------------------------------------------
def normaliser_url(url: str) -> str:
    """Ajoute https:// si aucun protocole n'est précisé."""
    if not urlparse(url).scheme:
        return "https://" + url
    return url


# -----------------------------------------------------------------------------
def est_url_valide(url: str) -> bool:
    """Retourne True si l'URL a un format valide."""
    resultat = urlparse(url)
    return resultat.scheme in ("http", "https") and bool(resultat.netloc)


# -----------------------------------------------------------------------------
def url_existe(url: str) -> bool:
    """Retourne True si l'URL répond (200 ou 403)."""
    try:
        reponse = requests.get(url, timeout=10)
        return reponse.status_code in (200, 403)
    except requests.exceptions.RequestException:
        return False


# -----------------------------------------------------------------------------
def generer_qrcode(donnees: str, texte_visible: str, fichier_sortie: str) -> None:
    """Génère un QR Code PNG avec le texte visible en dessous."""
    # 1. Générer l'image du QR Code
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(donnees)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # 2. Récupérer les dimensions
    largeur_qr, hauteur_qr = img_qr.size
    hauteur_texte = 60

    # 3. Créer une image blanche plus haute
    img_finale = Image.new(
        "RGB",
        (largeur_qr, hauteur_qr + hauteur_texte),
        color="white",
    )

    # 4. Coller le QR Code en haut
    img_finale.paste(img_qr, (0, 0))

    # 5. Écrire l'URL, centrée, en bas
    police = ImageFont.load_default()
    dessin = ImageDraw.Draw(img_finale)
    largeur_texte = dessin.textlength(texte_visible, font=police)
    x = (largeur_qr - largeur_texte) // 2
    y = hauteur_qr + 20
    dessin.text((x, y), texte_visible, fill="black", font=police)

    # 6. Sauvegarder
    img_finale.save(fichier_sortie)


# -----------------------------------------------------------------------------
def main() -> int:
    """Fonction programme principal."""

    parser = argparse.ArgumentParser(
        description="Génère un QR Code à partir d'une URL."
    )
    parser.add_argument("url", help="URL du site à encoder dans le QR Code")
    args = parser.parse_args()

    url = normaliser_url(args.url)

    if not est_url_valide(url):
        print(f"ERREUR : L'URL {url} n'est pas valide")
        return 1

    if not url_existe(url):
        print(f"ERREUR : L'URL {url} n'est pas accessible (code HTTP != 200)")
        return 1

    generer_qrcode(url, url, "qrcode_site.png")
    print("QR Code généré : qrcode_site.png")
    return 0


###############################################################################
if __name__ == "__main__":
    sys.exit(main())
