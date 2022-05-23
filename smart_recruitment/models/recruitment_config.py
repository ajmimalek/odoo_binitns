import secrets

import mechanicalsoup
import requests
from mechanicalsoup import LinkNotFoundError

from odoo import models, fields
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    li_username = fields.Char(string="Nom d'utilisateur", help="Email ou téléphone")
    li_password = fields.Char(string="Mot de Passe", help="Mot de passe Linkedin")

    def set_values(self):

        super(ResConfigSettings, self).set_values()
        # self.env['ir.config_parameter'].sudo().set_param('recruitment.company_page_id', self.company_page_id)
        self.env['ir.config_parameter'].sudo().set_param('recruitment.li_username', self.li_username)
        self.env['ir.config_parameter'].sudo().set_param('recruitment.li_password', self.li_password)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            # company_page_id=self.env['ir.config_parameter'].sudo().get_param('recruitment.company_page_id'),
            li_username=self.env['ir.config_parameter'].sudo().get_param('recruitment.li_username'),
            li_password=self.env['ir.config_parameter'].sudo().get_param('recruitment.li_password')
        )
        return res

    def get_access_token(self):
        linkedin_auth_provider = self.env.ref('smart_recruitment.provider_linkedin')
        client_secret = linkedin_auth_provider.client_secret
        if linkedin_auth_provider.client_id and linkedin_auth_provider.client_secret:
            redirect_uri = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            print(redirect_uri)
            url = requests.Request('GET', linkedin_auth_provider.auth_endpoint,
                                   params={
                                       'response_type': 'code',
                                       'client_id': linkedin_auth_provider.client_id,
                                       'redirect_uri': redirect_uri,
                                       'state': secrets.token_hex(8).upper(),
                                       'scope': linkedin_auth_provider.scope,
                                   }).prepare().url
            print(url)
            br = mechanicalsoup.StatefulBrowser()
            br.open(url)
            br.select_form('.login__form')
            br['session_key'] = self.li_username
            br['session_password'] = self.li_password
            br.submit_selected()
            if br.get_url() == redirect_uri:
                raise ValidationError("Veuillez vérifier vos identifiants Linkedin")
            else:
                try:
                    br.select_form('#oauth__auth-form')
                    br.submit_selected()
                except LinkNotFoundError:
                    print("Successfully logged in")
                code = br.get_url().split('=')[1]
                final_code = code.split('&')[0]
                print(final_code)
                print("Ligne 62 : ", client_secret)
                print(type(client_secret))
                access_token = requests.post('https://www.linkedin.com/oauth/v2/accessToken',
                                       params={
                                           'grant_type': 'authorization_code',
                                           'code': final_code,
                                           'redirect_uri': redirect_uri,
                                           'client_id': linkedin_auth_provider.client_id,
                                           'client_secret': client_secret
                                       }).json()['access_token']
                self.env['auth.oauth.provider'].sudo().search([('name', '=', 'LinkedIn')]).write({'access_token': access_token})
        elif linkedin_auth_provider.client_id and not linkedin_auth_provider.client_secret:
            raise ValidationError("Veuillez introduire le client secret")
        elif not linkedin_auth_provider.client_id and linkedin_auth_provider.client_secret:
            raise ValidationError("Veuillez introduire le client id")
        else:
            raise ValidationError("Veuillez introduire le client id et le client secret")
        title = "Opération Réussite!"
        message = "Votre Access Token est généré avec succès! Vous pouvez maintenant utiliser le service."
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'sticky': False,
            }
        }