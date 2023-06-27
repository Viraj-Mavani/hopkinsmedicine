import csv
import os
import random
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
import traceback
import sys


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
######### Cache #########
Path_cache = BasePath + '\\Cache\\'


def log_print(message):
    # Append the log message to the Log.txt file and print it
    with open(File_path_log, 'a', encoding='utf-8') as file:
        file.write(message + '\n')
        file.flush()
    print(message)


def exception():
    # Log and print the traceback of the exception
    error = traceback.format_exc()
    exception_type, exception_object, exception_traceback = sys.exc_info()
    log_print(error)


def convertCSVExcel(File_path_CSV, File_path_EXL):
    # Convert CSV file to Excel file
    df = pd.read_csv(File_path_CSV, encoding='utf-8', low_memory=False)
    df.to_excel(File_path_EXL, index=False)


def duplicate(File_path):
    # Remove duplicate rows from the Excel file
    try:
        data = pd.read_excel(File_path)
        data_file = data.drop_duplicates()
        data_file.to_excel(File_path, index=False)
    except:
        pass


def individual_data(profile_url, p_index, page):
    try:
        # time.sleep(5)     #Remove comment if it is facing server error
        indi_data = []
        # Check if the HTML page is already cached
        if os.path.exists('{}Profile_{}_page{}.html'.format(Path_cache, p_index, page)):
            with open('{}Profile_{}_page{}.html'.format(Path_cache, p_index, page), 'r', encoding='utf-8') as fh:
                individual_soup = BeautifulSoup(fh.read(), 'html.parser')
        else:
            # Fetch the individual profile page and cache it
            individual_obj = requests.get(profile_url, timeout=100)     # Use Retry mechanism for request if face any error in this request as Line 188
            with open('{}Profile_{}_page{}.html'.format(Path_cache, p_index, page), 'w', encoding='utf-8') as fh:
                fh.write(individual_obj.content.decode('utf-8'))
            individual_soup = BeautifulSoup(individual_obj.content, 'html.parser')

        # Extract relevant information from the individual profile page
        expertise_text = ''
        research_text = ''
        if individual_soup.find('div', class_='section personal'):
            individual_details = individual_soup.find('div', class_='section personal')
            name_tag = individual_details.find('div', class_='name').find('h1').text.strip() if individual_details.find('div', class_='name').find('h1') else ''
            title_tag = individual_details.find('ul', class_='titles').text.strip() if individual_details.find('ul', class_='titles') else ''
            gender_tag = individual_details.find('div', class_='gender').text.strip() if individual_details.find('div', class_='gender') else ''
            try:
                if individual_details.find('div', class_='expertise').find('h2'):
                    expertise_tag = individual_details.find('div', class_='expertise').find('h2')
                    expertise_text = expertise_tag.find_next_sibling('p').get_text(strip=True).replace('...read more', '')
            except AttributeError:
                pass
            try:
                if individual_details.find('div', class_='research').find('h2'):
                    research_tag = individual_details.find('div', class_='research').find('h2')
                    research_text = research_tag.find_next_sibling('p').get_text(strip=True).replace('...read more', '')
            except AttributeError:
                pass

                    
        phone_tag = ''
        location = ''
        education_tag = ''
        try:
            individual_appointment = individual_soup.find('div', id='Appointments')
            phone_tag = individual_appointment.find('div', class_='col-4 standard').find('div', class_='phone').get_text(separator=' ', strip=True)
        except AttributeError:      # Handle AttributeError if element is not found
            pass
        try:
            individual_location = individual_soup.find('div', id='Locations')
            location_tag = individual_location.find('div', class_='address')
            location = location_tag.get_text(separator='\n', strip=True).replace('map', '').strip()
        except AttributeError:
            pass
        try:
            education_section = individual_soup.find('div', id='Education')
            education_list = education_section.find_all('h3', string=['Degrees', 'Residencies', 'Fellowships'])
            education_tag = ''
            
            for heading in education_list:
                ul = heading.find_next_sibling('ul')
                lis = ul.find_all('li')
                for li in lis:
                    institute = li.get_text(strip=True).split(';')[-1].strip()
                    education_tag += institute + '; '
            
            education_tag = education_tag.rstrip('; ')
            
        except AttributeError:
            pass
        
        indi_data.append(name_tag)
        indi_data.append(title_tag)
        indi_data.append(gender_tag)
        indi_data.append(expertise_text)
        indi_data.append(research_text)
        indi_data.append(phone_tag)
        indi_data.append(location)
        indi_data.append(education_tag)

        with open(File_path_CSV, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(indi_data)
        log_print(f'Completed: {name_tag}     {Profile_url}')
    except:
        exception()


if __name__ == '__main__':
    # Create directories if they don't exist
    directories = [
        BasePath + '\\Log',         # Log directory
        BasePath + '\\OP',          # OP directory
        BasePath + '\\OPcsv',       # OPcsv directory
        Path_cache                  # Cache directory
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

    First_run = True        # Set it False if you do not want to remove files on next run
    if First_run:
        # Remove the existing CSV file
        if os.path.isfile(File_path_CSV):
            os.remove(File_path_CSV)
        if os.path.exists(File_path_log):
            os.remove(File_path_log)

    headers = ['Name', 'Title', 'Gender', 'Expertise', 'Research Interests', 'Phone', 'Location', 'Education']
    with open(File_path_CSV, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            # Write the headers to the CSV file if it's empty
            writer.writerow(headers)
            
    # List of user agents to prevant detecting the device and browser
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
        outerRetry = 1      # Retry mechanism for requests
        while outerRetry <= retry_attempts:
            try:
                # Get the content of the first page to extract the last page number
                obj_temp = requests.get(Search_url.format(1), headers=Headers, timeout=200)
                break
            except Exception as e:
                log_print(f"Error occurred")
                Headers = {'User-Agent': user_agent}
                delay = retry_delay * (2 ** outerRetry)
                log_print(f'Retrying in {delay} seconds...RETRY: {outerRetry}')
                time.sleep(delay)
                outerRetry += 1
                continue
        else:
            exit(1)

        soup_temp = BeautifulSoup(obj_temp.content, 'html.parser')
        last_page_number = 1

        paginate_element = soup_temp.find('ol', class_='paginate')
        if paginate_element is not None:
            # Get the last page number from the pagination element
            last_page_element = paginate_element.find_all('a', class_='page-button')[-1]
            last_page_number = int(last_page_element['data-page'])

        for index in range(1, last_page_number + 1):
            # time.sleep(10)     # Remove comment if it is facing server error
            user_agent = random.choice(user_agents)
            Headers = {'User-Agent': user_agent}
            innerRetry = 1
            while innerRetry <= retry_attempts:
                try:
                    # Get the content of each page
                    obj = requests.get(Search_url.format(index), headers=Headers, timeout=200)
                    break
                except Exception as e:
                    log_print(f"Error occurred")
                    Headers = {'User-Agent': user_agent}
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
                profile_index = profiles.index(profile)
                Profile_url = Base_url + profile.find('a', href=True).get('href')
                individual_data(Profile_url, profile_index, index)
            log_print(f"\n---------------------------------- Page {index} Completed out of {last_page_number} ----------------------------------\n")
        log_print("\nScript Completed")
        
    except:
        exception()

    finally:
        # Convert the CSV file to Excel format
        convertCSVExcel(File_path_CSV, File_path)
        # Remove duplicate entries in the Excel file
        duplicate(File_path)
        
        exit(0)
