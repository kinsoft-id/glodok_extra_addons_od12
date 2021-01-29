/**********************************************************************************
* 
*    Copyright (C) 2020 Cetmix OÜ
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
*    published by the Free Software Foundation, either version 3 of the
*    License, or (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU LESSER GENERAL PUBLIC LICENSE for more details.
*
*    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
*    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
**********************************************************************************/

odoo.define("prt_report_attachment_preview.ReportPreview", function(require) {
    "use strict";

    var Session = require("web.Session");
    var Sidebar = require("web.Sidebar");

    // Session
    Session.include({
        get_file: function(options) {
            var token = new Date().getTime();
            options.session = this;
            var params = _.extend({}, options.data || {}, {token: token});
            var url = options.session.url(options.url, params);
            if (
                url.indexOf("report/download") === -1 &&
                url.indexOf("web/content") === -1
            ) {
                return this._super.apply(this, arguments);
            }
            if (options.complete) {
                options.complete();
            }

            var w = window.open(url);
            if (!w || w.closed || typeof w.closed === "undefined") {
                // Popup was blocked
                return false;
            }
            return true;
        },
    });

    // Sidebar
    Sidebar.include({
        _redraw: function() {
            var self = this;
            this._super.apply(this, arguments);
            self.$el.find("a[href]").attr("target", "_blank");
        },
    });
});
