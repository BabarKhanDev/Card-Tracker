async function main(){
    let card_library = document.getElementById("cards")
    
    for (let i= 0; i < 11; i++){
        
        //                          name,    id, small_src, imgsrc, wishlist_amount
        card_element = await generate_card("apple", i, "https://m.media-amazon.com/images/I/61TUXDvMZGL._AC_SY741_.jpg", "https://m.media-amazon.com/images/I/61TUXDvMZGL._AC_SY741_.jpg", 0)
        card_library.appendChild(card_element)

    }
}