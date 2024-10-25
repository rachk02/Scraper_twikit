import asyncio
import json
import csv
import os
from twikit import Client
import configparser  # Pour lire le fichier config.ini

# Charger le fichier config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Récupérer les informations du fichier de configuration
USERNAME = config['AUTH']['username']
EMAIL = config['AUTH']['email']
PASSWORD = config['AUTH']['password']
QUERY = config['SEARCH']['query']

CSV_FILE = config['FILES']['csv_file']
JSON_FILE = config['FILES']['json_file']
COOKIE_FILE = config['FILES']['cookie_file']

# Initialiser le client
client = Client('en-US')

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
    await client.login(
        auth_info_1=USERNAME,
        auth_info_2=EMAIL,
        password=PASSWORD
    )
    await save_cookies()

async def search_and_save_tweets():
    """Recherche de tweets et sauvegarde en CSV et JSON."""
    print("Recherche en cours...")

    tweets = await client.search_tweet(QUERY, result_type='Latest', limit=500)

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
    await login()
    await search_and_save_tweets()

if __name__ == "__main__":
    asyncio.run(main())
