from odoo import fields, models, api


class HrJob(models.Model):
    _inherit = 'hr.job'
    keywords_tags = fields.Many2many('smart_recruitment.keywords', string="Liste des mots clés")
    """job_description = fields.Text(string="Description du poste", compute='_compute_job_description', store=True)

    @api.depends('website_description')
    def _compute_job_description(self):
        for job in self:
            print(job.website_description)"""