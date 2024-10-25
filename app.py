import asyncio
import json
import csv
import os
import signal
from twikit import Client, TooManyRequests  # Gestion des erreurs API
import configparser

# Charger le fichier config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Récupérer les informations depuis config.ini
USERNAME = config['AUTH']['username']
EMAIL = config['AUTH']['email']
PASSWORD = config['AUTH']['password']
QUERY = config['SEARCH']['query']
CSV_FILE = config['FILES']['csv_file']
JSON_FILE = config['FILES']['json_file']
COOKIE_FILE = config['FILES']['cookie_file']

# Initialiser le client Twikit
client = Client('en-US')

# Variable pour détecter une demande d'arrêt propre
stop_event = asyncio.Event()

def handle_exit_signal(signal_number, frame):
    """Gère l'interruption par Ctrl+C."""
    print("\nInterruption détectée. Arrêt en cours...")
    stop_event.set()

# Enregistrer les signaux pour gérer Ctrl+C
signal.signal(signal.SIGINT, handle_exit_signal)
signal.signal(signal.SIGTERM, handle_exit_signal)

async def save_cookies():
    """Sauvegarde des cookies dans un fichier JSON."""
    cookies = await client.get_cookies()
    with open(COOKIE_FILE, 'w') as f:
        json.dump(cookies, f)

async def load_cookies():
    """Chargement des cookies depuis un fichier JSON."""
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, 'r') as f:
            cookies = json.load(f)
        await client.set_cookies(cookies)

async def login():
    """Connexion avec gestion des cookies."""
    await load_cookies()
    try:
        await client.login(auth_info_1=USERNAME, auth_info_2=EMAIL, password=PASSWORD)
        await save_cookies()
        print("Connexion réussie.")
    except Exception as e:
        print(f"Erreur lors de la connexion : {e}")
        raise

async def search_and_save_tweets():
    """Recherche de tweets avec gestion des erreurs et progression."""
    print("Recherche en cours...")

    tweets = []
    retries = 0  # Nombre de tentatives en cas de TooManyRequests

    try:
        # Limiter à 1000 tweets
        async for tweet in client.search_tweet(QUERY, result_type='Latest', limit=1000):
            tweets.append(tweet)

            # Afficher le nombre de tweets récupérés en temps réel
            print(f"Tweets récupérés : {len(tweets)}")

            # Vérifier si une interruption est demandée
            if stop_event.is_set():
                print("\nArrêt demandé par l'utilisateur.")
                break

            # Pause entre les requêtes pour éviter la limite de l'API
            await asyncio.sleep(1)

    except TooManyRequests:
        if retries < 5:  # Maximum de 5 tentatives
            retries += 1
            wait_time = 2 ** retries  # Backoff exponentiel (2, 4, 8, etc.)
            print(f"Trop de requêtes. Nouvelle tentative dans {wait_time} secondes...")
            await asyncio.sleep(wait_time)  # Attendre avant de réessayer
            return await search_and_save_tweets()  # Relancer la recherche
        else:
            print("Échec après trop de tentatives. Veuillez réessayer plus tard.")
    except Exception as e:
        print(f"Erreur lors de la recherche de tweets : {e}")

    # Sauvegarder les tweets récupérés
    save_tweets_as_json(tweets)
    save_tweets_as_csv(tweets)

def save_tweets_as_json(tweets):
    """Enregistre les tweets au format JSON."""
    data = [
        {
            'author': tweet.user.name,
            'text': tweet.text,
            'created_at': tweet.created_at
        }
        for tweet in tweets
    ]
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Les tweets ont été enregistrés dans {JSON_FILE}.")

def save_tweets_as_csv(tweets):
    """Enregistre les tweets au format CSV."""
    with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Auteur', 'Texte', 'Date de création'])
        for tweet in tweets:
            writer.writerow([tweet.user.name, tweet.text, tweet.created_at])
    print(f"Les tweets ont été enregistrés dans {CSV_FILE}.")

async def main():
    """Fonction principale pour orchestrer le processus."""
    try:
        await login()
        await search_and_save_tweets()
    except Exception as e:
        print(f"Erreur dans le programme principal : {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgramme interrompu par l'utilisateur.")
