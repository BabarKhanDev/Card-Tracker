async function main() {
    // TODO something similar to build_wishlist.js where we section by set
    let card_library = document.getElementById("cards")
    let response = await fetch("/library_id")
    let library_ids = await response.json()
    for (const [card_id, _] of Object.entries(library_ids)) {
        let card_element = await generate_card(card_id)
        card_library.appendChild(card_element)
    }
}