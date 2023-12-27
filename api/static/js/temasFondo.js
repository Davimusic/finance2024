arrFondos = [
    {'fondo': 'https://res.cloudinary.com/dplncudbq/image/upload/v1692978372/mias/f1_npkojn.png',
    'color1':'#16272A',
    'color2':'black',
    'color3':'#697376',
    'color4':'#1e2c3a',
    },
    {'fondo': 'https://res.cloudinary.com/dplncudbq/image/upload/v1696994289/PhotoReal_awesome_city_4k_sun_shine_0_11zon_f6uqjp.webp',
    'color1':'#211b15',
    'color2':'#60442d',
    'color3':'#62534c',
    'color4':'#8c8c84',
    },
    {'fondo': 'https://res.cloudinary.com/dplncudbq/image/upload/v1692978372/mias/f3_w6ble7.png',
    'color1':'#141424',
    'color2':'#8a3a49',
    'color3':'#512d3f',
    'color4':'#5c554d',
    },
    {'fondo': 'https://res.cloudinary.com/dplncudbq/image/upload/v1657579476/mias/m2_s0ekov.jpg',
    'color1':'#22212c',
    'color2':'#705549',
    'color3':'#646e74',
    'color4':'#3f4751',
    },
    {'fondo': 'https://res.cloudinary.com/dplncudbq/image/upload/v1655397327/mias/4_azgtvh.jpg',
    'color1':'#374246',
    'color2':'#9e7c5f',
    'color3':'#e3b3d4',
    'color4':'#64a4be',
    },
    {'fondo': 'https://res.cloudinary.com/dplncudbq/image/upload/v1655397328/mias/3_iswt4d.jpg',
    'color1':'#846666',
    'color2':'#0f1f23',
    'color3':'#99a3b2',
    'color4':'#4c3f40',
    },{'fondo': 'https://res.cloudinary.com/dplncudbq/image/upload/v1655397345/mias/1_tolz58.jpg',
    'color1':'#3e2f37',
    'color2':'#d9916e',
    'color3':'#9f6d61',
    'color4':'#99a3b2',
    },
    {'fondo': 'https://res.cloudinary.com/dplncudbq/image/upload/v1656010336/mias/l2_vompkz.jpg',
    'color1':'#312d50',
    'color2':'#63599d',
    'color3':'#0e0b13',
    'color4':'#686580',
    },
    {'fondo': 'https://res.cloudinary.com/dplncudbq/image/upload/v1656010338/mias/l3_k2o6sa.jpg',
    'color1':'#302a24',
    'color2':'#ddb071',
    'color3':'#674b3c',
    'color4':'#7c6349',
    },
    {'fondo': 'https://res.cloudinary.com/dplncudbq/image/upload/v1656097007/mias/h2_jy6hgj.jpg',
    'color1':'#bd635a',
    'color2':'#090710',
    'color3':'#2e71c2',
    'color4':'#632b34',
    }]
let coor = 0


function cambiarTemaFondo(acc){
    if(acc === 'next'){
        if((arrFondos.length - 1) >= coor + 1){
            coor += 1
        } else {
            coor  = 0
        }
    } else if(acc === 'before'){
        if(coor -1 >= 0){
            coor -= 1
        } else {
            coor = arrFondos.length - 1
        }
    }

    actualizarFondo(arrFondos[coor])
    document.getElementById('botonSubmit').style.display = 'flex'
}

function actualizarFondo(obj){
    document.body.style.backgroundImage = `url('${obj['fondo']}')`;
    document.getElementById('menuDesplegable').style.backgroundImage = `url('${obj['fondo']}')`;
    let linkImagenFondo = document.getElementById('linkImagenFondo')
    if(linkImagenFondo){
        linkImagenFondo.value = obj['fondo']
    }

    for (let u = 1; u < 5; u++) {
        const elementos = document.getElementsByClassName(`color${u}`);
        if(linkImagenFondo){
            document.getElementById(`color${u}`).value = obj[`color${u}`]
        }
        
        for(let i = 0; i < elementos.length; i++) {
            elementos[i].style.backgroundColor = obj[`color${u}`];
        }
    }
}

function arranqueTemas(estilos){
    code = ''
    code += `
    ${menu()}
    <div style='display: flex;'>
        <img onclick="cambiarTemaFondo('before')" style="height: 40px; background: white; border-radius: 50%; transition: all 0.5s ease 0s; margin-top: 129.2px; margin-left: 100px;" class="mano efectoMenu" src="https://res.cloudinary.com/dplncudbq/image/upload/v1703638887/next_mvphmg.png" alt="">
        <img onclick="cambiarTemaFondo('next')"   style="height: 40px; background: white; border-radius: 50%; transition: all 0.5s ease 0s; margin-top: 129.2px; margin-left: 100px;" class="mano efectoMenu" src="https://res.cloudinary.com/dplncudbq/image/upload/v1703638887/before_zt59r1.png" alt="">
        <form method="post">
            <input id="linkImagenFondo" style="display:none;" value = "fondo" class="borde1 color4" type="text" name="linkImagenFondo" required>
            <input id="color1" style="display:none;" value = "color1" class="borde1 color4" type="text" name="color1" required>
            <input id="color2" style="display:none;" value = "color2" class="borde1 color4" type="text" name="color2" required>
            <input id="color3" style="display:none;" value = "color3" class="borde1 color4" type="text" name="color3" required>
            <input id="color4" style="display:none;" value = "color4" class="borde1 color4" type="text" name="color4" required>
            <button id="botonSubmit" style="display: none; background: none; border: none; height:40px;" type="submit"><img style="height: 40px; background: white; border-radius: 50%; transition: all 0.5s ease 0s; margin-top: 129.2px; margin-left: 100px;" class="mano efectoMenu" src="https://res.cloudinary.com/dplncudbq/image/upload/v1701543797/select_hkx3sf.png" alt=""></button>
        </form>
    </div>    
    <div style="display: flex; justify-content: center; align-items: center; height: 80vh; text-align: center; margin: 2%;"> 
        <div class="color1" style=" width: 50%; height: 10%; border-radius: 0.7em">color 1</div>
        <div class="color2" style=" width: 50%; height: 10%; border-radius: 0.7em">color 2</div>
        <div class="color3" style=" width: 50%; height: 10%; border-radius: 0.7em">color 3</div>
        <div class="color4" style=" width: 50%; height: 10%; border-radius: 0.7em">color 4</div>
    </div>
    `
    document.getElementById('padreMenu').innerHTML = code

    if(estilos.length != 0){
        esti = JSON.parse(estilos)
        actualizarFondo(esti)
    }
}

