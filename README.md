## Documentation du Projet de Collecte de Tweets

### Table des Matières
1. [Description du Projet](#description-du-projet)
2. [Prérequis](#prérequis)
3. [Étapes de Clonage et Installation](#etapes-de-clonage-et-installation)
4. [Fichier de Configuration (`config.ini`)](#fichier-de-configuration-configini)
5. [Dépendances (`requirements.txt`)](#dépendances-requirementstxt)
6. [Description des Fonctions Principales](#description-des-fonctions-principales)

---

### 1. Description du Projet

Ce projet est un script Python asynchrone qui permet de récupérer des tweets associés à des mots-clés spécifiques sur l'Université Virtuelle du Burkina Faso (UVBF). Les tweets sont sauvegardés en format CSV et JSON pour une analyse ultérieure. 

Le script utilise la bibliothèque `httpx` pour gérer les requêtes asynchrones et `twikit` pour interagir avec l'API de Twitter.

### 2. Prérequis

- **Python 3.7+**
- **Connexion Internet** pour accéder à l'API de Twitter
- **Compte et accès à l'API Twitter** (les identifiants doivent être fournis)

---

### 3. Étapes de Clonage et Installation

Suivez ces étapes pour configurer et exécuter le projet :

1. **Cloner le dépôt** :
   ```bash
   git clone <URL_DU_DEPOT>
   cd <NOM_DU_DEPOT>
   ```

2. **Créer un environnement virtuel** (fortement recommandé) :
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Sur Linux/macOS
   venv\Scripts\activate     # Sur Windows
   ```

3. **Installer les dépendances** :
   Assurez-vous d’avoir créé un fichier `requirements.txt` avec le contenu fourni dans la section [Dépendances](#dépendances-requirementstxt) ci-dessous, puis exécutez :
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer le fichier `config.ini`** : Créez un fichier `config.ini` et configurez-le comme expliqué dans la section [Fichier de Configuration](#fichier-de-configuration-configini).

5. **Exécuter le script** :
   ```bash
   python app.py
   ```

---

### 4. Fichier de Configuration (`config.ini`)

Le fichier `config.ini` contient les informations de configuration nécessaires pour l'authentification, les paramètres de recherche et les fichiers de sortie.

**Exemple de `config.ini`** :

```ini
[AUTH]
username = your_username
email = your_email
password = your_password

[SEARCH]
query = (Université UVBF OR UVBF OR #UVBF OR "Université Virtuelle du Burkina Faso" OR "UV-BF" OR "UV BF" OR "UV_BF") lang:fr

[FILES]
csv_file = tweets_uvbf.csv
json_file = tweets_uvbf.json
cookie_file = cookies.json

[SETTINGS]
minimum_tweets = 500
max_inactivity_tries = 2
max_retry_timeout = 3
```

- **[AUTH]** : Les informations d'identification pour se connecter à l'API de Twitter.
- **[SEARCH]** : Les mots-clés pour la recherche Twitter.
- **[FILES]** : Les noms des fichiers de sortie pour les tweets en CSV et JSON, ainsi que le fichier de cookies pour l'authentification.
- **[SETTINGS]** : Les paramètres de la collecte, comme le nombre de tweets minimum, les tentatives maximales d’inactivité et les tentatives maximales en cas de `Timeout`.

---

### 5. Dépendances (`requirements.txt`)

Créez un fichier `requirements.txt` contenant les dépendances suivantes :

```text
asyncio
httpx
twikit
configparser
```

Installez ces dépendances avec la commande :
```bash
pip install -r requirements.txt
```

---

### 6. Description des Fonctions Principales

Le script est composé des fonctions suivantes, chacune ayant un rôle spécifique dans le processus de collecte des tweets.

#### `get_tweets(tweets, client, max_retries)`

- **Description** : Récupère des tweets en utilisant l'API de Twitter. En cas de `Timeout`, la fonction réessaie jusqu'à `max_retries` fois avant d'arrêter la recherche.
- **Arguments** :
  - `tweets` : Instance de tweets récupérés. Si `None`, une nouvelle requête de recherche est lancée.
  - `client` : Client Twitter authentifié.
  - `max_retries` : Nombre maximal de tentatives en cas de `Timeout`.
- **Retour** : Retourne les tweets récupérés ou lève une exception si `max_retries` est atteint.

#### `authenticate(client, config)`

- **Description** : Authentifie l'utilisateur en utilisant les identifiants dans `config.ini`. Si des cookies d'authentification existent, ils sont utilisés pour éviter une nouvelle connexion.
- **Arguments** :
  - `client` : Instance du client Twitter pour la connexion.
  - `config` : Fichier de configuration `config.ini` contenant les informations de connexion.

#### `save_to_csv(tweet_data, csv_file)`

- **Description** : Enregistre un tweet individuel dans le fichier CSV spécifié.
- **Arguments** :
  - `tweet_data` : Dictionnaire contenant les informations du tweet.
  - `csv_file` : Chemin du fichier CSV pour enregistrer les tweets.

#### `save_to_json(tweets_data, json_file)`

- **Description** : Enregistre tous les tweets récupérés dans un fichier JSON.
- **Arguments** :
  - `tweets_data` : Liste des dictionnaires de tweets.
  - `json_file` : Chemin du fichier JSON.

#### `fetch_tweets(client, config)`

- **Description** : Récupère les tweets jusqu'à atteindre le `minimum_tweets` spécifié ou le nombre maximum de tentatives d'inactivité (`max_inactivity_tries`). Effectue des sauvegardes intermédiaires en JSON après chaque lot de tweets récupérés.
- **Arguments** :
  - `client` : Instance du client Twitter pour la récupération des tweets.
  - `config` : Fichier de configuration `config.ini` contenant les paramètres de collecte et de fichiers.
- **Détails supplémentaires** :
  - Gère les exceptions `TooManyRequests` pour éviter de dépasser les limites de l'API.
  - Relance la récupération en cas de `Timeout`, dans la limite du nombre de tentatives défini.

#### `main()`

- **Description** : Fonction principale pour exécuter le programme.
- **Étapes** :
  1. Charge les paramètres depuis le fichier `config.ini`.
  2. Authentifie le client Twitter.
  3. Lance la collecte de tweets avec les paramètres définis.
  
---

### Exemple d'Exécution

Une fois la configuration et les installations terminées, vous pouvez exécuter le script. Voici un exemple de sortie :

```plaintext
2024-10-25 18:03:42.339857 - Cookies chargés avec succès.
2024-10-25 18:03:42.339914 - Initialisation de la recherche...
2024-10-25 18:04:05.068649 - 1 tweets récupérés.
...
2024-10-25 18:15:50.400104 - Sauvegarde intermédiaire des tweets en JSON.
2024-10-25 18:18:40.840868 - Recherche terminée. 500 tweets récupérés et sauvegardés.
```

---

### Notes Importantes

- **Gestion des Limites d'API** : En cas de `TooManyRequests`, le script attend jusqu'à la fin de la limite.
- **Interruption** : En cas d'arrêt manuel (Ctrl + C), le programme sauvegardera les tweets récupérés jusqu'à ce point.

Cette documentation vous permet de cloner, configurer, et exécuter le projet en toute autonomie, avec des paramètres de personnalisation dans `config.ini`.