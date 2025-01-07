import os
import pandas as pd
import time
from bs4 import BeautifulSoup
from seleniumbase import Driver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

def configure_webdriver():
    # SeleniumBase provides a simplified way to create a driver with built-in stealth
    driver = Driver(uc=True,  # Uses undetected-chromedriver
                   headless=True,
                   agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return driver

def search_jobs(driver, country, job_position, job_location, date_posted):
    full_url = f'{country}/jobs?q={"+".join(job_position.split())}&l={job_location}&fromage={date_posted}'
    print(full_url)
    driver.get(full_url)
    driver.sleep(0.1)  # SeleniumBase's smart wait
    
    try:
        # Using SeleniumBase's improved element finding
        job_count_element = driver.find_element(
            By.CSS_SELECTOR, 
            'div[class*="jobsearch-JobCountAndSortPane-jobCount"] span'
        )
        total_jobs = job_count_element.text
        print(f"{total_jobs} found")
    except NoSuchElementException:
        print("No job count found")
        total_jobs = "Unknown"
    return job_position, total_jobs

def scrape_job_data(driver, country, job_position, total_jobs):
    df = pd.DataFrame(columns=['Link', 'Job Title', 'Company', 'Location', 'Job Description', 'Salary', 'Search Query'])
    job_count = 0

    while True:
        # Wait for job listings to be visible
        driver.wait_for_element_present('div.job_seen_beacon')
        soup = BeautifulSoup(driver.get_page_source(), 'lxml')
        boxes = soup.find_all('div', class_='job_seen_beacon')

        for box in boxes:
            link = box.find('a').get('href')
            link_full = country + link
            job_title = box.select_one('h2.jobTitle').text.strip()
            
            company_tag = box.find('span', {'data-testid': 'company-name'})
            company = company_tag.text if company_tag else None

            location_element = box.find('div', {'data-testid': 'text-location'})
            location = location_element.find('span').text if location_element and location_element.find('span') else location_element.text if location_element else ''
            
            # Navigate to job details page
            driver.get(link_full)
            driver.wait_for_element_present('#jobDescriptionText')
            soup_job_page = BeautifulSoup(driver.get_page_source(), 'lxml')
            
            job_description_element = soup_job_page.find('div', id='jobDescriptionText')
            job_description_text = job_description_element.get_text(strip=True) if job_description_element else "Unknown"

            salary_element = soup_job_page.find('div', id='salaryInfoAndJobType')
            salary_text = 'Unknown'
            if salary_element:
                spans = salary_element.find_all('span')
                salary_text = ' '.join([span.get_text(strip=True) for span in spans]) if spans else salary_element.text.strip()

            new_data = pd.DataFrame({
                'Link': [link_full], 
                'Job Title': [job_title], 
                'Company': [company],
                'Location': [location],
                'Job Description': [job_description_text], 
                'Salary': [salary_text],
                'Search Query': [job_position]
            })

            df = pd.concat([df, new_data], ignore_index=True)
            job_count += 1

        print(f"Scraped {job_count} of {total_jobs}")

        next_page = soup.find('a', {'aria-label': 'Next Page'})
        if next_page:
            next_page_url = country + next_page.get('href')
            driver.get(next_page_url)
            driver.sleep(0.1)  # Allow page to load
        else:
            break

    return df

def sort_data(df):
    return df[['Link', 'Job Title', 'Company', 'Location', 'Job Description', 'Salary', 'Search Query']]
