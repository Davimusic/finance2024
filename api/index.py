from flask import Flask, render_template, request, redirect, session
import pymongo                 
from bson.objectid import ObjectId  # para poder usar _id de mongo
from datetime import datetime
import bcrypt # solo para el logeo ya que solo permite encriptar pero no desencriptar
from cryptography.fernet import Fernet

clave = b'C0eBZ2GSloqabxyT855f6tkbSfdIaJDx_K1Ljiymxkk='#para encriptar informacion desencriptable
f = Fernet(clave)


app = Flask(__name__)
app.secret_key = 'mi clave secreta'


#conexcion a base de datos     
myClient = pymongo.MongoClient("mongodb+srv://davis123:davis123@cluster0.hujqu.mongodb.net/test3")
myDb = myClient["contabilidadPublica"]#basde de datos
myCollection=myDb["coleccion1"]#coleccion1


def cambiarValor(busca, cambia, text):
    tex = ''
    for u in text:
        if(u == busca):
            tex += cambia
        else:
            tex += u          
    return tex

def CRUD(accion, valorNum, ruta):
    print('desde crud')
    print(accion)

    if valorNum == "negativo":
        dinero =  retornarNumeroNegativo(int(request.form.get("dinero", '')))
    else:
        dinero = request.form.get("dinero", '')    
    
    referencia = request.form.get("referencia", '')
    fecha = cambiarValor('-', '/', request.form.get("fecha", '')) 
    texto = request.form.get("texto", '')
    codUnico = request.form.get("codUnico", '')
    signoNumerico = request.form.get("signoNumerico", '')

    print('codUnico')
    print(codUnico)

    doc = myCollection.find_one({"email": session['email']})
    paso = doc['usoDeReferencias']
    now = datetime.now()

    if(accion == "crear"):

        # Encuentra el índice del objeto con la referencia
        index = next((index for (index, d) in enumerate(paso) if desencriptarText(list(d.keys())[0]) == referencia), None)
        info = {"dinero": dinero, "fecha": fecha, "texto": cambiarValor(',', '-', texto), "fechaDeCreacion": f"{now.year}/{now.month}/{now.day}"}
        # Si la referencia existe, agrega la nueva información a la lista existente
        if index is not None:
            clave = list(paso[index].keys())[0]
            if isinstance(paso[index][clave], list):
                paso[index][clave].append(info)
            else:
                paso[index][clave] = [info]
        '''        
        else:
            # Si la referencia no existe, agrega una nueva entrada con una lista como valor
            paso.append({encriptarText(referencia): [info]})'''

    elif(accion == "editar"):

        if signoNumerico == 'negativo':
            dinero = retornarNumeroNegativo(int(dinero))
        else:
            dinero = retornarNumeroPositivo(int(dinero))

        info = {"dinero": dinero, "fecha": fecha, "texto": cambiarValor(',', '-', texto), "fechaDeCreacion": f"{now.year}/{now.month}/{now.day}"}

        for key in doc['usoDeReferencias']:
            for u in key.keys():
                if desencriptarText(u) == referencia:
                    key[u][int(codUnico)] = info



    elif(accion == "borrar"):

        for key in doc['usoDeReferencias']:
            for u in key.keys():
                if desencriptarText(u) == referencia:
                    # Remove the item at the index codUnico from the dictionary
                    key[u].pop(int(codUnico))

    updateTask = {"$set":{'usoDeReferencias': paso}}
    myCollection.update_one({"_id": doc['_id']}, updateTask)                

    return redirect(ruta)    

def retornarStringInformacion(arr, acc, idFiltrado):
    print('retornarStringInformacion arr')
    print(arr)
    print('idFiltrado')
    print(idFiltrado)

    texto = ""
    count = 0
    for u in arr:
        print('count')
        print(count)
        for key in u.keys():
            for user in u[key]:
                print('desde user')
                print(user)
                info = ""
                if acc == "negativo":
                    if int(user['dinero']) < 0:
                        info = f"{key}${user['dinero']}${user['fecha']}${user['texto']}${retornarSigoNumerico(int(user['dinero']))}${idFiltrado[count]}º" 
                elif acc == "positivo":
                    if int(user['dinero']) >= 0:
                        info = f"{key}${user['dinero']}${user['fecha']}${user['texto']}${retornarSigoNumerico(int(user['dinero']))}${idFiltrado[count]}º"
                elif acc == "todos":
                        info = f"{key}${user['dinero']}${user['fecha']}${user['texto']}${retornarSigoNumerico(int(user['dinero']))}${idFiltrado[count]}º"               
                texto += info
                count += 1
    print(f"texto: {texto}") 
    return texto 

def retornarSigoNumerico(num):
    if num < 0:
        return 'negativo'
    else:
        return 'positivo' 

def retornarReferencias():
    
    doc = myCollection.find_one({"email": session['email']})
    text = ''
    for item in doc['usoDeReferencias']:
        for key in item.keys():
            text += desencriptarText(key) + "$"
    text = text[:-1]  
    text += "º"     
    return text

def retornarNumeroNegativo(num):
    if num >= 0:
        return -num
    else:
        return num     

def retornarNumeroPositivo(num):
    if num > 0:
        return num
    else:
        return (-1 * num)

def retornarSignoSeparador():
    return "Z"

def filtroBuscar():
    buscarReferencia = request.form.get('buscarReferencia', '')
    buscarFecha = request.form.get('buscarFecha', '')
    return redirect(f'/{buscarReferencia}{retornarSignoSeparador()}{buscarFecha}')
    
def retornarInfoReferencia(valorNum):
    now = datetime.now()
    doc = myCollection.find_one({"email": session['email']})
    buscarInfo = []
    ids = []
    num = 0

    for item in doc['usoDeReferencias']:
        for llave in item.keys():
            for fecha in item[llave]:
                
                if f"{now.year}/{now.month}/{now.day}" == fecha['fechaDeCreacion']:
                    info = {desencriptarText(llave): [fecha]}
                    if info not in buscarInfo:
                        ids.append(num)
                        buscarInfo.append(info)
                num +=1
                        
    textContenido = ""
    textContenido += retornarReferencias()
    textContenido += retornarStringInformacion(buscarInfo, valorNum, ids)   
    return render_template('index.html', texto = textContenido)

def retornarReferenciasDesglosadas():
    '''
    dicc = {}
    nombresReferencias = myCollection.find({'nombresReferencias': {'$exists': True}})
        
    for i in nombresReferencias:
        for u in i['nombresReferencias']:
            referencias = myCollection.find({'referencia': u})
            print('referencias')
            print(referencias)
            arr = ['@ingresos@', '@egresos@']
            for q in arr:
                for i in range(1, 13):
                    num = ''
                    if i <= 9:
                        num = f'0{i}'
                    else:
                        num = i     
                    dicc[f'{u}{q}{num}'] = 0           
            for a in referencias:
                mes = a['fecha'][5:7]
                dinero = int(a['dinero'])
                if dinero < 0:
                    dicc[f'{u}@egresos@{mes}'] += int(a['dinero']) 
                else:
                    dicc[f'{u}@ingresos@{mes}'] += int(a['dinero'])  

    text = f'{retornarReferencias()},'
    for i in dicc:
        #print(i)
        #print(dicc[i])
        text += f"{str(i)}@{str(dicc[i])}@,"
    print('text')
    print(text)    
    return text
    #return render_template('graficosAnual.html', meses = text)'''

    dicc = {}
    doc = myCollection.find_one({"email": session['email']})
    
    for ref in doc['usoDeReferencias']:
        for u, referencias in ref.items():
            decrypted_u = desencriptarText(u)  # Decrypt the reference name
            print('referencias')
            print(referencias)
            arr = ['@ingresos@', '@egresos@']
            for q in arr:
                for i in range(1, 13):
                    num = ''
                    if i <= 9:
                        num = f'0{i}'
                    else:
                        num = i     
                    dicc[f'{decrypted_u}{q}{num}'] = 0           
            for a in referencias:
                mes = a['fecha'][5:7]
                dinero = int(a['dinero'])
                if dinero < 0:
                    dicc[f'{decrypted_u}@egresos@{mes}'] += int(a['dinero']) 
                else:
                    dicc[f'{decrypted_u}@ingresos@{mes}'] += int(a['dinero'])  

    text = f'{retornarReferencias()},'
    for i in dicc:
        text += f"{str(i)}@{str(dicc[i])}@,"
    print('text')
    print(text)    
    return text

def validacionLogeo(siLograLogear,siNoLogralogear):
    
    email = request.form.get("email")
    password = request.form.get("contrasena")
    contrasenaComparar = request.form.get("contrasenaComparar")
    estadoLogeo = request.form.get("estadoLogeo")

    if siLograLogear == '':
        if 'email' in session and session['email'] != '':
            return 'si esta logeado'
        else:
            return 'no esta logeado' 

    if request.method == "POST": 
        session['estadoLogeo'] = estadoLogeo
        if session['estadoLogeo'] == 'existente':
            doc = myCollection.find_one({"email": email})
            if doc is None:
                return eval(siNoLogralogear + "'Correo NO existente')")
            else:
                userPassword = password.encode('utf-8')
                if bcrypt.checkpw(userPassword, doc.get('password')):
                    session['email'] = email
                    return  eval(siLograLogear)
                else:
                    return eval(siNoLogralogear + "'contraseñas incorrectas')")
        elif session['estadoLogeo'] == 'nuevo':
            doc = myCollection.find_one({"email": email})
            if doc is None:
                if comprarContrasenas(password, contrasenaComparar):
                    if analizarSignosProhibidos(email, caracteres_permitidos=['@', '.']):
                        ashed_password = encriptarContrasena(password)
                        myCollection.insert_one({"email": email, 'password': ashed_password, "usoDeReferencias": []})
                        session['email'] = email
                        return  eval(siLograLogear)
                    else: 
                        return eval(siNoLogralogear + "'ingreso de signos no permitidos en el correo, solo letras, numeros, @ y . estàn permitidos')")  
                else:
                        return eval(siNoLogralogear + "'las contraseñas ingresadas no coinciden')")  
            else:
                return eval(siNoLogralogear + "'correo ya registrado')")   
    elif  request.method == "GET":
        if 'email' in session and session['email'] != '':
            return eval(siLograLogear)
        else:
            return eval(siNoLogralogear)

def comprarContrasenas(contrasena1, contrasena2):
    if(contrasena1 == contrasena2):
        return True
    else:
        return False

def analizarSignosProhibidos(text, solo_numeros=False, solo_letras=False, caracteres_permitidos=[], caracteres_prohibidos=[]):
    for caracter in text:
        if caracter in caracteres_prohibidos:
            return False
        if solo_numeros and not caracter.isdigit() and caracter not in caracteres_permitidos:
            return False
        elif solo_letras and not caracter.isalpha() and caracter not in caracteres_permitidos:
            return False
        elif not solo_numeros and not solo_letras and not caracter.isalnum() and caracter not in caracteres_permitidos:
            return False
    return True


def encriptarContrasena(text):
    bcryptPassword = text.encode('utf-8')  
    ashed_password = bcrypt.hashpw(bcryptPassword, bcrypt.gensalt()) 
    return ashed_password

def encriptarText(text):
    mensaje = str(text).encode()
    token = f.encrypt(mensaje).decode()  
    return token 

def desencriptarText(text):
    return f.decrypt(text).decode()

def update(id, llave, valor):
    query = {"_id": ObjectId(id)}
    updateTask = {"$set":{llave: valor}}
    myCollection.update_one(query, updateTask)

def buscar_informacion(referencia, fecha):
    buscarInfo = []
    doc = myCollection.find_one({"email": session['email']})
    ids = []
    num = 0

    for item in doc['usoDeReferencias']:
        for llave in item.keys():
            for fecha in item[llave]:
                if referencia and desencriptarText(llave) == referencia:
                    buscarInfo = [{desencriptarText(llave): item[llave]}]
                    ids.append(num)
                elif fecha:
                    for info in item[llave]:
                        if info['fecha'] == cambiarValor('-', '/', fecha):
                            for buscarItem in buscarInfo:
                                if desencriptarText(llave) in buscarItem:
                                    buscarItem[desencriptarText(llave)].append(info)
                                    break
                            else:
                                buscarInfo.append({desencriptarText(llave): [info]})
                                ids.append(num)
                elif referencia and fecha:
                    matching_items = [info for info in item[llave] if info['fecha'] == cambiarValor('-', '/', fecha)]
                    if matching_items:
                        buscarInfo.append({desencriptarText(llave): matching_items})
                        ids.append(num)
                num += 1


    texto = retornarReferencias() + retornarStringInformacion(buscarInfo, "todos", ids)
    if validacionLogeo('', '') ==  'si esta logeado':
        return render_template('index.html', texto = texto)
    else:
        return redirect('/')

@app.route('/', methods=["GET", "POST"])
def logeo():
    
    if request.method == "POST": 
        return validacionLogeo("redirect('/ingresos')", "render_template('logeo.html', mensaje = ")   #'error de logeo')
    else:
        return validacionLogeo("redirect('/ingresos')", "render_template('logeo.html', mensaje = '')")   

@app.route('/ingresos', methods=["GET", "POST"])
def inicio():

    if request.method == "POST": 
        accion = request.form["formUso"]
        if accion == "filtroBuscar":
            return filtroBuscar()   
        else:
            return CRUD(accion, '', "/")    
    else:  
        return validacionLogeo("retornarInfoReferencia('positivo')", "redirect('/')")

@app.route('/egresos', methods=["GET", "POST"])
def egresos():
    
    if request.method == "POST": 
        accion = request.form["formUso"]
        if accion == "filtroBuscar":
            return filtroBuscar()
        else:
            return CRUD(accion, 'negativo', "/egresos")        
    else:  
        return validacionLogeo("retornarInfoReferencia('negativo')", "redirect('/')")

@app.route('/vistaDeFlujoReferencias', methods=["GET", "POST"])
def vistaDeFlujoReferencias():
    if validacionLogeo('', '') ==  'si esta logeado':
        return render_template('graficosAnual.html', meses = retornarReferenciasDesglosadas())
    else:
        return redirect('/')       
    
@app.route('/vistaDeFlujoCompactado', methods=["GET", "POST"])
def vistaDeFlujoCompactado():
    if validacionLogeo('', '') ==  'si esta logeado':
        return render_template('graficosAnual.html', meses = retornarReferenciasDesglosadas())
    else:
        return redirect('/')   

@app.route('/crudreferencias', methods=["GET", "POST"])
def crudreferencias():
    if request.method == "POST": 
        accion = request.form["formUso"]
        crear = request.form["crear"]
        cambiar = request.form["cambiar"]
        nuevocambiar = request.form["nuevocambiar"]
        borrar = request.form["borrar"]
        doc = myCollection.find_one({"email": session['email']})

        if accion == 'crear':

            if crear == '':
                return render_template('crudReferencias.html', texto = retornarReferenciasDesglosadas(), aviso = 'campo vacio ingresado, no es posible.')
            
            if analizarSignosProhibidos(crear, caracteres_prohibidos=[retornarSignoSeparador()]) == False:
                return render_template('crudReferencias.html', texto = retornarReferenciasDesglosadas(), aviso =  'Solo es posible letras a excepciòn de la letra "' + retornarSignoSeparador() +  '" y numeros, no puedes usar espacio ni signos.')
            
            for key in doc['usoDeReferencias']:
                for u in key.keys():
                    decrypted_key = desencriptarText(u)
                    if decrypted_key == crear:
                        return render_template('crudReferencias.html', texto = retornarReferenciasDesglosadas(), aviso = 'referencia ya existente')

            # If the reference does not exist, append it to the 'usoDeReferencias' field
            doc['usoDeReferencias'].append({encriptarText(crear): {}})

            # Update the document in the database
            myCollection.update_one({"_id": doc['_id']}, {"$set": {"usoDeReferencias": doc['usoDeReferencias']}})
            
        elif accion == 'cambiar':

            if nuevocambiar == '':
                return render_template('crudReferencias.html', texto = retornarReferenciasDesglosadas(), aviso = 'campo vacio ingresado, no es posible.')
            
            if analizarSignosProhibidos(nuevocambiar, caracteres_prohibidos=[retornarSignoSeparador()]) == False:
                return render_template('crudReferencias.html', texto = retornarReferenciasDesglosadas(), aviso = 'Solo es posible letras a excepciòn de la letra "' + retornarSignoSeparador() +  '" y numeros, no puedes usar espacio ni signos.')
            
            arr = []
            for key in doc['usoDeReferencias']:
                for u in key.keys():
                    decrypted_key = desencriptarText(u)
                    if decrypted_key == nuevocambiar:
                        return render_template('crudReferencias.html', texto = retornarReferenciasDesglosadas(), aviso = 'referencia ya existente, no puedes usar la palabra: "{}" para mas de una referencia'.format(nuevocambiar))
                    if decrypted_key == cambiar:
                        arr.append({encriptarText(nuevocambiar): key[u]})
                    else:
                        arr.append({u: key[u]})

            # Update the document in the database
            myCollection.update_one({"_id": doc['_id']}, {"$set": {"usoDeReferencias": arr}})    
                    
        elif accion == 'borrar':

            arr = []
            for key in doc['usoDeReferencias']:
                for u in key.keys():
                    decrypted_key = desencriptarText(u)
                    if decrypted_key == borrar:
                        continue
                    else:
                        arr.append({u: key[u]})

            myCollection.update_one({"_id": doc['_id']}, {"$set": {"usoDeReferencias": arr}})

        return redirect('/crudreferencias')
    else:  
        return render_template('crudReferencias.html', texto = retornarReferenciasDesglosadas(), aviso = '') 

@app.route('/<dato>', methods=["GET", "POST"])
def filtroReferencia(dato):

    busqueda = []
    for u in dato.split(retornarSignoSeparador()):
        busqueda.append(u)
    referencia = busqueda[0]
    fecha = busqueda[1] 

    if referencia == '' and fecha == '': 
        return redirect('/ingresos')   

    if request.method == "GET":

        return buscar_informacion(referencia, fecha)
        
    else:

        accion = request.form["formUso"]
        if accion == "filtroBuscar":
            return filtroBuscar()
        else:
            return CRUD(accion, '', "/") 

@app.route('/anotaciones', methods=["GET", "POST"])
def anotaciones():

    buscar = myCollection.find({'anotaciones': {'$exists': True}})
    if request.method == "GET":
        
        texto = ""
        for i in buscar:
            texto += i['anotaciones']
        #print(texto)    
        return render_template('anotaciones.html', mensaje = str(texto))

    else:
        
        for i in buscar:
            id = i['_id']
        anotaciones = request.form.get("anotaciones", '')
        update(id, 'anotaciones', anotaciones)

        return redirect('/anotaciones')

@app.route('/salir')
def salir():
    session['email'] = ''
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5002)    

