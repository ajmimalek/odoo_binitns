from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from odoo import fields, models, _, exceptions
from time import sleep


class HrProfile(models.Model):
    _name = 'smart_recruitement.profile'
    _description = 'Model for collected profiles for specific job'

    name = fields.Char('Profile Name')
    current_company = fields.Text('Current Company')
    picture = fields.Text('Picture')
    linkedin_url = fields.Char('LinkedIn URL')
    saved = fields.Boolean('Saved', default=False)
    job_id = fields.Many2one('hr.job', 'Job Name', ondelete='set null', index=True)

    def send_message(self):
        msg = "Bonjour " + self.name + ",\n\nJ'espère que tu vas bien !\nTon expérience actuelle au sein du " + self.current_company + " est très intéressante.\nNous avons le plaisir de te proposer un poste d'un " + self.job_id.name + " avec notre équipe Jeune et motivé.\n\nSalutations,\n\n" + "L'équipe RH du BinitNS!"
        print(msg)
        if self.env['ir.config_parameter'].sudo().get_param('recruitment.li_username'):
            username = self.env['ir.config_parameter'].sudo().get_param('recruitment.li_username')
            print('Username: ' + username)
        else:
            raise exceptions.Warning("Veuillez saisir le nom d'utilisateur dans les paramètres d'identification LinkedIn")

        if self.env['ir.config_parameter'].sudo().get_param('recruitment.li_password'):
            password = self.env['ir.config_parameter'].sudo().get_param('recruitment.li_password')
            print('Password: ' + password)
        else:
            raise exceptions.Warning("Veuillez saisir le mot de passe dans les paramètres d'identification LinkedIn")
        chrome_options = Options()
        chrome_options.headless = True
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
        # Go to the profile page
        driver.get(self.linkedin_url)
        sleep(2)
        # Send message
        if driver.find_element(By.XPATH, "//a[@role='button']"):
            msg_link = driver.find_element(By.XPATH, "//a[@role='button']").get_attribute('href')
            sleep(2)
            driver.get(msg_link)
            sleep(2)
            driver.find_element(By.XPATH, "//div[@role='textbox']/p").send_keys(msg)
            sleep(2)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
        else:
            if driver.find_element(By.XPATH, "//button[startswith(@aria-label, 'Invitez')]"):
                driver.find_element(By.XPATH, "//button[startswith(@aria-label, 'Invitez')]").click()
                driver.find_element(By.XPATH, "//button[@aria-label='Ajouter une note']").click()
                driver.find_element(By.TAG_NAME, "textarea").send_keys(msg)
                sleep(2)
                driver.find_element(By.XPATH, "//button[@aria-label='Envoyer maintenant']").click()
            else:
                raise exceptions.Warning("Veuillez vérifier que vous êtes connecté à LinkedIn et que vous avez accès à votre profil")
        driver.close()