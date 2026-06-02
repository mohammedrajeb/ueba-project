# Rapport analytique — Projet UEBA

## 1. Introduction

Ce rapport présente le développement d'une plateforme UEBA destinée à détecter des comportements suspects à partir de logs utilisateurs et systèmes.

## 2. Contexte

Les menaces internes sont difficiles à détecter car elles impliquent souvent des comptes légitimes.

Une approche UEBA permet d'analyser le comportement normal des utilisateurs et de détecter les écarts pouvant indiquer une compromission ou un abus.

## 3. Dataset utilisé

Le projet utilise le dataset CERT Insider Threat r4.2.

Les fichiers principaux utilisés sont :

- logon.csv
- device.csv
- file.csv
- http.csv
- email.csv

Dans la première version du projet, les fichiers prioritaires sont :

- logon.csv
- device.csv
- file.csv

## 4. Architecture proposée

Logs → Preprocessing → Feature Engineering → Rule Engine → AI Model → Risk Analyzer → Alerts → Dashboard

## 5. Méthodologie

À compléter.

## 6. Modèle IA

Le modèle principal prévu est Isolation Forest.

Un modèle avancé basé sur un Autoencoder TensorFlow pourra être ajouté dans une deuxième phase.

## 7. Résultats

À compléter.

## 8. Limites et améliorations

À compléter.