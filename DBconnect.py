from hdfs import InsecureClient  # Assuming your custom package is similar
import pandas as pd
from sqlalchemy import create_engine
import os

# HDFS Configuration
hdfs_url = 'http://100.124.47.103:9870'
client = InsecureClient(hdfs_url, user='hadoop', timeout=60)

# List of CSV files and corresponding MySQL table names
hdfs_files = {
    '/home/hadoop/data/nameNode/data/recipe_Images.csv': 'recipe_images',
    '/home/hadoop/data/nameNode/data/recipes_Info.csv': 'recipe_info',
    '/home/hadoop/data/nameNode/data/recipe_Nutritions.csv': 'recipe_nutritions',
    '/home/hadoop/data/nameNode/data/recipe_Timeline.csv': 'recipe_timeline',
    '/home/hadoop/data/nameNode/data/youtube_recipe_videos.csv': 'youtube_videos',
    '/home/hadoop/data/nameNode/data/recipe_Cuisine.csv': 'recipe_Cuisine'
}

# MySQL Database Configuration
db_user = 'root'
db_password = '123123'
db_host = '100.124.47.103'       # Change if your DB is remote
db_port = '3306'                 # Default MySQL port
db_name = 'DataEng1'             # Target database

# Connect to MySQL using SQLAlchemy
engine = create_engine(f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# Loop through each file and ingest into MySQL
for hdfs_file_path, table_name in hdfs_files.items():
    try:
        # Read CSV from HDFS into a pandas DataFrame
        with client.read(hdfs_file_path, encoding='utf-8') as reader:
            df = pd.read_csv(reader)

        print(f" Successfully read {hdfs_file_path} from HDFS.")

        # Ingest DataFrame into the corresponding MySQL table
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
        # Use if_exists='append' if you don't want to replace existing data

        print(f" Data successfully ingested into the '{table_name}' table in MySQL.\n")

    except Exception as e:
        print(f" Error during ingestion of {hdfs_file_path}: {e}\n")
