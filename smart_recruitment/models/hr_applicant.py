from odoo import fields, models, api
from odoo.exceptions import ValidationError


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
                filename = attachment.name
                print("Website : ", filename)
            else:
                if elem.message_main_attachment_id:
                    attachment = self.env['ir.attachment'].search(
                    [('res_model', '=', 'hr.applicant'), ('id', '=', elem.message_main_attachment_id.id)])
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
                        text = text.split('\n')
                        # Remove empty strings
                        while "" in text:
                            text.remove("")
                        # remove \t
                        while "\t" in text:
                            text.remove("\t")
                        text = [word.strip() for word in text]
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
                        text = text.split('\n')
                        # Remove empty strings
                        while "" in text:
                            text.remove("")
                        # remove \t
                        while "\t" in text:
                            text.remove("\t")
                        text = [word.strip() for word in text]
                        print(text)
                        elem.write({'cv_data': "\n".join(text)})
                    else:
                        print("Ce type de fichier n'est pas supporté")
                else:
                    print("Aucun CV n'est associé à cette candidature")