from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)


client = MongoClient("mongodb://localhost:27017/")
db = client["hdt11"]

encargados_collection = db["encargados"]
proyectos_collection = db["proyectos"]



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/registrar-proyecto", methods=["GET", "POST"])
def registrar_proyecto():
    encargados = list(encargados_collection.find())

    if request.method == "POST":
        nombre = request.form["nombre"]
        fechaInicio = request.form["fechaInicio"]
        fechaFin = request.form["fechaFin"]
        presupuesto = request.form["presupuesto"]
        encargadoId = request.form["encargadoId"] 

        encargado = encargados_collection.find_one({"_id": ObjectId(encargadoId)})

        # Crear proyecto
        proyecto = {
            "nombre": nombre,
            "fechaInicio": fechaInicio,
            "fechaFin": fechaFin,
            "presupuesto": presupuesto,
            "finalizado": False,
            "encargadoId": encargadoId,  
            "encargado": {               
                "nombre": encargado["nombre"],
                "dpi": encargado["dpi"],
                "direccion": encargado["direccion"]
            },
            "familiasBeneficiadas": []
        }

        proyectos_collection.insert_one(proyecto)

        return redirect(url_for("ver_proyectos"))


    return render_template("registrar_proyecto.html", encargados=encargados)


@app.route("/ver-proyectos")
def ver_proyectos():
    proyectos = list(proyectos_collection.find())
    return render_template("ver_proyectos.html", proyectos=proyectos)


@app.route("/editar-proyecto/<id>", methods=["GET", "POST"])
def editar_proyecto(id):

    proyecto = proyectos_collection.find_one({"_id": ObjectId(id)})
    encargados = list(encargados_collection.find())

    if not proyecto:
        return "Proyecto no encontrado", 404

    if request.method == "POST":
        nombre = request.form["nombre"]
        fechaInicio = request.form["fechaInicio"]
        fechaFin = request.form["fechaFin"]
        presupuesto = request.form["presupuesto"]
        encargadoId = request.form["encargadoId"]

        encargado = encargados_collection.find_one({"_id": ObjectId(encargadoId)})

        proyectos_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "nombre": nombre,
                "fechaInicio": fechaInicio,
                "fechaFin": fechaFin,
                "presupuesto": presupuesto,
                "encargadoId": encargadoId,
                "encargado": {
                    "nombre": encargado["nombre"],
                    "dpi": encargado["dpi"],
                    "direccion": encargado["direccion"]
                }
            }}
        )

        return redirect(url_for("ver_proyectos"))

    return render_template("editar_proyecto.html", proyecto=proyecto, encargados=encargados)




@app.route("/agregar-familias/<id>", methods=["GET", "POST"])
def agregar_familia(id):

    proyecto = proyectos_collection.find_one({"_id": ObjectId(id)})

    if request.method == "POST":

        direcciones = request.form.getlist("direccion[]")
        ingresos = request.form.getlist("ingresoMensual[]")

        nuevas_familias = []

        for d, i in zip(direcciones, ingresos):
            nuevas_familias.append({
                "direccion": d,
                "ingresoMensual": float(i)
            })

        proyectos_collection.update_one(
            {"_id": ObjectId(id)},
            {"$push": {
                "familiasBeneficiadas": {"$each": nuevas_familias}
            }}
        )

        return redirect(url_for("ver_proyectos"))

    return render_template("agregar_familia.html", proyecto=proyecto)



@app.route("/eliminar-familia/<proyecto_id>/<familia_index>", methods=["POST"])
def eliminar_familia(proyecto_id, familia_index):
    proyecto = proyectos_collection.find_one({"_id": ObjectId(proyecto_id)})

    if not proyecto:
        return "Proyecto no encontrado", 404

    familias = proyecto["familiasBeneficiadas"]
    familia_index = int(familia_index)

    if familia_index < 0 or familia_index >= len(familias):
        return "Índice de familia inválido", 400

    familias.pop(familia_index)

    proyectos_collection.update_one(
        {"_id": ObjectId(proyecto_id)},
        {"$set": {"familiasBeneficiadas": familias}}
    )

    return redirect(url_for("ver_proyectos"))

@app.route("/editar-familia/<proyecto_id>/<familia_index>", methods=["GET", "POST"])
def editar_familia(proyecto_id, familia_index):

    proyecto = proyectos_collection.find_one({"_id": ObjectId(proyecto_id)})
    if not proyecto:
        return "Proyecto no encontrado", 404

    familia_index = int(familia_index)

    if familia_index < 0 or familia_index >= len(proyecto["familiasBeneficiadas"]):
        return "Índice de familia inválido", 400

    familia = proyecto["familiasBeneficiadas"][familia_index]

    if request.method == "POST":
        nueva_direccion = request.form["direccion"]
        nuevo_ingreso = float(request.form["ingresoMensual"])

        proyectos_collection.update_one(
            {"_id": ObjectId(proyecto_id)},
            {
                "$set": {
                    f"familiasBeneficiadas.{familia_index}.direccion": nueva_direccion,
                    f"familiasBeneficiadas.{familia_index}.ingresoMensual": nuevo_ingreso
                }
            }
        )

        return redirect(url_for("ver_proyectos"))

    return render_template(
        "editar_familia.html",
        proyecto=proyecto,
        familia=familia,
        index=familia_index
    )




@app.route("/finalizar-proyecto/<id>", methods=["POST"])
def finalizar_proyecto(id):
    proyectos_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"finalizado": True}}
    )
    return redirect(url_for("ver_proyectos"))



@app.route("/eliminar-proyecto/<id>", methods=["POST"])
def eliminar_proyecto(id):
    proyectos_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("ver_proyectos"))


@app.route("/ver-encargados")
def ver_encargados():
    encargados = list(encargados_collection.find())
    return render_template("ver_encargados.html", encargados=encargados)


@app.route("/registrar-encargado", methods=["GET", "POST"])
def registrar_encargado():
    if request.method == "POST":

        encargado = {
            "nombre": request.form["nombre"],
            "dpi": request.form["dpi"],
            "direccion": request.form["direccion"]
        }

        encargados_collection.insert_one(encargado)

        return redirect(url_for("ver_encargados"))

    return render_template("registrar_encargado.html")



@app.route("/editar-encargado/<id>", methods=["GET", "POST"])
def editar_encargado(id):

    encargado = encargados_collection.find_one({"_id": ObjectId(id)})

    if request.method == "POST":

        encargados_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "nombre": request.form["nombre"],
                "dpi": request.form["dpi"],
                "direccion": request.form["direccion"]
            }}
        )

        return redirect(url_for("ver_encargados"))

    return render_template("editar_encargado.html", encargado=encargado)

@app.route("/eliminar-encargado/<id>", methods=["POST"])
def eliminar_encargado(id):
    encargados_collection.delete_one({"_id": ObjectId(id)})

    proyectos_collection.update_many(
        {"encargadoId": id},
        {"$set": {"encargadoId": None, "encargado": None}}
    )

    return redirect(url_for("ver_encargados"))


if __name__ == "__main__":
    app.run(debug=True)
