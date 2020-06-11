# importamos la instancia de Flask (app)
from apptrivia import app
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from forms.login import LoginForm
from forms.register import RegisterForm
import os, random, datetime
# importamos los modelos a usar
from models.models import Categoria, Pregunta, User, Respuesta, Role
from flask import render_template, redirect, url_for, flash, request, session, jsonify, abort
from werkzeug.exceptions import HTTPException
from flask_principal import Principal, Permission, Identity, AnonymousIdentity, RoleNeed, UserNeed, identity_loaded, identity_changed

# para poder usar Flask-Login
login_manager = LoginManager(app)
login_manager.init_app(app)


@app.route('/trivia')
def index_trivia():
    return render_template('trivia.html')

@app.route('/trivia/categorias', methods=['GET'])
@login_required
def mostrar_categorias():
    categorias = Categoria.query.all()

    if "tiempo_inicio" not in session.keys():
        session['tiempo_inicio'] = datetime.datetime.now()
        for c in categorias:
            session[str(c.id)] = False
    return render_template('categorias.html', categorias=categorias)


@app.route('/trivia/<int:id_categoria>/pregunta', methods=['GET'])
@login_required
def mostrar_pregunta(id_categoria):
    preguntas = Pregunta.query.filter_by(categoria_id=id_categoria).all()
    # elegir pregunta aleatoria pero de la categoria adecuada
    pregunta = random.choice(preguntas)
    categ = Categoria.query.get(id_categoria)

    respuestas_posibles = pregunta.respuestas
    return render_template('preguntas.html', categoria=categ, pregunta=pregunta, respuestas_posibles=respuestas_posibles)    


@app.route('/trivia/<int:id_categoria>/<int:pregunta_id>/respuesta/<int:id_respuesta>', methods=['GET'])
@login_required
def evaluar_respuesta(id_categoria, pregunta_id, id_respuesta):
    r = Respuesta.query.get(id_respuesta)
    msg = "Error!!"
    if r.pregunta_id == pregunta_id and r.correcta:
        msg = "Éxito!"
        session[str(id_categoria)] = True
        
        termina_juego = True
        categs = Categoria.query.all()
        for c in categs:
            if session[str(c.id)] == False:
                # me voy del ciclo porque ya se que falta satisfacer alguna categoria.
                termina_juego = False
                break

        if termina_juego:
            session['tiempo_total'] = str(datetime.datetime.now() - session['tiempo_inicio'])
            return render_template('ganador.html')   
        
    return render_template('respuestas.html', message=msg)


#le decimos a Flask-Login como obtener un usuario
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

@app.route('/trivia/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index_trivia'))
    form = LoginForm()
    if form.validate_on_submit():
        #get by email valida
        user = User.get_by_email(form.email.data)
        if user is not None and user.check_password(form.password.data):
            # funcion provista por Flask-Login, el segundo parametro gestion el "recordar"
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next', None)
            if not next_page:
                next_page = url_for('index_trivia')
            return redirect(next_page)

        else:
            flash('Usuario o contraseña inválido')
            return redirect(url_for('login'))
    # no loggeado, dibujamos el login con el form vacio
    return render_template('login.html', form=form)

@app.route("/trivia/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    error = None
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        # Comprobamos que no hay ya un usuario con ese email
        user = User.get_by_email(email)
        if user is not None:
            flash('El email {} ya está siendo utilizado por otro usuario'.format(email))
        else:
            # Creamos el usuario y lo guardamos
            user = User(name=username, email=email)
            user.set_password(password)
            user.save()
            # Dejamos al usuario logueado
            login_user(user, remember=True)
            return redirect(url_for('index_trivia'))
    return render_template("register.html", form=form)


@app.route('/trivia/logout')
def logout():
    logout_user()
    # Flask-Principal: Remove session keys
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Flask-Principal: the user is now anonymous
    identity_changed.send(app, identity=AnonymousIdentity())
    return redirect(url_for('index_trivia'))

""" manejo de errores """

@app.errorhandler(404)
def page_not_found(e):
    #return jsonify(error=str(e)), 404
    return render_template('404.html')


@app.errorhandler(401)
def unathorized(e):
    return jsonify(error=str(e)), 404


@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify(error=str(e)), e.code

""" Flask-Principal"""

# Flask-Principal: ---  Setup ------------------------------------
principal = Principal()
principal.init_app(app)

# Flask-Principal: Creamos un permiso, para ser satisfecho hay que ser Admin
admin_permission = Permission(RoleNeed('admin'))


# Flask-Principal: Agregamos las necesidades a una identidad, una vez que se loguee el usuario.
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Seteamos la identidad al usuario
    identity.user = current_user

    # Agregamos una UserNeed a la identidad, con el usuario actual.
    if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

    # Agregamos a la identidad la lista de roles que posee el usuario actual.
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.rolename))



@app.route('/test')
@login_required
@admin_permission.require(http_exception=403)
def test_principal():
    return render_template('test.html')