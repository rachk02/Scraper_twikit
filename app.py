import asyncio
import httpx
from twikit import Client, TooManyRequests
from datetime import datetime
import csv
import json
from configparser import ConfigParser
from random import randint
import os

# Configuration globale
MINIMUM_TWEETS = 1000
CONFIG_FILE = 'config.ini'

async def get_tweets(tweets, client, max_retries=3):
    """Récupère les tweets de manière asynchrone avec gestion des tentatives en cas de délai."""
    retry_count = 0
    while retry_count < max_retries:
        try:
            if tweets is None:
                print(f'{datetime.now()} - Initialisation de la recherche...')
                tweets = await client.search_tweet(QUERY, product='Latest')
            else:
                wait_time = randint(5, 10)
                print(f'{datetime.now()} - Récupération des prochains tweets après {wait_time} secondes...')
                await asyncio.sleep(wait_time)
                tweets = await tweets.next()
            return tweets
        except httpx.ConnectTimeout:
            retry_count += 1
            print(f"{datetime.now()} - Timeout détecté. Nouvelle tentative {retry_count}/{max_retries}...")
            await asyncio.sleep(5)  # Attendre avant de réessayer
    print(f"{datetime.now()} - Nombre maximal de tentatives atteint. Échec de récupération des tweets.")
    return None

async def authenticate(client, config):
    """Authentifie le client via cookies ou identifiants."""
    username = config['X']['username']
    email = config['X']['email']
    password = config['X']['password']
    cookies_file = config['FILES']['cookie_file']

    if not os.path.exists(cookies_file):
        print(f"{datetime.now()} - Aucun cookie trouvé. Connexion requise.")
        await client.login(auth_info_1=username, auth_info_2=email, password=password)
        client.save_cookies(cookies_file)
        print(f"{datetime.now()} - Connexion réussie. Cookies sauvegardés.")
    else:
        try:
            client.load_cookies(cookies_file)
            print(f"{datetime.now()} - Cookies chargés avec succès.")
        except Exception as e:
            print(f"{datetime.now()} - Erreur lors du chargement des cookies : {e}. Reconnexion...")
            await client.login(auth_info_1=username, auth_info_2=email, password=password)
            client.save_cookies(cookies_file)

async def save_to_csv(tweet_data, csv_file):
    """Sauvegarde un tweet dans le fichier CSV."""
    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([tweet_data['text'], tweet_data['author'], tweet_data['date']])

async def save_to_json(tweets_data, json_file):
    """Sauvegarde tous les tweets dans un fichier JSON."""
    with open(json_file, 'w', encoding='utf-8') as json_file:
        json.dump(tweets_data, json_file, ensure_ascii=False, indent=4)

async def fetch_tweets(client, config):
    """Récupère et sauvegarde les tweets jusqu'à atteindre MINIMUM_TWEETS."""
    tweet_count = 0
    tweets = None
    tweets_data = []
    csv_file = config['FILES']['csv_file']
    json_file = config['FILES']['json_file']

    while tweet_count < MINIMUM_TWEETS:
        try:
            tweets = await get_tweets(tweets, client)
            if tweets is None:
                print(f"{datetime.now()} - Aucun tweet supplémentaire trouvé ou échec de récupération.")
                break

            for tweet in tweets:
                tweet_count += 1
                tweet_data = {
                    'text': tweet.text,
                    'author': tweet.user.name if tweet.user else 'Inconnu',
                    'date': tweet.created_at
                }
                tweets_data.append(tweet_data)
                print(f"{datetime.now()} - {tweet_count} tweets récupérés.")

                # Sauvegarde du tweet en CSV au fur et à mesure
                await save_to_csv(tweet_data, csv_file)

        except TooManyRequests as e:
            reset_time = datetime.fromtimestamp(e.rate_limit_reset)
            print(f"{datetime.now()} - Limite atteinte. Attente jusqu'à {reset_time}.")
            wait_time = (reset_time - datetime.now()).total_seconds()
            await asyncio.sleep(wait_time)
        except httpx.ConnectTimeout:
            print(f"{datetime.now()} - Timeout de connexion. Nouvelle tentative après une pause...")
            await asyncio.sleep(5)

    # Sauvegarder tous les tweets en JSON
    await save_to_json(tweets_data, json_file)
    print(f"{datetime.now()} - Recherche terminée. {tweet_count} tweets récupérés.")

async def main():
    """Fonction principale : Authentification et récupération des tweets."""
    config = ConfigParser()
    config.read(CONFIG_FILE)

    client = Client(language='en-US', timeout=httpx.Timeout(10.0))  # Timeout augmenté
    global QUERY
    QUERY = config['SEARCH']['query']

    # Authentification avec cookies ou identifiants
    await authenticate(client, config)

    # Récupération des tweets
    await fetch_tweets(client, config)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterruption détectée. Arrêt du programme.")
