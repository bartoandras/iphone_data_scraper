from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import re
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any
from database import Database

def get_total_pages(driver):
    try:
        # Find the pagination div containing total pages
        pagination = driver.find_element(By.CLASS_NAME, 'pagination')
        # Get the last <li> element which contains total page count
        total_pages = pagination.find_elements(By.TAG_NAME, 'li')[-2].text
        return int(total_pages.strip())
    except Exception as e:
        print(f"Error getting total pages: {e}")
        return 1

def scrape_page(driver):
    data = []
    products = driver.find_elements(By.CSS_SELECTOR, '.desktop_row_view.product-item')
    
    for product in products:
        try:
            # Extract model number from title
            title = product.find_element(By.CSS_SELECTOR, '.title a').text
            model = ''.join([char for char in title if char.isdigit()])
            
            # Extract price
            price = product.find_element(By.CSS_SELECTOR, '.price strong').text
            price = price.replace('Ft', '').replace(' ', '').strip()
            
            # Extract condition
            condition = None
            try:
                condition = product.find_element(By.CSS_SELECTOR, '.text-centera span[style*="color: orange"]').text
                if condition == 'N/A':
                    condition = None
            except:
                pass
            
            # Extract battery health
            battery = None
            try:
                battery = product.find_element(By.CSS_SELECTOR, '.text-centera span[style*="color: orange"] + span').text
                if battery == 'N/A':
                    battery = None
            except:
                pass
            
            # Extract product URL
            url = product.find_element(By.CSS_SELECTOR, '.title a').get_attribute('href')
            
            data.append({
                'model': model,
                'price': price,
                'condition': condition,
                'battery': battery,
                'url': url
            })
        except Exception as e:
            print(f"Error processing product: {e}")
            continue
    
    return data

def analyze_url(url: str) -> Dict[str, Any]:
    """Analyze the last segment of URL to determine iPhone model characteristics"""
    try:
        # Get the last segment of the URL
        last_segment = url.lower().split('/')[-1]
        
        # Initialize result with default values
        result = {
            "model": None,
            "pro": False,
            "max": False,
            "mini": False,
            "se": False,
            "capacity": None
        }
        
        # Extract model number (iphone-xx where xx can be number or letters)
        model_match = re.search(r'iphone[-\s_](\d{1,2}|[a-z]{2})', last_segment)
        if model_match:
            result["model"] = f"iPhone {model_match.group(1).upper()}"
        
        # Check for model variants in the last segment
        result["pro"] = "pro" in last_segment
        result["max"] = "max" in last_segment
        result["mini"] = "mini" in last_segment
        result["se"] = "se" in last_segment
        
        # Extract capacity as number
        capacity_match = re.search(r'(\d+)\s?(gb|go)', last_segment)
        if capacity_match:
            result["capacity"] = int(capacity_match.group(1))
            
        return result
        
    except Exception as e:
        print(f"Error analyzing URL {url}: {str(e)}")
        return {
            "pro": False,
            "max": False,
            "mini": False,
            "se": False,
            "capacity": False
        }

def calculate_average_prices(data: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """Calculate average prices per iPhone model"""
    model_prices = defaultdict(list)
    
    for entry in data:
        if entry.get('price') and entry.get('model'):
            try:
                price = int(entry['price'])
                model_prices[entry['model']].append(price)
            except (ValueError, TypeError):
                continue
    
    averages = {}
    for model, prices in model_prices.items():
        if prices:
            avg_price = sum(prices) / len(prices)
            averages[model] = {
                'average_price': round(avg_price, 2),
                'count': len(prices)
            }
    
    return averages

def extend_iphone_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extend iPhone data with additional fields"""
    for entry in data:
        url = entry.get('url', '')
        if url:
            analysis = analyze_url(url)
            entry.update(analysis)
        else:
            print(f"Entry missing URL: {entry}")
    return data

def scrape_all_pages():
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    
    # Initialize webdriver
    driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=options)
    
    try:
        # Navigate to first page
        driver.get('https://hasznaltalma.hu/iphone')
        time.sleep(3)
        
        # Get total pages
        total_pages = get_total_pages(driver)
        print(f"Found {total_pages} pages to scrape")
        
        all_data = []
        
        for page in range(1, total_pages + 1):
            if page > 1:
                driver.get(f'https://hasznaltalma.hu/iphone?filter%5B0%5D=personal&filter%5B5%5D=personal&min=0&page={page}')
                time.sleep(3)
            
            print(f"Scraping page {page}/{total_pages}")
            page_data = scrape_page(driver)
            if len(page_data) == 0:
                print("No listings found, ending scrape")
                break
            all_data.extend(page_data)
            print(f"Found {len(page_data)} listings on this page")
        
        # Extend data with additional fields
        extended_data = extend_iphone_data(all_data)
        
        # Initialize database
        db = Database()
        
        # Save data to database
        for entry in extended_data:
            try:
                # Convert price to integer
                entry['price'] = int(entry['price'])
                db.add_or_update_iphone(entry)
            except Exception as e:
                print(f"Error saving entry to database: {e}")
                continue
                
        # Calculate average prices
        averages = calculate_average_prices(extended_data)
        
        print(f"Successfully processed {len(extended_data)} iPhones from {total_pages} pages")
        print(f"Data saved to SQLite database")
        print('averages:', averages)
        
    finally:
        driver.quit()

if __name__ == '__main__':
    scrape_all_pages()
