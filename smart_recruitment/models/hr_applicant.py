from odoo import fields, models, api
from odoo.exceptions import ValidationError


def clean_data(text):
    text = text.split('\n')
    # Remove empty strings
    while "" in text:
        text.remove("")
    # remove \t
    while "\t" in text:
        text.remove("\t")
    text = [word.strip() for word in text]
    return text


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'
    _order = 'create_date desc'

    cv_url = fields.Char(string="CV File URL", compute="_get_cv_url", store=True)
    # List of CV Keywords to search
    cv_data = fields.Text(string="CV", compute="_get_cv_data", store=True)

    @api.depends('message_main_attachment_id')
    @api.model
    def _get_cv_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/web/content/'
        cv_url = ""
        for elem in self:
            if elem.message_main_attachment_id:
                print("Getted from Mail")
                cv_url = base_url + str(elem.message_main_attachment_id.id)
                elem.write({'cv_url': cv_url})
            else:
                print("Getted from Website")
                cv_url = base_url + str(
                    self.env['ir.attachment'].search([('res_model', '=', 'hr.applicant'), ('res_id', '=', elem.id)]).id)
                elem.write({'cv_url': cv_url})

    @api.depends('cv_url')
    @api.model
    def _get_cv_data(self):
        for elem in self:
            print("Collecting CV Data")
            print(elem.cv_url)
            if elem.job_id:
                attachment = self.env['ir.attachment'].search(
                    [('res_model', '=', 'hr.applicant'), ('res_id', '=', elem.id)])
                if attachment:
                    filename = attachment.name
                    print("Website : ", filename)
                    path = attachment._full_path(attachment.store_fname)
                    print("Path: " + path)
                    extension = filename.split(".")[-1]
                    print("C'est un fichier :", extension)
                    if extension == "pdf":
                        from pdfminer.high_level import extract_text
                        text = extract_text(path).split('\n')
                        text = [" ".join(word.split()) for word in text]
                        # Remove empty strings
                        while "" in text:
                            text.remove("")
                        print(text)
                        elem.write({'cv_data': "\n".join(text)})
                    elif extension == "docx":
                        import docx2txt as d2t
                        text = d2t.process(path)
                        text = clean_data(text)
                        print(text)
                        elem.write({'cv_data': "\n".join(text)})
                    elif extension == "doc":
                        print("Converting doc file to docx and storing in the place of the old file")
                        import win32com
                        import pythoncom
                        from win32com.client import Dispatch
                        word = win32com.client.Dispatch('word.application', pythoncom.CoInitialize())
                        word.DisplayAlerts = 0
                        doc = word.Documents.Open(path)
                        doc.SaveAs(path, 12)
                        doc.Close()
                        word.Quit()
                        import docx2txt as d2t
                        text = d2t.process(path + ".docx")
                        text = clean_data(text)
                        print(text)
                        elem.write({'cv_data': "\n".join(text)})
                    else:
                        print("Ce type de fichier n'est pas supporté")
                        if elem.exists():
                            elem.unlink()
                        raise ValidationError("Ce type de fichier n'est pas supporté")
                else:
                    print("Aucun CV n'est associé à cette candidature")
                    if elem.exists():
                        elem.unlink()
                    raise ValidationError("Aucun CV n'est associé à cette candidature")
            elif elem.message_main_attachment_id:
                attachment = self.env['ir.attachment'].search(
                    [('res_model', '=', 'hr.applicant'), ('id', '=', elem.message_main_attachment_id.id)])
                if attachment:
                    filename = attachment.name
                    print("Mail : ", filename)
                    path = attachment._full_path(attachment.store_fname)
                    print("Path: " + path)
                    extension = filename.split(".")[-1]
                    print("C'est un fichier :", extension)
                    if extension == "pdf":
                        from pdfminer.high_level import extract_text
                        text = extract_text(path).split('\n')
                        text = [" ".join(word.split()) for word in text]
                        # Remove empty strings
                        while "" in text:
                            text.remove("")
                        print(text)
                        elem.write({'cv_data': "\n".join(text)})
                    elif extension == "docx":
                        import docx2txt as d2t
                        text = d2t.process(path)
                        text = clean_data(text)
                        print(text)
                        elem.write({'cv_data': "\n".join(text)})
                    elif extension == "doc":
                        print("Converting doc file to docx and storing in the place of the old file")
                        import win32com
                        import pythoncom
                        from win32com.client import Dispatch
                        word = win32com.client.Dispatch('word.application', pythoncom.CoInitialize())
                        word.DisplayAlerts = 0
                        doc = word.Documents.Open(path)
                        doc.SaveAs(path, 12)
                        doc.Close()
                        word.Quit()
                        import docx2txt as d2t
                        text = d2t.process(path + ".docx")
                        text = clean_data(text)
                        print(text)
                        elem.write({'cv_data': "\n".join(text)})
                    else:
                        print("Ce type de fichier n'est pas supporté")
                        if elem.exists():
                            elem.unlink()
            else:
                print("Aucun CV n'est associé à cette candidature")
                if elem.exists():
                    elem.unlink()

    def fields_view_get(self, view_id=None, view_type='kanban', toolbar=False, submenu=False):
        res = super(HrApplicant, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                       submenu=submenu)
        if view_type == 'kanban':
            """Elimination par mots clés"""
            # Get a list of Job IDs
            job_ids = self.env['hr.job'].search([]).mapped('id')
            # Get Applicants & Keywords for each Job ID
            for job_id in job_ids:
                print("Job ID : ", job_id)
                # Get Keywords for each Job ID
                self.env.cr.execute(
                    """SELECT smart_recruitment_keywords_id FROM hr_job_smart_recruitment_keywords_rel WHERE hr_job_id = %s;""",
                    (job_id,))
                keywords = self.env.cr.fetchall()
                keyowrds_ids = [keyword[0] for keyword in keywords]
                keyword_names = self.env['smart_recruitment.keywords'].search([('id', 'in', keyowrds_ids)]).mapped(
                    'name')
                # Get Applicants CV Data for each Job ID
                applicants = self.search([('job_id', '=', job_id)]).mapped('cv_data')
                for applicant in applicants:
                    for keyword in keyword_names:
                        if keyword.upper() not in applicant.upper():
                            print("Cette candidature ne correspond pas aux mots clés")
                            print("Keyword : ", keyword)
                            applicant = self.search([('cv_data', '=', applicant)])
                            print("Applicant Name : ", applicant.mapped('name'))
                            # Turn kanban_state to blocked
                            applicant.write({'kanban_state': 'blocked'})
                            break
            """Elimination des candidatures en double"""
            # Create section "Candidatures en double"
            if self.env['hr.recruitment.stage'].search([('name', '=', 'Candidatures en double')]):
                print("Section Candidatures en double existe déjà")
            else:
                self.env['hr.recruitment.stage'].create({
                'name': 'Candidatures en double',
                'sequence': 6,
                })
            # Same applications from different sources
            # Same applications from same source
            self.env.cr.execute(
                """SELECT email_from, cv_data FROM hr_applicant WHERE job_id IS NULL;""")
            mails = self.env.cr.fetchall()
            # Get duplicate tuples from list
            # Using list comprehension + set() + count()
            duplicate_application = list(set([app for app in mails
                            if mails.count(app) > 1]))
            # Search for duplicate applications
            stage_id = self.env['hr.recruitment.stage'].search([('name', '=', 'Candidatures en double')]).id
            for dup in duplicate_application:
                duplicate = self.search([('email_from', '=', dup[0]), ('cv_data', '=', dup[1])]).write({
                    'stage_id': stage_id,
                    'kanban_state': 'blocked'})
        return res
