from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64

class Sale(models.Model):
    _inherit = 'sale.order'

    is_upload = fields.Boolean(string='Is Upload?', default=False)
    
    def upload_attachment_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Upload Attachment',
            'res_model': 'upload.attachment.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

class UploadAttachmentWizard(models.TransientModel):
    _name = 'upload.attachment.wizard'
    
    attachment = fields.Binary(string='Attachment')
    attachment_ids = fields.Many2many('ir.attachment', 'upload_attachments_rel', 'wizard_id', 'attachment_id', 'Attachments')

    @api.multi
    def process_wizard(self):
        obj = self.env[self._context.get('active_model')].browse(self._context.get('active_ids'))
        for x in obj:
            x.write({'is_upload':True})
            for attachment in self.attachment_ids:
                # decoded_data = base64.b64decode(attachment)
                decoded_data = attachment.datas

                self.env['ir.attachment'].sudo().create({
                    'name'      : x.name,
                    'datas'     : decoded_data,
                    'res_id'    : x.id,
                    'res_model' : x._name,
                })