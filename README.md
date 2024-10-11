## Job Scraper for Indeed

## Prerequisites 
Before using the script, make sure you have the following installed:

- [Python 3.x](https://www.python.org/downloads/)
- [Chrome browser](https://www.google.com/chrome/)
- [ChromeDriver](https://chromedriver.chromium.org/downloads)

This project consists of two Python scripts & bat file designed to scrape job listings from Indeed.com for various countries and job positions.

## Files:
1. Main.py
2. job_scraper_utils.py
3. Srape.bat

## Dependencies:
- Python 3.7+
- See requirements.txt for a full list of required packages

## Setup:
1. Install the required dependencies:
   ```bash
   
   pip install -r requirements.txt
   
   ```
2. Ensure you have Chrome browser installed on your system.

## Usage:

1. main.py:
   This is the main script that you'll run to scrape job listings.

   - It's currently set up to search for "Banker" jobs in "Melbourne", Australia.
   - The script will create a 'csv_files' directory in the same location as the script.
   - The scraped job data will be saved as a CSV file in this directory.

   To run:
   ```bash
   
   python main.py

   ```
   
   To modify the search parameters, edit the following variables in the main() function:
   - country = australia  (Choose from the list of country variables at the top of the script)
   - job_position = 'Banker'
   - job_location = 'Melbourne'
   - date_posted = 10  (Number of days to look back)

2. job_scraper_utils.py:
   This script contains utility functions used by main.py. It includes functions for:
   - Configuring the webdriver
   - Searching for jobs
   - Scraping job data
   - Cleaning and sorting the scraped data

   You don't need to run this script directly, but you can modify its functions to change how the scraping works.

Output:
The script will create a CSV file named in the format:
{job_position}_{job_location}_{current_date}.csv

This file will contain the following information for each job listing:
- Link
- Job Title
- Company
- Date Posted
- Location
- Job Description
- Salary
- Search Query

## Note:
Web scraping may be against the terms of service of some websites. Ensure you have permission to scrape data from Indeed.com and use the data responsibly. Be mindful of the rate at which you're making requests to avoid overloading the server.

## Note:
The scrape.bat file, is to be used when you have multiple main.py for different positions and locations. will need to modify ":: Set the list of Python scripts to run"
