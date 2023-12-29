from flask import Flask, render_template, request, redirect, session
import pymongo                 
from bson.objectid import ObjectId  # para poder usar _id de mongo
from datetime import datetime, timedelta
import bcrypt # solo para el logeo ya que solo permite encriptar pero no desencriptar
from cryptography.fernet import Fernet
import json

#import smtplib
#from email.message import EmailMessage

import io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, LongTable, Paragraph, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from collections import defaultdict
from reportlab.lib.units import mm

clave = b'C0eBZ2GSloqabxyT855f6tkbSfdIaJDx_K1Ljiymxkk='#para encriptar informacion desencriptable
f = Fernet(clave)

app = Flask(__name__)
app.secret_key = 'mi clave secreta'

#conexcion a base de datos     
myClient = pymongo.MongoClient('mongodb+srv://davis123:davis123@cluster0.hujqu.mongodb.net/test3')
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
    
    referencia = request.form.get("referencia", '')
    fecha = cambiarValor('-', '/', request.form.get("fecha", '')) 
    texto = request.form.get("texto", '')
    codUnico = request.form.get("codUnico", '')
    signoNumerico = request.form.get("signoNumerico", '')
    rutActual = request.form.get("rutActual", '')
    actualReferenciaModal = request.form.get("actualReferenciaModal", '')

    if analizarSignosProhibidos(request.form.get("dinero", ''), solo_numeros= True, caracteres_permitidos=['-']) == False:
        return render_template('logeo.html', mensaje = 'En ingreso de dinero solo puedes ingresar números', ruta = rutActual)
    
    if valorNum == "negativo":
        dinero =  retornarNumeroNegativo(int(request.form.get("dinero", '')))
    else:
        dinero = request.form.get("dinero", '')    

    doc = myCollection.find_one({"email": session['email']})
    paso = doc['usoDeReferencias']
    now = datetime.now()

    if analizarSignosProhibidos(texto, solo_numeros=False, solo_letras=False, caracteres_permitidos= [' ', '.', ',', '-'], caracteres_prohibidos= ["'", '"', '`']) == False:
        return render_template('logeo.html', mensaje = 'No puedes algun tipo de comilla para textos usar solo puedes ingresar números y letras en "Texto adicional" información no guardada')

    if(accion == "crear"):

        # Encuentra el índice del objeto con la referencia
        index = next((index for (index, d) in enumerate(paso) if desencriptarText(list(d.keys())[0]) == referencia), None)
        info = {"dinero": encriptarText(dinero), "fecha": encriptarText(fecha), "texto": encriptarText(cambiarValor(',', '-', texto)), "fechaDeCreacion": f"{now.year}/{now.month}/{now.day}"}
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
        if actualReferenciaModal != referencia:
            referencia, actualReferenciaModal = actualReferenciaModal, referencia

        if signoNumerico == 'negativo':
            dinero = retornarNumeroNegativo(int(dinero))
        else:
            dinero = retornarNumeroPositivo(int(dinero))

        print('llegaaaa') 
        print(referencia)   

        info = {"dinero": encriptarText(dinero), "fecha": encriptarText(fecha), "texto": encriptarText(cambiarValor(',', '-', texto)), "fechaDeCreacion": ''}

        # Crea una copia del diccionario para iterar sobre él
        usoDeReferencias_copia = doc['usoDeReferencias'].copy()

        for i, key in enumerate(usoDeReferencias_copia):
            for u in key.keys():
                if desencriptarText(u) == referencia:
                    # Guarda la fecha de creación original
                    fechaCreacionOriginal = key[u][int(codUnico)]['fechaDeCreacion']
                    
                    # Actualiza la información directamente en el diccionario original
                    doc['usoDeReferencias'][i][u][int(codUnico)] = info
                    doc['usoDeReferencias'][i][u][int(codUnico)]['fechaDeCreacion'] = fechaCreacionOriginal
                    
                    if actualReferenciaModal != referencia:
                        pas = doc['usoDeReferencias'][i][u][int(codUnico)]
                        #borra el objeto actual de donde esta y serà pasado a la nueva referencia
                        doc['usoDeReferencias'][i][u].pop(int(codUnico))
                        for a, key in enumerate(usoDeReferencias_copia):
                            for e in key.keys():
                                if desencriptarText(e) == actualReferenciaModal:
                                    doc['usoDeReferencias'][a][e].append(pas) 

    elif(accion == "borrar"):

        for key in doc['usoDeReferencias']:
            for u in key.keys():
                if desencriptarText(u) == referencia:
                    # Remove the item at the index codUnico from the dictionary
                    key[u].pop(int(codUnico))

    updateTask = {"$set":{'usoDeReferencias': paso}}
    myCollection.update_one({"_id": doc['_id']}, updateTask)                

    try:
        rutActual
        return redirect(rutActual)
    except NameError:
        return redirect(ruta)  

def retornarStringInformacion(arr, acc, idFiltrado):
    
    texto = ""
    for u in arr:
        for key in u.keys():
            
            count = 0  # Reinicia el contador para cada clave
            
            for user in u[key]:
                
                info = ""
                if acc == "negativo":
                    if int(user['dinero']) < 0:
                        info = f"{key}${user['dinero']}${user['fecha']}${user['texto']}${retornarSigoNumerico(int(user['dinero']))}${idFiltrado[key][count]}º" 
                elif acc == "positivo":
                    if int(user['dinero']) >= 0:
                        info = f"{key}${user['dinero']}${user['fecha']}${user['texto']}${retornarSigoNumerico(int(user['dinero']))}${idFiltrado[key][count]}º"
                elif acc == "todos":
                    info = f"{key}${user['dinero']}${user['fecha']}${user['texto']}${retornarSigoNumerico(int(user['dinero']))}${idFiltrado[key][count]}º"               
                if info:
                    #print(f"Appending info: {info}")
                    texto += info
                else:
                    print(f"Info not appended for key {key} and user {user}")
                count += 1
    #print(f"texto: {texto}") 
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
    ids = {}

    for item in doc['usoDeReferencias']:
        for llave in item.keys():
            for index, fecha in enumerate(item[llave]):
                # Decrypt the 'texto' field
                fecha['texto'] = desencriptarText(fecha['texto'])
                fecha['dinero'] = desencriptarText(fecha['dinero'])
                fecha['fecha'] = desencriptarText(fecha['fecha'])
                if f"{now.year}/{now.month}/{now.day}" == fecha['fechaDeCreacion']:
                    info = {desencriptarText(llave): [fecha]}
                    if info not in buscarInfo:
                        if desencriptarText(llave) not in ids:
                            ids[desencriptarText(llave)] = []
                        ids[desencriptarText(llave)].append(index)
                        buscarInfo.append(info)
    
    textContenido = ""
    textContenido += retornarReferencias()
    textContenido += retornarStringInformacion(buscarInfo, valorNum, ids)  
    print('textContenido')
    print(textContenido) 
    return render_template('index.html', texto = textContenido + '*' + json.dumps(doc['estilos']))

def retornarReferenciasDesglosadas():
    dicc = {}
    doc = myCollection.find_one({"email": session['email']})
    
    for ref in doc['usoDeReferencias']:
        for u, referencias in ref.items():
            decrypted_u = desencriptarText(u)  # Decrypt the reference name
            #print('referencias')
            #print(referencias)
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
                m = desencriptarText(a['fecha'])
                mes = m[5:7]
                dinero = int(desencriptarText(a['dinero']))
                if dinero < 0:
                    dicc[f'{decrypted_u}@egresos@{mes}'] += int(desencriptarText(a['dinero'])) 
                else:
                    dicc[f'{decrypted_u}@ingresos@{mes}'] += int(desencriptarText(a['dinero']))  

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
                        myCollection.insert_one({"email": email,
                                                'password': ashed_password, 
                                                "usoDeReferencias": [],
                                                'estilos': {'fondo':'https://res.cloudinary.com/dplncudbq/image/upload/v1656550241/mias/8_ksv971.png',
                                                            'color1': '#16272A',
                                                            'color2': 'black',
                                                            'color3': '#697376',
                                                            'color4': '#1e2c3a'}})
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

def buscar_informacion(referencia, fechaUsuario):
    buscarInfo = {}
    doc = myCollection.find_one({"email": session['email']})
    ids = {}

    for item in doc['usoDeReferencias']:
        for llave in item.keys():
            for index, info in enumerate(item[llave]):
                # Decrypt the 'texto', 'dinero', 'fecha', and 'referencia' fields
                decrypted_info = {
                    'texto': desencriptarText(info['texto']),
                    'dinero': desencriptarText(info['dinero']),
                    'fecha': desencriptarText(info['fecha'])
                }
                decrypted_llave = desencriptarText(llave)

                if referencia and fechaUsuario:
                    if (decrypted_llave == referencia and decrypted_info['fecha'] == cambiarValor('-', '/', fechaUsuario)):
                        if decrypted_llave not in buscarInfo:
                            buscarInfo[decrypted_llave] = []
                        buscarInfo[decrypted_llave].append(decrypted_info)
                        if decrypted_llave not in ids:
                            ids[decrypted_llave] = []
                        ids[decrypted_llave].append(index)
                elif referencia and decrypted_llave == referencia:
                    if decrypted_llave not in buscarInfo:
                        buscarInfo[decrypted_llave] = []
                    buscarInfo[decrypted_llave].append(decrypted_info)
                    if decrypted_llave not in ids:
                        ids[decrypted_llave] = []
                    ids[decrypted_llave].append(index)
                elif fechaUsuario and decrypted_info['fecha'] == cambiarValor('-', '/', fechaUsuario):
                    if decrypted_llave not in buscarInfo:
                        buscarInfo[decrypted_llave] = []
                    buscarInfo[decrypted_llave].append(decrypted_info)
                    if decrypted_llave not in ids:
                        ids[decrypted_llave] = []
                    ids[decrypted_llave].append(index)

    # Eliminar las referencias sin coincidencias
    ids = {k: v for k, v in ids.items() if v}

    texto = retornarReferencias() + retornarStringInformacion([buscarInfo], "todos", ids)
    if validacionLogeo('', '') ==  'si esta logeado':
        print('texto')
        print(texto)
        return render_template('index.html', texto = texto + '*' + json.dumps(doc['estilos']))
    else:
        return redirect('/')

def obtener_mes(fecha):
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    mes = int(fecha.split('/')[1]) - 1
    return meses[mes]

def formatearNumero(num):
    num = float(num)  # Convierte la cadena a un número de punto flotante
    return "${:,.0f}".format(num).replace(",", ".")

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
        #session['email'] = '' 
        #redirect('/') 
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

@app.route('/temas', methods=["GET", "POST"])
def temas():
    doc = myCollection.find_one({"email": session['email']})

    if request.method == "POST": 
        linkImagenFondo = request.form["linkImagenFondo"]
        color1 = request.form["color1"]
        color2 = request.form["color2"]
        color3 = request.form["color3"]
        color4 = request.form["color4"]
        paso = doc['estilos']
        paso = {'fondo': linkImagenFondo,
                'color1': color1, 'color2': color2, 'color3': color3, 'color4': color4}
        updateTask = {"$set":{'estilos': paso}}
        myCollection.update_one({"_id": doc['_id']}, updateTask) 
        
        return render_template('temas.html', estilos = json.dumps(paso))
    else:
        return validacionLogeo(f"render_template('temas.html', estilos = '{json.dumps(doc['estilos'])}')", "redirect('/')")

@app.route('/vistaDeFlujoReferencias', methods=["GET", "POST"])
def vistaDeFlujoReferencias():
    doc = myCollection.find_one({"email": session['email']})

    if validacionLogeo('', '') ==  'si esta logeado':
        return render_template('graficosAnual.html', meses = retornarReferenciasDesglosadas() + '*' + json.dumps(doc['estilos']))
    else:
        return redirect('/')       
    
@app.route('/vistaDeFlujoCompactado', methods=["GET", "POST"])
def vistaDeFlujoCompactado():
    doc = myCollection.find_one({"email": session['email']})

    if validacionLogeo('', '') ==  'si esta logeado':
        return render_template('graficosAnual.html', meses = retornarReferenciasDesglosadas() + '*' + json.dumps(doc['estilos']))
    else:
        return redirect('/')  

@app.route('/pdf', methods=["GET"])
def pdf():
    # MongoDB operations
    '''
    doc = myCollection.find_one({"email": session['email']})

    packet = io.BytesIO()
    pdf = SimpleDocTemplate(packet, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    styleN = styles['BodyText']
    styleN.wordWrap = 'CJK'
    styleBH = styles['Normal']
    styleBH.wordWrap = 'CJK'

    sumaTotalAnual = 0
    mesesIngresosAnual = {'Enero': 0, 'Febrero': 0, 'Marzo': 0, 'Abril': 0, 'Mayo': 0, 'Junio': 0, 'Julio': 0, 'Agosto': 0 , 'Septiembre': 0, 'Octubre': 0, 'Noviembre': 0, 'Diciembre': 0} 
    mesesEgresosAnual  = {'Enero': 0, 'Febrero': 0, 'Marzo': 0, 'Abril': 0, 'Mayo': 0, 'Junio': 0, 'Julio': 0, 'Agosto': 0 , 'Septiembre': 0, 'Octubre': 0, 'Noviembre': 0, 'Diciembre': 0} 

    for i, key in enumerate(doc['usoDeReferencias']):
        for u in key.keys():
            data = []
            conte = doc['usoDeReferencias'][i][u]
            data.append(['---------------'])#para espacio
            data.append([Paragraph(desencriptarText(u), styleN)])
            data.append([])#para espacio
            suma = 0
            mesesIngresos = {'Enero': 0, 'Febrero': 0, 'Marzo': 0, 'Abril': 0, 'Mayo': 0, 'Junio': 0, 'Julio': 0, 'Agosto': 0 , 'Septiembre': 0, 'Octubre': 0, 'Noviembre': 0, 'Diciembre': 0} 
            mesesEgresos  = {'Enero': 0, 'Febrero': 0, 'Marzo': 0, 'Abril': 0, 'Mayo': 0, 'Junio': 0, 'Julio': 0, 'Agosto': 0 , 'Septiembre': 0, 'Octubre': 0, 'Noviembre': 0, 'Diciembre': 0} 
            for a in conte:
                row = [Paragraph(desencriptarText(a['texto']), styleN), desencriptarText(a['dinero']), desencriptarText(a['fecha'])]
                suma += int(desencriptarText(a['dinero']))
                if int(desencriptarText(a['dinero'])) < 0:
                    mesesEgresos[obtener_mes(desencriptarText(a['fecha']))] += int(desencriptarText(a['dinero']))
                    mesesEgresosAnual[obtener_mes(desencriptarText(a['fecha']))] += int(desencriptarText(a['dinero']))
                else: 
                    mesesIngresos[obtener_mes(desencriptarText(a['fecha']))] += int(desencriptarText(a['dinero']))    
                    mesesIngresosAnual[obtener_mes(desencriptarText(a['fecha']))] += int(desencriptarText(a['dinero']))
                data.append(row)

            data.append([])#para espacio
            data.append(['Meses ingresos'])
            for mes, valor in mesesIngresos.items():
                data.append([mes, valor])

            data.append([])#para espacio
            data.append(['Meses egresos'])
            for mes, valor in mesesEgresos.items():
                data.append([mes, valor])

            data.append([])  # Espacio
            data.append(['Total por mes'])
            for mes in mesesIngresos.keys():
                total = mesesIngresos[mes] - mesesEgresos[mes]
                data.append([mes, total])        

            data.append([])#para espacio
            data.append([f'total anual {desencriptarText(u)}: ${suma}'])
            sumaTotalAnual += suma


    data = []
    data.append(['---------------'])  # Espacio
    data.append(['Total anual solo ingresos'])
    for mes, valor in mesesIngresosAnual.items():
        data.append([mes, valor])

    data.append([])  # Espacio
    data.append(['Total anual solo egresos'])
    for mes, valor in mesesEgresosAnual.items():
        data.append([mes, valor])

    data.append([])  # Espacio
    data.append(['Total anual'])
    for mes in mesesIngresosAnual.keys():
        total = mesesIngresosAnual[mes] + mesesEgresosAnual[mes]
        data.append([mes, total]) 

    data.append([])#para espacio
    data.append([f'total anual toda referencia: ${sumaTotalAnual}'])

    elements.append(table)

    # Construye el PDF con los elementos
    pdf.build(elements)'''
    # MongoDB operations
    doc = myCollection.find_one({"email": session['email']})

    packet = io.BytesIO()
    pdf = SimpleDocTemplate(packet, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    styleN = styles['BodyText']
    styleN.wordWrap = 'CJK'
    styleBH = styles['Normal']
    styleBH.wordWrap = 'CJK'
    styleBH.alignment = 1  # Center alignment
    styleBH.fontSize = 14
    styleBH.leading = 16

    # Add creation date and time at the beginning of the document
    creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"Fecha y hora de creación del archivo: {creation_time}", styleN))
    elements.append(Spacer(1, 12))

    sumaTotalAnual = 0
    mesesIngresosAnual = {'Enero': 0, 'Febrero': 0, 'Marzo': 0, 'Abril': 0, 'Mayo': 0, 'Junio': 0, 'Julio': 0, 'Agosto': 0 , 'Septiembre': 0, 'Octubre': 0, 'Noviembre': 0, 'Diciembre': 0} 
    mesesEgresosAnual  = {'Enero': 0, 'Febrero': 0, 'Marzo': 0, 'Abril': 0, 'Mayo': 0, 'Junio': 0, 'Julio': 0, 'Agosto': 0 , 'Septiembre': 0, 'Octubre': 0, 'Noviembre': 0, 'Diciembre': 0} 
    mesesTotalAnual    = {'Enero': 0, 'Febrero': 0, 'Marzo': 0, 'Abril': 0, 'Mayo': 0, 'Junio': 0, 'Julio': 0, 'Agosto': 0 , 'Septiembre': 0, 'Octubre': 0, 'Noviembre': 0, 'Diciembre': 0} 

    for i, key in enumerate(doc['usoDeReferencias']):
        for u in key.keys():
            data = []
            conte = doc['usoDeReferencias'][i][u]
            title = [[Paragraph('<b>' + desencriptarText(u) + '</b>', styleBH)]]
            title_table = Table(title, colWidths=[450])
            title_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('SPAN', (0, 0), (-1, 0)),  # Merge cells in the first row
            ]))
            elements.append(title_table)
            elements.append(Spacer(1, 12))  # Add a space after each table

            suma = 0
            mesesIngresos = {'Enero': 0, 'Febrero': 0, 'Marzo': 0, 'Abril': 0, 'Mayo': 0, 'Junio': 0, 'Julio': 0, 'Agosto': 0 , 'Septiembre': 0, 'Octubre': 0, 'Noviembre': 0, 'Diciembre': 0} 
            mesesEgresos  = {'Enero': 0, 'Febrero': 0, 'Marzo': 0, 'Abril': 0, 'Mayo': 0, 'Junio': 0, 'Julio': 0, 'Agosto': 0 , 'Septiembre': 0, 'Octubre': 0, 'Noviembre': 0, 'Diciembre': 0} 
            mesesTotal    = {'Enero': 0, 'Febrero': 0, 'Marzo': 0, 'Abril': 0, 'Mayo': 0, 'Junio': 0, 'Julio': 0, 'Agosto': 0 , 'Septiembre': 0, 'Octubre': 0, 'Noviembre': 0, 'Diciembre': 0} 

            data.append([[Paragraph('<b>' + f'contenido {desencriptarText(u)}' + '</b>', styleBH)]])
            for a in conte:
                row = [Paragraph(desencriptarText(a['texto']), styleN), formatearNumero(desencriptarText(a['dinero'])), desencriptarText(a['fecha'])]
                suma += int(desencriptarText(a['dinero']))
                if int(desencriptarText(a['dinero'])) < 0:
                    mesesEgresos[obtener_mes(desencriptarText(a['fecha']))] += int(desencriptarText(a['dinero']))
                    mesesEgresosAnual[obtener_mes(desencriptarText(a['fecha']))] += int(desencriptarText(a['dinero']))
                else: 
                    mesesIngresos[obtener_mes(desencriptarText(a['fecha']))] += int(desencriptarText(a['dinero']))    
                    mesesIngresosAnual[obtener_mes(desencriptarText(a['fecha']))] += int(desencriptarText(a['dinero']))
                data.append(row)
            
            if len(data) != 0:
                elements.append(tabla2('', data)) 
                elements.append(Spacer(1, 12))
            
            elements.append(tabla(f'Meses ingresos {desencriptarText(u)}', mesesIngresos, 'mesValor'))
            elements.append(Spacer(1, 12))  # Add a space after each table
            
            elements.append(tabla(f'Meses egresos {desencriptarText(u)}', mesesEgresos, 'mesValor'))
            elements.append(Spacer(1, 12))  # Add a space after each table
            
            for mes in mesesIngresos:
                mesesTotal[mes] = mesesIngresos[mes] + mesesEgresos[mes]  

            elements.append(tabla(f'Meses total {desencriptarText(u)}', mesesTotal, 'mesValor'))
            elements.append(Spacer(1, 12))  # Add a space after each table
            elements.append(PageBreak())  # Add a page break after each reference 

    elements.append(tabla(f'Total anual solo ingresos', mesesIngresosAnual, 'mesValor'))
    elements.append(Spacer(1, 12))  # Add a space after each table
    elements.append(tabla(f'Total anual solo egresos', mesesEgresosAnual, 'mesValor'))
    elements.append(Spacer(1, 12))  # Add a space after each table
    for mes in mesesIngresosAnual:
        mesesTotalAnual[mes] = mesesIngresosAnual[mes] + mesesEgresosAnual[mes]
                                                            
    elements.append(tabla(f'Total anual', mesesTotalAnual, 'mesValor'))
    elements.append(Spacer(1, 12))  # Add a space after each table
    elements.append(PageBreak())  # Add a page break after each reference  

    # Add page numbers at the end of each page
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = "Page %s" % page_num
        canvas.drawRightString(200*mm, 20*mm, text)

    pdf.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    # Move the pointer to the start of the BytesIO object
    packet.seek(0)

    # Create an email message object
    message = MIMEMultipart()
    message['Subject'] = 'Envio de información financiera'
    message['From'] = 'relaxMusicProject@outlook.es'
    message['To'] = 'davipianof@gmail.com'
    message.attach(MIMEText(f"Estado finaciero creado el: {creation_time}"))

    # Attach the PDF to the email
    part = MIMEBase('application', "octet-stream")
    part.set_payload(packet.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="referencias.pdf"')
    message.attach(part)

    # Send the email
    smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
    smtp.starttls()
    smtp.login('relaxMusicProject@outlook.es', "D@vimusic1919")
    smtp.send_message(message)
    smtp.quit()

    return render_template('logeo.html', mensaje = 'El estado finaciero fue enviado con exito a tu correo', ruta = '/ingresos' )
    return render_template('graficosAnual.html', meses = retornarReferenciasDesglosadas())

def tabla(titulo, dicc, acc):
    data = []
    styles = getSampleStyleSheet()
    styleN = styles['BodyText']
    styleN.wordWrap = 'CJK'
    styleBH = styles['Normal']
    styleBH.wordWrap = 'CJK'
    styleBH.alignment = 1  # Center alignment
    styleBH.fontSize = 14
    styleBH.leading = 16

    data.append([[Paragraph('<b>' + f'{titulo}' + '</b>', styleBH)]])

    if acc == 'mesValor':
        print('mirar dic')
        print(dicc)
        for mes, valor in dicc.items():
            data.append([mes, formatearNumero(valor)])
    elif acc == 'anotaciones':  
        #data.append([Paragraph('<b>' + f'{titulo}' + '</b>', styleBH)]) 
        data.append(dicc)  

    table = Table(data, colWidths=[100, 350], repeatRows=1)
    table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 14),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('SPAN', (0, 0), (-1, 0)),  # Merge cells in the first row
                        ])) 
    return table   

def tabla2(titulo, data):
    styles = getSampleStyleSheet()
    styleN = styles['BodyText']
    styleN.wordWrap = 'CJK'
    styleBH = styles['Normal']
    styleBH.wordWrap = 'CJK'
    styleBH.alignment = 1  # Center alignment
    styleBH.fontSize = 14
    styleBH.leading = 16


    table = Table(data, colWidths=[100, 200, 150], repeatRows=1)
    table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 14),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('SPAN', (0, 0), (-1, 0)),  # Merge cells in the first row
                            ]))
    return table

@app.route('/crudreferencias', methods=["GET", "POST"])
def crudreferencias():
    doc = myCollection.find_one({"email": session['email']})

    if request.method == "POST": 
        accion = request.form["formUso"]
        crear = request.form["crear"]
        cambiar = request.form["cambiar"]
        nuevocambiar = request.form["nuevocambiar"]
        borrar = request.form["borrar"]        

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
        print('verifica')
        print(doc)  
        return render_template('crudReferencias.html', texto = retornarReferenciasDesglosadas() + '*' + json.dumps(doc['estilos']), aviso = '') 

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

@app.route('/salir')
def salir():
    session['email'] = ''
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5002)    

