from playwright.sync_api import sync_playwright
import time
import urllib.parse

places = ["泉州开元寺", "泉州西街", "泉州钟楼", "泉州承天禅寺", "泉州府文庙", "泉州清净寺", "泉州通淮关岳庙", "泉州中山南路"]

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for place in places:
            try:
                # Search on Amap directly
                url = f"https://ditu.amap.com/search?query={urllib.parse.quote(place)}&city=350500"
                page.goto(url)
                page.wait_for_selector(".poibox", timeout=5000)
                time.sleep(1)
                print(f"{place}: {page.url}")
            except Exception as e:
                print(f"{place}: Error {e}")
        browser.close()

run()
