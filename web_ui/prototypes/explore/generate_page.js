async function main(){
    
    // Set up environment
    card_api_url = "http://127.0.0.1:5000"
    body = document.getElementById("sets")

    // Get the sets
    let response = await fetch(card_api_url + "/all_sets")
    let set_data = await response.json();


    // Loop through all sets and create an icon for it
    Object.entries(set_data).forEach((entry) => {
        let set_id = entry[0]
        let set_image_url = entry[1]["image_URL"]
        let set_name = entry[1]["name"]
        
        make_set_button(set_id, set_image_url, set_name, body) 
    });

}

function update_card_scale(scale){
    var r = document.querySelector(':root');

    scale = scale * 0.5 + 1

    r.style.setProperty('--width', String(250 * scale) + "px");
    r.style.setProperty('--height', String(350 * scale) + "px");
    r.style.setProperty('--text-size', String(scale) + "em");
}

function make_set_button(set_id, set_image_url, set_name, body){

    let set_container = document.createElement("div")
    set_container.setAttribute("class", "set_container")

    let set_element = document.createElement("img")
    set_element.setAttribute("alt", set_name + "logo")
    set_element.setAttribute("class", "set_image")
    set_element.setAttribute("src", set_image_url)

    let set_text = document.createElement("p")
    set_text.setAttribute("class", "set_text")
    set_text.innerHTML = set_name

    set_container.appendChild(set_element)
    set_container.appendChild(set_text)
    body.appendChild(set_container)
}