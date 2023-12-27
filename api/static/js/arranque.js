let Referencia = []
let marginInternos = "margin-top:30px; margin-bottom:10px;"
let altoPantalla = window.innerHeight;
let actualReferenciaModal = ''

function arranque(inf){
    let info = inf.split('*')[0]
    let estilos = inf.split('*')[1]
    
    Referencia = ordenarAlfaNumerico(retornarReferencias(info))
    let code = ``
    code += `
    ${menu()}
    <div id="padre" style="margin: 3%; position:relative; ${heightPantalla()};">
        <div id="porAhora" style="position: absolute; width:100%; ${retornarDecicionResponsiva('margin-top: 60px;','margin-top: 4.5%;')} overflow-y: auto; height: ${Math.floor((window.innerHeight / 100) * 90)}px;">
            <div style="${retornarDecicionResponsiva('display:block;','display:flex;')} width:100%">` 

        code += retornarComponentePorIngresoEgreso(`${retornarComponente(retornarDecicionResponsiva('width:96%;',''), marginInternos,"pedro", "", "", "", "crear","sin valor")}`, '')    
            
    code += `${retornarInterfasIngresoDeInformacionJuntoContabla(info)}
            </div><!--para usar z-index las cordenadas deben tener position absolute-->
        <div id="root" style="z-index: 1000; position: absolute; top: 0; left: 0; right: 0; margin: 0 auto;"></div>  
    </div>`
    document.getElementById("padreMenu").innerHTML = code

    let divPadre = document.getElementById("root")
    let cod = ""
    cod += modal()
    divPadre.innerHTML = cod;

    if(estilos[0] != ''){
        console.log(estilos);
        esti = JSON.parse(estilos)
        actualizarFondo(esti)
    }
}

function retornarComponentePorIngresoEgreso(positivo, negativo){
    if(positivo != ''){
        return positivo
    } else {
        return negativo
    }
    /** 
    if(window.location.pathname == '/ingresos' || window.location.pathname == '/egresos' ){
        return positivo
    } else {
        return negativo
    }*/

}

function reemplazarCaracter(busca, cambia, cadena){
    console.log('entra');
    let text = ""
    for (let u = 0; u < cadena.length; u++) {
        if(cadena[u] == busca){
            text += cambia
        } else {
            text += cadena[u]
        }
    }
    console.log(`remplazarCaracter: ${text}`);
    return text;
}

function heightPantalla(){
    return `${window.innerHeight}px`
}

function retornarReferencias(inf){
    let buscar = traducirInfoDesdeBackend(inf)
    let arr = []
    for (let u = 0; u < buscar[0].length; u++) {
        arr.push(buscar[0][u])
    }
    //console.log(arr);
    return arr
}

let totalIngresoDia = 0
function retornarInterfasIngresoDeInformacionJuntoContabla(inf){
    let arrInf = traducirInfoDesdeBackend(inf)
    let arr = [["Referencia", "Dinero", "Fecha", "Texto adicional"], []]
    
    for (let u = 1; u < arrInf.length; u++) {
        arr[1].push(arrInf[u])
    }

    arr[1] = invertirArreglo(arr[1])

    let text = `
    <div class="borde1 sombra" style=" width:100%; ${espacio(retornarDecicionResponsiva("","margin-left:5%;"))} ${retornarComponentePorIngresoEgreso('', retornarDecicionResponsiva('margin-top: 40px;',''))}">
        ${retornarMotoresDeBusqueda()}
        <div class="color1" style="height: ${(altoPantalla/100)*67.5}px; overflow: scroll;">  
            <table class="color1 padding1" style="padding-top: 2%; width:100%;">
                <tr class="color2" style="position: sticky; top:0;">
        `
    for (let u = 0; u < arr[0].length; u++) {
        text += `
                    <th>${arr[0][u]}</th>`
    }
        text +=`    <th>Acciones</th>
                </tr>`

    let banderaColor = 0;
    for (let u = 0; u < arr[1].length; u++) {
        let color = ""  
        
        if(banderaColor == 0){
            banderaColor = 1;
            color = `color3`
        } else {
            banderaColor = 0;
        }

        text +=`<tr class="${color}">`    
        for (let e = 0; e < (arr[1][u].length - 2); e++) {
            text+=`<td>${arr[1][u][e]}</td>`
        } 

        //totalIngresoDia += parseInt(arr[1][u][1])

        let mirar = `editar${u}`
        let idBorrar = `borrar${u}`
        let tituloEditar = `¡¡¡Estas en modo edición de contenido!!!`
        let tituloBorrar = `¡¡¡Estas en modo Borrar de contenido!!! <br> ¡¡¡Una vez borres el contenido será irrecuperable!!!`
        let infoEditar = "`" + arr[1][u] + "," + tituloEditar + "`"  
        let infoBorrar = "`" + arr[1][u] + "," + tituloBorrar + "`"  

        text +=`    <td style="justify-content: space-around; display:flex;">
                        <img id="${mirar}" onclick="eventoUnico('${mirar}', 'botonEditarTabla(${infoEditar})')" class="efectoMenu mano" style="height:30px; border-radius:50%; background: white; padding: 5px;" src="https://res.cloudinary.com/dplncudbq/image/upload/v1701787300/edit_cdqnpt.png" alt="">
                        <img id="${idBorrar}" onclick="eventoUnico('${idBorrar}', 'botonEditarTabla(${infoBorrar})')" class="efectoMenu mano" style="height:30px; border-radius:50%; background: white; padding: 5px;" src="https://res.cloudinary.com/dplncudbq/image/upload/v1701787300/trash_cq9i3d.png" alt="">
                    </td>
                </tr>`                
        }
            
        
        var today = new Date();
        var day = today.getDate();
        var month = today.getMonth() + 1;
        var year = today.getFullYear();
        const ruta = window.location.pathname.slice(1);
        //const ajustadoTotalIngresoDia = totalIngresoDia < 0 ? totalIngresoDia.toString().slice(1) : totalIngresoDia.toString();
        
        
        text+= `
            </table>
        </div>
        ${retornarComponentePorIngresoEgreso(`<div class="color2" style='padding: 10px; border-bottom-left-radius: 0.5em; border-bottom-right-radius: 0.5em;'>${generarTexto(ruta, arr[1])}</div>`, '')}
    </div>`
    return text;
}

function espacio(acc){
    return (window.location.pathname === '/ingresos' || window.location.pathname === '/egresos') ? acc : '';
}

function generarTexto(parametro, arrDinero) {
    var today = new Date();
    var day = today.getDate();
    var month = today.getMonth() + 1;
    var year = today.getFullYear();
    let arrDineros = []
    for (let u = 0; u < arrDinero.length; u++) {
        arrDineros.push(parseInt(arrDinero[u][1]))
    }

    if (parametro === 'ingresos' || parametro === 'egresos') {
        let dinero = 0;
        if(parametro === 'ingresos'){
            dinero = procesarNumeros(arrDineros, 'sumaPositivosNegativos')[0]
        } else {
            dinero = procesarNumeros(arrDineros, 'sumaPositivosNegativos')[1]
        }
        return `Total ${parametro} anotados el ${month}/${day}/${year}: $${dinero}`
    } else {
        var palabras = parametro.split('Z');
        if(palabras[1].length != 0){
            return `Total ${palabras[0]} anotados el ${palabras[1]}: $${procesarNumeros(arrDineros, 'sumaAbsoluta')}, total ingresos: $${procesarNumeros(arrDineros, 'sumaPositivosNegativos')[0]}, total egresos: $${procesarNumeros(arrDineros, 'sumaPositivosNegativos')[1]}, total dinero disponible neto: $${procesarNumeros(arrDineros, 'sumaNormal')}`
        } else {
            return `Total anotados de la referencia ${palabras[0]}: $${procesarNumeros(arrDineros, 'sumaAbsoluta')}`
        }
    }
}

function procesarNumeros(arr, opcion) {
    switch(opcion) {
        case 'sumaAbsoluta':
            return arr.reduce((a, b) => a + Math.abs(b), 0);
        case 'sumaNormal':
            return arr.reduce((a, b) => a + b, 0);
        case 'sumaPositivosNegativos':
            let sumaPositivos = arr.filter(n => n > 0).reduce((a, b) => a + b, 0);
            let sumaNegativos = arr.filter(n => n < 0).reduce((a, b) => a + b, 0);
            return [sumaPositivos, sumaNegativos];
        default:
            return 'Opción no válida';
    }
}

function retornarMotoresDeBusqueda(){
    let text = `
    <form method="post">
        <input style="display:none;" value = "filtroBuscar" class="borde1 color4" type="text" name="formUso" required>
        <div style="display:flex; border-top-left-radius: 0.5em; border-top-right-radius: 0.5em;" class="color2"> 
            <div style="${retornarDecicionResponsiva('display:block;', 'display:flex;')} justify-content: space-between; width: 85%;" class="padding1">
                <div class="" style="margin-bottom:10px; padding-right: 2%;">
                    <label for="">Referencia</label>
                </div> 
                <select style="height: 25px; width:100%;" class="borde1 color4" name="buscarReferencia"">`
                    text +=`<option value=""></option>`
                for (let u = 0; u < Referencia.length; u++) {
                    text +=`<option value="${Referencia[u]}">${Referencia[u]}</option>`
                }
                text +=    
                `
                </select>
                <div class="" style="margin-bottom:10px; padding-right: 2%; ${retornarDecicionResponsiva('','padding-left: 2%;')} ">
                    <label for="">Fecha</label>
                </div> 
                <input style="height: 25px;" value = "" class="borde1 color4" type="date" name="buscarFecha">
                
            </div>
            <button  style="background: none; border: none; height:40px; padding-top: 8px;" type="submit"><img id='motorBusqueda' onclick="rotar('motorBusqueda')" class="efectoMenu" style="background: white; height:40px; border-radius:50%;" src="${retornarLinkBotonSelect()}" alt=""></button>    
        </div>
    </form>
    `
    return text;
}

function retornarLinkBotonSelect(){
    return 'https://res.cloudinary.com/dplncudbq/image/upload/v1701543797/select_hkx3sf.png'
}

function traducirInfoDesdeBackend(inf){
    let arr = [[]], text = "", coordenada = 0;
    for (let u = 0; u < inf.length; u++) {
        if(inf[u] == "º"){
            arr.push([])
            arr[coordenada].push(text)
            text = ""
            coordenada += 1;
        } else if(inf[u] == "$"){
            arr[coordenada].push(text)
            text = ""
        } else {
            text += inf[u]
        }
    }
    arr.pop()
    return arr
}

function botonEditarTabla(codigo){
    let arr = codigo.split(',');
    let text = ""  
    let accion = ""

    if(arr[6] == "¡¡¡Estas en modo edición de contenido!!!"){
        accion = "editar"
    } else {
        accion = "borrar"
    }    

    text =   retornarComponente("", "margin-top:30px; margin-bottom:10px;", arr[0], arr[1], reemplazarCaracter("/", "-", arr[2]), arr[3], accion, arr[5], arr[4], 'paraModal', window.location.pathname)
    actualizarBloqueEnUso("editar contenido modal")
    ActivarModal(text, arr[6])
    actualReferenciaModal = arr[0]
    document.getElementById('actualReferenciaModalForm').value = actualReferenciaModal
}

function retornarDecicionResponsiva(desdeCelular, desdeComputador){
    let anchoPantalla = window.innerWidth;

    if(anchoPantalla <= 1200){
        return desdeCelular
    } else {
        return desdeComputador
    }
}
                                                                                                        
function retornarComponente(accion2, marginInternos,referencia, dinero, fecha, textoAdicional, formUso, codigoUnico, signoNumerico, uso, ruta){
    let cod = ''
    //console.log(`accion2: ${accion2}, marginInternos: ${marginInternos}, referencia: ${referencia}, dinero: ${dinero}, fecha: ${fecha}, textoAdicional: ${textoAdicional}, formUso: ${formUso}, codigoUnico: ${codigoUnico}, signoNumerico: ${signoNumerico}`);
    console.log(Referencia);
    if(window.location.pathname === '/ingresos'  || window.location.pathname === '/egresos' || uso === 'paraModal'){
        cod = `
        <div class="color1 borde1 padding1 sombra" style="max-width:380px; display: inline-block; margin-bottom:5%; height:fit-content; ${accion2}"> 
            <form method="post">
                <input style="display:none;" value = "${formUso}" class="borde1 color4" type="text" name="formUso" id="formUso" required>
                <input style="display:none;" value = "${codigoUnico}" class="borde1 color4" type="text" name="codUnico" required>
                <input style="display:none;" value = "${signoNumerico}" id='signoNumerico${uso}' class="borde1 color4" type="text" name="signoNumerico" required>
                <input style="display:none;" value = "${window.location.pathname}" type="text" name="rutActual">
                ${retornarCambioReferenciaForm(uso)}

                <div style="margin-bottom:10px;">
                    <label for="">Referencia</label>
                </div> 
                <select style="width:100%;" class="borde1 color4" name="referencia" id="referencia" required>`
                for (let u = 0; u < Referencia.length; u++) {
                    let seleccionar = ""
                    console.log(`referencia: ${referencia}, arr[u]: ${Referencia[u]} `);
                    if(referencia == Referencia[u]){
                        seleccionar = "selected"
                    }
                cod +=`<option ${seleccionar} value="${Referencia[u]}">${Referencia[u]}</option>`
                }
                cod +=    
                `
                </select>
                ${retornarEditorSignoNumerico(uso, signoNumerico, marginInternos)}
                <div style="${marginInternos}">
                    <label for="">Ingreso de dinero</label>
                </div>    
                <input id='formDinero' style="width:100%;" value="${dinero}" class="borde1 color4" type="number" name="dinero" id="dinero" required> 
                
                <div style="${marginInternos}">
                    <label for="">Fecha a ingresar</label>
                </div>    
                <input style="width:100%;" value = "${fecha}" class="borde1 color4" type="date" name="fecha" id="fecha" required>
                
                <div style="${marginInternos}">
                    <label for="">Texto adicional</label>
                </div>    
                <input style="width:100%;" value="${textoAdicional}" class="borde1 color4" type="text" name="texto" id="texto">
                
                <button id="botonSubmit" onclick="desactivarBotonDespuesDeUsado('botonSubmit')" style="${marginInternos} background: none; border: none; height:40px;" type="submit"><img id='botonSubmitImage' onclick="rotar('botonSubmitImage')" class="efectoMenu" style="background: white; height:40px; border-radius:50%;" src="${retornarLinkBotonSelect()}" alt=""></button>
            </form>
        </div>`
    }

    return cod;
}

function retornarCambioReferenciaForm(uso){
    return  (uso === 'paraModal') ? `<input style='display: none;' class="borde1 color4" value = "" type="text" id='actualReferenciaModalForm' name="actualReferenciaModal">` : '';
}

function retornarEditorSignoNumerico(uso, signoNumerico, ){
    let cod = ''
    if(uso === 'paraModal'){
        let arrSignos = ['positivo', 'negativo']
        let arrValores = ['ingresos', 'egresos']
        cod +=
        `
        <div style="${marginInternos}">
            <label for="">Estado numérico</label>
        </div> 
        <select onChange='actualizarSignoNumerico(this.value, "${uso}")' style="width:100%;" class="borde1 color4" id="selectSignoNumerico">`
                for (let u = 0; u < arrSignos.length; u++) {
                    let seleccionar = ""
                    if(signoNumerico == arrSignos[u]){
                        seleccionar = "selected"
                    }
                cod +=`<option ${seleccionar} value="${arrSignos[u]}">${arrValores[u]}</option>`
                }
                cod +=    
        `
        </select>` 
    }
    return cod
}

function actualizarSignoNumerico(newValue, uso){
    console.log(newValue);
    document.getElementById('signoNumerico'+uso).value= newValue
}

let habilitarUsoEvento = true
function eventoUnico(id, accion){
    if(habilitarUsoEvento == true){
        //console.log(`${id}, ${accion}`);
        habilitarUsoEvento = false;

        arre = accion.split('-'); 
        
        //console.log(arre);
        for (let u = 0; u < arre.length; u++) {
            //console.log(arre[u]);                                    arre[u]
            document.getElementById(id).addEventListener("click", eval(accion))
        }
        setTimeout(rehabilitarUsoEventos, 500)
    } 
}

function rehabilitarUsoEventos(){
    //console.log(`rehabilitado uso de eventos anidados`);
    habilitarUsoEvento = true;
}

function invertirArreglo(arr){
    let arre = []
    //console.log(arr);
    for (let u = arr.length - 1; u >= 0; u--) {
        arre.push(arr[u])
    }
    //console.log(arre);
    return arre
}

function ordenarAlfaNumerico(arr){
    arr.sort((a, b) => {
        a = a.toLowerCase();
        b = b.toLowerCase();
        
        if (a < b) {
            return -1;
        } else if (a > b) {
            return 1;
        } else {
            return 0;
        }
    });

    return arr
}

function rotar(id){
    let obj = document.getElementById(id)
    obj.animate([
        { transform: 'rotate(0deg)' },
        { transform: 'rotate(360deg)' }
    ], {
        duration: 2000,
        iterations: Infinity
    });
}

let banderaBoton = 0
function desactivarBotonDespuesDeUsado(id){
    let referencia = document.getElementById('referencia').value
    let dinero = document.getElementById('dinero').value
    let fecha = document.getElementById('fecha').value
    let boton = document.getElementById(id)
    if(referencia != '' && dinero != '' && fecha != ''){
        if (banderaBoton == 0) {
            banderaBoton = 1
            rotar(id)
        } else {
            boton.disabled = true;
            
            console.log('boton bloqueado');
        }
    } 
}

