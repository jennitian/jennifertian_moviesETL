# Movie Data ETL
module 8 challenge
## Goals
To write a python function that takes in the wikipedia, kaggle, and ratings data and cleans it then uploads the dataframes to sequel.
## Findings
As we go through our dataframes we are able to combine the wikipedia movie dataframe into the kaggle dataframe. With these we get a list of 7033 rows of movies, although not all of them have values for each column. This is probably enough data to perform analysis and predict trends of success for future movie endeavors. 
## Assumptions
When cleaning the data some assumptions are made to eliminate bad data in the sets.
- First we drop columns with too many >90% null values. We assume that 10% of a large dataframe will presumably not give us very much information that we can apply to future movies.
- We also assume that the data in these databases is fairly homogenous before we merge. We can check this using scatter plots and remove outliers that are mismatched in different datasets.
- As we clean our data and try to create uniform data in columns, data will inevitably be lost. We assume that losing small number of data points will not affect analysis as a whole because there are still thousands of other datapoints.
- As we convert columns to different datatypes, errors will likely arise, we will most likely ignore these datapoints as well assuming it doesn't affect the majority of the data in the column.
- We also need to assume homogeneity between different data sets after we merge and fill in missing or null values from one dataframe to the column of another dataframe (i.e both wiki movies and kaggle have columns for budget, box office revenue, etc.)
- Finally, we assume that certain columns will not provide important information for our analysis (i.e Production company, video, etc.) so we drop those columns to shorten the database.