import time
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import pandas as pd
import re


def single_recipe_func(link):
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')

        prep_time = soup.find('time', datetime=True).text.strip() if soup.find('time', datetime=True) else "Not Available"
        cook_time = soup.find_all('time', datetime=True)[1].text.strip() if len(soup.find_all('time', datetime=True)) > 1 else "Not Available"
        image_tag = soup.find('div', class_='image__container').find('picture').find('img', class_='image__img')
        image_url = image_tag['src'] if image_tag else "Not Available"
        # Find the paragraph inside the specified div and get its text
        paragraph_text = soup.find('div',
                                   class_='editor-content post-header__description mt-sm pr-xxs hidden-print').find(
            'p').text.strip() if soup.find('div',
                                           class_='editor-content post-header__description mt-sm pr-xxs hidden-print') else "Not Available"

        info = {
            "Preparation Time": prep_time,
            "Cooking Time": cook_time,
            "Image URL":image_url,
            "Description":paragraph_text,
        }

        nutrition_list = soup.find('ul', class_='nutrition-list')
        nutrition = {}

        for item in nutrition_list.find_all('li', class_='nutrition-list__item'):
            label = item.find('span').get_text(strip=True)
            value = item.get_text(strip=True).replace(label, '').strip()
            value = re.findall(r'\d+\.?\d*', value)
            nutrition[label] = value[0]
        info["nutrition"] = nutrition

        return info
    except Exception as e:
        print(f"Error in single_recipe_func for link {link}: {e}")
        return None  # Return None if there's an error

def all_recipes_func(link):
    stored = {}
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')

        link = soup.find_all('a', class_='link d-block')
        link.pop(-1)
        link.pop(-1)
        count = 0
        for li in link:
            url = li['href']
            full_url = urljoin(base_url, url)
            last_part = full_url.split("/")[-1]

            recipe_data = single_recipe_func(full_url)

            if recipe_data is None:  # If recipe_data is None, skip this recipe
                continue

            category = full_url.split("/")[-2]

            if category not in stored:
                stored[category] = []

            recipe_data["Recipe Name"] = last_part
            stored[category].append(recipe_data)
            count += 1
            print(count, last_part, "." * 5)

        return stored
    except Exception as e:
        print(f"Error in all_recipes_func for link {link}: {e}")
        return {}  # Return an empty dict if there's an error

url = [
    "https://www.bbcgoodfood.com/recipes/category/cuisine-collections?page=1",
    "https://www.bbcgoodfood.com/recipes/category/cuisine-collections?page=2",
    "https://www.bbcgoodfood.com/recipes/category/cuisine-collections?page=3",
    "https://www.bbcgoodfood.com/recipes/category/cuisine-collections?page=4"
]

base_url = 'https://www.bbcgoodfood.com'

stored = {}
for ur in url:
    try:
        response = requests.get(ur)
        soup = BeautifulSoup(response.text, 'html.parser')

        link = soup.find_all('a', class_='link d-block')
        link.pop(-1)
        link.pop(-1)
        count = 0
        for li in link:
            url = li['href']
            full_url = urljoin(base_url, url)
            last_part = full_url.split("/")[-1]
            print(count, last_part, full_url)

            # Process each recipe page and handle any potential errors
            store = all_recipes_func(full_url)
            if store:
                stored[last_part] = store
            count += 1
            time.sleep(3)
        time.sleep(3)
    except Exception as e:
        print(f"Error in processing URL {ur}: {e}")

# Flattening the data
flattened_data = []
recipe_id = 1

for category, category_data in stored.items():
    recipes = category_data.get("recipes", [])

    for recipe_details in recipes:
        try:
            row = {
                "Recipe_ID": recipe_id,
                "Category": category,
                "Recipe_Name": recipe_details.get("Recipe Name", ""),
                "Preparation_Time": recipe_details.get("Preparation Time", ""),
                "Cooking_Time": recipe_details.get("Cooking Time", ""),
                "Image URL": recipe_details.get("Image URL", ""),
                "Description":recipe_details.get("Description", ""),
            }

            # Add nutrition details
            nutrition = recipe_details.get("nutrition", {})
            for key, value in nutrition.items():
                row[key] = value

            flattened_data.append(row)
            df = pd.DataFrame(flattened_data)
            df.to_json("recipes_data.json", orient="records", lines=True)
            df.to_csv("Recipes_data.csv", index=False)
            recipe_id += 1
        except Exception as e:
            print(f"Error processing recipe {recipe_details.get('Recipe Name', 'Unknown')}: {e}")
            continue  # Continue processing the next recipe if there's an error



print("successfully!")
