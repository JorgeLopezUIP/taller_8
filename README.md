Prueba de que funciona 
![imagen](https://github.com/user-attachments/assets/69efb737-e1be-4480-9b3d-3f8f706d7091)
 varios emails enviados a mi segundo correo desde el servidor local 

Para instalar y usar Celery y Flask-Mail en un mismo proyecto, primero debes instalar ambos paquetes. Usa los siguientes comandos para instalar Celery y Flask-Mail:

pip install celery flask-mail

Una vez instalados, configura Flask-Mail para manejar el envío de correos electrónicos. Crea una instancia de la aplicación Flask y configura las opciones de correo:

from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.example.com'  # Cambia a tu servidor de correo
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tu_email@example.com'
app.config['MAIL_PASSWORD'] = 'tu_contraseña'

mail = Mail(app)

Ahora, configura Celery para que funcione en paralelo con Flask y permita la ejecución de tareas en segundo plano, como enviar correos electrónicos de manera asíncrona. Primero, necesitas configurar un broker como Redis. Instálalo con:

pip install redis

Luego, configura Celery en tu aplicación Flask:

from celery import Celery

# Configuración de Celery
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'  # URL del broker Redis
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'  # Backend para almacenar los resultados

celery = make_celery(app)

Luego, crea una tarea Celery para enviar un correo electrónico en segundo plano:

@celery.task
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

@app.route("/send_email")
def send_email():
    msg = Message('Asunto del correo',
                  recipients=['destinatario@example.com'])
    msg.body = "Este es el cuerpo del correo."

    # Llamar la tarea de Celery para enviar el correo de manera asíncrona
    send_async_email.apply_async(args=[app, msg])
    return "Correo enviado!"

Con esta configuración, cuando accedas a la ruta /send_email, Celery manejará el envío del correo en segundo plano, lo que evita bloquear el hilo principal de la aplicación Flask. Asegúrate de ejecutar tanto el servidor Flask como el worker de Celery para que todo funcione correctamente. Para iniciar el worker de Celery, ejecuta el siguiente comando en la terminal:

celery -A app.celery worker

Esto te permitirá usar Celery y Flask-Mail en el mismo proyecto para enviar correos electrónicos de manera asíncrona sin bloquear la ejecución principal de tu aplicación.
