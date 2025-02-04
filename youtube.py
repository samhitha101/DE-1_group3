import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

file_path = 'cleaned_recipes.csv'

df = pd.read_csv(file_path)
chrome_options = Options()
chrome_options.add_argument("--headless")

service = Service(executable_path="C:\\Users\\chiki\\OneDrive\\Desktop\\srh classes\\daa engenerr\\project\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)


def search(recipe_id, recipe_name):

    search_query = recipe_name.replace("-", "+")
    youtube_url = f"https://www.youtube.com/results?search_query=how+to+make+{search_query}"

    driver.get(youtube_url)
    time.sleep(3)

    videos = driver.find_elements(By.XPATH, "//ytd-video-renderer")[:3]
    results = []

    for video in videos:
        try:
            title = video.find_element(By.ID, "video-title").text

            video_url = video.find_element(By.ID, "video-title").get_attribute("href")

            views = video.find_element(By.XPATH, ".//span[contains(text(), 'views')]").text


            results.append({
                "Recipe_ID": recipe_id,
                "Recipe_Name": recipe_name,
                "Title": title,
                "Video_URL": video_url,
                "Views": views,

            })
        except Exception as e:
            print(f"Error parsing video: {e}")

    print(".")
    return results



data=[]
for recipe_id, recipe_name in zip(df['Recipe_ID'], df['Recipe_Name']):
    print(recipe_id,recipe_name,"."*5)
    top_videos = search(recipe_id, recipe_name)
    data.append(top_videos)


videos_csv = [item for sublist in data for item in sublist]

df = pd.DataFrame(videos_csv)
df.to_json("youtube_recipe_videos.json", orient="records", lines=True)
df.to_csv("youtube_recipe_videos.csv", index=False)

print("JSON and CSV file saved successfully!")

driver.quit()

