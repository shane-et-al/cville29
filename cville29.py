import requests
from bs4 import BeautifulSoup
import string
import json
import re

def cleanup(s):
    return s.replace("’","'").strip().strip(string.punctuation)

def find_article(element):
    # Try to find the link to the original article so we can extract the date
    previous_ps=element.find_all_previous('p')
    for i in range(7):
        if len(previous_ps)<=i:
            break
        anchor = previous_ps[i].find("a",href=re.compile("charlottesville29.com\/[0-9]{4}\/[0-9]{2}\/[0-9]{2}\/"))
        if anchor and len(previous_ps[i].findAll(string=True, recursive=False))==0:
            return anchor
    # If we can't find it, we can't find it. There are some egregious HTML errors in here.
    return None

url = "https://charlottesville29.com/five-finds-on-friday/"
html  = requests.get(url).text
soup = BeautifulSoup(html, features="html.parser")

# styling for entries is *inconsistent*, so we'll use this regex to catch (hopefully) all of them
entries = soup.find_all('p', attrs={'style':re.compile("padding-left: [2-9]0px;")})

restaurantcount = {}
restauranturl = {}
restaurantrecs = {}

rnames = set()

with open("./metadata.json","r") as infile:
    METADATA = json.load(infile)

for element in entries:
    if not str.isnumeric(element.text[0]):
        continue
    
    article = find_article(element)
    if article:
        date = "/".join(article["href"].split("/")[3:6])
        finder = article.text
    else:
        date = "unknown"
        finder = "unknown"
    
    
    # Limitations: Sometimes people recommend more than one restaurant; we'll only count the first one because it's harder to distinguish subsequent recommendations and regular links
    # Sometimes, there's no link (because there's no website, because of neglect, or because it's "wife's meatballs"), which we won't count at all.
    item = element.find('strong')
    if not item:
        item = element.find('b')
    if not item:
        continue
    restaurant = item.find_next_sibling('a')
    if restaurant:
        rname = cleanup(restaurant.text)
        if rname in METADATA["name_normalization"]:
            rname = METADATA["name_normalization"][rname]
        rnames.add(rname)
        rurl = restaurant["href"]
        
        rec_text = "".join(s.text for s in restaurant.next_siblings).replace("\n"," ").strip().lstrip(".").strip().strip("“”\"")

        recommendation = {"item":cleanup(item.text),"date":date,"finder":finder,"recommendation":rec_text}
        if rname in restaurantcount:
            restaurantcount[rname] += 1
            if item:
                restaurantrecs[rname].append(recommendation)
        else:
            restaurantcount[rname] = 1
            restauranturl[rname] = rurl
            if item:
                restaurantrecs[rname] = [recommendation]

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