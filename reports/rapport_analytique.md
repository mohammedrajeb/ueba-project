# Rapport Analytique — Projet UEBA

> **Plateforme :** User and Entity Behavior Analytics  
> **Dataset :** CERT Insider Threat r4.2  
> **Stack :** Python · Elasticsearch · Grafana - TensorFlow

---

## 1. Introduction

Ce projet consiste à développer une plateforme UEBA destinée à détecter des comportements suspects à partir de logs utilisateurs et systèmes.

L'objectif principal est d'identifier des signaux pouvant révéler une menace interne, un compte compromis, une activité anormale ou une tentative d'exfiltration de données.

Contrairement à une détection classique basée uniquement sur des signatures connues, l'approche UEBA repose sur l'analyse du comportement des utilisateurs et des entités. Le système cherche à comprendre ce qui est habituel, puis à faire ressortir les comportements qui s'éloignent de cette normalité.

Dans ce projet, la plateforme analyse les logs du dataset CERT r4.2, construit des indicateurs comportementaux, applique un moteur de règles, utilise un modèle d'intelligence artificielle de type Isolation Forest, puis génère des alertes consultables dans Elasticsearch et Grafana.

---

## 2. Objectifs du projet

Les objectifs principaux du projet sont les suivants :

- Collecter et analyser des logs issus du dataset CERT r4.2
- Transformer les logs bruts en variables comportementales exploitables
- Détecter des comportements suspects liés aux connexions, aux périphériques USB et aux copies de fichiers
- Construire un moteur de règles explicable
- Intégrer un modèle d'intelligence artificielle non supervisé
- Produire un score de risque final
- Exporter les alertes localement au format CSV
- Indexer les alertes dans Elasticsearch
- Visualiser les résultats dans un dashboard Grafana

Le projet répond aux trois livrables attendus : un moteur UEBA, un dashboard de supervision et un rapport analytique.

---

## 3. Dataset utilisé

Le projet utilise le dataset **CERT Insider Threat r4.2**, qui simule l'activité d'utilisateurs dans une organisation et contient plusieurs types de logs :

| Fichier              | Contenu                                              |
|----------------------|------------------------------------------------------|
| `logon.csv`          | Événements de connexion et déconnexion               |
| `device.csv`         | Événements liés aux périphériques USB                |
| `file.csv`           | Copies de fichiers vers supports amovibles           |
| `http.csv`           | Navigation web                                       |
| `email.csv`          | Activité email                                       |
| `psychometric.csv`   | Scores psychométriques Big Five                      |
| Dossiers LDAP        | Informations organisationnelles sur les utilisateurs |

Dans cette première version, trois fichiers ont été utilisés en priorité : `logon.csv`, `device.csv` et `file.csv`. Ce choix permet de construire un moteur UEBA initial centré sur les scénarios les plus importants : connexions inhabituelles, usage USB suspect et copie de fichiers vers support amovible.

Les fichiers `http.csv`, `email.csv`, `psychometric.csv` et LDAP sont conservés pour des enrichissements futurs.

---

## 4. Architecture générale

Le pipeline suit le flux de traitement suivant :

```
Logs CERT r4.2
      ↓
Prétraitement
      ↓
Feature Engineering
      ↓
Rule Engine
      ↓
Isolation Forest
      ↓
Risk Analyzer
      ↓
Alertes CSV
      ↓
Elasticsearch
      ↓
Dashboard Grafana
```

Le projet est organisé en plusieurs modules Python :

| Module                      | Rôle                                              |
|-----------------------------|---------------------------------------------------|
| `load_data.py`              | Lecture sécurisée des fichiers CSV                |
| `preprocessing.py`          | Transformation des dates et extraction temporelle |
| `feature_engineering.py`    | Création des variables comportementales           |
| `rule_engine.py`            | Calcul du score de risque par règles              |
| `isolation_forest_model.py` | Détection d'anomalies par IA                      |
| `risk_analyzer.py`          | Calcul du score de risque final                   |
| `elastic_connector.py`      | Envoi des alertes vers Elasticsearch              |
| `main.py`                   | Point d'entrée principal du pipeline              |

---

## 5. Prétraitement des logs

Le prétraitement transforme les logs bruts en données exploitables. Les étapes principales sont :

1. Conversion de la colonne `date` en format datetime
2. Extraction du jour
3. Extraction de l'heure
4. Extraction du mois
5. Extraction du jour de la semaine
6. Détection des weekends
7. Détection des activités hors horaires de travail

Les horaires de travail ont été définis entre **7h et 20h**. Une activité en dehors de cette plage est marquée comme activité hors horaires.

Les nouvelles colonnes produites sont : `day`, `hour`, `month`, `weekday`, `is_weekend`, `outside_working_hours`.

---

## 6. Feature Engineering

Le feature engineering transforme les événements bruts en indicateurs comportementaux agrégés par utilisateur et par jour.

```
Unité d'analyse :  user + day
```

### 6.1 Features issues de `logon.csv`

| Variable              | Description                                      |
|-----------------------|--------------------------------------------------|
| `logon_events`        | Nombre de connexions                             |
| `logoff_events`       | Nombre de déconnexions                           |
| `logon_outside_hours` | Connexions/déconnexions hors horaires            |
| `unique_logon_pcs`    | Nombre de postes différents utilisés             |

### 6.2 Features issues de `device.csv`

| Variable                 | Description                                   |
|--------------------------|-----------------------------------------------|
| `usb_events`             | Nombre total d'événements USB                 |
| `usb_connect_events`     | Nombre de connexions de périphériques         |
| `usb_disconnect_events`  | Nombre de déconnexions de périphériques       |
| `usb_outside_hours`      | Événements USB hors horaires                  |
| `unique_usb_pcs`         | Nombre de postes avec activité USB            |

### 6.3 Features issues de `file.csv`

| Variable                  | Description                                  |
|---------------------------|----------------------------------------------|
| `file_copy_events`        | Nombre de fichiers copiés                    |
| `file_copy_outside_hours` | Copies de fichiers hors horaires             |
| `unique_files_copied`     | Nombre de fichiers uniques copiés            |
| `unique_file_pcs`         | Nombre de postes utilisés pour les copies    |

---

## 7. Moteur de règles UEBA

Le moteur de règles constitue la première couche de détection. Il applique des règles simples, explicables et compréhensibles. Chaque règle ajoute un certain nombre de points au score de risque.

Les règles principales sont :

- Activité de connexion hors horaires
- Utilisation de périphérique USB
- Utilisation USB hors horaires
- Volume élevé de copies de fichiers
- Copie de fichiers hors horaires
- Utilisation de plusieurs postes
- Combinaison dangereuse entre connexion hors horaires, USB et copie de fichiers

Le moteur produit deux colonnes :

| Colonne         | Description                                        |
|-----------------|----------------------------------------------------|
| `rule_score`    | Niveau de risque détecté par les règles            |
| `rule_reasons`  | Explication du comportement jugé suspect           |

Cette approche est importante car elle rend la détection **interprétable**, ce qui est essentiel dans un contexte de cybersécurité.

---

## 8. Modèle IA — Isolation Forest

Le modèle utilisé est **Isolation Forest**, un modèle non supervisé de détection d'anomalies. Il est adapté au contexte UEBA car les comportements malveillants sont rares par rapport aux comportements normaux.

Le paramètre `contamination` a été fixé à **0.02**, soit environ 2 % d'anomalies attendues dans les données.

Les colonnes ajoutées par le modèle sont :

| Colonne               | Description                                         |
|-----------------------|-----------------------------------------------------|
| `anomaly_prediction`  | `-1` si le comportement est considéré anormal       |
| `anomaly_score`       | Score d'anomalie brut                               |
| `is_anomaly`          | `1` si une anomalie a été détectée                  |

---

## 9. Risk Analyzer

Le Risk Analyzer combine les résultats du moteur de règles et du modèle Isolation Forest pour produire un score de risque final.

Le score est calculé à partir du `rule_score`. Si le modèle IA détecte une anomalie, un bonus de risque est ajouté. Le score final est plafonné à **100**.

### Classification des niveaux de risque

| Score      | Niveau     |
|------------|------------|
| 0 à 30     | `low`      |
| 31 à 60    | `medium`   |
| 61 à 80    | `high`     |
| 81 à 100   | `critical` |

Les colonnes produites sont :

| Colonne        | Description                                              |
|----------------|----------------------------------------------------------|
| `risk_score`   | Score de risque final (0–100)                            |
| `risk_level`   | Niveau de risque classifié                               |
| `alert_reason` | Raison combinée issues des règles et de la détection IA  |

---

## 10. Résultats obtenus

### Échantillon 10 000 lignes par fichier

| Métrique                           | Valeur  |
|------------------------------------|---------|
| Comportements utilisateur/jour     |   4 816 |
| Alertes générées (`risk_score > 0`)|   1 691 |

Distribution des niveaux de risque :

| Niveau de risque | Nombre  |
|------------------|--------:|
| `low`            |   4 425 |
| `medium`         |     289 |
| `high`           |      42 |
| `critical`       |      60 |

### Échantillon 50 000 lignes par fichier

| Métrique                          | Valeur  |
|-----------------------------------|---------|
| Comportements utilisateur/jour    |  23 069 |
| Alertes générées                  |   8 464 |

Ces résultats montrent que le pipeline est capable de traiter un volume plus important de logs tout en conservant une structure d'analyse cohérente.

---

## 11. Export et indexation Elasticsearch

Le pipeline exporte deux fichiers locaux :

```
data/processed/ueba_features.csv   →  Tous les comportements analysés
data/alerts/alerts.csv             →  Comportements avec risk_score > 0
```

Les alertes sont ensuite envoyées vers Elasticsearch dans l'index `ueba-alerts`.

Les champs indexés sont :

| Champ           | Description                          |
|-----------------|--------------------------------------|
| `user`          | Identifiant de l'utilisateur         |
| `day`           | Date de l'alerte                     |
| `risk_score`    | Score numérique de risque            |
| `risk_level`    | Niveau de risque classifié           |
| `alert_reason`  | Raison déclenchant l'alerte          |
| `rule_score`    | Score issu des règles métier         |
| `is_anomaly`    | Booléen — détection Isolation Forest |
| `anomaly_score` | Score d'anomalie brut                |

Une vérification via l'API Elasticsearch a confirmé **1 691 documents** indexés après exécution du pipeline sur 10 000 lignes par fichier.

---

## 12. Dashboard Grafana

Un dashboard Grafana a été créé pour visualiser les alertes UEBA. Il est connecté à Elasticsearch via l'index `ueba-alerts`.

| Panel                  | Description                                                  |
|------------------------|--------------------------------------------------------------|
| Total Alerts           | Nombre total d'alertes indexées                              |
| Critical Alerts        | Alertes classifiées comme critiques (`risk_level: critical`) |
| Alerts by Risk Level   | Distribution des alertes par niveau de risque                |
| Top Risky Users        | Utilisateurs ayant généré le plus d'alertes                  |
| Recent Alerts          | Table détaillée triée par score de risque décroissant        |

Le dashboard a été exporté dans :

```
dashboards/grafana_dashboard.json
```

---

## 13. Limites du projet

| Limite                  | Description                                                                                                                            |
|-------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| Couverture des logs     | Seuls `logon.csv`, `device.csv` et `file.csv` sont traités ; les logs HTTP, email, LDAP et psychométriques ne sont pas encore intégrés |
| Règles manuelles        | Le scoring par règles est compréhensible mais peut produire des faux positifs                                                          |
| Modèle non supervisé    | Isolation Forest détecte des comportements rares, mais un comportement rare n'est pas systématiquement malveillant                     |
| Validation partielle    | Les résultats ont été validés sur des échantillons ; un traitement complet pourrait nécessiter des optimisations                       | 
| Données psychométriques | Le fichier `psychometric.csv` n'a pas été utilisé pour éviter une approche sensible sur le plan éthique                                |

---

## 14. Conclusion

Ce projet a permis de construire une plateforme UEBA complète et fonctionnelle.

Le moteur développé est capable de charger des logs, les prétraiter, construire des variables comportementales, appliquer un moteur de règles, utiliser un modèle IA de détection d'anomalies, calculer un score de risque final et générer des alertes exportables et visualisables.

Cette première version constitue une base solide pour un système UEBA plus avancé, qui pourra être enrichi avec des logs HTTP, emails, LDAP et des modèles IA supplémentaires.

---