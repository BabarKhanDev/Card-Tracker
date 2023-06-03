function show_upload_menu(){
    let menu = document.getElementById("upload_menu_container");
    menu.style.display = "flex";
}

document.onkeydown = function(evt) {
    evt = evt || window.event;
    if (evt.key  == "Escape") {
        let menu = document.getElementById("upload_menu_container")
        menu.style.display = "none";
    }
};

async function submit_data(){
    let formData = new FormData();

    let files = document.getElementById("card-upload").value
    console.log(files)

    formData.append("file", files)
    console.log(formData)

    let response = await fetch("/upload_cards", {
        method:'POST',
        body: formData
    })

    let responseJSON = await response.JSON
    console.log(responseJSON)

}