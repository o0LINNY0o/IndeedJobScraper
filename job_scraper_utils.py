import os
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def configure_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    return driver

def search_jobs(driver, country, job_position, job_location, date_posted):
    full_url = f'{country}/jobs?q={"+".join(job_position.split())}&l={job_location}&fromage={date_posted}'
    print(full_url)
    driver.get(full_url)
    try:
        job_count_element = driver.find_element(By.XPATH,
                                                '//div[starts-with(@class, "jobsearch-JobCountAndSortPane-jobCount")]')
        total_jobs = job_count_element.find_element(By.XPATH, './span').text
        print(f"{total_jobs} found")
    except NoSuchElementException:
        print("No job count found")
        total_jobs = "Unknown"
    return job_position, total_jobs

def scrape_job_data(driver, country, job_position, total_jobs):
    df = pd.DataFrame(columns=['Link', 'Job Title', 'Company', 'Date Posted', 'Location', 'Job Description', 'Salary', 'Search Query'])
    job_count = 0

    while True:
        soup = BeautifulSoup(driver.page_source, 'lxml')
        boxes = soup.find_all('div', class_='job_seen_beacon')

        for box in boxes:
            link = box.find('a').get('href')
            link_full = country + link
            job_title = box.find('a', class_='jcs-JobTitle css-jspxzf eu4oa1w0').text
            
            company_tag = box.find('span', {'data-testid': 'company-name'})
            company = company_tag.text if company_tag else None

            try:
                date_posted = box.find('span', class_='date').text
            except AttributeError:
                date_posted = box.find('span', {'data-testid': 'myJobsStateDate'}).text.strip()

            location_element = box.find('div', {'data-testid': 'text-location'})
            location = location_element.find('span').text if location_element and location_element.find('span') else location_element.text if location_element else ''

            # Scrape job description and salary information from the job page
            driver.get(link_full)
            soup_job_page = BeautifulSoup(driver.page_source, 'lxml')
            
            job_description_element = soup_job_page.find('div', id='jobDescriptionText')
            job_description_text = job_description_element.get_text(strip=True) if job_description_element else "Unknown"

            salary_element = soup_job_page.find('div', id='salaryInfoAndJobType')
            salary_text = 'Unknown'
            if salary_element:
                spans = salary_element.find_all('span')
                salary_text = ' '.join([span.get_text(strip=True) for span in spans]) if spans else salary_element.text.strip()

            new_data = pd.DataFrame({
                'Link': [link_full], 'Job Title': [job_title], 'Company': [company],
                'Date Posted': [date_posted], 'Location': [location],
                'Job Description': [job_description_text], 'Salary': [salary_text],
                'Search Query': [job_position]
            })

            df = pd.concat([df, new_data], ignore_index=True)
            job_count += 1

        print(f"Scraped {job_count} of {total_jobs}")

        next_page = soup.find('a', {'aria-label': 'Next Page'})
        if next_page:
            next_page_url = country + next_page.get('href')
            driver.get(next_page_url)
        else:
            break

    return df

def clean_data(df):
    def clean_posted(x):
        x = x.replace('PostedPosted', '').strip()
        x = x.replace('EmployerActive', '').strip()
        x = x.replace('PostedToday', '0').strip()
        x = x.replace('PostedJust posted', '0').strip()
        x = x.replace('today', '0').strip()
        x = x.replace('days ago', '').strip()
        x = x.replace('day ago', '').strip()
        x = x.replace('+', '').strip()
        return x

    df['Date Posted'] = df['Date Posted'].apply(clean_posted)
    return df

def sort_data(df):
    def convert_to_integer(x):
        try:
            return int(x)
        except ValueError:
            return float('inf')

    df['Date_num'] = df['Date Posted'].apply(lambda x: x[:2].strip())
    df['Date_num2'] = df['Date_num'].apply(convert_to_integer)
    df.sort_values(by=['Date_num2'], inplace=True)
    df = df[['Link', 'Job Title', 'Company', 'Date Posted', 'Location', 'Job Description', 'Salary', 'Search Query']]
    return df
