#import dependencies
import json
import pandas as pd
import numpy as np
import re

#importing wiki json file
file_dir = '/Users/jennifertian/Desktop/class_files'
with open(f'{file_dir}/wikipedia-movies.json', mode='r') as file:
    wiki_movies_raw = json.load(file)
wiki_movies_df = pd.DataFrame([movie for movie in wiki_movies_raw
               if ('Director' in movie or 'Directed by' in movie)
                   and 'imdb_link' in movie
                   and 'No. of episodes' not in movie])

#importing csv files
kaggle_metadata = pd.read_csv(f'{file_dir}/movies_metadata.csv', low_memory=False)
ratings = pd.read_csv(f'{file_dir}/ratings.csv')

#form variables
form_one = r'\$\s*\d+\.?\d*\s*[mb]illi?on'
form_two = r"\$\s*\d{1,3}(?:[,\.]\d{3})+(?!\s[mb]illion)"
date_form_one = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s[123]\d,\s\d{4}'
date_form_two = r'\d{4}.[01]\d.[123]\d'
date_form_three = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}'
date_form_four = r'\d{4}'

#creating function that takes in 3 datasets/merges/cleans them
def etl(wiki_data, kaggle, rating):
    #cleaning wiki_data as df
    wiki_data['imdb_id'] = wiki_data['imdb_link'].str.extract(r'(tt\d{7})')
    wiki_data.drop_duplicates(subset='imdb_id', inplace=True)
    #drop columns with too many null columns
    wiki_data = wiki_data[[column for column in wiki_data.columns if wiki_data[column].isnull().sum() < len(wiki_data) * 0.9]]
    
    #create function to fix data
    def parse_dollars(s):
        if type(s) != str:
            return np.nan
        # if input is in form of $###.# million
        if re.match(r'\$\s*\d+\.?\d*\s*milli?on', s, flags=re.IGNORECASE):
            s = re.sub('\$|\s|[a-zA-Z]','', s)
            value = float(s) * 10**6
            return value
        # if input is of the form $###.# billion
        elif re.match(r'\$\s*\d+\.?\d*\s*billi?on', s, flags=re.IGNORECASE):
            s = re.sub('\$|\s|[a-zA-Z]','', s)
            value = float(s) * 10**9
            return value
        # if input is of the form $###,###,###
        elif re.match(r'\$\s*\d{1,3}(?:[,\.]\d{3})+(?!\s[mb]illion)', s, flags=re.IGNORECASE):
            s = re.sub('\$|,','', s)
            value = float(s)
            return value

        # otherwise, return NaN
        else:
            return np.nan
    # converting datatypes in wiki_data
    for key in ['Budget', 'Box office', 'Release date', 'Running time']:
        join_lists = lambda x: ' '.join(x) if type(x) == list else x
        wiki_data[key].apply(join_lists).dropna()
        if key in ['Budget', 'Box office']:
            wiki_data[key] = wiki_data[key].str.extract(f'({form_one}|{form_two})', flags=re.IGNORECASE)[0].apply(parse_dollars)
            wiki_data.drop(key, axis=1, inplace=True)
        elif key == 'Running time':
            runtime = wiki_data[key].str.extract(r'(\d+)\s*ho?u?r?s?\s*(\d*)|(\d+)\s*m')
            runtime = runtime.apply(lambda col: pd.to_numeric(col, errors='coerce')).fillna(0)
            wiki_data[key] = runtime.apply(lambda row: row[0]*60 + row[1] if row[2] == 0 else row[2], axis=1)
            wiki_data.drop(key, axis=1, inplace=True)
        elif key == 'Release date':
            wiki_data[key] = pd.to_datetime(wiki_data[key].str.extract(f'({date_form_one}|{date_form_two}|{date_form_three}|{date_form_four})')[0], infer_datetime_format=True)
        


    #cleaning wiki_data as dict
    wiki_data = dict(wiki_data)
    alt_titles = {}

    #combine all alternate titles into one column
    for key in ['Also known as','Arabic','Cantonese','Chinese','French',
                'Hangul','Hebrew','Hepburn','Japanese','Literally',
                'Mandarin','McCune–Reischauer','Original title','Polish',
                'Revised Romanization','Romanized','Russian',
                'Simplified','Traditional','Yiddish']:
        if key in wiki_data:
            alt_titles[key] = wiki_data[key]
            wiki_data.pop(key)
    if len(alt_titles) > 0:
        wiki_data['alt_titles'] = alt_titles

    # merge column names
    def change_column_name(old_name, new_name):
        if old_name in wiki_data:
            wiki_data[new_name] = wiki_data.pop(old_name)
    change_column_name('Adaptation by', 'Writer(s)')
    change_column_name('Country of origin', 'Country')
    change_column_name('Directed by', 'Director')
    change_column_name('Distributed by', 'Distributor')
    change_column_name('Edited by', 'Editor(s)')
    change_column_name('Length', 'Running time')
    change_column_name('Original release', 'Release date')
    change_column_name('Music by', 'Composer(s)')
    change_column_name('Produced by', 'Producer(s)')
    change_column_name('Producer', 'Producer(s)')
    change_column_name('Productioncompanies ', 'Production company(s)')
    change_column_name('Productioncompany ', 'Production company(s)')
    change_column_name('Released', 'Release Date')
    change_column_name('Release Date', 'Release date')
    change_column_name('Screen story by', 'Writer(s)')
    change_column_name('Screenplay by', 'Writer(s)')
    change_column_name('Story by', 'Writer(s)')
    change_column_name('Theme music composer', 'Composer(s)')
    change_column_name('Written by', 'Writer(s)')
     
    # to numeric and to datetime functions
    for key in ['id', 'popularity']:
        try: 
            kaggle[key] = pd.to_numeric(kaggle[key], errors='raise')
        except:
            pass
    for key in ['release_date', 'timestamp']:
        try:
            kaggle[key] = pd.to_datetime(kaggle[key], unit='s')
        except:
            pass
        try:
            rating[key] = pd.to_datetime(rating[key], unit='s')
        except:
            pass
    
    movies_df = pd.merge(wiki_data, kaggle, on='imdb_id', suffixes=['_wiki','_kaggle'])
    #drop columns
    movies_df.drop(columns=['title_wiki','release_date_wiki','Language','Production company(s)'], inplace=True)

    #function to replace values
    def fill_missing_kaggle_data(df, kaggle_column, wiki_column):
        df[kaggle_column] = df.apply(
            lambda row: row[wiki_column] if row[kaggle_column] == 0 else row[kaggle_column]
            , axis=1)
        df.drop(columns=wiki_column, inplace=True)
    #run functions
    fill_missing_kaggle_data(movies_df, 'runtime', 'running_time')
    fill_missing_kaggle_data(movies_df, 'budget_kaggle', 'budget_wiki')
    fill_missing_kaggle_data(movies_df, 'revenue', 'box_office')
    #drop video column
    movies_df.drop(columns='video', axis=1)
    return wiki_data, len(kaggle), len(rating)

print(etl(wiki_movies_df, kaggle_metadata, ratings))