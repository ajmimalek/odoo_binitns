from odoo import fields, models, api


def clean_data(text):
    text = text.split('\n')
    # Remove empty strings
    while '' in text:
        text.remove('')
    # remove \t
    while "\t" in text:
        text.remove("\t")
    text = [word.strip() for word in text]
    return text


class HrJob(models.Model):
    _inherit = 'hr.job'
    keywords_tags = fields.Many2many('smart_recruitment.keywords', string="Liste des mots clés")
    job_description = fields.Text(string="Description du poste", compute='_compute_job_description', store=True)

    @api.depends('website_description')
    def _compute_job_description(self):
        for job in self:
            if job.website_description:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(job.website_description, 'html.parser')
                # Get the text from the HTML
                desc = soup.get_text()
                job.job_description = clean_data(desc)
            print("----------------------------------------------------")
