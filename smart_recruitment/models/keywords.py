from odoo import fields, models, api


class SkillsKeywords(models.Model):
    _name = 'smart_recruitment.keywords'
    _description = 'Liste des mots clés pour une offre d\'emploi'

    name = fields.Char(string="Compétence", required=True)
    tag_color = fields.Integer(string='Couleur du Tag', default=4)

    @api.constrains('name')
    def _check_name(self):
        from textblob import TextBlob
        for record in self:
            if TextBlob(record.name).correct() != record.name:
                raise models.ValidationError("Veuillez vérifier l'orthographe de votre mot clé, Vous voulez peut-être dire: %s" % TextBlob(record.name).correct())