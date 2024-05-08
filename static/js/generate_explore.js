async function main() {

    // Set up environment
    body = document.getElementById("sets")

    // Get the sets
    let response = await fetch("/all_sets")
    let set_data = await response.json();

    // When we first see a series we want to create a section for it
    found_series = new Set()

    // Loop through all sets and create an icon for it
    Object.entries(set_data).forEach((entry) => {
        let series = entry[1]["series"]

        if (!(found_series.has(series))) {
            create_section(series, body)
            found_series.add(series)
        }

        let image_url = entry[1]["image_url"]
        let name = entry[1]["name"]
        let id = entry[1]["id"]

        make_set_button(image_url, name, series, id)
    });

}

function create_section(series, body) {

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

function make_set_button(image_url, name, series, id) {

    let set_container = document.createElement("a")
    set_container.setAttribute("class", "set_container")
    set_container.setAttribute("href", "../explore/" + id)

    let set_element = document.createElement("img")
    set_element.setAttribute("alt", name + "logo")
    set_element.setAttribute("class", "set_image")
    set_element.setAttribute("src", image_url)

    let set_text = document.createElement("p")
    set_text.setAttribute("class", "set_text")
    set_text.innerHTML = name

    set_container.appendChild(set_element)
    set_container.appendChild(set_text)

    let series_container = document.getElementById(series + "_sets")
    series_container.appendChild(set_container)
}