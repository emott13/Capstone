function scrollLeftt(track) {
    switch (track) {
        case 'first':
            document.getElementById("carouselTrack1").scrollBy({
                left: -300,
                behavior: "smooth"
            });
            break;
        case 'second':
            document.getElementById("carouselTrack2").scrollBy({
                left: -300,
                behavior: "smooth"
            });
            break;
        case 'third':
            document.getElementById("carouselTrack3").scrollBy({
                left: -300,
                behavior: "smooth"
            });
            break;
    }
    
}

function scrollRight(track) {
    switch (track) {
        case 'first':
            document.getElementById("carouselTrack1").scrollBy({
                left: 300,
                behavior: "smooth"
            });
            break;
        case 'second':
            document.getElementById("carouselTrack2").scrollBy({
                left: 300,
                behavior: "smooth"
            });
            break;
        case 'third':
            document.getElementById("carouselTrack3").scrollBy({
                left: 300,
                behavior: "smooth"
            });
            break;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const track = document.getElementById("carouselTrack1");

    // Clone items for illusion of infinity
    const items = Array.from(track.children);

    items.forEach(item => {
        const clone = item.cloneNode(true);
        track.appendChild(clone);
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const track = document.getElementById("carouselTrack2");

    // Clone items for illusion of infinity
    const items = Array.from(track.children);

    items.forEach(item => {
        const clone = item.cloneNode(true);
        track.appendChild(clone);
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const track = document.getElementById("carouselTrack3");

    // Clone items for illusion of infinity
    const items = Array.from(track.children);

    items.forEach(item => {
        const clone = item.cloneNode(true);
        track.appendChild(clone);
    });
});

let quantityContainer = document.querySelector(".quantity");
let minusBtn = quantityContainer.querySelector(".minus");
let plusBtn = quantityContainer.querySelector(".plus");
let inputBox = quantityContainer.querySelector(".input-box");

updateButtons();

quantityContainer.addEventListener("click", (e) => {
    if(e.target.classList.contains("minus")){
        inputBox.value = parseInt(inputBox.value) - 1;
    }
    else if(e.target.classList.contains("plus")){
        inputBox.value = parseInt(inputBox.value) + 1;
    }
    updateButtons();
});

function updateButtons(){
    let value = parseInt(inputBox.value);
    minusBtn.disabled = value <= parseInt(inputBox.min);
    plusBtn.disabled = value >= parseInt(inputBox.max);
}