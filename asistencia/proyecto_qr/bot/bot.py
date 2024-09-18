from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse  # Asegúrate de que esta línea esté incluida
from datetime import datetime, timedelta
import pytz
import mysql.connector
from mysql.connector import Error
from config.config import config

app = Flask(__name__)

config_app = config["app"]
config_db = config["database"]

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=config_db["host"],
            port=config_db["port"],
            user=config_db["user"],
            password=config_db["password"],
            database=config_db["database"]    
        )
        return connection
    except Error as err:
        print(f"Error connecting to the database: {err}")
        return None

def validar_code_registrado(code_unique, phone_number):
    phone_number = phone_number.replace("whatsapp:", "")
    connection = get_db_connection()
    if connection is None:
        return "No se pudo conectar a la base de datos."

    try:
        cursor = connection.cursor()

        # Verificar si el código existe en la tabla code_qr y obtener su fecha de generación
        cursor.execute("SELECT date FROM code_qr WHERE code_unique = %s", (code_unique,))
        result = cursor.fetchone()

        if result:
            # Obtener la fecha de generación del código QR
            fecha_generacion = result[0]  # Esta es un objeto datetime, no una cadena
            print(f"Código QR {code_unique} es válido. Procediendo a verificar la validez del QR...")

            # Obtener la hora actual con la zona horaria de Bogotá
            tz = pytz.timezone('America/Bogota')
            current_time = datetime.now(tz)

            # Convertir fecha_generacion a la misma zona horaria
            if fecha_generacion.tzinfo is None:
                fecha_generacion = tz.localize(fecha_generacion)

            # Calcular el tiempo máximo permitido (30 segundos después de la fecha de generación)
            tiempo_maximo = fecha_generacion + timedelta(seconds=30)

            # Verificar si el código QR es válido según el tiempo transcurrido
            if current_time <= tiempo_maximo:
                # Insertar registro de asistencia en la tabla asistencia
                timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(
                    "INSERT INTO asistencia (code_unique, date, phone_number) VALUES (%s, %s, %s)",
                    (code_unique, timestamp, phone_number)
                )
                connection.commit()
                
                print(f"Asistencia registrada: Código QR={code_unique}, Fecha={timestamp}, Teléfono={phone_number}")
                return "El código fue válido y se registró en la base de datos."

            else:
                print(f"Código QR {code_unique} ha expirado.")
                return "El código QR ha expirado."

        else:
            print(f"Código QR {code_unique} no existe en la base de datos.")
            return "El código no existe en la base de datos."

    except mysql.connector.Error as err:
        print(f"Error en la base de datos: {err}")
        return f"Hubo un error al conectar con la base de datos: {err}"

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión a la base de datos cerrada.")

@app.route('/sms', methods=['POST'])
def sms_reply():
    from_number = request.form.get('From')
    message_body = request.form.get('Body')

    # Validar y registrar código QR recibido
    response_message = validar_code_registrado(message_body, from_number)

#    unique_id = message_body
#    current_time = datetime.now(pytz.timezone('America/Bogota'))
#    timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')

    # Verificar si en la lista el OTP ya ha sido usado
#    otp_used = any(otp == unique_id for otp, _ in used_otps)


#    if otp_used:
#        response_message = "Code duplication detected. This code has already been used."
#    else:
#        try:
        # Validar el OTP con el servicio
#            response = requests.post(validate_url, data={'otp_code': unique_id, "number": from_number.replace("whatsapp:", "")})

#            if response.ok:
#                try:
#                    validation_result = response.json()
#                    print(f"Resultado de validación: {validation_result}")
                # Almacenar el OTP usado
#                    if isinstance(validation_result, dict):
#                        if validation_result.get("status") == "success":

#                            used_otps.append((unique_id, timestamp))
#                            response_message = (f"{unique_id}")
#                        else:
#                            response_message = "The QR ID is not valid or has already been used."
#                    else:
#                        response_message = "Unexpected response from the validation service."
#                except ValueError:
#                    response_message = "Error interpreting the response from the validation service."
#            else:
#                response_message = "Error connecting22 to the validation service."
#        except requests.RequestException:
#            response_message = "Error connecting to the validation service."

    #Crear la respuesta de Twilio
    resp = MessagingResponse()
    resp.message(response_message)
    return str(resp)

if __name__ == '__main__':
    app.run(debug=config_app['debug'], port=config_app['port'], host=config_app['host'])