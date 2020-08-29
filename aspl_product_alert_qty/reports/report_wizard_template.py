# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
# -*- coding: utf-8 -*-
from odoo import models,api,fields

import logging
_logger = logging.getLogger(__name__)

    
class ReportProductQtyWizardTemplate(models.AbstractModel):
    _name='report.aspl_product_alert_qty.report_wizard_template'

    @api.multi
    def get_report_values(self,docids,data=None):
        if data:
            record=self.env['wizard.report'].browse(data['ids'])
        else:
            record = self.env['wizard.report'].browse(self._context.get('wizard_id'))
        return {'doc_ids': record,
                'doc_model':'wizard.report',
                'data': data,
                'docs': record,
                '_group_products': self.group_products,
        }

    def group_products(self, data):
        if data:
            record = self.env['wizard.report'].browse(data['ids'])
        else:
            record = self.env['wizard.report'].browse(self._context.get('wizard_id'))

        if record.group_by == 'category':

            if record.category_ids:
                _logger.critical(('11111'))
                categ_ids = record.category_ids
                products = self.env['product.product'].search([('type', '=', 'product'),('categ_id.id','in',categ_ids.ids), ('product_tmpl_id.show_in_alert','=',True)])
            else:
                _logger.critical(('2222'))
                categ_ids = self.env['product.category'].search([])
                products = self.env['product.product'].search([('type', '=', 'product'), ('product_tmpl_id.show_in_alert','=',True)])

                # test
                pp = self.env['product.template'].search([('id','=',395)])
                _logger.critical((pp.type, pp.show_in_alert, pp.product_variant_ids))
                _logger.critical((pp.id in products.ids))
                # 
            _logger.critical(("Cattttttttttttttttt", record.group_by, products))
            locations = self.env['stock.location'].search([('usage', '=', 'internal'), ('scrap_location','=',False)])
            dict = {}
            _logger.critical((categ_ids.mapped('display_name')))
            for each in categ_ids:
                list = []
                for product in products:
                    if product.categ_id.id == each.id:
                        if product.same_for_all == True:
                            if product.immediately_usable_qty <= product.alert_qty:
                                if record.breakdown_location:
                                    for loc in locations:
                                        list.append({'code': product.default_code,
                                                     'name':product.name,
                                                     'avl_qty':product.with_context(location=loc.id).immediately_usable_qty,
                                                     'alert_qty':product.alert_qty,
                                                     'reorder_qty':product.reordering_min_qty,
                                                     'category':each.name,
                                                     'location':loc.complete_name
                                                    })
                                else:
                                    list.append({'code': product.default_code,
                                                 'name':product.name,
                                                 'avl_qty':product.immediately_usable_qty,
                                                 'alert_qty':product.alert_qty,
                                                 'reorder_qty':product.reordering_min_qty,
                                                 'category':each.name,
                                                 'location':False
                                                })
                        else:
                            for line in product.alert_product_ids:
                                if product.reordering_min_qty <= product.immediately_usable_qty <= line.alert_qty:
                                    list.append({'code': product.default_code,
                                                 'name':product.name,
                                                 'avl_qty':product.immediately_usable_qty,
                                                 'alert_qty': line.alert_qty,
                                                 'reorder_qty': product.reordering_min_qty,
                                                 'category':each.name,
                                                 'location': line.location_id.complete_name
                                                 })
                    if len(list) != 0:
                        dict[each.name] = list
            return dict

        elif record.group_by == 'location':
            _logger.critical((categ_ids))
            if record.location_ids:
                loc_id = record.location_ids
            else:
                loc_id = self.env['stock.location'].search([('usage', '=', 'internal'), ('scrap_location','=',False) ])
            products = self.env['product.product'].search([('type', '=', 'product'), ('product_tmpl_id.show_in_alert','=',True)])
            dict = {}
            for each in loc_id:
                list = []
                for product in products:
                    if product.same_for_all == True:
                        if product.immediately_usable_qty <= product.alert_qty:
                            list.append({'code': product.default_code,
                                         'name': product.name,
                                         'avl_qty': product.immediately_usable_qty,
                                         'alert_qty': product.alert_qty,
                                         'reorder_qty': product.reordering_min_qty,
                                         'category': product.categ_id.name,
                                         'location':each.complete_name,
                                         })
                    else:
                        for line in product.alert_product_ids:
                            if product.immediately_usable_qty <= line.alert_qty:
                                if line.location_id.id == each.id:
                                    list.append({'code': product.default_code,
                                                 'name': product.name,
                                                 'avl_qty': product.immediately_usable_qty,
                                                 'alert_qty': line.alert_qty,
                                                 'reorder_qty': product.reordering_min_qty,
                                                 'category': product.categ_id.name,
                                                 'location': each.complete_name,
                                                 })
                if len(list) != 0:
                    dict[each.complete_name] = list
            return dict

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: