# Selenium imports
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options

# Odoo imports
from odoo import fields, models, api

class HrJob(models.Model):
    _inherit = 'hr.job'

    years_of_experience = fields.Integer('Years of Experience')

    def publish_linkedin(self):
        """ Button function for sharing post and job on linkedin """
        print("Publishing to LinkedIn")

    def collect_profiles(self):
        """ Button function for collecting profiles from linkedin """
        print("Collecting profiles from LinkedIn")
        chrome_options = Options()
        #chrome_options.headless = True
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
        titles = driver.find_elements(By.XPATH, '//div[@class="yuRUbf"]/a[@href]/h3')
        names = [title.text[:title.text.find('-')] for title in titles]
        print("Names found: ", names)
        print("Length of names: ", len(names))
        # Open linkedin
        driver.get("https://www.linkedin.com/uas/login")
        time.sleep(3)
        email = driver.find_element(By.ID, "username")
        email.send_keys("mouradbenahmed68@gmail.com")
        password = driver.find_element(By.ID, "password")
        password.send_keys("workisbusiness12")
        time.sleep(3)
        password.send_keys(Keys.RETURN)
        time.sleep(3)
        # Scrape LinkedIn profiles for each link
        # Close browser
        driver.close()
        # Reset ID Sequence
        self.env.cr.execute("ALTER SEQUENCE smart_recruitement_profile_id_seq RESTART WITH 1")
        # delete profiles where saved is false
        profiles = self.env['smart_recruitement.profile'].search(
            [('job_id', '=', self.id), ('saved', '=', False)]).unlink()
        # Add profiles to database
        for i in range(len(links_values)):
            self.env['smart_recruitement.profile'].create({
                'name': names[i],
                'linkedin_url': links_values[i],
                'job_id': self.id
            })
            print("Profile " + str(i) + " added to database")
        # Return Kanban view
        return {
            'name': 'Profiles Linkedin',
            'type': 'ir.actions.act_window',
            'res_model': 'smart_recruitement.profile',
            #'view_id': self.env.ref('hr_recruitment.view_hr_profiles_kanban_linkedin').id,
            'view_mode': 'kanban',
            'view_type': 'kanban,list',
            'res_id': self.id,
            'target': 'current',
        }
