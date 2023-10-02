import requests
from bs4 import BeautifulSoup

url = "https://charlottesville29.com/five-finds-on-friday/"
html  = requests.get(url).text
soup = BeautifulSoup(html, features="html.parser")

entries = soup.find_all('p', attrs={'style':'padding-left: 30px;'})

restaurants = {}
restaurantname = {}
restaurantrecs = {}

for entry in entries:
    if not str.isnumeric(entry.text[0]):
        continue
    restaurant = entry.find('a')
    if restaurant:
        item = entry.find('strong')
        if not item:
            item = entry.find('b')
        if restaurant['href'] in restaurants:
            restaurants[restaurant['href']] += 1
            if item:
                restaurantrecs[restaurant['href']].append(item.text.strip())
        else:
            restaurants[restaurant['href']] = 1
            restaurantname[restaurant['href']] = restaurant.text
            if item:
                restaurantrecs[restaurant['href']] = [(item.text.strip())]

restaurants = sorted(restaurants.items(), key=lambda x:x[1], reverse=True)

finds = []
for r in restaurants:
    print(r)
    if r[0] in restaurantrecs:
        finds.append({"name":restaurantname[r[0]],"url":r[0],"times picked":r[1],"recommendations":restaurantrecs[r[0]]})
    else:
        finds.append({"name":restaurantname[r[0]],"url":r[0],"times picked":r[1],"recommendations":[]})

import json
json.dump(finds,open("./finds.json","w"))
