card_api_url = "http://127.0.0.1:5000"

async function update_wishlist(id, amount){
    let formData = new FormData();
    formData.append('card_id', id);
    formData.append('amount', amount);

    console.log(JSON.stringify(formData))
    let response = await fetch(card_api_url+"/wishlist", {
        method:'POST',
        body: formData
    })
}



async function generate_card(name, id, imgsrc, wishlist_amount){

    let img_element = document.createElement("img")
    img_element.setAttribute("alt", name + " card" ) 
    img_element.setAttribute("class", "card_image")
    img_element.setAttribute("src", imgsrc)
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

function generate_big_card(imgsrc, alt){

    console.log(imgsrc)

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
    close_button.setAttribute("onclick", 
        `
        let cards = document.querySelectorAll(".big_card_container")
        cards.forEach(card => {
            card.remove()
        })
        `
    )

    big_card_container.appendChild(close_button)



    document.body.appendChild(big_card_container)
    console.log("test")

}

async function main(){

    let set_name = "swsh12pt5"

    let card_library = document.getElementById("cards")
    
    // Get the sets
    let response_cards = await fetch(card_api_url + "/set/" + set_name)
    let card_data = await response_cards.json()
    card_data.sort((a,b) => a.id - b.id)
    console.log(card_data)

    // Get the wishlist
    let response_wishlist = await fetch(card_api_url + "/wishlist") 
    let wishlist = await response_wishlist.json()
    console.log(wishlist)

    card_data.forEach(async function (card) {

        let wanted = 0
        let wishlist_id = set_name + "-" + card.id

        if (Object.keys(wishlist).includes(wishlist_id)){
            wanted = wishlist[wishlist_id]
            console.log("Want " + card.name + " x " + wanted)
        }

        card_element = await generate_card(card.name, wishlist_id, card.images.large, wanted)
        card_library.appendChild(card_element)
    })

}