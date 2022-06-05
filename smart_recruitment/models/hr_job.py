from odoo import fields, models, api


class HrJob(models.Model):
    _inherit = 'hr.job'
    keywords_tags = fields.Many2many('smart_recruitment.keywords', string="Liste des mots clés")
    description = fields.Text(string="Description du poste", compute='_get_description', store=True)

    @api.depends('website_description')
    @api.model
    def _get_description(self):
        for elem in self:
            print(elem)