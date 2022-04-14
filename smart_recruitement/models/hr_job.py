# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from time import sleep

# Odoo imports
from odoo import fields, models, api


class HrJobShare(models.Model):
    _inherit = 'hr.job'

    #profile_id = fields.One2many('smart_recruitement.profile', string='Profile ID')

    def publish_linkedin(self):
        """ Button function for sharing post and job on linkedin """
        print("Publishing to LinkedIn")

    def collect_profiles(self):
        """ Button function for collecting profiles from linkedin """
        print("Collecting profiles from LinkedIn")
        # Headless browser
        chrome_options = Options()
        chrome_options.headless = True
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get("https://www.google.com/")
        search_query = driver.find_element(By.NAME, "q")
        search_query.send_keys('site:linkedin.com/in/ AND "{}" AND "Tunisia"'.format(self.name))
        # Press Enter to search
        search_query.send_keys(Keys.RETURN)
        links = driver.find_elements(By.XPATH, '//div[@class="yuRUbf"]/a[@href]')
        links_values = [link.get_attribute("href") for link in links]
        print("Links found: ", links_values)
        titles = driver.find_elements(By.XPATH, '//div[@class="yuRUbf"]/a[@href]/h3')
        names = [title.text[:title.text.find('-')] for title in titles]
        print("Names found: ", names)
        current_company = driver.find_elements(By.XPATH, '//div[@class="MUxGbd wuQ4Ob WZ8Tjf"]/span[last()]')
        companies = [company.text for company in current_company]
        print("Companies found: ", companies)
        # Close browser
        driver.close()
        # Add profiles to database
        for i in range(len(links_values)):
            self.env['smart_recruitement.profile'].create({
                'name': names[i],
                'linkedin_url': links_values[i],
                'current_company': companies[i],
                'job_id': self.id
            })
            print("Profile added to database")
