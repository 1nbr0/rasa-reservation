# Bot de Réservation de Restaurant 🍽️

Ce projet propose un bot de réservation pour un restaurant, permettant aux utilisateurs de réserver une table, de vérifier la disponibilité, d'obtenir un numéro de réservation, d'ajouter un commentaire, d'annuler une réservation, d'afficher des informations sur la réservation, de consulter les allergènes, de voir le menu du jour et d'accéder au menu complet.

## Fonctionnalités ⚙️

- [x] **Réserver une Table**

  - Permet aux utilisateurs de réserver une table en fournissant la date de réservation, le nombre de personnes, le nom de réservation et le numéro de téléphone.

- [x] **Vérifier la Disponibilité**

  - Vérifie la disponibilité des tables pour la date spécifiée.

- [x] **Obtenir un Numéro de Réservation**

  - Génère un numéro de réservation unique pour chaque réservation effectuée.

- [x] **Ajouter un Commentaire à la Réservation**

  - Permet aux utilisateurs d'ajouter un commentaire à leur réservation.

- [x] **Annuler une Réservation**

  - Permet d'annuler une réservation existante.

- [x] **Afficher Information Réservation et Modifier Commentaire**

  - Affiche les détails de la réservation et permet de modifier le commentaire associé.

- [x] **Obtenir la Liste des Allergènes**

  - Fournit une liste des allergènes présents dans les plats du restaurant.

- [x] **Obtenir le Menu du Jour**

  - Affiche le menu du jour proposé par le restaurant.

- [x] **Obtenir le Lien vers le Menu Complet**

  - Donne accès au menu complet du restaurant.

- [ ] **Intégration sur une Plateforme**
  - Le bot peut être intégré sur différentes plateformes de messagerie pour faciliter les réservations.

## Utilisation 📝

### Guide d'installation et d'utilisation de Rasa Chatbot

Ce guide explique comment installer Rasa localement et démarrer un chatbot avec des actions.

---

## Installation

### Prérequis

- Assurez-vous d'avoir Python 3.6 ou une version ultérieure installée sur votre système. Vous pouvez vérifier en exécutant la commande suivante :

```bash
python --version
```

### Création de l'environnement virtuel (optionnel mais recommandé)

```bash
python -m venv rasa_env
```

#### Activez l'environnement virtuel :

- Sur Windows :

```bash
rasa_env\Scripts\activate
```

- Sur macOS et Linux :

```bash
source rasa_env/bin/activate
```

### Installation de Rasa

```bash
pip install rasa
```

### Installation des dépendances supplémentaires pour les actions personnalisées

```bash
pip install rasa-sdk
```

---

## Utilisation

### Entraînement du modèle

```bash
rasa train
```

### Lancement du serveur d'actions

```bash
rasa run actions
```

### Utilisation du chatbot

```bash
rasa shell
```
