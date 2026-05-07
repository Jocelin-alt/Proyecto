from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from GestorTareas import GestorTareas

app = Flask(__name__)
app.secret_key = "clave"

db = GestorTareas()



@app.route('/', methods=['GET', 'POST'])
def login():

    if 'usuario_id' in session:
        return redirect(url_for('panel'))

    if request.method == 'POST':

        correo = request.form.get('email')
        password = request.form.get('password')

        usuario = db.obtener_usuario2(correo, password)

        if usuario:

            session['usuario_id'] = str(usuario['_id'])
            session['usuario'] = usuario['username']

            flash('Bienvenido')
            return redirect(url_for('panel'))

        else:
            flash('Correo o contraseña incorrectos')

    return render_template('login.html')



@app.route('/registro', methods=['GET', 'POST'])
def registro():

    if request.method == 'POST':

        nombre = request.form.get('nombre')
        correo = request.form.get('email')
        password = request.form.get('password')
        confirmar = request.form.get('confirmar_password')

        if not nombre or not correo or not password:

            flash('Completa todos los campos')
            return redirect(url_for('registro'))

        if password != confirmar:

            flash('Las contraseñas no coinciden')
            return redirect(url_for('registro'))

        existe = db.usuarios.find_one({
            "email": correo
        })

        if existe:

            flash('Ese correo ya existe')
            return redirect(url_for('registro'))

        nuevo_usuario = {
            "username": nombre,
            "email": correo,
            "password": password,
            "fecha": datetime.now()
        }

        db.usuarios.insert_one(nuevo_usuario)

        flash('Cuenta creada correctamente')

        return redirect(url_for('login'))

    return render_template('registro.html')


@app.route('/panel', methods=['GET', 'POST'])
def panel():

    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    usuario = session['usuario_id']

    if request.method == 'POST':

        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')

        db.crear_tarea(
            usuario,
            titulo,
            descripcion
        )

        flash('Actividad agregada')

        return redirect(url_for('panel'))

    pendientes = db.obtener_tareas_usuario(
        usuario,
        'pendiente'
    )

    completadas = db.obtener_tareas_usuario(
        usuario,
        'completada'
    )

    canceladas = db.obtener_tareas_usuario(
        usuario,
        'cancelada'
    )

    return render_template(
        'dashboard.html',
        pendientes=pendientes,
        completadas=completadas,
        canceladas=canceladas
    )


@app.route('/completar/<id>')
def completar(id):

    if 'usuario_id' in session:

        db.actualizar_estado_tarea(
            id,
            'completada'
        )

        flash('Tarea completada')

    return redirect(url_for('panel'))


@app.route('/cancelar/<id>', methods=['POST'])
def cancelar(id):

    if 'usuario_id' in session:

        motivo = request.form.get('motivo')

        db.actualizar_estado_tarea(
            id,
            'cancelada'
        )

        tareas = db.obtener_tareas_usuario(
            session['usuario_id']
        )

        for tarea in tareas:

            if tarea['_id'] == id:

                db.tareas.update_one(
                    {"titulo": tarea['titulo']},
                    {
                        "$set": {
                            "motivo": motivo
                        }
                    }
                )

                break

        flash('Tarea cancelada')

    return redirect(url_for('panel'))


@app.route('/eliminar/<id>')
def eliminar(id):

    if 'usuario_id' in session:

        db.eliminar_tarea(id)

        flash('Tarea eliminada')

    return redirect(url_for('panel'))



@app.route('/editar/<id>', methods=['GET', 'POST'])
def editar(id):

    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    tareas = db.obtener_tareas_usuario(
        session['usuario_id']
    )

    tarea_actual = None

    for tarea in tareas:

        if tarea['_id'] == id:
            tarea_actual = tarea
            break

    if request.method == 'POST':

        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')

        db.tareas.update_one(
            {"titulo": tarea_actual['titulo']},
            {
                "$set": {
                    "titulo": titulo,
                    "descripcion": descripcion
                }
            }
        )

        flash('Tarea actualizada')

        return redirect(url_for('panel'))

    return render_template(
        'editar.html',
        tarea=tarea_actual
    )



@app.route('/logout')
def logout():

    session.clear()

    flash('Sesión cerrada')

    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)