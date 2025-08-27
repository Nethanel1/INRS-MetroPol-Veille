import requests
from bs4 import BeautifulSoup
import json
import os
import io
import pdfplumber
import re
from datetime import datetime, timezone

# URLs
BASE_URL = "https://www.inrs.fr"
METROPOL_HOME_URL = f"{BASE_URL}/publications/bdd/metropol.html"
FICHE_URL_TEMPLATE = f"{BASE_URL}/publications/bdd/metropol/fiche.html?refINRS=METROPOL_"

# Chemin de sortie
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'data.json')

def get_list_by_name_url():
    """Trouve l'URL du PDF 'Liste des méthodes disponibles par nom'."""
    print(f"Accès à la page d\'accueil Metropol : {METROPOL_HOME_URL}")
    try:
        response = requests.get(METROPOL_HOME_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        list_link = soup.find('a', string="Liste des méthodes disponibles par nom")
        if list_link and list_link.has_attr('href'):
            url = BASE_URL + list_link['href']
            print(f"URL du PDF trouvée : {url}")
            return url
    except Exception as e:
        print(f"Erreur lors de la recherche de l\'URL du PDF : {e}")
    return None

def get_all_fiches_from_pdf(pdf_url):
    """Extrait les références des fiches du texte du PDF et reconstruit les URLs."""
    print(f"Téléchargement et analyse textuelle du PDF : {pdf_url}")
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        
        fiches = []
        references = set() # Utiliser un set pour éviter les doublons de références

        with io.BytesIO(response.content) as pdf_file:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        # Regex pour trouver les références de type M-xxx ou M-xxxx
                        found_refs = re.findall(r"(M-\d{1,4})", text)
                        for ref in found_refs:
                            references.add(ref)
        
        for ref in sorted(list(references)):
            # Le format de l'URL est METROPOL_ suivi du numéro SANS le M-
            ref_number = ref.split('-')[1]
            fiches.append({
                'title': "Titre à récupérer",
                'url': f"{FICHE_URL_TEMPLATE}{ref_number}"
            })

        print(f"{len(fiches)} fiches uniques trouvées dans le PDF.")
        return fiches

    except Exception as e:
        print(f"Une erreur est survenue lors du traitement du PDF : {e}")
        return []


def get_fiche_details(fiche_url):
    """Extrait le titre et l'historique d'une fiche."""
    print(f"  -> Extraction de : {fiche_url}")
    try:
        response = requests.get(fiche_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, '''html.parser''')

        # Stratégie de titre : utiliser la balise <title> en priorité
        if soup.title and soup.title.string:
            # Nettoyer le titre : "Fumées de bitume M-2 - MétroPol - INRS" -> "Fumées de bitume M-2"
            title = soup.title.string.split('''-''')[0].strip()
        else:
            # Fallback sur le premier H1 si la balise title est absente
            title_tag = soup.find('''h1''')
            title = title_tag.get_text(strip=True) if title_tag else "Titre non trouvé"

        history = []
        history_title = soup.find('''h2''', string=lambda text: text and '''historique''' in text.lower())
        if history_title:
            history_container = history_title.find_next_sibling('''div''')
            if history_container:
                items = history_container.find_all(['''p''', '''li'''])
                for item in items:
                    text = item.get_text(strip=True)
                    if text:
                        history.append(text)
        return title, history
    except requests.RequestException:
        return "Fiche non trouvée", []


def main():
    """Fonction principale."""
    pdf_url = get_list_by_name_url()
    if not pdf_url:
        print("Arrêt du script.")
        return

    fiches = get_all_fiches_from_pdf(pdf_url)
    if not fiches:
        print("Aucune fiche trouvée. Arrêt du script.")
        return

    all_data = []
    for i, fiche in enumerate(fiches):
        title, history = get_fiche_details(fiche['url'])
        # On n'ajoute que les fiches qui ont été trouvées
        if title not in ["Titre non trouvé", "Fiche non trouvée"]:
            all_data.append({
                'id': fiche['url'].split('=')[-1],
                'title': title,
                'url': fiche['url'],
                'history': history if history else ["Aucun historique disponible."]
            })
            # Encodage pour la console Windows, en ignorant les caractères non supportés
            title_for_print = title.encode('cp1252', errors='replace').decode('cp1252')
            print(f"  ({i+1}/{len(fiches)}) Fiche traitée : {title_for_print}")
        else:
            print(f"  ({i+1}/{len(fiches)}) Fiche ignorée : {fiche['url']}")

    all_data.sort(key=lambda x: x['title'])

    output_data = {
        'last_updated_utc': datetime.now(timezone.utc).isoformat(),
        'fiches_count': len(all_data),
        'data': all_data
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\nScraping terminé. {len(all_data)} fiches valides ont été sauvegardées dans {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
