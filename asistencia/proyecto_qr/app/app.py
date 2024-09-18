from flask import Flask, request, jsonify, render_template
import qrcode
import io
import base64
import urllib.parse
from datetime import datetime, timedelta
import pytz
import mysql.connector
from mysql.connector import Error
from config.config import config
import random
#from flask_cors import CORS

app = Flask(__name__)
#CORS(app)

config_app = config["app"]
config_db = config["database"]
config_whatsapp = config["whatsapp"]

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host= config_db["host"],
            port= config_db["port"],
            user= config_db["user"],
            password= config_db["password"],
            database= config_db["database"]    
        )
        return connection
    except Error as err:
        print(f"Error connecting to the database: {err}")
        return None


def save_to_database(code_unique,timestamp):
    connection = get_db_connection()
    if connection is None:
        return 

    try:
        print("connection established, query running...")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO code_qr (code_unique, date) VALUES ( %s, %s)",(code_unique,timestamp,))
        connection.commit()
        cursor.close()
        connection.close()
        print(f"Se guardo exitosamente en la Base de Datos: Codigo_Unico_QR={code_unique}, FECHA={timestamp}")

    except mysql.connector.Error as err:
        print(f"Error connecting to the database;{err}")



@app.route('/scanner', methods=['GET'])
def scanner():

    code_unique =  ''.join([str(random.randint(0, 9)) for _ in range(15)])
   
    current_time = datetime.now(pytz.timezone('America/Bogota'))
    timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')

    message = f"{code_unique}"
    encoded_message = urllib.parse.quote(message)

    qr_data = f"https://api.whatsapp.com/send?phone={config_whatsapp['number']}&text={encoded_message}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    image_io = io.BytesIO()
    img.save(image_io, 'PNG')
    img_str = base64.b64encode(image_io.getvalue()).decode()

    save_to_database(code_unique=code_unique, timestamp=timestamp)
    #return jsonify({"qr_code": img_str, "timestamp": timestamp}), 200
    return render_template('qr_view.html', qr_code=img_str, code_unique=code_unique, timestamp={"hour":current_time.strftime('%H:%M:%S'), "date":current_time.strftime('%Y-%m-%d')})

#@app.route('/validate_otp', methods=['POST'])
#def validate_otp():
#   global used_otps
#    user_otp = request.form.get('otp_code')
#    number = request.form.get('number')
#    current_time = datetime.now(pytz.timezone('America/Bogota'))
#
#    # Verificar si el OTP es válido
#    if totp.verify(user_otp, valid_window=1):
        # Verificar si el OTP ya fue usado y si no ha expirado
#        for otp, timestamp, otp_time in used_otps:
#            if otp == user_otp:
#                if current_time - otp_time <= otp_lifetime:
#                    save_to_database(timestamp,number)
#                    return jsonify({"status": "success", "redirect_url": f"https://api.whatsapp.com/send?phone={config_whatsapp['number']}"})
#                else:
#                    return jsonify({"status": "failed", "message": "OTP expired"}), 400

#        return jsonify({"status": "failed", "message": "OTP not found or has already been used"}), 401
#    else:
#        return jsonify({"status": "failed", "message": "OTP invalid"}), 404



if __name__ == '__main__':
    app.run(debug=config_app["debug"], port=config_app["port"], host=config_app['host'])