async function generate_card(name, id, small_src, imgsrc, wishlist_amount){

    let img_element = document.createElement("img")
    img_element.setAttribute("alt", name + " card" ) 
    img_element.setAttribute("class", "card_image")
    img_element.setAttribute("src", small_src)
    img_element.onclick = async () => await generate_big_card(imgsrc, name + " card")

    let wishlist_add = document.createElement("div")
    wishlist_add.setAttribute("class", "wishlist_add")
    wishlist_add.innerHTML = "+"
    wishlist_add.onclick = async () => update_wishlist(id, "1")

    let wishlist_sub = document.createElement("div")
    wishlist_sub.setAttribute("class", "wishlist_sub")
    wishlist_sub.innerHTML = "-"
    wishlist_sub.onclick = async () => await update_wishlist(id, "-1")

    let wishlist_count = document.createElement("div")
    wishlist_count.setAttribute("class", "wishlist_count")
    wishlist_count.innerHTML = "In Wishlist: " + wishlist_amount

    let wishlist_container = document.createElement("div")
    wishlist_container.setAttribute("id", "wishlist_container-"+id)
    wishlist_container.setAttribute("class", "wishlist_container")
    wishlist_container.appendChild(wishlist_sub)
    wishlist_container.appendChild(wishlist_count)
    wishlist_container.appendChild(wishlist_add)

    let card_element = document.createElement("div")
    card_element.setAttribute("class", "card")
    card_element.setAttribute("wishlist_id", id)
    card_element.appendChild(img_element)
    card_element.appendChild(wishlist_container)

    return card_element
}

function close_big_card(){
    let cards = document.querySelectorAll(".big_card_container")
    cards.forEach(card => {
        card.remove()
    })
}

document.onkeydown = function(evt) {
    evt = evt || window.event;
    if (evt.key  == "Escape") {
        close_big_card()
    }
};

function generate_big_card(imgsrc, alt){

    let big_card_container = document.createElement("div")
    big_card_container.setAttribute("class", "big_card_container")

    let img_element = document.createElement("img")
    img_element.setAttribute("alt", alt)
    img_element.setAttribute("class", "big_card_image")
    img_element.setAttribute("src", imgsrc)
    big_card_container.appendChild(img_element) 

    let close_button = document.createElement("div")
    close_button.setAttribute("class", "big_card_close")
    close_button.innerHTML = "X "
    close_button.onclick = () => close_big_card()

    big_card_container.appendChild(close_button)

    document.body.appendChild(big_card_container)

}