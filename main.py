import discord
import requests
import time
import json
from bs4 import BeautifulSoup
import cloudscraper
import os
from dotenv import load_dotenv


def main():  
    
    load_dotenv()
    TOKEN = os.getenv('TOKEN')

    client = discord.Client()

    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')
    @client.event

    async def on_message(message):
        if message.author == client.user:
            return
        if "!check" in message.content.lower():
            await message.channel.send("Checking account...")
            msg = message.content.split(" ")
            value = str(get_account_value(msg[1]))
        
            await message.channel.send(value)

    client.run(TOKEN)



def get_account_value(adress):
    headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
                'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0. 8' ,
                'Accept-Language': 'en-US, en;q=0.5',
                'DNT': '1',
                'Connection':'keep-alive',
                'Upgrade-Insecure-Requests':'1',
                'Accept-Encoding':'identity',
            }

    adress_url = "https://opensea.io/" + adress

    valid,x = 403,0

    while (valid != 200):
        # cloudscraper used to bypass cloudflare
        r = cloudscraper.create_scraper()

        site_data = r.get(adress_url,headers=headers)
        soup = BeautifulSoup(site_data.text, "html.parser")
        print(site_data.status_code)
        valid = site_data.status_code
        time.sleep(x)
        x+=2

    collections = []
    # finds all collections in users account
    for link in soup.find_all('a', href=True):
        if "/collection/" in link['href']:
            collections.append(link['href'])

    # removes duplicate collections
    n = int(len(collections)/2)
    collections = collections[:-n or None]

    print(collections)

    collection_value = 0
    for i in range(0, len(collections)):
        # gets the stats of each collection
        collection_url = "https://api.opensea.io/api/v1" + collections[i] + "/stats"
        headers = {"Accept": "application/json"}
        response = requests.request("GET", collection_url, headers=headers)
        print(response.text)

        # converts response to dictionary type and gets floor price
        dict = json.loads(response.text)
        fp = dict.get("stats").get("floor_price")
        try:
            collection_value+=fp
        except TypeError:
            pass

        print(fp)
        print(collections[i])
    
    print("Account of adress " + str(adress) + " has a floor value of " + str(collection_value) + "E ($" + str(get_eth_price() * collection_value) + ")")
    return ("Account of adress " + str(adress) + " has a floor value of " + str(collection_value) + "E ($" + str(get_eth_price() * collection_value) + ")")

# get eth price in usd
def get_eth_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    r = requests.get(url)
    dict = json.loads(r.text)
    eth_price = dict.get("ethereum").get("usd")
    return int(eth_price)

if __name__ == '__main__':
    main()