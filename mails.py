"""from flask import Flask 
from flask_mail import Mail, Message 
from celery import Celery, Task
from extensions import app, mail


app.config.from_mapping({ 
    "MAIL_SERVER": "smtp.gmail.com", 
    "MAIL_PORT": 587, 
    "MAIL_USE_TLS": True, 
    "MAIL_USERNAME": "lopezjor8890@gmail.com",
    "MAIL_PASSWORD": "vexv aocn vcso bhdr",
    "MAIL_DEFAULT_SENDER": "lopezjor8890@gmail.com",
})



@celery.task
def email(): 
    with app.app_context(): 
        msg = Message(
            subject="Desea eliminar el libro", 
            recipients=["animatronicosalvaje4@gmail.com"], 
            body="Por favor confirma"
        )
    mail.send(msg)

    return "Mensaje enviado correctamente"
"""
