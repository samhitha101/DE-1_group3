from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

# Initialize driver once
driver = webdriver.Chrome()



time.sleep(2)

# Phase 1: Scrape recipe links
recipe_links = []

for page in range(1, 10):
    driver.get(f"https://www.allrecipes.com/recipes/?page={page}")

    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))  
        )
        cookie_button.click()
    except Exception as e:
        print("No cookie banner found.")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.mntl-card-list-items"))
    )
    recipe_cards = driver.find_elements(By.CSS_SELECTOR, "a.mntl-card-list-items")
    recipe_links.extend([card.get_attribute("href") for card in recipe_cards])
    print(f"Page {page} scraped. Total links: {len(recipe_links)}")
    time.sleep(2)  # Be polite with delays

# Remove duplicate links
recipe_links = list(set(recipe_links))[:500]

# Phase 2: Scrape individual recipes
# Initialize CSV files with headers
with open('recipes.csv', 'w', newline='', encoding='utf-8') as f:
    csv.writer(f).writerow(['recipe_id', 'name', 'author', 'prep_time', 'cook_time', 'total_time', 'servings', 'url'])


with open('nutrition.csv', 'w', newline='', encoding='utf-8') as f:
    csv.writer(f).writerow(['nutrition_id', 'recipe_id', 'calories', 'protein', 'carbs', 'fat'])

# Now scrape individual recipes
recipe_id = 1

for url in recipe_links:
    try:
        driver.get(url)
        time.sleep(1)  # Add delay
        
        # Extract metadata
        name = driver.find_element(By.TAG_NAME, 'h1').text
        author = (driver.find_element(By.CLASS_NAME, "mntl-attribution__item-name")).text if driver.find_elements(By.CLASS_NAME, "mntl-attribution__item-name") else "Unknown"
        print(author)
        # Extract time data using the structure from your screenshot
        time_elements = driver.find_elements(By.XPATH, '//*[contains(@class, "mm-recipes-details__content")]')
        prep_time = time_elements[0].text if len(time_elements) > 0 else "N/A"
        print(prep_time)
        cook_time = time_elements[1].text if len(time_elements) > 1 else "N/A"
        total_time = time_elements[2].text if len(time_elements) > 2 else "N/A"
        
        # Extract servings
        servings = driver.find_element(By.CSS_SELECTOR, 'span[data-ingredient-servings]').text if driver.find_elements(By.CSS_SELECTOR, 'span[data-ingredient-servings]') else "N/A"

        # Write to recipes.csv
        with open('recipes.csv', 'a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow([recipe_id, name, author, prep_time, cook_time, total_time, servings, url])


        # Extract nutrition
        nutrition = {}
        try:
            #nutrition_items = driver.find_elements(By.XPATH, './/*[contains(@class, "mm-recipes-nutrition-facts-summary__table")]')
            tbody = driver.find_element(By.XPATH, './/*[contains(@class, "mm-recipes-nutrition-facts-summary__table")]')

            # Find all rows within the tbody
            rows = tbody.find_elements(By.TAG_NAME, "tr")

            # Extract data from each row
            table_data = []
            for row in rows:
                # Find all cells (td elements) in the current row
                cells = row.find_elements(By.TAG_NAME, "td")
                # Extract text from each cell and add it to a list
                row_data = [cell.text for cell in cells]
                table_data.append(row_data)
            print (table_data)

        except:
            pass

        with open('nutrition.csv', 'a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow([
                recipe_id, 
                recipe_id,
                table_data[0][0],
                table_data[3][0],
                table_data[2][0],
                table_data[1][0],
            ])

        print(f"Scraped recipe {recipe_id}: {name}")
        recipe_id += 1

    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        continue

driver.quit()
print("Scraping complete!")