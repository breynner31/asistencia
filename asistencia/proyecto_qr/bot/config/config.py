import os

config = {
    'app':{
        'host': os.getenv('HOST', '0.0.0.0'),
        'port': os.getenv('PORT', 5003),
        'debug': os.getenv('DEBUG', False)
    },
    'database': {
        'host': os.getenv('DB_HOST', 'db'),
        'port': os.getenv('PORT', 3306),
        'user': os.getenv('USER', 'root'),
        'password': os.getenv('PASSWORD', 'brey'),
        'database': os.getenv('DATABASE', 'user_db')
    },
    'service_qr':{
        'host': os.getenv('HOST', 'app'),
        'port': os.getenv('PORT', 5008)
    }
}