from hdfs import InsecureClient
import pandas as pd
import os
 
hdfs_url = 'http://100.124.47.103:9870'  
hdfs_base_path = '/home/hadoop/data/nameNode/data/'  
local_csv_path = '/Users/sandeepsharma/Downloads/nutrition.csv'  
 
client = InsecureClient(hdfs_url, user='hadoop', timeout=60)
 
filename = os.path.basename(local_csv_path)
hdfs_path = os.path.join(hdfs_base_path, filename)  
 
try:
    df = pd.read_csv(local_csv_path)
    
    with client.write(hdfs_path, encoding='utf-8') as writer:
        df.to_csv(writer, index=False)
    
    print(f"File {local_csv_path} has been successfully saved to {hdfs_path}")
except Exception as e:
    print(f"Failed to save {local_csv_path} to HDFS: {e}")




