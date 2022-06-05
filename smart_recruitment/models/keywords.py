from odoo import fields, models, api


class SkillsKeywords(models.Model):
    _name = 'smart_recruitment.keywords'
    _description = 'Liste des mots clés pour une offre d\'emploi'

    name = fields.Char(string="Compétence", required=True)
    tag_color = fields.Integer(string='Coleur du Tag', default=4)

