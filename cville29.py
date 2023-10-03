import requests
from bs4 import BeautifulSoup
import string

url = "https://charlottesville29.com/five-finds-on-friday/"
html  = requests.get(url).text
soup = BeautifulSoup(html, features="html.parser")

entries = soup.find_all('p', attrs={'style':'padding-left: 30px;'})

restaurantcount = {}
restauranturl = {}
restaurantrecs = {}

for entry in entries:
    if not str.isnumeric(entry.text[0]):
        continue
    restaurant = entry.find('a')
    if restaurant:
        rname = restaurant.text.strip().strip(string.punctuation)
        rurl = restaurant["href"]
        item = entry.find('strong')
        if not item:
            item = entry.find('b')
        if rname in restaurantcount:
            restaurantcount[rname] += 1
            if item:
                restaurantrecs[rname].append(item.text.strip().strip(string.punctuation))
        else:
            restaurantcount[rname] = 1
            restauranturl[rname] = rurl
            if item:
                restaurantrecs[rname] = [(item.text.strip().strip(string.punctuation))]

restaurantcount = sorted(restaurantcount.items(), key=lambda x:x[1], reverse=True)

finds = []
for r in restaurantcount:
    print(r)
    if r[0] in restaurantrecs:
        finds.append({"name":r[0],"url":restauranturl[r[0]],"times picked":r[1],"recommendations":restaurantrecs[r[0]]})
    else:
        finds.append({"name":r[0],"url":restauranturl[r[0]],"times picked":r[1],"recommendations":[]})

import json
json.dump(finds,open("./finds.json","w"))
