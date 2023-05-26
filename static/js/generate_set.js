card_api_url = "http://127.0.0.1:5000"

async function main(){

    let url = window.location.href.split("/")
    let set_name = url[url.length -1]
    console.log(set_name)

    let card_library = document.getElementById("cards")
    
    // Get the sets
    let response_cards = await fetch(card_api_url + "/set/" + set_name)
    let card_data = await response_cards.json()
    card_data.sort((a,b) => a.id - b.id)

    // Get the wishlist
    let response_wishlist = await fetch(card_api_url + "/wishlist") 
    let wishlist = await response_wishlist.json()

    card_data.forEach(async function (card) {

        let wanted = 0
        let wishlist_id = card.id

        if (Object.keys(wishlist).includes(wishlist_id)){
            wanted = wishlist[wishlist_id]
        }

        card_element = await generate_card(card.name, wishlist_id, card.images.small, card.images.large, wanted)
        card_library.appendChild(card_element)
    })

}