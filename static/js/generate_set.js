async function main() {

    let url = window.location.href.split("/")
    let set_name = url[url.length - 1]

    let card_library = document.getElementById("cards")

    // Get the sets
    let response_cards = await fetch("/set/" + set_name)
    let card_data = await response_cards.json()
    card_data.sort((a, b) => a.id - b.id)

    // Get the wishlist
    let response_wishlist = await fetch("/wishlist_id")
    let wishlist = await response_wishlist.json()

    card_data.forEach(async function (card) {

        let wanted = 0
        let wishlist_id = card.id

        if (Object.keys(wishlist).includes(wishlist_id)) {
            wanted = wishlist[wishlist_id]
        }

        card_element = await generate_card(card.name, wishlist_id, card.image_url_small, card.image_url_large, wanted)
        card_library.appendChild(card_element)
    })
}