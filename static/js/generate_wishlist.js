let card_api_url = "http://127.0.0.1:5000"

async function main(){
    let card_library = document.getElementById("sets")
    
    // Get a list of cards that we have wishlisted, along with a list of just the ids
    let response = await fetch(card_api_url + "/wishlist_cards")
    let wishlisted_cards = await response.json()
    let wishlist_ids = wishlisted_cards.map(obj => obj.set.id)

    // Get the quantity wishlisted of each wishlisted card
    let response_wishlist = await fetch(card_api_url + "/wishlist_json") 
    let wishlist = await response_wishlist.json()

    // Get a sorted list of all of the set ids
    let response_sets = await fetch(card_api_url + "/all_sets")
    let all_sets = await response_sets.json()
    let sorted_set_ids = all_sets.map(obj => obj.id)
    let id_to_name = all_sets.map(obj => [obj.id, obj.name])

    // Filter this list of set ids to the ones that we have wishlisted, this has preserved the release order
    let filtered_sorted_set_ids = sorted_set_ids.filter(name => wishlist_ids.includes(name));
    console.log(filtered_sorted_set_ids)

    // Create a section for each set
    found_series = new Set()
    filtered_sorted_set_ids.forEach(async function (set_id){

        if (!(found_series.has(set_id))){
            
            let set_name = id_to_name.filter(obj => (obj[0] == set_id))[0][1]
            
            create_section(set_name, set_id, card_library)
            found_series.add(set_id)
        }

    })

    // Add the cards to their relevant section
    wishlisted_cards.forEach(async function (card) {

        let wanted = 0
        let wishlist_id = card.id

        let set_id = card.id.split("-")[0]

        if (Object.keys(wishlist).includes(wishlist_id)){
            wanted = wishlist[wishlist_id]
        }

        card_element = await generate_card(card.name, wishlist_id, card.images.small, card.images.large, wanted, true, true)
        document.getElementById(set_id + "_cards").appendChild(card_element)
    })

}

function create_section(series, set_id, body){

    let series_section = document.createElement("section")
    series_section.setAttribute("id", series)
    series_section.setAttribute("class", "series_section")

    let series_cards_container = document.createElement("div")
    series_cards_container.setAttribute("id", set_id + "_cards")
    series_cards_container.setAttribute("class", "series_container")

    let series_label = document.createElement("h2")
    series_label.innerHTML = series.replace(/\b\w/g, char => char.toUpperCase()) // This will replace the first character of each string with a capital letter
    series_label.setAttribute("class", "series_label")
    
    series_section.appendChild(series_label)
    series_section.appendChild(series_cards_container)
    body.appendChild(series_section)
    
}