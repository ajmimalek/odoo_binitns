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
    image_path = modules.get_module_resource('linkedin_integration', 'static/img', 'BinitNS_Hiring.png')
    return base64.b64encode(open(image_path, 'rb').read())


class HrJob(models.Model):
    _inherit = 'hr.job'
    post_image = fields.Image(string="Image Publication LinkedIn",
                              help="Cette Image va être ajoutée à la publication sur LinkedIn",
                              default=_get_default_image())

    def publish_linkedin(self):
        """ Button function for sharing post and job on linkedin """
        print("Publishing to LinkedIn")
        linkedin_auth_provider = self.env.ref('linkedin_integration.provider_linkedin')
        access_token = self.env['auth.oauth.provider'].search([('name', '=', 'LinkedIn')]).access_token
        if access_token:
            print(access_token)
            profile_id = requests.get(linkedin_auth_provider.data_endpoint,
                                      headers={'Authorization': 'Bearer ' + access_token}).json()['id']
            print("Profile ID : ", profile_id)
            desc = ""
            if not self.description:
                desc = ""
            else:
                desc = self.description
            text = "Offre d'emploi : " + self.name + "\n" + desc
            print("Text : ", text)
            shares = requests.post('https://api.linkedin.com/v2/shares', headers={
                'Authorization': 'Bearer ' + access_token}, data={
                "content": {
                    "contentEntities": [
                        {
                            "thumbnails": [
                                {
                                    "resolvedUrl": "https://i.ibb.co/JxX1hDW/Binit-NS-Hiring.png"
                                }
                            ]
                        }
                    ],
                    "shareMediaCategory": "IMAGE"
                },
                "distribution": {
                    "linkedInDistributionTarget": {}
                },
                "owner": "urn:li:person:" + profile_id,
                "text": {
                    "text": text
                }
            }).json()
            print(shares)
            title = "Statut : " + str(shares['status'])
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': title,
                    'message': shares['message'],
                    'sticky': False,
                }
            }
        else:
            raise Warning("Veuillez générer un token d'accès pour LinkedIn")

    def collect_profiles(self):
        """ Button function for collecting profiles from linkedin """
        print("Collecting profiles from LinkedIn")
        cwd = os.getcwd()  # Get the current working directory (cwd)
        path = cwd + '\odoo\custom_addons\linkedin_integration\models\config.txt'
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
            # delete profiles where saved is false
            profiles = self.env['linkedin_integration.profile'].search(
                [('saved', '=', False)]).unlink()
            print("Profiles deleted")
            # Reset ID Sequence
            self.env.cr.execute("SELECT setval('linkedin_integration_profile_id_seq', "
                                "(SELECT MAX(id) FROM linkedin_integration_profile)+1)")
            # Scrape LinkedIn profiles from search results and save them in the database
            for index, link in enumerate(links_values):
                driver.get(link)
                sleep(4)
                # Get Name of the profile
                name = driver.find_element(By.TAG_NAME, 'h1').text
                print("Name: ", name)
                # Get the cuurent company of the profile
                try:
                    current_company = driver.find_element(By.XPATH, '//button[starts-with(@aria-label, "Current company")]').get_attribute("aria-label")
                    current_company = current_company[current_company.find(":")+1:current_company.find(".")+1]
                except NoSuchElementException:
                    current_company = "Pas d'emploi actuel"
                print("Current company: ", current_company)
                # Get the school of the profile
                try:
                    school = driver.find_element(By.XPATH, '//button[starts-with(@aria-label, "Education")]').get_attribute("aria-label")
                    school = school[school.find(":")+1:school.find(".")+1]
                except NoSuchElementException:
                    school = "Pas d'école"
                print("School: ", school)
                # Get the picture of the profile
                picture = driver.find_element(By.XPATH, '//img[@alt="' + name + '"]').get_attribute("src")
                if picture.startswith('data:image'):
                    picture = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460__340.png"
                print("Picture: ", picture)
                # Go to Experiences section
                try:
                    driver.find_element(By.XPATH, "//a[contains(@href,'details/experience')]").click()
                except NoSuchElementException:
                    print("Pas de page d'expériences : situé dans la section 'Experiences' dans profile")
                sleep(2)
                texts = driver.find_elements(By.XPATH,
                                             '//span[@class="t-14 t-normal t-black--light"]/span[@aria-hidden="true"]')
                data = [elem.text for elem in texts]
                exp = []
                for elem in data:
                    if ('mo' in elem or 'yr' in elem) and True in [char.isdigit() for char in elem]:
                        exp.append(elem)
                exp = [elem[elem.find('·') + 2:] for elem in exp]
                mois = 0
                for elem in exp:
                    print("elem = ", elem)
                    if 'mos' in elem:
                        print("mois : ", elem[elem.find('mos') - 2])
                        mois += int(elem[elem.find('mos') - 2])
                    elif 'mo' in elem:
                        mois += 1
                    if 'yrs' in elem:
                        print("années : ", elem[elem.find('yrs') - 2])
                        mois += int(elem[elem.find('yrs') - 2]) * 12
                    elif 'yr' in elem:
                        mois += 12
                saved_profiles = self.env['linkedin_integration.profile'].search([('saved', '=', True)]).mapped('name')
                if name not in saved_profiles:
                    self.env['linkedin_integration.profile'].create({
                            'name': name,
                            'linkedin_url': link,
                            'current_company': current_company,
                            'school': school,
                            'picture': picture,
                            'months_experiences': mois,
                            'job_id': self.id
                    })
                    print("Profile " + str(index) + " added to database")
        except NoSuchElementException:
            print("Error while scraping LinkedIn profiles")
        # Close browser
        driver.close()
        return {
            'name': _('Profiles LinkedIn'),
            'res_model': 'linkedin_integration.profile',
            'view_mode': 'kanban',
            'domain': [('job_id', '=', self.id)],
            'context': {},
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('linkedin_integration.view_hr_profiles_kanban_view').id, 'kanban')],
        }
