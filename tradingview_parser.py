# Import libraries
import requests
import re
from bs4 import BeautifulSoup
def get_ideas(market='binance', pages=5):

    ideas = []
    for i in range(5):
        page = requests.get(f"https://www.tradingview.com/ideas/search/BINANCE/page-{i}/")
        soup = BeautifulSoup(page.text, 'html.parser')
        cards = soup.find_all(class_=re.compile(r'tv-widget-idea__description-row tv-widget-idea__description-row--clamped*'))

        for card in cards:
            ideas.append(card.getText())
    return ideas

def main():
    ideas = get_ideas()
    for i in ideas:
        print(i)

if __name__ == '__main__':
    main()