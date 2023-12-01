function aviso(mensaje){
    let divPadre = document.getElementById('padreMenu')
    divPadre.innerHTML = `
            ${menu()}
            <form method="post" class="color1 borde1 padding1 sombra" style="margin: auto; width: 90%; height: 65%; margin-top: ${((window.innerHeight/100)*15)}px;">
                <textarea oninput="quitarSaltosDeLinea(this.value)" style="background: #3a3a3b; width:100%; height: 80%;" class="borde1" name="" id="textArea1" cols="30" rows="10">${agregarSaltosDeLinea(mensaje)}</textarea>
                <textarea class="borde1 color2"  style="display:none;" name="anotaciones" id="textArea2" cols="30" rows="10">${mensaje}</textarea>
                <button style="margin-top:20px; background: none; border: none; height:40px;" type="submit"><img class="efectoMenu" style="background: white; height:40px; border-radius:50%;" id="botonEditar" src="https://res.cloudinary.com/dplncudbq/image/upload/v1671160860/mias/descarga_uomlyb.png" alt=""></button>
            </form> 
    `
}

function quitarSaltosDeLinea(text){
    document.getElementById('textArea2').value = text.replace(/\n/g, "º")
}

function agregarSaltosDeLinea(text){
    return text.replace(/\º/g, '\n')
}

