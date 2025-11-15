from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


encargados = [
    {
        "_id": "E001",
        "nombre": "Luis Pérez",
        "dpi": "1234567890101",
        "direccion": "Zona 10, Ciudad Guatemala"
    }
]

proyectos = [
    {
        "_id": "P001",
        "nombre": "Proyecto Pozo Comunitario",
        "descripcion": "Construcción de pozo para abastecimiento de agua.",
        "fechaInicio": "2025-11-01",
        "fechaFin": "2026-01-12",
        "presupuesto": 50000,
        "finalizado": False,

        "encargadoId": "E001",
        "encargado": {
            "nombre": "Luis Pérez",
            "dpi": "1234567890101",
            "direccion": "Zona 10, Ciudad Guatemala"
        },

        "familiasBeneficiadas": [
            {"direccion": "Aldea El Carmen", "ingresoMensual": 1800},
            {"direccion": "Sector La Unión", "ingresoMensual": 2300}
        ]
    }
]

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/registrar-proyecto", methods=["GET", "POST"])
def registrar_proyecto():
    if request.method == "POST":

        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        encargadoId = request.form["encargado"]


        encargado = next(e for e in encargados if e["_id"] == encargadoId)

        proyectos.append({
            "_id": f"P{len(proyectos) + 1:03d}",
            "nombre": nombre,
            "descripcion": descripcion,
            "encargadoId": encargadoId,
            "encargado": {
                "nombre": encargado["nombre"],
                "dpi": encargado["dpi"],
                "direccion": encargado["direccion"]
            },
            "familiasBeneficiadas": []
        })

        return redirect(url_for("ver_proyectos"))

    return render_template("registrar_proyecto.html", encargados=encargados)


@app.route("/agregar-familia/<id>", methods=["GET", "POST"])
def agregar_familia(id):
    proyecto = next((p for p in proyectos if p["_id"] == id), None)

    if request.method == "POST":

        direcciones = request.form.getlist("direccion[]")
        ingresos = request.form.getlist("ingresoMensual[]")

        for d, i in zip(direcciones, ingresos):
            proyecto["familiasBeneficiadas"].append({
                "direccion": d,
                "ingresoMensual": i
            })

        return redirect(url_for("ver_proyectos"))

    return render_template("agregar_familia.html", proyecto=proyecto)



@app.route("/ver-proyectos")
def ver_proyectos():
    return render_template("ver_proyectos.html", proyectos=proyectos, encargados=encargados)


@app.route("/ver-encargados")
def ver_encargados():
    return render_template("ver_encargados.html", encargados=encargados)

@app.route("/registrar-encargado", methods=["GET", "POST"])
def registrar_encargado():
    if request.method == "POST":
        nombre = request.form["nombre"]
        dpi = request.form["dpi"]
        direccion = request.form["direccion"]

        encargados.append({
            "_id": f"E{len(encargados) + 1:03d}",
            "nombre": nombre,
            "dpi": dpi,
            "direccion": direccion
        })

        return redirect(url_for("ver_encargados"))

    return render_template("registrar_encargado.html")




if __name__ == "__main__":
    app.run(debug=True)

