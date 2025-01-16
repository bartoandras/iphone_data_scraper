from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

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
            condition = 'N/A'
            try:
                condition = product.find_element(By.CSS_SELECTOR, '.text-centera span[style*="color: orange"]').text
            except:
                pass
            
            # Extract battery health
            battery = 'N/A'
            try:
                battery = product.find_element(By.CSS_SELECTOR, '.text-centera span[style*="color: orange"] + span').text
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

def scrape_all_pages():
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    
    # Initialize webdriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
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
            all_data.extend(page_data)
            print(f"Found {len(page_data)} listings on this page")
        
        # Save data to CSV
        with open('iphone_data.csv', 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['model', 'price', 'condition', 'battery', 'url']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_data)
            
        print(f"Successfully scraped {len(all_data)} iPhones from {total_pages} pages")
        
    finally:
        driver.quit()

if __name__ == '__main__':
    scrape_all_pages()
