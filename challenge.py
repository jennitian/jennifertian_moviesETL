#import dependencies
import json
import pandas as pd
import numpy as np
import re

#importing wiki json file
file_dir = '/Users/jennifertian/Desktop/class_files'
with open(f'{file_dir}/wikipedia-movies.json', mode='r') as file:
    wiki_movies_raw = json.load(file)
wiki_movies_df = pd.DataFrame(wiki_movies_raw)

#importing csv files
kaggle_metadata = pd.read_csv(f'{file_dir}/movies_metadata.csv', low_memory=False)
ratings = pd.read_csv(f'{file_dir}/ratings.csv')

#creating function that takes in 3 datasets/merges/cleans them
def etl(wiki_data, kaggle_metadata, ratings):
    