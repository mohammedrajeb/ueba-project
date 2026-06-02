# Grafana Dashboard — UEBA Security Project

> **Dashboard Name :** UEBA Security Dashboard
> **Data Source :** Elasticsearch · `http://elasticsearch:9200`
> **Index :** `ueba-alerts` · **Time Field :** `day`

---

## Objectif

Ce dashboard visualise les alertes **UEBA** (*User and Entity Behavior Analytics*) générées à partir du dataset *CERT r4.2 — Insider Threat*.

Il est connecté à **Elasticsearch** et consomme les données de l'index `ueba-alerts`, produites par le pipeline Python UEBA.

### Sources de données utilisées

| Source       | Rôle dans le projet                        |
|--------------|------------------------------------------|
| `logon.csv`  | Analyse des connexions et déconnexions   |
| `device.csv` | Analyse des événements USB               |
| `file.csv`   | Analyse des copies de fichiers           |
| `http.csv`   | Analyse de l'activité web                |
| `email.csv`  | Analyse de l'activité email              |
| `LDAP/`      | Enrichissement contextuel des utilisateurs|

### Étapes du pipeline

| Étape                    | Description                                                  |
|--------------------------|--------------------------------------------------------------|
| Feature Engineering      | Construction des variables comportementales                  |
| Rule-Based Scoring       | Calcul du score de risque par règles métier                  |
| Isolation Forest         | Détection d'anomalies non supervisée                         |
| TensorFlow Autoencoder   | Détection avancée d'anomalies par reconstruction             |
| Risk Analysis            | Calcul du score final et classification du niveau de risque  |
| LDAP Context Enrichment  | Ajout du département, de l'équipe et du superviseur          |
| Elasticsearch Indexing   | Indexation des alertes dans `ueba-alerts`                    |

---

## Source de données

```
Type       : Elasticsearch
URL Docker : http://elasticsearch:9200
URL locale : http://localhost:9200
Index      : ueba-alerts
Time Field : day
```

---

## Commande d'exécution du pipeline

La version complète du pipeline peut être exécutée avec :

```bash
python -m src.main \
  --sample-size 10000 \
  --include-http \
  --include-email \
  --include-ldap \
  --use-autoencoder \
  --send-to-elasticsearch
```

Résultat obtenu lors du dernier test complet :

```
Final results shape  : (4816, 50)
Alerts shape         : (1704, 50)
Indexed into         : ueba-alerts  →  1704 alertes
```

---

## Panels du Dashboard

### 1 · Total Alerts

Affiche le **nombre total** d'alertes UEBA indexées dans Elasticsearch.

```
Visualization : Stat
Lucene Query  : *
Metric        : Count
Group by      : Date Histogram on day
Calculation   : Total
```

```
Valeur obtenue (10 000 lignes/fichier) :  1 704 alertes
```

---

### 2 · Critical Alerts

Affiche le nombre d'alertes classifiées comme **critiques**.

```lucene
risk_level.keyword:critical
```

```
Visualization : Stat
Metric        : Count
Group by      : Date Histogram on day
Calculation   : Total
```

---

### 3 · Alerts by Risk Level

Affiche la distribution des alertes par **niveau de risque**.

```
Visualization : Bar gauge
Metric        : Count
Group by      : Terms aggregation on risk_level.keyword
Order         : Top
Order by      : Count
Size          : 10
```

| Niveau       | Description                        |
|--------------|------------------------------------|
| `low`        | Comportement légèrement inhabituel |
| `medium`     | Activité suspecte modérée          |
| `high`       | Comportement à risque élevé        |
| `critical`   | Comportement fortement suspect     |

---

### 4 · Top Risky Users

Identifie les **utilisateurs** générant le plus grand nombre d'alertes.

```
Visualization : Bar gauge
Lucene Query  : *
Metric        : Count
Group by      : Terms aggregation on user.keyword
Order         : Top
Order by      : Count
Size          : 10
```

> Ce panel permet de repérer rapidement les utilisateurs présentant un comportement suspect récurrent.

---

### 5 · Recent Alerts

Table détaillée des alertes UEBA, **triée par score de risque décroissant**.

| Colonne           | Description                            |
|-------------------|----------------------------------------|
| `Day`             | Date de l'alerte                       |
| `User`            | Identifiant de l'utilisateur           |
| `Risk Score`      | Score numérique final                  |
| `Risk Level`      | Niveau de risque classifié             |
| `Alert Reason`    | Explication de l'alerte                |
| `Rule Score`      | Score issu des règles métier           |
| `Is Anomaly`      | Détection Isolation Forest             |
| `Anomaly Score`   | Score brut du modèle Isolation Forest  |

La table applique une mise en forme conditionnelle selon le `Risk Score` et le `Risk Level`, avec mise en évidence des alertes critiques.

---

### 6 · Alerts by Department

Affiche les **départements** générant le plus d'alertes, via l'enrichissement LDAP.

```
Visualization : Bar gauge
Lucene Query  : *
Metric        : Count
Group by      : Terms aggregation on department.keyword
Order         : Top
Order by      : Count
Size          : 10
```

Exemples de départements affichés :

```
FieldService · Sales · Assembly · Engineering · Security · SoftwareManagement · Research
```

---

### 7 · Top Supervisors by Alerts

Affiche les **superviseurs** associés aux utilisateurs générant le plus d'alertes.

```
Visualization : Bar gauge
Lucene Query  : *
Metric        : Count
Group by      : Terms aggregation on supervisor.keyword
Order         : Top
Order by      : Count
Size          : 10
```

> Ce panel aide à contextualiser les alertes dans la structure managériale de l'organisation.

---

### 8 · TensorFlow Autoencoder Anomalies

Affiche le nombre d'alertes détectées comme anomalies par le modèle **TensorFlow Autoencoder**.

```lucene
autoencoder_is_anomaly:[1 TO 1]
```

```
Visualization : Stat
Metric        : Count
Group by      : Date Histogram on day
Calculation   : Total
```

```
Valeur obtenue lors du dernier test :  97 anomalies Autoencoder
```

---

### 9 · Alerts with Email Activity

Affiche le nombre d'alertes contenant une **activité email**.

```lucene
email_events:[1 TO *]
```

```
Visualization : Stat
Metric        : Count
Group by      : Date Histogram on day
Calculation   : Total
```

```
Valeur obtenue lors du dernier test :  366 alertes avec activité email
```

---

## Champs disponibles dans Elasticsearch

Les documents indexés dans `ueba-alerts` contiennent les champs suivants :

### Champs de base

| Champ          | Description                        |
|----------------|------------------------------------|
| `user`         | Identifiant de l'utilisateur       |
| `day`          | Date de l'alerte                   |
| `risk_score`   | Score de risque final (0–100)      |
| `risk_level`   | Niveau de risque classifié         |
| `alert_reason` | Raison déclenchant l'alerte        |
| `rule_score`   | Score issu des règles métier       |
| `rule_reasons` | Détail des règles déclenchées      |

### Champs Isolation Forest

| Champ                  | Description                        |
|------------------------|------------------------------------|
| `anomaly_prediction`   | `-1` si comportement anormal       |
| `anomaly_score`        | Score d'anomalie brut              |
| `is_anomaly`           | `1` si anomalie détectée           |

### Champs TensorFlow Autoencoder

| Champ                           | Description                            |
|---------------------------------|----------------------------------------|
| `autoencoder_reconstruction_error` | Erreur de reconstruction            |
| `autoencoder_threshold`         | Seuil de détection                     |
| `autoencoder_is_anomaly`        | `1` si anomalie Autoencoder détectée   |

### Champs HTTP

| Champ               | Description                              |
|---------------------|------------------------------------------|
| `http_events`       | Nombre total d'événements web            |
| `http_outside_hours`| Activité web hors horaires               |
| `unique_urls`       | Nombre d'URLs uniques visitées           |
| `unique_domains`    | Nombre de domaines uniques               |
| `unique_http_pcs`   | Nombre de postes avec activité web       |

### Champs Email

| Champ                    | Description                              |
|--------------------------|------------------------------------------|
| `email_events`           | Nombre total d'emails                    |
| `email_outside_hours`    | Emails hors horaires                     |
| `total_email_size`       | Volume total des emails                  |
| `avg_email_size`         | Taille moyenne des emails                |
| `total_attachments`      | Nombre total de pièces jointes           |
| `emails_with_attachments`| Emails contenant des pièces jointes      |
| `to_recipients_count`    | Nombre de destinataires directs          |
| `cc_recipients_count`    | Nombre de destinataires en copie         |
| `bcc_recipients_count`   | Nombre de destinataires en copie cachée  |
| `unique_email_pcs`       | Nombre de postes avec activité email     |

### Champs LDAP

| Champ               | Description                              |
|---------------------|------------------------------------------|
| `employee_name`     | Nom complet de l'employé                 |
| `role`              | Rôle dans l'organisation                 |
| `position`          | Poste occupé                             |
| `business_unit`     | Unité commerciale                        |
| `functional_unit`   | Unité fonctionnelle                      |
| `department`        | Département                              |
| `team`              | Équipe                                   |
| `supervisor`        | Superviseur direct                       |
| `ldap_source_file`  | Fichier LDAP source                      |

---

## Export du Dashboard

Le dashboard a été exporté depuis Grafana et sauvegardé dans le projet :

```
dashboards/grafana_dashboard.json
```

Ce fichier permet de restaurer ou partager le dashboard Grafana.

---

## Statut actuel

Le dashboard est **fonctionnel et enrichi**. Il couvre :

- [x] Volumétrie globale des alertes
- [x] Alertes critiques
- [x] Répartition par niveau de risque
- [x] Utilisateurs les plus risqués
- [x] Table des alertes détaillées
- [x] Répartition par département (LDAP)
- [x] Superviseurs associés aux alertes (LDAP)
- [x] Anomalies TensorFlow Autoencoder
- [x] Alertes avec activité email

Cette version correspond au **dashboard final** du projet UEBA.

---

*Généré dans le cadre du projet UEBA — EMSI 4CIR Anfa*