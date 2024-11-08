# Cloud Drive App

## Description
Cloud Drive App est une application web développée avec Django qui permet aux utilisateurs de gérer et stocker leurs fichiers dans un espace de stockage personnel en ligne.

## Prérequis
Avant de commencer, il faut s'assurer d'avoir les éléments suivants installés sur votre système :
- Python 3.12
- pip (le gestionnaire de paquets de Python)
- virtualenv (pour créer un environnement virtuel isolé)

## Dépendances
Les dépendances à installer seront téléchargées en suivants les intructions d'installation. Parmi elles se trouve le framework web Django qui a permis le développement de l'application web en python.

## Installation

### Cloner le projet
Tout d'abord, il faut cloner le dépôt du projet avec le lien https://github.com/BenjaminCIR/Cloud-Drive-App (ou décompressez le dossier zip qui contient le code source) :

git clone https://github.com/BenjaminCIR/Cloud-Drive-App.git

Puis mettez le chemin vers l'emplacement du dossier dans votre terminal :

cd Cloud-Drive-App

### Créer et activer un environnement virtuel
Créez votre environnement virtuel en utilisant la commande :
python -m venv venv

Puis activez le :
Sur Linux : source venv/bin/activate
Sur Windows : .\venv\Scripts\activate

### Installer les dépendances
Installez les dépendances requises par le projet en utilisant le fichier "requirements.txt". Cela permettra de configurer toutes les bibliothèques nécessaires pour faire fonctionner l'application.

Assurez-vous que vous êtes toujours dans l’environnement virtuel, puis exécutez la commande suivante :

pip install -r requirements.txt

### Configurer la base de données
Avant de lancer l'application, vous devez configurer la base de données en appliquant les migrations pour créer les tables nécessaires en vous rendant dans le dossier cloud_app :
cd cloud_app

puis en faisant la commande suivante :
python manage.py migrate

### Lancer l'application
Pour tester l'application, il faut démarrer le serveur :
python manage.py runserver

L'application sera alors disponible à l'adresse http://127.0.0.1:8000/polls

## Fonctionnalités
A l'arrivée sur l'application, vous serez automatiquement redirigés vers la page de connexion s'il s'agit de votre première connexion. Vous pouvez alors créer un compte puis vous connecter.
Attention, le mot de passe de votre compte doit contenir au moins 8 caractères, des lettres et des chiffres et ne doit pas être trop ressemblant à votre nom d'utilisateur.

Lorsque vous êtes connecté, vous avez accès aux fonctionnalités de gestion de fichiers et dossiers suivantes :
- Création de dossiers
- Téléchargement de fichiers
- Suppression
- Déplacement
- Modification du nom des fichiers et dossiers
