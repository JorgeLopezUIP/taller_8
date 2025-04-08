from flask import Flask, render_template, request,redirect,url_for,session,flash 
from flask_mail import Mail,Message
import redis, os
from celery import Celery 
from celery_config import make_celery 
from dotenv import load_dotenv
import os

load_dotenv()

keydb = redis.Redis(host="localhost", port=6380, decode_responses=True)

app = Flask(__name__, template_folder= "templates")
app.secret_key = os.urandom(16)
celery= make_celery(app)

app.config.from_mapping({ 
    "MAIL_SERVER": "smtp.gmail.com", 
    "MAIL_PORT": 587, 
    "MAIL_USE_TLS": True, 
    "MAIL_USERNAME": os.getenv('MAIL_USERNAME'), 
    "MAIL_PASSWORD": os.getenv('MAIL_PASSWORD'), 
    "MAIL_DEFAULT_SENDER": os.getenv('MAIL_DEFAULT_SENDER'), 
})

mail = Mail(app)

@celery.task
def enviar_mensaje(tarea,titulo,genero,autor,link): 
    msg = Message( 
        subject=f"{tarea} libro",
        recipients=["animatronicosalvaje4@gmail.com"],
        body=(f"Desea {tarea} este libro:\ntitulo: {titulo}\ngenero: {genero}\nautor: {autor}\nHaga clic en el siguente link para confirmar: {link}")
    )
    mail.send(msg)

@app.route("/", methods = ["GET", "POST"])
def index(): 
     libros = {}
     for key in keydb.keys("libro:*"): 
        if not key.endswith("id"):
            libro = keydb.hgetall(key)
            libros[key] = libro
     return render_template("index.html", libros = libros)

@app.route("/registro",methods = ["POST", "GET"]) 
def registrar_libro(): 
    if request.method == "POST": 
        nombre = request.form["nombre"]
        genero = request.form["genero"]
        autor = request.form["autor"] 

        session["nombre"]=nombre
        session["genero"]=genero
        session["autor"]=autor

        libro_id = keydb.incr("libro:id")
        session["libro_id"]=libro_id
        #key = f"libro:{libro_id}"
        url = f"http://localhost:8000/registro_confirmar/{libro_id}"
        enviar_mensaje.delay("registrar",nombre,genero,autor, url)

        #keydb.hset(key, mapping= {"libro": nombre, "genero": genero, "autor": autor}) 
        return render_template("registro.html")
        
    return render_template("registro.html")

@app.route("/registro_confirmar/<int:libro_id>",methods = ["POST", "GET"])
def confirmar_registro(libro_id):
    if libro_id != session.get('libro_id'):
        return "Error: los datos de confirmación no coinciden.", 400
    
    nombre = session["nombre"]
    genero = session["genero"]
    autor = session["autor"]
    key = f"libro:{libro_id}"

    keydb.hset(key, mapping= {"libro": nombre, "genero": genero, "autor": autor})

    return redirect(url_for("index"))

@app.route("/eliminar/<int:index>") 
def eliminar_libro(index):
    key = f"libro:{index}"
    libro = keydb.hgetall(key)

    nombre_libro = libro.get("libro")
    genero_libro = libro.get("genero")
    autor_libro = libro.get("autor")
    
    enviar_mensaje.delay("eliminar", nombre_libro, genero_libro, autor_libro, f"http://localhost:8000/confirmar_eliminar/{index}") 

    #keydb.delete(key)
    #keydb.delete(f"libro:{index}")
    return redirect(url_for("index"))

@app.route("/confirmar_eliminar/<int:index>",methods=["GET"])
def confirmar_eliminacion(index): 
    key = f"libro:{index}"
    if keydb.exists(key):
        keydb.delete(key)
        print(f"Libro {index} eliminado")
    else:
        print(f"Error: el libro {index} no existe para eliminar")
    return redirect(url_for("index"))

@app.route("/editar/<int:index>",methods = ["POST", "GET"]) 
def editar_libro(index): 
    key = f"libro:{index}"
    if request.method == "POST": 
        nuevo_nombre = request.form["nombre"]
        nuevo_genero = request.form["genero"]
        nuevo_autor = request.form["autor"]

        keydb.hset(key, mapping={
                   "libro": nuevo_nombre,
                   "genero": nuevo_genero, 
                   "autor": nuevo_autor
                   })
        return redirect(url_for("index")) 
    
    datos_libro = keydb.hgetall(key)
    return render_template("editar.html", libro = datos_libro, libro_id = index)

@app.route("/buscar", methods = ["POST", "GET"])
def buscar_libro():
    if request.method == "POST": 
        buscar_titulo = request.form["titulo"]
        resultado = None 
        
        for key in keydb.scan_iter("libro:*"):
            if keydb.type(key) != b"hash": 
                continue

            libro = keydb.hgetall(key)
            if libro.get("libro", "").lower() == buscar_titulo.lower(): 
                resultado = libro
                break

        if resultado:
            historial = session.get("historial", [])
            historial.append({
                "titulo": resultado["libro"],
                "genero": resultado["genero"],
                "autor": resultado["autor"],
                "busqueda": buscar_titulo
            })
            session['historial'] = historial   
            flash('Libro encontrado y añadido al historial.')
            return redirect(url_for("historial"))
        else:
            flash('No se encontró el libro.')
            return redirect(url_for("buscar_libro"))
    
    return render_template("buscar.html") 

@app.route("/historial", methods=["GET"])
def historial(): 
    historial_data = session.get("historial", [])
    return render_template("historial.html", resultado=historial_data)


if __name__ == "__main__":
    app.run()


    