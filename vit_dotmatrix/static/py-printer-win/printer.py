PRINTER_NAME = "EPSON LX-300+"

import win32print
from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/dotmatrix/print', methods=['POST'])
def index():
    printer_data = request.form['printer_data']
    p = win32print.OpenPrinter(PRINTER_NAME)
    job = win32print.StartDocPrinter(p, 1, ("DOTMATRIX", None, "RAW"))
    win32print.StartPagePrinter(p)
    win32print.WritePrinter(p, printer_data.encode())
    win32print.EndPagePrinter(p)

    out = {'status':'OK'}
    return jsonify(out)

