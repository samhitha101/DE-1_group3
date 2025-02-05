from hdfs import InsecureClient
import pandas as pd
import os

# HDFS Configuration
hdfs_url = 'http://100.124.47.103:9870'
hdfs_base_path = '/home/hadoop/data/nameNode/data/'

# List of CSV files
local_csv_paths = [
    '/Users/sandeepsharma/Downloads/recipes_Info.csv',
    '/Users/sandeepsharma/Downloads/recipe_Cuisine.csv',
    '/Users/sandeepsharma/Downloads/youtube_recipe_videos.csv',
    '/Users/sandeepsharma/Downloads/recipe_Timeline.csv',
    '/Users/sandeepsharma/Downloads/recipe_Nutritions.csv',
    '/Users/sandeepsharma/Downloads/recipe_Images.csv',
]

# Connect to HDFS
client = InsecureClient(hdfs_url, user='hadoop', timeout=60)

# Upload each CSV file
for local_csv_path in local_csv_paths:
    filename = os.path.basename(local_csv_path)
    hdfs_path = os.path.join(hdfs_base_path, filename)

    try:
        df = pd.read_csv(local_csv_path)
        with client.write(hdfs_path, encoding='utf-8') as writer:
            df.to_csv(writer, index=False)
        print(f"Uploaded '{filename}' to '{hdfs_path}'")
    except Exception as e:
        print(f"Failed to upload '{filename}': {e}")
