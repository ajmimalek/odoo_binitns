from odoo import fields, models, api
from textblob import TextBlob


class SkillsKeywords(models.Model):
    _name = 'smart_recruitment.keywords'
    _description = 'Liste des mots clés pour une offre d\'emploi'

    name = fields.Char(string="Compétence", required=True)
    tag_color = fields.Integer(string='Couleur du Tag', default=4)

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if TextBlob(record.name).correct() != record.name:
                message = "Veuillez vérifier l'orthographe de votre mot clé, Vous voulez peut-être dire: %s" % str(TextBlob(record.name).correct())
                raise models.ValidationError(message)
