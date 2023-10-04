import requests
from bs4 import BeautifulSoup
import string
import json

def cleanup(s):
    return s.replace("’","'").strip().strip(string.punctuation)

url = "https://charlottesville29.com/five-finds-on-friday/"
html  = requests.get(url).text
soup = BeautifulSoup(html, features="html.parser")

entries = soup.find_all('p', attrs={'style':'padding-left: 30px;'})

restaurantcount = {}
restauranturl = {}
restaurantrecs = {}

rnames = set()

with open("./metadata.json","r") as infile:
    METADATA = json.load(infile)

for entry in entries:
    if not str.isnumeric(entry.text[0]):
        continue
    # Limitations: Sometimes people recommend more than one restaurant; we'll only count the first one because it's harder to distinguish subsequent recommendations and regular links
    # Sometimes, there's no link (no website, neglect, or "wife's meatballs"), which we won't count.
    restaurant = entry.find('a')
    if restaurant:
        rname = cleanup(restaurant.text)
        if rname in METADATA["name_normalization"]:
            rname = METADATA["name_normalization"][rname]
        rnames.add(rname)
        rurl = restaurant["href"]
        item = entry.find('strong')
        if not item:
            item = entry.find('b')
        if rname in restaurantcount:
            restaurantcount[rname] += 1
            if item:
                restaurantrecs[rname].append(cleanup(item.text))
        else:
            restaurantcount[rname] = 1
            restauranturl[rname] = rurl
            if item:
                restaurantrecs[rname] = [cleanup(item.text)]

restaurantcount = sorted(restaurantcount.items(), key=lambda x:x[1], reverse=True)

finds = []
for r in restaurantcount:
    if r[0] in restaurantrecs:
        finds.append({"name":r[0],"url":restauranturl[r[0]],"times picked":r[1],"recommendations":restaurantrecs[r[0]]})
    else:
        finds.append({"name":r[0],"url":restauranturl[r[0]],"times picked":r[1],"recommendations":[]})

with open("./finds.json","w", encoding="utf-8") as out:
    json.dump(finds, out, indent=4, ensure_ascii=False)

rnames = sorted(rnames)
with open("rnames.txt","w") as out:
    for n in rnames:
        out.write(n+"\n")