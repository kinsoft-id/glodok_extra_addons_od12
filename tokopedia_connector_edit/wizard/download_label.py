from odoo import fields, models, api, _
from odoo.exceptions import UserError

class DownloadLabelWizard(models.TransientModel):
    _name = 'download.label.wizard'

    def process_wizard(self):
        sale_order_obj = self.env[self._context.get('active_model')].browse(self._context.get('active_ids'))
        tab_id = []
        for so in sale_order_obj:
            tab_id.append(so.attachment_id.id)
        
        url = '/web/binary/download_label?tab_id=%s' % tab_id
        print(url)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
            # if x.download_label:
            #     raise UserError(_("Label sudah di download."))
            # else:
            #     x.download_label = True
            #     return {
            #         'name': 'Download Label',
            #         'type': 'ir.actions.act_url',
            #         'url': '/web/content/?model=sale.order&id={}&field=shipping_label_data&download=true'.format(x.id),
            #         'target': 'self',
            #     }