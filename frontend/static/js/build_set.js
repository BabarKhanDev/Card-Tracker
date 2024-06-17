async function main() {

    // Set up page
    let url = window.location.href.split("/")
    let set_name = url[url.length - 1]
    let card_library = document.getElementById("cards")

    // Get the cards within the set
    let response_cards = await fetch("/set/" + set_name)
    let card_data = await response_cards.json()
    card_data.sort((a, b) => a.id - b.id)

    // Build each card
    for (const card of card_data) {
        let card_element = await generate_card(card.id)
        card_library.appendChild(card_element)
    }
}