from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    li_username = fields.Char(string="User Name", help="Your Linkedin Username")
    li_password = fields.Char(string="Password", help="Your Linkedin Password")

    def set_values(self):

        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('recruitment.company_page_id', self.company_page_id)
        self.env['ir.config_parameter'].sudo().set_param('recruitment.li_username', self.li_username)
        self.env['ir.config_parameter'].sudo().set_param('recruitment.li_password', self.li_password)

    def get_values(self):
            res = super(ResConfigSettings, self).get_values()
            res.update(
                company_page_id=self.env['ir.config_parameter'].sudo().get_param('recruitment.company_page_id'),
                li_username = self.env['ir.config_parameter'].sudo().get_param('recruitment.li_username'),
                li_password = self.env['ir.config_parameter'].sudo().get_param('recruitment.li_password')
            )
            return res