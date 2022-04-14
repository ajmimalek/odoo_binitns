from odoo import fields, models, api


class Profile(models.Model):
    _name = 'smart_recruitement.profile'
    _description = 'Model for collected profiles for specific job'

    name = fields.Char('Profile Name')
    current_company = fields.Char('Current Company')
    linkedin_url = fields.Char('LinkedIn URL')
    saved = fields.Boolean('Saved', default=False)
    job_id = fields.Many2one('hr.job', 'Job Name')
