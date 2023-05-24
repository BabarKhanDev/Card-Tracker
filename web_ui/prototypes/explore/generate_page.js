async function main(){
    
    // Set up environment
    card_api_url = "http://127.0.0.1:5000"
    body = document.getElementById("sets")

    // Get the sets
    let response_sets = await fetch(card_api_url + "/all_sets")
    let set_data = await response_sets.json();

    // When we first see a series we want to create a section for it
    found_series = new Set()

    // Loop through all sets and create an icon for it
    Object.entries(set_data).forEach((entry) => {
        let series = entry[1]["series"]

        if (!(found_series.has(series))){
            create_section(series, body)
            found_series.add(series)
        }
        
        let set_image_url = entry[1]["image_URL"]
        let set_name = entry[1]["name"]
        let set_id = entry[1]["id"]
        
        make_set_button(set_image_url, set_name, series, set_id) 
    });

}

function update_card_scale(scale){
    var r = document.querySelector(':root');

    scale = scale * 0.5 + 1

    r.style.setProperty('--width', String(250 * scale) + "px");
    r.style.setProperty('--height', String(350 * scale) + "px");
    r.style.setProperty('--text-size', String(scale) + "em");
}

function create_section(series, body){



    let series_section = document.createElement("section")
    series_section.setAttribute("id", series)
    series_section.setAttribute("class", "series_section")

    let series_sets_container = document.createElement("div")
    series_sets_container.setAttribute("id", series + "_sets")
    series_sets_container.setAttribute("class", "series_container")

    let series_label = document.createElement("h2")
    series_label.innerHTML = series[0].toUpperCase() + series.slice(1).toLowerCase()
    series_label.setAttribute("class", "series_label")
    
    series_section.appendChild(series_label)
    series_section.appendChild(series_sets_container)
    body.appendChild(series_section)
    
}

function make_set_button(set_image_url, set_name, series, id){

    let set_container = document.createElement("a")
    set_container.setAttribute("class", "set_container")
    set_container.setAttribute("href", "../set/"+id)

    let set_element = document.createElement("img")
    set_element.setAttribute("alt", set_name + "logo")
    set_element.setAttribute("class", "set_image")
    set_element.setAttribute("src", set_image_url)

    let set_text = document.createElement("p")
    set_text.setAttribute("class", "set_text")
    set_text.innerHTML = set_name

    set_container.appendChild(set_element)
    set_container.appendChild(set_text)

    series_container = document.getElementById(series+"_sets")
    series_container.appendChild(set_container)
}