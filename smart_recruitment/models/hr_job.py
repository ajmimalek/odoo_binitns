import base64
import os
from time import sleep

import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Odoo imports
from webdriver_manager.chrome import ChromeDriverManager

from odoo import fields, models, modules, _


def _get_default_image():
    image_path = modules.get_module_resource('smart_recruitment', 'static/img', 'BinitNS_Hiring.png')
    return base64.b64encode(open(image_path, 'rb').read())


class HrJob(models.Model):
    _inherit = 'hr.job'
    post_image = fields.Image(string="Image Publication LinkedIn",
                              help="Cette Image va être ajoutée à la publication sur LinkedIn",
                              default=_get_default_image())

    def publish_linkedin(self):
        """ Button function for sharing post and job on linkedin """
        print("Publishing to LinkedIn")
        linkedin_auth_provider = self.env.ref('smart_recruitment.provider_linkedin')
        access_token = self.env['auth.oauth.provider'].search([('name', '=', 'LinkedIn')]).access_token
        if access_token:
            print(access_token)
            profile_id = requests.get(linkedin_auth_provider.data_endpoint, headers={'Authorization': 'Bearer ' + access_token}).json()['id']
            print("Profile ID : ", profile_id)
            shares = requests.post('https://api.linkedin.com/v2/shares', headers={
                     'Authorization': 'Bearer ' + access_token}, data={
                "content": {
                    "contentEntities": [
                        {
                            "entityLocation": "https://www.example.com/content.html",
                            "thumbnails": [
                                {
                                    "resolvedUrl": "https://www.example.com/image.jpg"
                                }
                            ]
                        }
                    ],
                    "title": "Test Share with Content"
                },
                "distribution": {
                    "linkedInDistributionTarget": {}
                },
                "owner": "urn:li:person:" + profile_id,
                "text": {
                    "text": self.description
                }
            }).json()
            print(shares)
        else:
            raise Warning("Veuillez générer un token d'accès pour LinkedIn")

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
        # chrome_options.headless = True
        chrome_options.add_argument("log-level=3")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        # Authenticate on Linkedin
        driver.get("https://www.linkedin.com/login")
        sleep(2)
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        sleep(2)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        sleep(2)
        # Search for profiles
        driver.get("https://www.google.com/")
        search_query = driver.find_element(By.NAME, "q")
        search_query.send_keys('site:linkedin.com/in/ AND "{}" AND "Tunisia"'.format(self.name))
        # Press Enter to search
        search_query.send_keys(Keys.RETURN)
        links = driver.find_elements(By.XPATH, '//div[@class="yuRUbf"]/a[@href]')
        links_values = [link.get_attribute("href") for link in links]
        print("Links found: ", links_values)
        # Go to Google page i [2..4]
        for i in range(2, 5):
            try:
                driver.find_element(By.XPATH, '//a[@aria-label="Page ' + str(i) + '"]').click()
            except NoSuchElementException:
                break
            sleep(2)
            links = driver.find_elements(By.XPATH, '//div[@class="yuRUbf"]/a[@href]')
            for link in links:
                links_values.append(link.get_attribute("href"))
            print("Links ", i, " found: ", links_values)
        try:
            # Reset ID Sequence
            self.env.cr.execute("ALTER SEQUENCE smart_recruitement_profile_id_seq RESTART WITH 1")
            # delete profiles where saved is false
            profiles = self.env['smart_recruitement.profile'].search(
                [('job_id', '=', self.id), ('saved', '=', False)]).unlink()
            print("Profiles deleted")
            # Scrape LinkedIn profiles from search results and save them in the database
            for index, link in enumerate(links_values):
                driver.get(link)
                sleep(4)
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
                picture = driver.find_element(By.XPATH, '//img[@alt="' + name + '"]').get_attribute("src")
                if picture.startswith('data:image'):
                    picture = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460__340.png"
                print("Picture: ", picture)
                self.env['smart_recruitement.profile'].create({
                    'name': name,
                    'linkedin_url': link,
                    'current_company': current_company,
                    'picture': picture,
                    'job_id': self.id
                })
                print("Profile " + str(index) + " added to database")
        except NoSuchElementException:
            print("Error while scraping LinkedIn profiles")
        # Close browser
        driver.close()
        return {
            'name': _('Profiles LinkedIn'),
            'res_model': 'smart_recruitement.profile',
            'view_mode': 'kanban,list',
            'domain': [('job_id', '=', self.id)],
            'context': {},
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('smart_recruitment.view_hr_profiles_kanban_view').id, 'kanban')]
        }
