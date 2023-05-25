function update_card_scale(scale){
    var r = document.querySelector(':root');

    scale = scale * 0.5 + 1

    r.style.setProperty('--width', String(250 * scale) + "px");
    r.style.setProperty('--height', String(350 * scale) + "px");
}

function update_card_padding(padding){
    var r = document.querySelector(':root');

    r.style.setProperty('--padding', String(10 * padding) + "em");
}