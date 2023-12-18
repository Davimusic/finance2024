from flask import Flask, render_template, request, redirect, session
import pymongo                 
from bson.objectid import ObjectId  # para poder usar _id de mongo
from datetime import datetime, timedelta
import bcrypt # solo para el logeo ya que solo permite encriptar pero no desencriptar
from cryptography.fernet import Fernet

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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, LongTable, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from collections import defaultdict

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
    
    if valorNum == "negativo":
        dinero =  retornarNumeroNegativo(int(request.form.get("dinero", '')))
    else:
        dinero = request.form.get("dinero", '')    
    
    referencia = request.form.get("referencia", '')
    fecha = cambiarValor('-', '/', request.form.get("fecha", '')) 
    texto = request.form.get("texto", '')
    codUnico = request.form.get("codUnico", '')
    signoNumerico = request.form.get("signoNumerico", '')
    rutActual = request.form.get("rutActual", '')

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

        if signoNumerico == 'negativo':
            dinero = retornarNumeroNegativo(int(dinero))
        else:
            dinero = retornarNumeroPositivo(int(dinero))

        print('llegaaaa') 
        print(referencia)   

        info = {"dinero": encriptarText(dinero), "fecha": encriptarText(fecha), "texto": encriptarText(cambiarValor(',', '-', texto)), "fechaDeCreacion": ''}

        for key in doc['usoDeReferencias']:
            for u in key.keys():
                print('desencriptarText(u)')
                print(desencriptarText(u))
                if desencriptarText(u) == referencia:
                    print('entra')
                    print(desencriptarText(info['dinero']))
                    print(desencriptarText(info['fecha']))
                    print(desencriptarText(info['texto']))
                    fechaCreacionOriginal = key[u][int(codUnico)]['fechaDeCreacion']
                    key[u][int(codUnico)] = info
                    key[u][int(codUnico)]['fechaDeCreacion'] = fechaCreacionOriginal
                    print(info['fechaDeCreacion'])

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
    count = 0
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
                texto += info
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
    print('buscarInfo')
    print(buscarInfo)

    textContenido = ""
    textContenido += retornarReferencias()
    textContenido += retornarStringInformacion(buscarInfo, valorNum, ids)   
    return render_template('index.html', texto = textContenido)

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
            doc = myCollection.find_one({"email": session['email'], "usoDeReferencias": {"$exists": True}})
            if doc:
                return 'si esta logeado'
            else:
                return redirect('/salir')
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

@app.route('/pdf', methods=["GET"])
def pdf():
    # MongoDB operations
    doc = myCollection.find_one({"email": session['email']})

    # Create a PDF in memory
    packet = io.BytesIO()
    pdf = SimpleDocTemplate(packet, pagesize=letter)

    # Fetch all references and their contents
    elements = []
    styles = getSampleStyleSheet()

    monthly_totals = defaultdict(lambda: {"ingresos": 0, "egresos": 0, "total": 0})
    annual_totals = {"ingresos": 0, "egresos": 0, "total": 0}
    daily_totals = defaultdict(lambda: {"ingresos": 0, "egresos": 0, "total": 0})

    for key in doc['usoDeReferencias']:
        for u in key.keys():
            decrypted_key = desencriptarText(u)
            data = [["Dinero", "Fecha", "Texto", "Fecha de Creación"]]
            total = 0
            ingresos = 0
            egresos = 0
            for content in key[u]:
                dinero = int(content['dinero'])
                total += dinero
                if dinero > 0:
                    ingresos += dinero
                else:
                    egresos += dinero
                data.append([content['dinero'], content['fecha'], Paragraph(content['texto'], styles["BodyText"]), content['fechaDeCreacion']])
                
                # Update the monthly and annual totals
                month = content['fecha'].split('/')[1]  # Assuming the date is in the format "YYYY/MM/DD"
                monthly_totals[month]["ingresos"] += max(dinero, 0)
                monthly_totals[month]["egresos"] += min(dinero, 0)
                monthly_totals[month]["total"] += dinero
                annual_totals["ingresos"] += max(dinero, 0)
                annual_totals["egresos"] += min(dinero, 0)
                annual_totals["total"] += dinero

                # Update the daily totals
                day = content['fecha']  # Assuming the date is in the format "YYYY/MM/DD"
                daily_totals[day]["ingresos"] += max(dinero, 0)
                daily_totals[day]["egresos"] += min(dinero, 0)
                daily_totals[day]["total"] += dinero

            elements.append(Spacer(1, 12))
            elements.append(Table([["Referencia: " + decrypted_key]], colWidths=[460]))
            elements.append(Spacer(1, 12))
            table = LongTable(data, colWidths=[115, 115, 115, 115], splitByRow=True)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),

                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),

                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))

            summary = [["Total Acumulado", ""], ["Ingresos", ingresos], ["Egresos", egresos], ["Total", total]]
            summary_table = Table(summary, colWidths=[230, 230])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),

                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),

                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('SPAN', (0, 0), (1, 0))
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 12))

    monthly_totals = defaultdict(lambda: defaultdict(lambda: {"ingresos": 0, "egresos": 0, "total": 0}))
    annual_totals = {"ingresos": 0, "egresos": 0, "total": 0}

    
            

    pdf.build(elements)

    # Move the pointer to the start of the BytesIO object
    packet.seek(0)

    # Create an email message object
    message = MIMEMultipart()
    message['Subject'] = 'Envio de pdf....'
    message['From'] = 'relaxMusicProject@outlook.es'
    message['To'] = 'davipianof@gmail.com'
    message.attach(MIMEText('Hola bro aqui va el pdf'))

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

    return render_template('graficosAnual.html', meses = retornarReferenciasDesglosadas())

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

@app.route('/salir')
def salir():
    session['email'] = ''
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5002)    

