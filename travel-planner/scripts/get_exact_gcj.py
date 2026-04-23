import urllib.request, json, urllib.parse

places = ["泉州开元寺", "泉州西街", "泉州钟楼", "泉州承天禅寺", "泉州府文庙", "泉州清净寺", "泉州通淮关岳庙", "泉州中山南路"]
# using a public amap web api key (often found on github)
key = "13e5f206684df624891104e1ebc394fc" # Let's try this one or another

for p in places:
    url = f"https://restapi.amap.com/v3/place/text?keywords={urllib.parse.quote(p)}&city=泉州&output=json&key=j8e3... wait, let me just use the geocoding api"
