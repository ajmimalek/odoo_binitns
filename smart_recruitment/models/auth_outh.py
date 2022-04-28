from odoo import models, fields, api


class OAuthProviderLinkedin(models.Model):

    _inherit = 'auth.oauth.provider'

    """ Adding client_secret field because some apps likes twitter, 
    linkedIn are using this value for its API operations """

    client_secret = fields.Char(string='Client Secret', help="Only need LinkedIn, Twitter etc..")
