#Importing needed packages:
import pandas as pd
import matplotlib.pyplot as plt
from pylab import rcParams
import numpy as np
from bs4 import BeautifulSoup
import requests
import re

#First, functions on converting needed columns to numerical values:
def num_col_maker(df, col_list):
    '''
    Takes in a pandas dataframe and a column list, outputs those columns as numeric.
    For this project, should be Weight and OFP grade
    '''
    num_col_names = [str(x)+'_Num' for x in col_list]
    for i, col in enumerate(num_col_names):
        df[col] = pd.to_numeric(df[col_list[i]])
    return df

def grade_num_col_maker(df):
    '''
    Takes in a pandas dataframe and converts columns with _Grade in the name to numeric values.
    This 
    '''
    grade_cols = [str(col) for col in df.columns if ('_Grade' in col) and ('_Num' not in col)]
    for col in grade_cols:
        num_col = col+'_Num'
        df[num_col] = pd.to_numeric(df[col])
    return df, grade_cols

def numerical_columns_combined(df, col_list):
    '''
    Takes in a dataframe and turns the listed columns (and grade columns) into numerical values.
    Drops out the original, non-numeric columns in the outputted dataframe.
    '''
    #making columns numeric:
    num_df_1 = num_col_maker(df, col_list)
    num_df_2, grade_cols = grade_num_col_maker(num_df_1)
    
    #Dropping out the non-numerical columns:
    combined_list = col_list + grade_cols
    output_df = num_df_2.drop(columns = combined_list)
    return output_df

#Next, preprocessing for batting and throwing:
def bats_preprocessing(df):
    '''
    Takes in a dataframe and preprocesses the Bat column as follows:
    Right --> Bats_Right = 1, Left --> Bats_Left = 1, Switch --> both = 1
    '''
    df['Bats_Right'] = 0
    df['Bats_Left'] = 0
    for i, bat in enumerate(df.Bats):
        if bat == 'Switch':
            df.Bats_Right[i] = 1
            df.Bats_Left[i] = 1
        elif bat == 'Right':
            df.Bats_Right[i] = 1
        elif bat == 'Left':
            df.Bats_Left[i] = 1
    return df

def throws_preprocessing(df):
    '''
    Takes in a dataframe and preprocesses the Throws column as follows:
    Right = 1, Left = 0
    '''
    df['Throws_Right'] = 0
    for i, throw in enumerate(df.Throws):
        if throw == 'Right':
            df.Throws_Right[i] = 1
    return df

def throws_bats_processor(df):
    '''
    Takes in a dataframe and preprocesses the Throws and Bats columns into numerical 1/0 columns:
    Throws --> Throws_Right: Right = 1, Left = 0
    Bats --> Bats_Right and Bats_Left (due to switch hitting)
    '''
    bats_df = bats_preprocessing(df)
    output_df = throws_preprocessing(bats_df)
    return output_df

#Pre-processing height:
def height_converter_to_inches(height):
    '''
    Takes in a height of format f'in", converts it to pure inches.
    '''
    clean_height = height.strip('"').split("'") #takes out the inches quotes, then splits into height and feet
    feet = int(clean_height[0])
    inches = int(clean_height[1])
    output = (feet*12 + inches)
    return output

def height_inches_column(df):
    '''
    Takes in a dataframe with a "Height" column in f'in" format, and converts all the values to inches.
    '''
    heights = df.Height
    inch_heights = [height_converter_to_inches(height) for height in heights]
    df['Height_Inches'] = inch_heights
    return df

#Pre-processing ETA data:
def eta_cleaner(eta):
    '''
    Takes in a player's MLB ETA data, and converts it to the year.
    '''
    #If there is a space in the date:
    if ' ' in eta:
        return eta.split(' ')[1]
    #Standard date format (MM/DD/YYYY):
    elif ('/' in eta) and (eta != 'N/A'):
        return eta.split('/')[2]
    #Dash in the year:
    elif '-' in eta:
        return eta.split('-')[1]
    else:
        if (len(eta) == 4) and ('n' not in eta.lower()):
            return eta
        else:
            return 0

def cleaned_eta_column(df):
    '''
    Takes in a dataframe with an MLB_ETA column, and returns the year of the player's ETA.
    Note: if there is no ETA, the output will be 0.
    '''
    etas = df.MLB_ETA
    clean_etas = [int(eta_cleaner(eta)) for eta in etas]
    df['ETA_clean'] = clean_etas
    return df

#Cleaning birthdays (converting to datetime):
def born_cleaner(df):
    '''
    Takes in a dataframe with a Born column, turns the Born column from an object datatype to a datetime.
    '''
    clean_dates = []
    for date in df.Born:
        if date.split('/')[2] == '0000':
            clean_date = pd.to_datetime('1/1/1900') #setting a default date if there is non listed, so I know
        else:
            clean_date = pd.to_datetime(date)
        clean_dates.append(clean_date)
    df['Born_DT'] = clean_dates
    return df

#Finally, a "master" function to bring it all together:
def master_hitter_cleaner(df, drop_original_columns=True):
    '''
    Brings in a pandas dataframe of hitter scouting report data, and processes all the above 
    functions to clean it sequentially.  Outputs the cleaned dataframe.
    Uses the drop_original_columns argument to drop out the pre-cleaned columns if set to True.
    '''
    #Utilizing these as a default:
    num_col_list = ['Weight', 'OFP']

    #Running the above functions in the correct order
    numerical_df = numerical_columns_combined(df, num_col_list)
    throws_bats_df = throws_bats_processor(numerical_df)
    height_df = height_inches_column(throws_bats_df)
    eta_df = cleaned_eta_column(height_df)
    output_df = born_cleaner(eta_df)
 
    #Dropping columns, if drop_original_columns is True:
    if drop_original_columns == True:
        drop_columns = ['Born','Bats', 'Throws', 'Height', 'MLB_ETA']
        output_df = output_df.drop(columns = drop_columns)
    
    return output_df

