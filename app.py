from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'clave_simple'


usuarios = {}


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

        if correo in usuarios:
            flash('El correo ya existe')
            return redirect(url_for('registro'))

        usuarios[correo] = {
            "nombre": nombre,
            "password": clave
        }

        flash('Cuenta creada correctamente')
        return redirect(url_for('login'))

    return render_template('registro.html')



@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['email']
        clave = request.form['password']

        if correo in usuarios and usuarios[correo]['password'] == clave:
            session['usuario'] = usuarios[correo]['nombre']
            session['correo'] = correo
            return redirect(url_for('dashboard'))
        else:
            flash('Correo o contraseña incorrectos')

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



@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html')



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)