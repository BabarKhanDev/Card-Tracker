async function main() {
    // TODO something similar to build_wishlist.js where we section by set
    let card_library = document.getElementById("cards")
    let response = await fetch("/uploads")
    let library_uploads = await response.json()
    for (const upload of library_uploads) {
        let card_element = await generate_uploaded_card(upload.imgsrc, upload.upload_id)
        card_library.appendChild(card_element)
    }
}