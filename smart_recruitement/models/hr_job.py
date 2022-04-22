# Selenium imports
import os
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options

# Odoo imports
from odoo import fields, models, api, _


class HrJob(models.Model):
    _inherit = 'hr.job'
    years_of_experience = fields.Char("Années d'expérience requise")

    def publish_linkedin(self):
        """ Button function for sharing post and job on linkedin """
        print("Publishing to LinkedIn")

    @api.model
    def collect_profiles(self):
        """ Button function for collecting profiles from linkedin """
        print("Collecting profiles from LinkedIn")
        chrome_options = Options()
        chrome_options.headless = True
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        # Search for profiles
        driver.get("https://www.google.com/")
        search_query = driver.find_element(By.NAME, "q")
        search_query.send_keys('site:linkedin.com/in/ AND "{}" AND "Tunisia"'.format(self.name))
        # Press Enter to search
        search_query.send_keys(Keys.RETURN)
        links = driver.find_elements(By.XPATH, '//div[@class="yuRUbf"]/a[@href]')
        links_values = [link.get_attribute("href") for link in links]
        print("Links found: ", links_values)
        print("Length of links: ", len(links_values))
        cwd = os.getcwd()  # Get the current working directory (cwd)
        path = cwd + '\odoo\custom_addons\smart_recruitement\models\config.txt'
        # Open linkedin
        driver.get("https://www.linkedin.com/uas/login")
        file = open(path, 'r')
        lines = file.readlines()
        username = lines[0]
        time.sleep(3)
        email = driver.find_element(By.ID, "username")
        email.send_keys(username)
        password = driver.find_element(By.ID, "password")
        password.send_keys("workisbusiness12")
        time.sleep(3)
        password.send_keys(Keys.RETURN)
        time.sleep(3)
        # Reset ID Sequence
        self.env.cr.execute("ALTER SEQUENCE smart_recruitement_profile_id_seq RESTART WITH 1")
        # delete profiles where saved is false
        profiles = self.env['smart_recruitement.profile'].search(
            [('job_id', '=', self.id), ('saved', '=', False)]).unlink()
        # Scrape LinkedIn profiles from search results and save them in the database
        for index, link in enumerate(links_values):
            driver.get(link)
            time.sleep(2)
            # Get Name of the profile
            name = driver.find_element(By.TAG_NAME, 'h1').text
            print("Name: ", name)
            # Get the cuurent company of the profile
            try:
                current_company = driver.find_element(By.XPATH, "//div[@aria-label='Current company']").text
            except NoSuchElementException:
                current_company = "Pas d'emploi actuel"
            print("Current company: ", current_company)
            # Get the picture of the profile
            picture = driver.find_element(By.XPATH, '//img[@title="' + name + '"]').get_attribute("src")
            if picture.startswith('data:image'):
                picture = "https://pngset.com/images/default-profile-picture-circle-symbol-logo-trademark-number-transparent-png-890174.png"
            print("Picture: ", picture)
            self.env['smart_recruitement.profile'].create({
                'name': name,
                'linkedin_url': link,
                'current_company': current_company,
                'picture': picture,
                'job_id': self.id
            })
            print("Profile " + str(index) + " added to database")
            if index == len(links_values) / 2:
                time.sleep(4)
        # Close browser
        driver.close()
        # Return Kanban view
        return {
            'name': _('Profiles Linkedin'),
            'type': 'ir.actions.act_window',
            'res_model': 'smart_recruitement.profile',
            # 'view_id': self.env.ref('hr_recruitment.view_hr_profiles_kanban_linkedin').id,
            'view_mode': 'kanban',
            'view_type': 'kanban,list',
            'res_id': self.id,
            'target': 'current',
        }
