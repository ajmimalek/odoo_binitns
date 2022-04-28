import base64
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from linkedin_scraper import Person, actions
# Odoo imports
from odoo import fields, models, modules


def _get_default_image():
    image_path = modules.get_module_resource('smart_recruitment', 'static/img', 'BinitNS_Hiring.png')
    return base64.b64encode(open(image_path, 'rb').read())


class HrJob(models.Model):
    _inherit = 'hr.job'
    years_of_experience = fields.Char("Années d'expérience requise")
    post_image = fields.Image(string="Image Publication LinkedIn",
                              help="Cette Image va être ajoutée à la publication sur LinkedIn",
                              default=_get_default_image())

    def publish_linkedin(self):
        """ Button function for sharing post and job on linkedin """
        print("Publishing to LinkedIn")

    def collect_profiles(self):
        """ Button function for collecting profiles from linkedin """
        print("Collecting profiles from LinkedIn")
        cwd = os.getcwd()  # Get the current working directory (cwd)
        path = cwd + '\odoo\custom_addons\smart_recruitment\models\config.txt'
        file = open(path, 'r')
        lines = file.readlines()
        username = lines[0]
        password = lines[1]
        file.close()
        # Search for Linkedin Profiles
        chrome_options = Options()
        #chrome_options.headless = True
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        # Search for profiles
        driver.get("https://www.google.com/")
        search_query = driver.find_element(By.NAME, "q")
        search_query.send_keys('site:linkedin.com/in/ AND "{}" AND "Tunisia"'.format(self.name))
        # Press Enter to search
        search_query.send_keys(Keys.RETURN)
        links = driver.find_elements(By.XPATH, '//div[@class="yuRUbf"]/a[@href]')
        links_values = [link.get_attribute("href") for link in links]
        print("Links found: ", links_values)
        # Authenticate using any Linkedin account credentials
        actions.login(driver, username, password)
        person = Person(links_values[0], driver=driver)
        print(person)
        # Close browser
        driver.close()
