function show_upload_menu(){
    let menu = document.getElementById("upload_menu_container");
    menu.style.display = "flex";
}

document.onkeydown = function(evt) {
    evt = evt || window.event;
    if (evt.key  == "Escape") {
        let menu = document.getElementById("upload_menu_container");
        menu.style.display = "none";
    }
};

async function submit_data(){
    
    let files = document.getElementById("card-upload").files;
    let formData = new FormData();

    for (let i = 0; i < files.length; i++) {
        formData.append("file", files[i]);
    }

    let response = await fetch("/upload_cards", {
        method:'POST',
        body: formData
    });

    let status = await response.text();
    console.log(status);
    //TODO, do something with status
    // We probably want to just close the menu

}   

function upload_main(){
    // Update file count when files are selected
    document.getElementById("card-upload").addEventListener("change", function() {
        let files = this.files;
        let fileCountElement = document.getElementById("file-count");
        fileCountElement.textContent = files.length + " files selected";
    });
}