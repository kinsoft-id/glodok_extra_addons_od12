import os
from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/dotmatrix/print', methods=['POST'])
def index():
    printer_data = request.form['printer_data']
    os.system('echo "%s" | lpr -l' % (printer_data,))
    out = {'status':'OK'}
    return jsonify(out)