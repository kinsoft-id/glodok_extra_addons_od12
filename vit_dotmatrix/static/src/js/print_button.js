//#############################################################################
//  @@@ web_print_printer_data custom JS @@@
//#############################################################################
odoo.define('vit_dotmatrix.print_button', function (require) {
    "use strict";

var FormController = require('web.FormController');


FormController.include({
    _onButtonClicked: function (event) {
    if(event.data.attrs.custom === "print"){
        //your code
        var printer_data=event.data.record.data.printer_data;
        if (!printer_data){
            alert('No data to print. Please click Update Printer Data on Dot Matrix Tab');
            return;
        }        
        console.log(printer_data);


        
        var url = "http://localhost:8000/dotmatrix/print";
        $.ajax({
            type: "POST",
            url: url,
            data: {
                printer_data : printer_data
            },
            success: function(data) {
                alert('Print Succeeded!');
                console.log(data);
            },
            error: function(data) {
                alert('Dotmatrix Print Failed. Please check the Printer Proxy running');
                console.log(data);
            },
        });
    }
    this._super(event);
    },
});

  
});