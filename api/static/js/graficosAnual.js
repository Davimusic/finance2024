let arrContenido = [], flujo = '', refenciaActual = '', arrReferencias =  [], path = '', arrConcatenado = [];

function infoAnual(meses){
    path = window.location.pathname
    arrContenido = traducirInformacionGraficos(`${meses}`)
    flujo = 'ingresos'
    arrReferencias = ordenarAlfaNumerico(retornarReferenciasGraficos(meses))
    refenciaActual = arrReferencias[0]
    crearGrafica()
}

function retornarFiltroReferencias(arr){
    let Referencia = arr
    let flujo = ['ingresos', 'egresos']

    let text = `
        <div style="${retornarDecicionResponsiva('padding-top:100px;', 'padding-top:80px;')}">
            <div style=" ${retornarDecicionResponsiva('display:block;', 'display:flex;')} justify-content: space-between; width: 85%; padding: 1%; margin:0px auto; background: #1312129a;" class="borde1">`
                if(path != '/vistaDeFlujoCompactado'){
                    text +=
                    `<div class="" style="margin-bottom:10px; padding-right: 2%;">
                        <label for="">Referencia</label>
                    </div> 
                    <select onchange="refrescarGrafico('referencia', this.id, this.value)" style="height: 25px; width:100%;" class="borde1 color4" id="selectGraficoReferencia">`
                    for (let u = 0; u < Referencia.length; u++) {
                        text +=`<option value="${Referencia[u]}">${Referencia[u]}</option>`
                    }
                    text +=    
                    `
                    </select>`
                } 
                    text += `
                    <div class="" style="margin-bottom:10px; padding-right: 2%; padding-left: 2%; ${retornarDecicionResponsiva('padding-top:10px;', '')}">
                        <label for="">Flujo</label>
                    </div> 
                    <select onchange="refrescarGrafico('flujo', this.id, this.value)" style="height: 25px; width:100%;" class="borde1 color4" id="selectGraficoFlujo">`
                    for (let u = 0; u < flujo.length; u++) {
                        text +=`<option value="${flujo[u]}">${flujo[u]}</option>`
                    }
                    text +=    
                    `
                    </select> 
            </div>
        </div>
    ` 
    return text;
}

function refrescarGrafico(acc, id, val){
    console.log(`refrescarGrafico`);
    console.log(`acc: ${acc},  id: ${id},  val: ${val}`);
    
    let select = document.getElementById(id)
    let valor = select.value

    if(acc == 'flujo'){
        flujo = valor
    } else {
        refenciaActual = valor
    }

    crearGrafica()
    actualizarValorSlide(id, valor)
}

let diccFlitros = {}
function actualizarValorSlide(id, valor){
    diccFlitros[id] = valor
    for (const key in diccFlitros) {
        document.getElementById(key).value = diccFlitros[key];
    }
    console.log('actualizarValorSlide');
    console.log(`id: ${id}, valor: ${valor}`);
    console.log(diccFlitros)
}

function retornarReferenciasGraficos(text){
    let referencia = text.split(',')
    referencia = referencia[0].split('$')
    referencia[referencia.length - 1] = referencia[referencia.length - 1].substring(0, referencia[referencia.length - 1].length - 1);
    return referencia
}

function traducirInformacionGraficos(text){
    let arr = []
    let arrtext = text.split(',');
    for (let e = 1; e < arrtext.length; e++) {
        arr.push(arrtext[e].split('@'))
        arr[e -1].pop()
    } 
    arr.pop()   
    //console.log(arr);
    return arr
}

function retornarInformacionCoordenadaArr(arr, index){
    let arre = []
    for (let u = 0; u < arr.length; u++) {
        arre.push(arr[u][parseInt(index)])        
    }
    console.log(arre);
    return arre
}

function retornarTraducirDiccionario_a_Arreglo(dicc){
    let arr = []
    for (const u in dicc) {
        arr.push(dicc[u])
    }
    return arr
}

function crearGrafica(){

    let cadena = [], arrFiltrado = [], sumaIngresos = 0, sumaEgresos = 0
    
    let dicc = {'01':'enero', '02':'febrero', '03':'marzo', '04':'abril', '05':'mayo', '06':'junio', '07':'julio', '08':'agosto', '09':'septiembre', '10':'octubre', '11':'noviembre', '12':'diciembre'}
    let diccCompactoIngresos = {'enero': 0, 'febrero': 0, 'marzo': 0, 'abril': 0, 'mayo': 0, 'junio': 0, 'julio': 0, 'agosto': 0, 'septiembre': 0, 'octubre': 0, 'noviembre': 0, 'diciembre': 0}
    let diccCompactoEgresos = {'enero': 0, 'febrero': 0, 'marzo': 0, 'abril': 0, 'mayo': 0, 'junio': 0, 'julio': 0, 'agosto': 0, 'septiembre': 0, 'octubre': 0, 'noviembre': 0, 'diciembre': 0}
    let labels = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviemre", "Diciembre", 'ingresos', 'egresos', 'flujo actual']
    if(path == '/vistaDeFlujoReferencias'){
        for (let u = 0; u < arrContenido.length; u++) {
            if(arrContenido[u][0] == refenciaActual && arrContenido[u][1] == flujo){
                arrFiltrado.push(arrContenido[u][3])
            }
            
            if(arrContenido[u][0] == refenciaActual){
                if(arrContenido[u][1] == 'ingresos'){
                    sumaIngresos += parseInt(arrContenido[u][3])
                } else {
                    sumaEgresos += parseInt(arrContenido[u][3])
                }
            }
        }
    } else {
        refenciaActual = 'brutos'
        for (let u = 0; u < arrContenido.length; u++) {
                
                if(arrContenido[u][1] == 'ingresos'){
                    diccCompactoIngresos[dicc[arrContenido[u][2]]] += parseInt(arrContenido[u][3])
                    sumaIngresos += parseInt(arrContenido[u][3])
                } else {
                    diccCompactoEgresos[dicc[arrContenido[u][2]]] += parseInt(arrContenido[u][3])
                    sumaEgresos += parseInt(arrContenido[u][3])
                }
        }
        
        if(flujo == 'ingresos'){
            arrFiltrado = retornarTraducirDiccionario_a_Arreglo(diccCompactoIngresos)
        } else {
            arrFiltrado = retornarTraducirDiccionario_a_Arreglo(diccCompactoEgresos)
        }
    }
    
    let dinerosTraducidosParaPocentajes = []
    
    /*/de prueba, testeo
    if(flujo == 'ingresos'){
        arrFiltrado = [1471000, 50000, 2000000, 1300000, 700000, 0, 0, 0, 0, 50000, 0, 0]
    } else {
        arrFiltrado = [-1471000, -50000, -2000000, -1300000, -700000, 0, -4000000, -3000, 0, -50000, 0, -4500000]
    }*/

    
    fucionarArreglos(arrFiltrado)
    fucionarArreglos([sumaIngresos, sumaEgresos, (sumaIngresos + sumaEgresos)])
    dinerosTraducidosParaPocentajes = retornarDinerosEnPocentajes(arrConcatenado)
    let cod = ''

    cod += 
    `
    ${menu()}
    ${retornarFiltroReferencias(arrReferencias)}
    <div id="contenido" style="text-align: center; justify-content: center; width: 100%; height: ${((window.innerHeight / 100) * 75)}px; ${retornarDecicionResponsiva('padding-top: 3%;', 'padding-top: 0%;')} overflow-x: auto; margin:0px auto;">
        <div class="borde1 padding1 sombra" style="margin-left: 4%; margin-right: 4%; padding-top: 0px; background: #1312129a; height:fit-content; display:block; ${retornarDecicionResponsiva('margin-top: 2%;', '')}">
            <h3 style='text-align: center; justify-content: center; margin-bottom: 1%;'>${flujo} ${refenciaActual}</h3>`
        for (let u = 0; u < dinerosTraducidosParaPocentajes.length; u++) {
        cod += retornarBarrasEstadisticas(`barra${u}`, arrConcatenado[u], labels[u])
        }  
    cod += `
        </div>
    </div>
    `//<button onclick="generarPDF()">Generar PDF</button>
    
    document.getElementById('padreMenu').innerHTML = cod
    generarAnimacionBarras(dinerosTraducidosParaPocentajes)
    arrConcatenado = []
}

function generarPDF() {
    var miDiv = document.getElementById('contenido');
    html2canvas(miDiv, {scrollY: -window.scrollY, scale: 1}).then(function(canvas) {
        var imgData = canvas.toDataURL('image/png');
        var pdf = new jsPDF('p', 'mm', 'a4');
        var width = pdf.internal.pageSize.width;
        var height = pdf.internal.pageSize.height;
        height = canvas.height * width / canvas.width;
        pdf.addImage(imgData, 'PNG', 0, 0, width, height);

        document.getElementById('selectGraficoFlujo').value = 'egresos'
        refrescarGrafico('flujo', 'selectGraficoFlujo', 'egresos');

        /*/ Introduce un retraso de 2 segundos
        setTimeout(function() {
            // Captura el segundo estado del div
            html2canvas(miDiv, {scrollY: -window.scrollY, scale: 1}).then(function(canvas2) {
                var imgData2 = canvas2.toDataURL('image/png');
                pdf.addPage();
                pdf.addImage(imgData2, 'PNG', 0, 0, width, height);

                // Guarda el PDF
                pdf.save('miPDF.pdf');
            });
        }, 5000);  // Retraso de 5 segundos*/
    // Guarda el PDF
    pdf.save('miPDF.pdf');
    });
}
        
    

function fucionarArreglos(arr){
    for (let u = 0; u < arr.length; u++) {
        arrConcatenado.push(arr[u])
    }
}

function retornarDinerosEnPocentajes(arre){
    console.log(`arre: ${arre}, largo: ${arre.length}`);    

    let arr = [], maxValue = 1;
    for (let u = 0; u < arre.length; u++) {
        let valor = retornarNumSiemprePositivo(parseInt(arre[u]))
        if(valor > maxValue){
            maxValue = valor
        }
    }
    //console.log(`max value : ${maxValue}`);
    for (let u = 0; u < arre.length; u++) {
        let nuevoValor = (parseInt(arre[u]) * ((window.innerWidth / 100) * retornarDecicionResponsiva('37', '60')))/maxValue //42  el 200 y 400 el el maximo valor que declarè en el div que muestra el porcentaje
        if(nuevoValor < 0){
            nuevoValor = -1 * nuevoValor
        }
        //console.log(`nuevoValor: ${nuevoValor}`);
        arr.push(nuevoValor)
    }
    console.log(arr);
    return arr
}

function retornarNumSiemprePositivo(num){
    //console.log(num);
    if(num < 0){
        num = -1 * num
    }
    //console.log(num);
    return num
}

function cambiarColor(id, color){
    let ob = document.getElementById(id)
    ob.style.transition = '0.25s'
    ob.style.background = color
}

function retornarBarrasEstadisticas(id, dineroBruto, mes){
    let cod = `
    <div onmouseover="cambiarColor('padre${id}', '#000000bd')" onmouseout="cambiarColor('padre${id}', '#ffffff00')"  id='padre${id}' style="display:flex; margin-bottom: 0.5%; border-radius: 0.5em;">
        <label style="width: 150px; text-align: left;" for="">${mes}</label>
        <div style="width: ${((window.innerWidth / 100) * 70)}px;">
            <div class="borde1 color3" id='${id}' style="cursor: pointer; height: 20px;" ></div>
        </div>
        <label style="width: 100px; padding-left: 5%;" for="">$${dineroBruto}</label>
    </div>`
    return cod
} 

let copiaDinerosTraducidosParaPocentajes = []
function generarAnimacionBarras(dinerosTraducidosParaPocentajes){
    copiaDinerosTraducidosParaPocentajes = dinerosTraducidosParaPocentajes
    
    for (let u = 0; u < copiaDinerosTraducidosParaPocentajes.length; u++) {
        let ba = `barra${u}`
        console.log(ba);
        let barra = document.getElementById(ba)
        barra.style.transition = '1000ms';
        barra.style.width = `0px`;
        barra.classList.add('color2');
    }
    setTimeout(correrBarras, 300)
}

function correrBarras(){
    for (let u = 0; u < copiaDinerosTraducidosParaPocentajes.length; u++) {
        let ba = `barra${u}`
        let barra = document.getElementById(ba)
        barra.style.transition = '3s';
        barra.style.width = `${copiaDinerosTraducidosParaPocentajes[u]}px`;
        if(flujo == 'egresos'){
            barra.classList.add('color3');
        } else {
            barra.classList.remove('color3');
            barra.classList.add('color2');
        }
    }
}

