import csv
import os
import random
import string
import time
import pandas as pd
import requests
# import re
from bs4 import BeautifulSoup
import sqlite3
from sqlite3 import Error
import traceback
import sys

# from requests.adapters import HTTPAdapter
# from requests.exceptions import RequestException
# from urllib3.exceptions import ConnectTimeoutError


# BasePath = 'F:\\WebScrapping\\hopkinsmedicine'
BasePath = os.getcwd()
######### Excel #########
File_path = BasePath + '\\OP\\Output.xlsx'
######### CSV #########
File_path_CSV = BasePath + '\\OPcsv\\Output.csv'
File_path_error_CSV = BasePath + '\\OPcsv\\Error.csv'
######### Error #########
File_path_error = BasePath + '\\Error\\Error.xlsx'
######### Log #########
File_path_log = BasePath + '\\Log\\Log.txt'
File_path_log_index_LetterE1 = BasePath + '\\Log\\Log_Index.txt'
File_path_log_Run_Flag = BasePath + '\\Log\\Run_Flag.txt'


def log_print(message):
    with open(File_path_log, 'a', encoding='utf-8') as file:
        file.write(message + '\n')
        file.flush()
    print(message)


def exception():
    error = traceback.format_exc()
    exception_type, exception_object, exception_traceback = sys.exc_info()


def individual_data(profile_url):
    try:
        time.sleep(5)
        indi_data = []
        individual_obj = requests.get(profile_url, timeout=100)
        individual_soup = BeautifulSoup(individual_obj.content, 'html.parser')

        if individual_soup.find('div', class_='section personal'):
            individual_details = individual_soup.find('div', class_='section personal')
            name_tag = individual_details.find('div', class_='name').find('h1').text.strip() if individual_details.find('div', class_='name').find('h1') else '-'
            title_tag = individual_details.find('ul', class_='titles').text.strip() if individual_details.find('ul', class_='titles') else '-'
            gender_tag = individual_details.find('div', class_='gender').text.strip() if individual_details.find('div', class_='gender') else '-'
            expertise_tag = individual_details.find('div', class_='expertise').find('span', class_='read-more-wrapper').get_text(separator=' ', strip=True) if individual_details.find('div', class_='expertise').find('span', class_='read-more-wrapper') else '-'
            expertise_tag = expertise_tag.replace('...read less', '')
            research_tag = individual_details.find('div', class_='research').find('span', class_='read-more-wrapper').get_text(separator=' ', strip=True) if individual_details.find('div', class_='research').find('span', class_='read-more-wrapper') else '-'
            research_tag = research_tag.replace('...read more', '')

        if individual_soup.find('div', id='Appointments'):
            individual_appointment = individual_soup.find('div', id='Appointments')
            phone_tag = individual_appointment.find('div', class_='col-4 standard').find('div', class_='phone').get_text(separator=' ', strip=True) if individual_appointment.find('div', class_='col-4 standard').find('div', class_='phone') else '-'

        if individual_soup.find('div', id='Locations'):
            individual_location = individual_soup.find('div', id='Locations')
            location_tag = individual_location.find('div', class_='address').text.strip() if individual_location.find('div', class_='address') else '-'
            location_tag = location_tag.replace('map', '')
        # if individual_soup.find('div', id='Education'):
        #     individual_location = individual_soup.find('div', id='Education')
        #     education_tag = individual_location.find('div', class_='name').find('h1') if individual_location.find('div', class_='name').find('h1')
        indi_data.append(name_tag)
        indi_data.append(title_tag)
        indi_data.append(gender_tag)
        indi_data.append(expertise_tag)
        indi_data.append(research_tag)
        indi_data.append(phone_tag)
        indi_data.append(location_tag)
        # indi_data.append(education_tag)

        with open(File_path_CSV, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(indi_data)
    except:
        exception()


if __name__ == '__main__':
    # Create directories if they don't exist
    directories = [
        BasePath + '\\Log',
        BasePath + '\\OP',
        BasePath + '\\OPcsv'
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

    First_run = True
    if First_run:
        # if not os.path.exists(File_path_log_Run_Flag):
        #     with open(File_path_log_Run_Flag, "a", encoding='utf-8') as f:
        #         f.write("")
        if os.path.isfile(File_path_CSV):
            os.remove(File_path_CSV)
        if os.path.exists(File_path_log):
            os.remove(File_path_log)

    headers = ['Name', 'Title', 'Gender', 'Expertise', 'Research Interests', 'Phone', 'Location', 'Education']
    with open(File_path_CSV, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(headers)

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; Trident/5.0)",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; MDDCJS)",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Edg/92.0.902.55",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Edg/92.0.902.55"
    ]
    user_agent = random.choice(user_agents)
    Headers = {'User-Agent': user_agent}

    Base_url = 'https://www.hopkinsmedicine.org'
    Search_url = Base_url + '/profiles/search?count=500&Page={}'

    retry_attempts = 5
    retry_delay = 2

    try:
        outerRetry = 1
        # error_message_flag = False
        while outerRetry <= retry_attempts:
            try:
                obj_temp = requests.get(Search_url.format(1), headers=Headers, timeout=200)
                break
            except Exception as e:
                log_print(f"Error occurred")
                # exception()
                delay = retry_delay * (2 ** outerRetry)
                log_print(f'Retrying in {delay} seconds...RETRY: {outerRetry}')
                time.sleep(delay)
                outerRetry += 1
                continue
        else:
            exit(1)

        soup_temp = BeautifulSoup(obj_temp.content, 'html.parser')

        # error_message = soup_temp.find('div', class_='alert alert-danger')
        # if error_message:
        #     error_message_flag = True
        # break

        if len(soup_temp.find_all('ol', class_='paginate')) > 0:
            last_page_element = soup_temp.find_all('a', class_='page-button')[-2]
            last_page_number = int(last_page_element.get_text(strip=True))
            del obj_temp
            del soup_temp
        else:
            last_page_number = 1

        for index in range(1, last_page_number + 1):
            time.sleep(10)
            user_agent = random.choice(user_agents)
            Headers = {'User-Agent': user_agent}
            innerRetry = 1
            while innerRetry <= retry_attempts:
                try:
                    obj = requests.get(Search_url.format(index), headers=Headers, timeout=200)
                    break
                except Exception as e:
                    log_print(f"Error occurred")
                    # exception()
                    delay = retry_delay * (2 ** innerRetry)
                    log_print(f'Retrying in {delay} seconds...RETRY: {innerRetry}')
                    time.sleep(delay)
                    innerRetry += 1
                    continue
            else:
                exit(1)

            soup = BeautifulSoup(obj.content, 'html.parser')
            res = soup.find('div', class_='faculty-results-wrapper').find('ul', class_='faculty-results-list')
            profiles = res.find_all('div', class_='main-wrap')
            for profile in profiles:
                Profile_url = Base_url + profile.find('a', href=True).get('href')
                individual_data(Profile_url)
    except:
        exception()

    finally:
        # data = pd.read_excel(File_path)
        # data_file = data.drop_duplicates()
        # data_file.to_excel(File_path, index=False)
        log_print("\nComplete")
        exit()
