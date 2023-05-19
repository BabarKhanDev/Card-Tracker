function generate_card(name, total, imgsrc, holo=false){
    let img_element = document.createElement("img")
    img_element.setAttribute("alt", "Image of " + name)
    img_element.setAttribute("class", "card_image")
    img_element.setAttribute("src", imgsrc)

    let card_element = document.createElement("div")
    card_element.setAttribute("class", "card")
    card_element.appendChild(img_element)

    return card_element
}

function update_card_scale(scale){
    var r = document.querySelector(':root');

    scale = scale * 0.5 + 1

    r.style.setProperty('--width', String(250 * scale) + "px");
    r.style.setProperty('--height', String(350 * scale) + "px");
}

function main(){
    let card_library = document.getElementById("cards")
    
    for (let i= 0; i < 11; i++){

        card_element = generate_card("apple", i, "../cards/apple.jpg")
        card_library.appendChild(card_element)

    }
}