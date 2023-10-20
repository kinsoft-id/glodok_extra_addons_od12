# -*- coding: utf-8 -*-
######################################################################################################
#
# Copyright (C) B.H.C. sprl - All Rights Reserved, http://www.bhc.be
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied,
# including but not limited to the implied warranties
# of merchantability and/or fitness for a particular purpose
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
import logging
try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO
import zipfile
from datetime import datetime
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import content_disposition
import ast
import base64

_logger = logging.getLogger(__name__)


class Binary(http.Controller):

    @http.route('/web/binary/download_label', type='http', auth="public")
    def download_document(self, tab_id, **kw):
        new_tab = ast.literal_eval(tab_id)
        print(new_tab)
        attachment_ids = request.env['ir.attachment'].search([('id', 'in', new_tab)])
        file_dict = {}
        for attachment_id in attachment_ids:
            print(attachment_id)
            file_store = attachment_id.store_fname
            if file_store:
                file_name = attachment_id.name
                file_path = attachment_id._full_path(file_store)
                file_dict["%s:%s" % (file_store, file_name)] = dict(path=file_path, name=file_name)
        zip_filename = datetime.now()
        zip_filename = "%s.zip" % zip_filename
        bitIO = BytesIO()
        zip_file = zipfile.ZipFile(bitIO, "w", zipfile.ZIP_DEFLATED)
        for file_info in file_dict.values():
            zip_file.write(file_info["path"], "%s.pdf" % file_info["name"])
        zip_file.close()
        return request.make_response(bitIO.getvalue(),
                                     headers=[('Content-Type', 'application/x-zip-compressed'),
                                              ('Content-Disposition', content_disposition(zip_filename))])

    @http.route('/api/v1/file/<model_name>/<int:ref_id>/<view_pdf_name>', type='http', auth="public", website=True, sitemap=False)
    def open_pdf_file(self, model_name=None, ref_id=0, view_pdf_name=None, **kw):
        if model_name and ref_id and view_pdf_name:
            res_id = request.env[model_name].sudo().browse(ref_id)
            if res_id.shipping_label_data:
                # docs = res_id.shipping_label_data
                docs = res_id.tp_text_shipping_html
                # base64_pdf = base64.b64decode(docs)
                # pdf = base64_pdf
                # return self.return_web_pdf_view(pdf)
                return self.return_web_pdf_view(docs)

    def return_web_pdf_view(self, pdf=None):
        # pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        pdfhttpheaders = [('Content-Type', 'text/html'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

