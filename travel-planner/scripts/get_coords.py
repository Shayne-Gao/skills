from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="my_travel_planner_quanzhou_test")
places = ["开元寺, 鲤城区, 泉州市", "西街, 鲤城区, 泉州市", "钟楼, 鲤城区, 泉州市", "承天禅寺, 鲤城区, 泉州市", "泉州府文庙, 鲤城区, 泉州市", "清净寺, 鲤城区, 泉州市", "通淮关岳庙, 鲤城区, 泉州市", "天后宫, 鲤城区, 泉州市", "中山南路, 鲤城区, 泉州市"]
for p in places:
    loc = geolocator.geocode(p)
    if loc:
        print(f"{p}: [{loc.latitude}, {loc.longitude}]")
    else:
        print(f"{p}: Not found")
