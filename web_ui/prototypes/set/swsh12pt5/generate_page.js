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

function update_card_padding(padding){
    var r = document.querySelector(':root');

    r.style.setProperty('--padding', String(10 * padding) + "em");
}

async function main(){
    let card_library = document.getElementById("cards")
    
    // Get the sets
    card_api_url = "http://127.0.0.1:5000"
    let response_cards = await fetch(card_api_url + "/set/swsh12pt5")
    let card_data = await response_cards.json()
    card_data.sort((a,b) => a.id - b.id)
    console.log(card_data)

    card_data.forEach(function (card) {
        card_element = generate_card(card.name, card.id, card.images.large)
        card_library.appendChild(card_element)
    })


}