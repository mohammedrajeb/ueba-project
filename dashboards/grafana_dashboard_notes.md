# 📊 Grafana Dashboard — UEBA Security Project

> **Dashboard Name :** UEBA Security Dashboard  
> **Data Source :** Elasticsearch · `http://elasticsearch:9200`  
> **Index :** `ueba-alerts` · **Time Field :** `day`

---

## 🎯 Objectif

Ce dashboard visualise les alertes **UEBA** (*User and Entity Behavior Analytics*) générées à partir du dataset *CERT r4.2 — Insider Threat*.

Il est connecté à **Elasticsearch** et consomme les données de l'index `ueba-alerts`, produites par le pipeline Python UEBA via les étapes suivantes :

| Étape                   | Description                                      |
|-------------------------|--------------------------------------------------|
| Feature Engineering | Construction des features comportementales           |
| Rule-Based Scoring  | Calcul du score de risque par règles métier          |
| Isolation Forest    | Détection d'anomalies non supervisée                 |
| Risk Analysis       | Analyse finale et classification du niveau de risque |

---

## 🗄️ Source de données

```
Type      :  Elasticsearch
URL       :  http://elasticsearch:9200
Index     :  ueba-alerts
Time Field:  day
```

---

## 📋 Panels du Dashboard

### 1 · Total Alerts

Affiche le **nombre total** d'alertes UEBA indexées dans Elasticsearch.

```
Valeur attendue (10 000 lignes/fichier) :  1 691 alertes
```

---

### 2 · Critical Alerts

Affiche le nombre d'alertes classifiées comme **critiques**.

```lucene
risk_level.keyword:critical
```

```
Valeur attendue :  60 alertes critiques
```

---

### 3 · Alerts by Risk Level

Distribution des alertes par **niveau de risque**, via une agrégation Elasticsearch.

```
Agrégation : Terms aggregation sur risk_level.keyword
```

Niveaux disponibles :

| Niveau        | Description                           |
|---------------|---------------------------------------|
| 🟢 `low`      | Comportement légèrement inhabituel   |
| 🟡 `medium`   | Activité suspecte modérée            |
| 🔴 `high`     | Comportement à risque élevé          |
| ⚫ `critical` | Menace interne potentielle confirmée |

---

### 4 · Top Risky Users

Identifie les **utilisateurs** générant le plus grand nombre d'alertes.

```
Agrégation : Terms aggregation sur user.keyword
```

> Ce panel permet de repérer rapidement les utilisateurs présentant un comportement suspect récurrent.

---

### 5 · Recent Alerts *(Table)*

Table détaillée des alertes UEBA les plus récentes, **triée par score de risque décroissant**.

| Colonne        | Description                              |
|----------------|------------------------------------------|
| `Day`          | Date de l'alerte                         |
| `User`         | Identifiant de l'utilisateur             |
| `Risk Score`   | Score numérique de risque                |
| `Risk Level`   | Niveau de risque classifié               |
| `Alert Reason` | Raison déclenchant l'alerte              |
| `Rule Score`   | Score issu des règles métier             |
| `Is Anomaly`   | Booléen — détection Isolation Forest     |
| `Anomaly Score`| Score d'anomalie brut                    |

---

## 💾 Export du Dashboard

Le dashboard a été exporté depuis Grafana et sauvegardé dans le projet :

```
dashboards/grafana_dashboard.json
```

---

## ✅ Statut actuel

Le dashboard initial est **fonctionnel** et inclut l'ensemble des panels requis pour le livrable du projet UEBA.
