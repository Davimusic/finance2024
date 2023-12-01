let bloqueEnUso = "sin activar";

function actualizarBloqueEnUso(text){
    bloqueEnUso = text
    //console.log(`bloqueEnUso: ${bloqueEnUso}`);
}

function ActivarModal(contenido, titulo){
    if(bloqueEnUso == "sin activar"){
        alert("elija bloque")
    } else {
		if(contenido != undefined){
			//console.log(`ActivarModal: ${contenido}`);
			document.getElementById("root").innerHTML = modal(contenido, titulo)
        	setTimeout(actualizarModal, 100)
		} 
    }
}

function actualizarModal(){
	let idModal = document.getElementById("modala");
	idModal.style.display = "block";
    setTimeout(mostrarModal, 100)
}

function mostrarModal(){
	let idModal = document.getElementById("modala");
	idModal.style.boxShadow = "0px -1px 24px 0px rgba(0,0,0,0.75)";
	idModal.style.height = "fit-content";
	idModal.style.opacity = "1";
	idModal.style.transition = "1s";
}

function desactivarModal(){
	let idModal = document.getElementById("modala");
	idModal.style.transition = "1s";
	idModal.style.height = "0px";
	idModal.style.opacity = "0";
	setTimeout(esconderModal, 500)
}

function esconderModal(){
	let idModal = document.getElementById("modala");
	idModal.style.display = "none";
}

function modal(contenido, titulo){
	let conte = ""

	if(contenido != undefined){
		conte = contenido
	} 

	
	cod = `
	<div class='borde1' style = "text-align: center; background: #ffffff91; backdrop-filter: blur(5px); display: none; padding: 2%; opacity: 0; height: 0px" id="modala">
		<header class='borde1' style = "position: sticky; top: 0; padding: 2%; background: #3c8179; display:flex; justify-content: space-between;">
			<div style="display:flex; justify-content: space-between;">
				<div> ${titulo} </div>
			</div>
			<div style="cursor: pointer; justify-content: left;" onclick="desactivarModal()"> X </div>
		</header>
		<div style="padding-top: 20px;" class="">
                ${conte}
		</div>
	</div>
	`
    return cod
}

function saludar(text){
	alert(text);
}

function activarModificacion(id){
	document.getElementById(id).readOnly = false;
}