import urllib.request, urllib.parse, json

key = "0250860ccb5953fa5d655e8acf40ebb7"
places = ["泉州开元寺", "泉州西街", "泉州钟楼", "泉州承天禅寺", "泉州府文庙", "泉州清净寺", "泉州通淮关岳庙", "泉州中山南路"]

for p in places:
    url = f"https://restapi.amap.com/v3/place/text?keywords={urllib.parse.quote(p)}&city={urllib.parse.quote('泉州')}&offset=1&page=1&key={key}&extensions=all"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('pois') and len(data['pois']) > 0:
                loc = data['pois'][0]['location'] # lng,lat
                name = data['pois'][0]['name']
                lng, lat = loc.split(',')
                print(f'{p}: [{lat}, {lng}] // {name}')
            else:
                print(f'{p}: NOT FOUND')
    except Exception as e:
        print(f'{p}: ERROR {e}')
