
# Veille Documentaire INRS Metropol

Ce projet a pour but de suivre automatiquement les mises à jour des fiches "Metropol" publiées par l'INRS (Institut National de Recherche et de Sécurité).

Le site web généré est visible ici : [https://nethanel1.github.io/INRS-MetroPol-Veille/](https://nethanel1.github.io/INRS-MetroPol-Veille/)

## Fonctionnement

Le projet est composé de trois parties principales :

1.  **Un scraper en Python** (`/scraper/scraper.py`) : Ce script visite le site de l'INRS, récupère la liste de toutes les fiches Metropol, puis extrait l'historique de chacune. Le tout est compilé dans un unique fichier `docs/data.json`.

2.  **Un site web statique** (`/docs`) : Une simple page HTML, stylisée avec Bootstrap, qui lit le fichier `data.json` et affiche les informations de manière claire et consultable, avec une fonction de recherche.

3.  **Une automatisation via GitHub Actions** (`/.github/workflows/scrape_data.yml`) : Tous les jours à 2h du matin, GitHub exécute automatiquement le scraper. Si des modifications sont trouvées dans les données, le fichier `data.json` est mis à jour et sauvegardé dans le dépôt.

## Déploiement

Pour mettre en place votre propre version de ce projet :

1.  **Poussez ce code sur un nouveau dépôt GitHub.**

2.  **Activez GitHub Pages :**
    *   Allez dans les `Settings` (Paramètres) de votre dépôt.
    *   Naviguez vers la section `Pages` dans le menu de gauche.
    *   Sous `Build and deployment`, choisissez `Deploy from a branch`.
    *   Sélectionnez la branche `main` (ou `master`) et le dossier `/docs`.
    *   Cliquez sur `Save`.

3.  **Lancez le premier scraping manuellement :**
    *   Allez dans l'onglet `Actions` de votre dépôt.
    *   Cliquez sur `Scrape INRS Data` dans le menu de gauche.
    *   Cliquez sur le bouton `Run workflow`.

Après quelques minutes, votre site sera en ligne et à jour ! Il se mettra ensuite à jour automatiquement tous les jours.
