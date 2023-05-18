function generate_card(total, imgsrc, holo=false){

    let total_element = document.createElement("p")
    total_element.setAttribute("class", "card_total")
    total_element.innerHTML = "You have: " + total

    let img_element = document.createElement("img")
    img_element.setAttribute("alt", "Image of " + name)
    img_element.setAttribute("src", imgsrc)

    let card_element = document.createElement("div")
    card_element.setAttribute("class", "card")
    card_element.appendChild(img_element)
    card_element.appendChild(total_element)    

    return card_element
}

function update_card_scale(scale){
    var r = document.querySelector(':root');

    scale = scale * 0.5 + 1

    r.style.setProperty('--width', String(250 * scale) + "px");
    r.style.setProperty('--height', String(350 * scale) + "px");
    r.style.setProperty('--text_large', String(1.1 * scale) + "em");
    r.style.setProperty('--text_small',  String(0.8 * scale) + "em");
}

function main(){
    let card_library = document.getElementById("cards")
    
    for (let i= 0; i < 11; i++){

        card_element = generate_card(i, "../cards/apple.jpg")
        card_library.appendChild(card_element)

    }
}