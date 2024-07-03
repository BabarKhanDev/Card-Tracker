async function generate_card(
    id,
    show_wishlist = true,
    delete_if_wishlist_zero = false,
    show_library = true,
    delete_if_library_zero = false
) {

    let response = await fetch(`/card/${id}`)
    let card_details = await response.json()

    let img_element = document.createElement("img")
    img_element.setAttribute("alt", name + " card")
    img_element.setAttribute("class", "card_image")
    img_element.setAttribute("src", card_details.image_url_small)
    img_element.onclick = async () => generate_big_card(card_details.image_url_large, name + " card")

    let card_element = document.createElement("div")
    card_element.setAttribute("class", "card")
    card_element.setAttribute("wishlist_id", id)
    card_element.append(img_element)

    if (show_wishlist) {
        let response = await fetch("/wishlist_id")
        let wishlist = await response.json()
        let wishlist_count = wishlist[id] || 0

        let wishlist_container = create_wishlist_container(id, delete_if_wishlist_zero, wishlist_count)
        card_element.append(wishlist_container)
    }

    if (show_library) {
        let response = await fetch("/upload_count/" + id)
        let library_count = (await response.json())[id] || 0
        let library_container = create_library_container(id, library_count)
        card_element.append(library_container)
    }

    return card_element
}

async function generate_uploaded_card(image_path, upload_id) {
    let img_element = document.createElement("img")
    img_element.setAttribute("alt", "Uploaded card")
    img_element.setAttribute("class", "img_library card_image")
    img_element.setAttribute("src", image_path)
    img_element.onclick = async () => generate_match_resolver(image_path, upload_id)

    return img_element
}

async function update_wishlist(id, amount, delete_if_wishlist_zero) {
    let formData = new FormData();
    formData.append('card_id', id);
    formData.append('amount', amount);

    let response = await fetch("/wishlist_id", {
        method: 'POST',
        body: formData
    })

    let wishlist = await response.json()
    let counter = document.getElementById("wishlist_count_" + id);

    // if we unwishlist then the id will not be in the wishlist dictionary
    if (id in wishlist) {
        counter.innerHTML = "Wishlist: " + String(wishlist[id])
    } else {
        if (delete_if_wishlist_zero) {
            let card_container = document.querySelector('[wishlist_id=' + id + ']');
            card_container.remove()
        } else {
            counter.innerHTML = "In Wishlist: 0"
        }

    }

}

function generate_big_card(imgsrc, alt) {

    let big_card_container = document.createElement("div")
    big_card_container.setAttribute("class", "big_card_container")

    let img_element = document.createElement("img")
    img_element.setAttribute("alt", alt)
    img_element.setAttribute("class", "big_card_image")
    img_element.setAttribute("src", imgsrc)
    big_card_container.appendChild(img_element)

    let close_button = document.createElement("span")
    close_button.setAttribute("class", "big_card_close material-symbols-outlined")
    close_button.innerHTML = 'close'
    close_button.onclick = () => close_menus()

    big_card_container.appendChild(close_button)

    document.body.appendChild(big_card_container)

}

async function generate_match_resolver(imgsrc, upload_id) {

    let match_resolver_container = document.createElement("div")
    match_resolver_container.setAttribute("class", "match_resolver_container")

    // First row - our image, takes up 2/3 of the page
    let img_element = document.createElement("img")
    img_element.className = "big_card_image"
    img_element.src = imgsrc

    // Second row - our matches, takes up 1/3 of the page
    // match list can be a row element with each match in it
    let matches_element = document.createElement("div")
    matches_element.className = "matches_element"
    let response = await fetch("/matches/" + upload_id)
    let matches = await response.json()
    for (const match of matches) {
        matches_element.appendChild(await generate_card(match.card_id, false, false, false, false));
    }

    let close_button = document.createElement("span")
    close_button.classList.add("big_card_close", "material-symbols-outlined")
    close_button.innerHTML = 'close'
    close_button.onclick = () => close_menus()

    match_resolver_container.append(img_element, matches_element, close_button)
    document.body.appendChild(match_resolver_container)

}

function close_menus() {
    let cards = document.querySelectorAll(".match_resolver_container,.big_card_container")
    cards.forEach(card => {
        card.remove()
    })
}

document.onkeydown = function (evt) {
    evt = evt || window.event;
    if (evt.key === "Escape") {
        close_menus()
    }
};

function create_wishlist_container(id, delete_if_wishlist_zero, wishlist_amount) {
    let wishlist_add = document.createElement("div")
    wishlist_add.setAttribute("class", "wishlist_add")
    wishlist_add.innerHTML = "+"
    wishlist_add.onclick = async () => update_wishlist(id, "1")

    let wishlist_sub = document.createElement("div")
    wishlist_sub.setAttribute("class", "wishlist_sub")
    wishlist_sub.innerHTML = "-"
    wishlist_sub.onclick = async () => await update_wishlist(id, "-1", delete_if_wishlist_zero)

    let wishlist_count = document.createElement("div")
    wishlist_count.setAttribute("class", "wishlist_count")
    wishlist_count.setAttribute("id", "wishlist_count_" + id)
    wishlist_count.innerHTML = "In Wishlist: " + wishlist_amount

    let wishlist_container = document.createElement("div")
    wishlist_container.setAttribute("id", "wishlist_container-" + id)
    wishlist_container.setAttribute("class", "wishlist_container")
    wishlist_container.append(wishlist_sub, wishlist_count, wishlist_add)

    return wishlist_container
}

function create_library_container(id, library_amount) {

    let library_count = document.createElement("div")
    library_count.setAttribute("class", "library_count")
    library_count.setAttribute("id", "library_count_" + id)
    library_count.innerHTML = "In Library: " + library_amount

    let library_container = document.createElement("div")
    library_container.setAttribute("id", "wishlist_container-" + id)
    library_container.setAttribute("class", "wishlist_container")
    library_container.append(library_count)

    return library_container
}