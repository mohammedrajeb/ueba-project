# Données brutes — CERT Insider Threat r4.2

Ce dossier est réservé aux données brutes du dataset CERT Insider Threat utilisé par le projet UEBA.

> Le dataset brut **n'est pas inclus** dans ce dépôt en raison de sa taille importante.
> Il doit être téléchargé manuellement depuis la page officielle CMU/KiltHub.

---

## Source du dataset

| Champ        | Détails                                                                                                                                             |
|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| Fournisseur  | Carnegie Mellon University (CERT)                                                                                                                   |
| Lien de téléchargement | [kilthub.cmu.edu — Insider Threat Test Dataset](https://kilthub.cmu.edu/articles/dataset/Insider_Threat_Test_Dataset/12841247?file=24856766) |

---

## Fichier à télécharger

| Champ          | Valeur                             |
|----------------|------------------------------------|
| Nom            | `r4.2.tar`                         |
| Format         | `.bz2`                             |
| Taille         | 4,49 Go                            |
| Somme MD5      | `cf64caa378acb77cd0c608a5576d998c` |

---

## Structure locale attendue

Après téléchargement et extraction, placer les fichiers dans ce dossier selon la structure suivante :

```text
data/raw/
├── logon.csv
├── device.csv
├── file.csv
├── http.csv
├── email.csv
├── psychometric.csv
├── LDAP/
│   ├── 2009-12.csv
│   ├── 2010-01.csv
│   ├── ...
│   └── 2011-05.csv
├── license.txt
└── readme.txt
```

---

## Remarques importantes

- Le dataset brut est intentionnellement exclu de Git via `.gitignore` en raison de la taille importante de certains fichiers comme `http.csv`.
- Seuls le code du projet, les résultats traités, les modèles entraînés, les rapports, les figures, les notebooks et les fichiers du dashboard sont versionnés sur GitHub.
- **Ne pas committer les fichiers du dataset brut dans le dépôt.**