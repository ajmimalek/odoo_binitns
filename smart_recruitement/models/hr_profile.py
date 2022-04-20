from odoo import fields, models


class HrProfile(models.Model):
    _name = 'smart_recruitement.profile'
    _description = 'Model for collected profiles for specific job'

    name = fields.Char('Profile Name')
    current_company = fields.Text('Current Company')
    linkedin_url = fields.Char('LinkedIn URL')
    saved = fields.Boolean('Saved', default=False)
    job_id = fields.Many2one('hr.job', 'Job Name', ondelete='set null', index=True)