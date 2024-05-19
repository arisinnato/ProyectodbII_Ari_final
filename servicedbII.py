from flask import Flask, request, render_template, redirect, url_for, flash, session 
from pymongo import MongoClient, collection  
from bson.objectid import ObjectId 
from collections import defaultdict
from werkzeug.security import check_password_hash


app = Flask(__name__, template_folder="./templates")
app.config['SECRET_KEY'] = "clave secreta"

elementsList = []

client = MongoClient('mongodb://localhost:27017/')
db = client['ProjectodbII_Ari']
examenes = db['examenes']
categorias = db['categorias']
usuarios = db['user']
indicaciones = db['indicaciones']

#################################### HOME ########################################################

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html.jinja')


################################### REGISTRAR ########################################################## 

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        username = request.form['username']
        password = request.form['password']
        usuarios.insert_one({"nombre": nombre, "apellido": apellido,
                             "username": username, "password": password})
        flash("usuario registrado correctamente (congrats)")

        return redirect(url_for('login'))  
    else:
        return render_template('register.html.jinja')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print("username" + username)
        print("password" + password)
        
        usuario = usuarios.find_one({'username': username}, {'password': password})

        if usuario:
            return render_template('home2.html.jinja')
        else:
            message = 'Correo electrónico o contraseña incorrecta'
            return render_template('login.html.jinja', mensaje = message)
            

    else: 
        return render_template('login.html.jinja')
        


######################################## EXAMENES ################################################################################

@app.route('/exams')
def listar_examenes():
    lista_examenes = list(examenes.find())
    return render_template('/Examenes/lista_examenes.html.jinja', examenes=lista_examenes)

@app.route('/crear_examen', methods=['GET', 'POST'])
def crear_examen():
    if request.method == 'POST':
        codigo = request.form['codigo']
        categoria = request.form['categoria']
        tipo_muestra = request.form['tipo_muestra']
        precio = request.form['precio']
        indicaciones_lista = request.form.getlist('indicaciones')

        nuevo_examen = {
            'codigo': codigo,
            'categoria': categoria,
            'tipo_muestra': tipo_muestra,
            'precio': precio,
            'indicaciones': indicaciones_lista
        }
        examenes.insert_one(nuevo_examen)
        return redirect('/')
    else:
        categorias_lista = list(categorias.find())
        indicaciones_lista = list(indicaciones.find())
        return render_template('/Examenes/create_exam.html.jinja', categorias=categorias_lista, indicaciones=indicaciones_lista)
    
@app.route('/modificar_examen/<id>', methods=['GET', 'POST'])
def modificar_examen(id):
    examen = examenes.find_one({'_id': ObjectId(id)})
    if request.method == 'POST':
        codigo = request.form['codigo']
        categoria = request.form['categoria']
        tipo_muestra = request.form['tipo_muestra']
        precio = request.form['precio']
        indicaciones_lista = request.form.getlist('indicaciones')

        examenes.update_one({'_id': ObjectId(id)}, {'$set': {
            'codigo': codigo,
            'categoria': categoria,
            'tipo_muestra': tipo_muestra,
            'precio': precio,
            'indicaciones': indicaciones_lista
        }})
        return redirect('/')
    else:
        categorias_lista = list(categorias.find())
        indicaciones_lista = list(indicaciones.find())
        return render_template('/Examenes/mod_examen.html.jinja', examen=examen, categorias=categorias_lista, indicaciones=indicaciones_lista)

@app.route('/consultar_examen/<id>')
def consultar_examen(id):
    examen = examenes.find_one({'_id': ObjectId(id)})
    return render_template('/Examenes/consultar_examen.html.jinja', examen=examen)

@app.route('/eliminar_examen/<id>', methods=['POST'])
def eliminar_examen(id):
    examenes.delete_one({'_id': ObjectId(id)})
    return redirect('/')

################################# CATEGORIA ###############################################

@app.route('/crear_categoria', methods=['GET', 'POST'])
def crear_categoria():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        categorias.insert_one({"nombre": nombre, "descripcion": descripcion})
        return redirect('/listar_categorias')
    else:
        return render_template('/Categorias/crear_categoria.html.jinja')

@app.route('/modificar_categoria/<id>', methods=['GET', 'POST'])
def modificar_categoria(id):
    categoria = categorias.find_one({'_id': ObjectId(id)})
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']

        categorias.update_one({'_id': ObjectId(id)}, {'$set': {
            'nombre': nombre,
            'descripcion': descripcion
        }})
        return redirect('/')
    else:
        return render_template('/Categorias/modificar_categoria.html.jinja', categoria=categoria)
    
@app.route('/listar_categorias')
def lista_categorias():
    categorylist = categorias.find({})
    return render_template("/Categorias/listar_categorias.html.jinja", categorylist=categorias)



@app.route('/eliminar_categoria/<id>', methods=['POST'])
def eliminar_categoria(id):
    categorias.delete_one({'_id': ObjectId(id)})
    return redirect('/')


################################ CATALOGO ###########################################

@app.route('/consultar_catalogo', methods=['GET'])
def consultar_catalogo():
        examenes_filtrados = examenes.find()
        categorias =db['categorias'].find()

        lista_examenes = list(examenes_filtrados)
        return render_template('/Catalogo/consultar_catalogo.html.jinja', examenes=lista_examenes, categorias=categorias)


############################################ REPORTE ##############################################

@app.route('/ver_reporte')
def ver_reporte():
    cantidad_por_categoria = defaultdict(int)
    for examen in examenes.find():
        cantidad_por_categoria[examen['categorias']] += 1

    indicaciones_frecuencia = defaultdict(int)
    for examen in examenes.find():
        for indicacion in examen['indicaciones']:
            indicaciones_frecuencia[indicacion] += 1
    indicacion_mas_comun = max(indicaciones_frecuencia, key=indicaciones_frecuencia.get)

    cantidad_por_intervalo = defaultdict(int)
    for examen in examenes.find():
        precio = examen['precio']
        if precio <= 100:
            cantidad_por_intervalo['1 - 100 bs'] += 1
        elif precio <= 200:
            cantidad_por_intervalo['101 - 200 bs'] += 1
        elif precio <= 300:
            cantidad_por_intervalo['201 - 300 bs'] += 1
        elif precio <= 500:
            cantidad_por_intervalo['301 - 500 bs'] += 1
        else:
            cantidad_por_intervalo['501+ bs'] += 1

    return render_template('ver_reporte.html.jinja', cantidad_por_categoria=cantidad_por_categoria, indicacion_mas_comun=indicacion_mas_comun, cantidad_por_intervalo=cantidad_por_intervalo)


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)