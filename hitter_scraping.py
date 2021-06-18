#Importing needed packages:
import pandas as pd
import matplotlib.pyplot as plt
from pylab import rcParams
import numpy as np
from bs4 import BeautifulSoup
import requests
import re

def hitter_page_scraper(player_link):
    '''
    Takes in a link to a hitter's scouting report, and uses BS4 to scrape the contents.
    '''
    home_response = requests.get(player_link)
    page = home_response.text
    player_soup = BeautifulSoup(page, 'lxml')
    return player_soup

def hitter_name_puller(soup):
    '''
    Takes in a batter's page from BS4, returns their name and basic info from the page.
    '''
    #First will pull the name, then DOB, handedness, height, weight, and positions:
    name = soup.find('table', class_='info').find('p', class_='name').get_text()
    info_orig = soup.find('table', class_='info').find('td').get_text().split(name)[1][1:].split('\n')
    info_final = [item.split(':')[1][1:].strip(' (Age') for item in info_orig if item]
    info_final.insert(0, name)
    return info_final[0:6]

def hitter_evaluation_info(soup):
    '''
    Takes in a batter's page from BS4, returns info on the evaluation from the page. 
    '''
    eval_info = [item.get_text().replace('\n', '').replace('\t', '') for item in soup.find('table', class_='evaluator').find('tbody').find_all('td',class_=lambda x: x!= 'header')]
    return eval_info

def hitter_physical_health_info(soup):
    '''
    Takes in a batter's page from BS4, returns info on their health from the page. 
    '''
    return soup.find('table', class_='mechanics').find_all('td')[-1].get_text()

def hitter_eta_risk_of_puller(soup):
    '''
    Takes in a batter's page from BS4, reutrns info on their MLB ETA, Risk Factor, and OFP score.
    '''
    rep_stuff = [item.get_text().strip(' ') for item in soup.find('table', class_='repertoire').find_all('td')[4:7]]
    return rep_stuff

def hitter_tools_grades_reports(soup):
    '''
    Takes in a batter's page from BS4, returns info on their graded tools and tool reports from the scout.
    '''
    #First need to find the rows for hit, power, speed, glove, and arm:
    tools_full = soup.find('table', class_='tool').find_all('tr', class_=lambda x: x!= 'header')

    #Then, can get grades:
    tools_grades = [tool.find_all('td', class_='mid') for tool in tools_full]
    tools_grades_text = [tool[0].get_text().strip(' ') for tool in tools_grades]

    #Now, Reports:
    tools_reports = [tool.find_all('td')[-1].get_text().strip('\t')[1:] for tool in tools_full] #Need to get rid of leading spaces

    return tools_grades_text, tools_reports

def hitter_overall_report(soup):
    '''
    Takes in a batter's page from BS4, returns their overall scouting report from the scout.
    '''
    overall_report = soup.find('table', class_='overall').find('p').get_text()[1:]
    return overall_report

def hitter_info_puller_combined(link):
    '''
    Takes in a hitter's link, returns info from their scouting report using the above functions.
    '''
    #First using the scraper to pull their page's data:
    player_soup = hitter_page_scraper(link)

    #Now using the above functions to get their data:
    basic_info = hitter_name_puller(player_soup)
    #eval_info = hitter_evaluation_info(player_soup)
    phys_health = hitter_physical_health_info(player_soup)
    eta_risk = hitter_eta_risk_of_puller(player_soup)
    tools_grades, tools_reports = hitter_tools_grades_reports(player_soup)
    overall_report = hitter_overall_report(player_soup)

    #Combining lists:
    final_player_data = basic_info #+ eval_info 
    final_player_data.append(phys_health) 
    final_player_data += (eta_risk + tools_grades + tools_reports)
    final_player_data.append(overall_report) #This is a string, not a list so can't be added above
    return final_player_data

def hitter_puller_list(link_list):
    '''
    Takes in a list of player links, collects their scouting report info.
    '''
    output = []
    for link in link_list:
        hitter_info = hitter_info_puller_combined(link)
        output.append(hitter_info)
    return output



