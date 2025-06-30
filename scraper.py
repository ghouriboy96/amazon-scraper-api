# scraper.py
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller

def convert_to_selenium_cookie(cookie):
    return {
        "name": cookie["name"],
        "value": cookie["value"],
        "domain": cookie["domain"],
        "path": cookie.get("path", "/"),
        "secure": cookie.get("secure", False),
        "expiry": int(cookie["expirationDate"]) if "expirationDate" in cookie else None
    }

def amazon_price_scrapper(asin_list, Min_price_list, Max_price_list, input_cookies):
    results = []

    # Setup Chrome options
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    # options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--lang=ja-JP")
    options.add_argument("--headless")  # Required for server environments

    chromedriver_autoinstaller.install()
    driver = webdriver.Chrome(options=options)
    try:
        driver.get("https://www.amazon.co.jp/s?k=%E3%82%A4%E3%83%A4%E3%83%9B%E3%83%B3")
        time.sleep(3)
        for cookie in input_cookies:
            try:
                driver.add_cookie(convert_to_selenium_cookie(cookie))
            except Exception:
                continue
        driver.refresh()
        time.sleep(5)
    except Exception as e:
        pass
        # print("Error loading cookies:", e)

    for i, price in enumerate(Min_price_list):
        try:
            Min_price_list[i] = float(str(price).replace("￥", "").replace(",", "").strip())
        except ValueError:
            Min_price_list[i] = 0.0

    for i, price in enumerate(Max_price_list):
        try:
            Max_price_list[i] = float(str(price).replace("￥", "").replace(",", "").strip())
        except ValueError:
            Max_price_list[i] = 0.0

    for i, asin in enumerate(asin_list):
        product_url = f"https://www.amazon.co.jp/s?k={asin}"
        # print(f"\n🔄 Scraping ASIN: {asin}")
        driver.get(product_url)

        try:
            if "No results for " in driver.find_element(By.CSS_SELECTOR, ".s-no-outline").text:
                results.append({
                    "ASIN": asin,
                    "title": "No title found",
                    "price ¥": "No price found",
                    "url": "No link found",
                    "status": False
                })
                continue
        except:
            pass  # In case .s-no-outline doesn't exist

        try:
            product = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".a-section.a-spacing-small.puis-padding-left-small.puis-padding-right-small"))
            )
        except:
            results.append({
                "ASIN": asin,
                "title": "No product found",
                "price ¥": "N/A",
                "url": "N/A",
                "status": False
            })
            continue

        try:
            title = product.find_element(By.CSS_SELECTOR, "h2 span").text
        except:
            title = "No title found"

        try:
            price = product.find_element(By.CSS_SELECTOR, "span.a-price span.a-offscreen").text
        except:
            try:
                price = product.find_element(By.CSS_SELECTOR, "span.a-color-price").text
            except:
                price = "No price found"

        try:
            price = float(re.sub(r"[^\d.]", "", str(price)))
        except:
            price = 0.0

        try:
            link_element = product.find_element(By.CSS_SELECTOR, ".a-link-normal.s-line-clamp-4.s-link-style.a-text-normal")
            product_link = link_element.get_attribute("href")
        except:
            try:
                link_element = product.find_element(By.CSS_SELECTOR, "a.a-link-normal.s-no-outline")
                product_link = link_element.get_attribute("href")
            except:
                product_link = "No link found"

        driver.get(product_link)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "prodDetAttrValue"))
            )
        except:
            pass

        asin_found = False
        try:
            table = driver.find_elements(By.CSS_SELECTOR, "tr")
            for row in table:
                try:
                    key = row.find_element(By.CSS_SELECTOR, "th").text.strip()
                    value = row.find_element(By.CSS_SELECTOR, "td").text.strip()
                    if key == "ASIN" and value == asin:
                        asin_found = True
                        break
                except:
                    pass
        except:
            pass

        price_matched = False

        if Min_price_list[i] <= price <= Max_price_list[i] and asin_found:
            price_matched = True #send line notification

        results.append({
            "ASIN": asin,
            "title": title,
            "price ¥": price,
            "url": product_link,
            "status": asin_found,
            "price matched": price_matched
        })

        # print(f"✅ {asin} - {title} - ¥{price}")

    driver.quit()
    return results
