from flask import Flask, render_template, request, redirect, url_for, session, flash
from GestorTareas import GestorTareas

app = Flask(__name__)

app.secret_key = 'fdg4t3gfre3v4'

gestor = GestorTareas()
gestor.crear_usuario("Joss", "Josselin@gmail.com", "123456")





@app.route('/signup', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['email']
        clave = request.form['password']
        confirmar = request.form['confirmar_password']

        if clave != confirmar:
            flash('Las contraseñas no coinciden')
            return redirect(url_for('registro'))

        usuario_existente = gestor.usuarios.find_one({"email": correo})

        if usuario_existente:
            flash('El correo ya existe')
            return redirect(url_for('registro'))

        
        resultado = gestor.crear_usuario(nombre, correo, clave)
        
        if resultado:
            flash('Cuenta creada correctamente')
            return redirect(url_for('login'))
        else:
            flash('Error al crear la cuenta')
            return redirect(url_for('registro'))

    return render_template('registro.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'id_sesion' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        user_mail = request.form.get('email')
        user_pass = request.form.get('password')

        cuenta = gestor.obtener_usuario2(user_mail, user_pass)

        if cuenta:
            session['id_sesion'] = str(cuenta['_id'])
            session['user_name'] = cuenta['nombre']
            
            flash(f'Sesión iniciada: Hola {cuenta["nombre"]}', 'primary')
            return redirect(url_for('dashboard'))
        else:
            flash('Acceso denegado: credenciales erróneas.', 'danger')

    return render_template('login.html')


@app.route('/reset', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        correo = request.form['email']
        nueva = request.form['nueva_password']

        if correo in usuarios:
            usuarios[correo]['password'] = nueva
            flash('Contraseña actualizada')
            return redirect(url_for('login'))
        else:
            flash('Correo no encontrado')

    return render_template('recuperar.html')



@app.route('/tareas')
def dashboard():
    if 'id_sesion' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)