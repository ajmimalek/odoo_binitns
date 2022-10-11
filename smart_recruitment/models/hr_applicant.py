from odoo import fields, models, api
from odoo.exceptions import ValidationError


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


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'
    _order = 'create_date desc'

    cv_url = fields.Char(string="CV File URL", compute="_get_cv_url", store=True)
    # List of CV Keywords to search
    cv_data = fields.Text(string="CV", compute="_get_cv_data", store=True)
    matchPercentage = fields.Float(string="Match Percentage", compute="_get_match_percentage", store=True)

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
                        #print(text)
                        elem.write({'cv_data': "\n".join(text)})
                    elif extension == "docx":
                        import docx2txt as d2t
                        text = d2t.process(path)
                        text = clean_data(text)
                        #print(text)
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
                        #print(text)
                        elem.write({'cv_data': "\n".join(text)})
                    else:
                        print("Ce type de fichier n'est pas supporté")
                        if elem.exists():
                            elem.unlink()
            else:
                print("Aucun CV n'est associé à cette candidature")
                if elem.exists():
                    elem.unlink()

    @api.depends('job_id.job_description')
    @api.model
    def _get_match_percentage(self):
        for elem in self:
            if elem.job_id and elem.job_id.job_description:
                """print("CV Data : ", elem.cv_data)
                print("----------------------------------------------------")
                print("Job Description : ", elem.job_id.job_description)
                print("----------------------------------------------------")"""
                # A list of text
                text = [elem.cv_data, elem.job_id.job_description]
                from sklearn.feature_extraction.text import CountVectorizer
                # Convert a collection of text documents to a matrix of token counts.
                cv = CountVectorizer()
                # Learn the vocabulary dictionary and return document-term matrix.
                count_matrix = cv.fit_transform(text)
                # Compute the cosine similarity matrix.
                from sklearn.metrics.pairwise import cosine_similarity
                # Print the similarity scores
                print("\nScores de Similitudes:")
                print(cosine_similarity(count_matrix))
                # Get the similarity score between the two documents
                matchPercentage = cosine_similarity(count_matrix)[0][1] * 100
                matchPercentage = round(matchPercentage, 2)  # round to two decimal
                print("Votre CV est identique à " + str(matchPercentage) + "% par rapport à l'offre d'emploi")
                elem.matchPercentage = float(matchPercentage)

    def fields_view_get(self, view_id=None, view_type='kanban', toolbar=False, submenu=False):
        res = super(HrApplicant, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                       submenu=submenu)
        if view_type == 'kanban':
            """Elimination par mots clés"""
            # Get a list of Job IDs
            job_ids = self.env['hr.job'].search([]).mapped('id')
            # Search for duplicate applications
            stage_id_double = self.env['hr.recruitment.stage'].search([('name', '=', 'Candidatures en double')], limit=1).id
            # Get Applicants & Keywords for each Job ID
            for job_id in job_ids:
                print("Job ID : ", job_id)
                # Eliminer candidature en double pour ce job_id
                self.env.cr.execute(
                    """SELECT partner_name, cv_data FROM hr_applicant WHERE job_id = %s;""", (job_id,))
                applications = self.env.cr.fetchall()
                print("Applications : ", applications)
                duplicate_apps = list(set([app for app in applications
                                           if applications.count(app) > 1]))
                print("Duplicate Applications : ", duplicate_apps)
                for dup in duplicate_apps:
                    count_duplicates = self.search_count([('partner_name', '=', dup[0]), ('cv_data', '=', dup[1]), ('job_id', '=', job_id)])
                    print("Count Duplicates : ", count_duplicates)
                    self.search([('partner_name', '=', dup[0]), ('cv_data', '=', dup[1])],
                                limit=count_duplicates - 1).write({
                        'stage_id': stage_id_double,
                        'kanban_state': 'blocked'})
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
                            applic = self.search([('cv_data', '=', applicant)])
                            for app in applic.stage_id:
                                print("Stage Name : ", app.name)
                            if applic.stage_id.name == 'Qualification initiale':
                                print("Applicant Name : ", applic.mapped('name'))
                                # Turn kanban_state to blocked
                                applic.write({'kanban_state': 'blocked'})
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
            self.env.cr.execute(
                """SELECT body, cv_url, cv_data FROM mail_message, hr_applicant
                    WHERE mail_message.res_id = hr_applicant.id
                    AND mail_message.model = 'hr.applicant'
                    AND mail_message.message_type = 'email' """)
            mail_applications = self.env.cr.fetchall()
            print("Mail Applications : ", len(mail_applications))
            for mail_application in mail_applications:
                mail_application_content = mail_application[0]
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(mail_application_content, 'html.parser')
                # Get the text from the HTML
                mail_application_content = soup.get_text()
                print("Mail Application Content : ", mail_application_content)
                if "keejob" in mail_application_content.lower():
                    print("Cette candidature est provenant d'un keejob")
                    mail_application_list = clean_data(mail_application_content)
                    for mailapp in mail_application_list:
                        print("Mail Application : ", mailapp)
                        if '"' in mailapp:
                            pos = [pos for pos, char in enumerate(mailapp) if char == '"']
                            poste_keejob = mailapp[pos[0] + 1:pos[1]]
                            print("Poste : ", poste_keejob)
                            # check if the job exists in hr_job
                            if self.env['hr.job'].search([('name', '=', poste_keejob)]):
                                print("Job exists")
                            else:
                                print("Job does not exist")
                                # Create job
                                self.env['hr.job'].create({'name': poste_keejob})
                        if 'Candidat' in mailapp:
                            candidat_keejob = mailapp[mailapp.find('Candidat:') + len('Candidat: '): mailapp.find('Région')]
                            print("Candidat : ", candidat_keejob)
                    # add the applicant to the job
                    if self.search([('name', '=', candidat_keejob + " (Keejob)")]):
                        print("Applicant exists")
                    else:
                        self.search([('cv_url', '=', mail_application[1])]).write({
                            'job_id': self.env['hr.job'].search([('name', '=', poste_keejob)]).id,
                            'name': candidat_keejob + " (Keejob)",
                            'partner_name': candidat_keejob,
                            'stage_id': 1})
                    print("------------------------------------------------------")
                if "tanitjobs" in mail_application_content.lower():
                    print("Cette candidature est provenant d'un TanitJobs")
                    mail_application_list = clean_data(mail_application_content)
                    print(mail_application_list)
                    for mailapp in mail_application_list:
                        # print("Mail Application : ", mailapp)
                        if '"' in mailapp and mailapp.count('"') == 1:
                            # merge next element with current element
                            mailapp = mailapp + " " + mail_application_list[mail_application_list.index(mailapp) + 1]
                            #print("Mail Application merged : ", mailapp)
                        if 'Nom:' in mailapp:
                            candidat_tanitjobs = mailapp[mailapp.find('Nom:') + len('Nom:'): mailapp.find('Email')]
                            print("Candidat : ", candidat_tanitjobs)
                        if 'poste' in mailapp.lower():
                            import re
                            indexes = [x.start() for x in re.finditer('"', mailapp)]
                            print("Indexes : ", indexes)
                            poste_tanitjobs = mailapp[indexes[0] + 1:indexes[1]].strip()
                            print("Poste : ", poste_tanitjobs)
                    # check if the job exists in hr_job
                    if self.env['hr.job'].search([('name', '=', poste_tanitjobs)]):
                        print("Job exists")
                    else:
                        print("Job does not exist")
                        # Create job
                        self.env['hr.job'].create({'name': poste_tanitjobs})
                        # add the applicant to the job
                    if self.search([('name', '=', candidat_tanitjobs + " (TanitJobs)")]):
                        print("Applicant exists")
                    else:
                        self.search([('cv_url', '=', mail_application[1])]).write({
                            'job_id': self.env['hr.job'].search([('name', '=', poste_tanitjobs)]).id,
                            'name': candidat_tanitjobs + " (TanitJobs)",
                            'partner_name': candidat_tanitjobs,
                            'stage_id': 1})
                    print("------------------------------------------------------")
            # Same applications from same source
            self.env.cr.execute(
                """SELECT email_from, cv_data FROM hr_applicant WHERE job_id IS NULL;""")
            mails = self.env.cr.fetchall()
            # Get duplicate tuples from list
            # Using list comprehension + set() + count()
            duplicate_application = list(set([app for app in mails
                                              if mails.count(app) > 1]))
            for dup in duplicate_application:
                self.search([('email_from', '=', dup[0]), ('cv_data', '=', dup[1])]).write({
                    'stage_id': stage_id_double,
                    'kanban_state': 'blocked'})
        return res
