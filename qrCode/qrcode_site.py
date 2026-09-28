import sys
import qrcode
import argparse
import requests
from urllib.parse import urlparse
from PIL import Image


# -----------------------------------------------------------------------------
def normaliser_url(url: str) -> str:
    """Ajoute https:// si aucun protocole n'est précisé."""
    if not urlparse(url).scheme:
        return "https://" + url
    return url


# -----------------------------------------------------------------------------
def est_url_valide(url: str) -> bool:
    """Retourne True si l'URL a un format valide."""
    if " " in url:
        return False

    resultat = urlparse(url)
    return resultat.scheme in ("http", "https") and "." in resultat.netloc


# -----------------------------------------------------------------------------
def url_existe(url: str) -> bool:
    """Retourne True si l'URL répond (200 ou 403)."""
    try:
        reponse = requests.get(url, timeout=10)
        return reponse.status_code in (200, 403)
    except requests.exceptions.RequestException:
        return False


# -----------------------------------------------------------------------------
def generer_qrcode(donnees: str, fichier_sortie: str) -> None:
    """Génère un QR Code PNG sans texte en dessous."""
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(donnees)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img_qr.save(fichier_sortie)


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
        print(f"ERREUR : L'URL {url} n'est pas accessible")
        return 1

    generer_qrcode(url, "qrcode_site.png")

    print("QR Code généré : qrcode_site.png")
    return 0


###############################################################################
if __name__ == "__main__":
    sys.exit(main())
