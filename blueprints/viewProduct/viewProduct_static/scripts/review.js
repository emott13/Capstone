let createReviewForm = document.getElementById("create-review");

// Make create review stars show correctly
updateReviewCreate(createReviewForm.rating.value);


// Set main product image for zoom function
function setMainImage(url){
    let main = document.getElementById('main-product-img');
    if(main){
        main.src = url;
    }
    let overlay = document.getElementById('image-zoom');
    let zoomed = document.getElementById('zoomed-img');
    if(overlay && overlay.style.display !== 'none' && zoomed){
        zoomed.src = url;
    }
}
// Scrolling smoothness on image zoom
function scrollThumbs(dir){
    let container = document.getElementById('thumbnail-container');
    if(container){
        container.scrollBy({ left: dir * 70, behavior: 'smooth' });
    }
}
// Image zoom movement on cursor
function zoomPan(e) {
    let zoomed = e.currentTarget;
    let rect = zoomed.getBoundingClientRect();
    let x = e.clientX - rect.left;
    let y = e.clientY - rect.top;
    let xPct = (x / rect.width) * 100;
    let yPct = (y / rect.height) * 100;
    zoomed.style.transformOrigin = xPct + "% " + yPct + "%";
}
// Image zoom resets after cursor moved away
function resetZoomOrigin(){
    const zoomed = document.getElementById('zoomed-img');
    if(zoomed){
        zoomed.style.transformOrigin = 'center center';
    }
}
// Open lightbox for image zoom
function openZoom(src){
    let overlay = document.getElementById('image-zoom');
    let zoomed = document.getElementById('zoomed-img');
    let main = document.getElementById('main-product-img');
    let imgSrc = src || (main ? main.src : '');
    if(!overlay || !zoomed){
        return;
    }
    zoomed.src = imgSrc;
    overlay.style.display = 'block';
    zoomed.addEventListener('mousemove', zoomPan);
    zoomed.addEventListener('mouseleave', resetZoomOrigin);
}
// Close lightbox
function closeZoom(){
    let overlay = document.getElementById('image-zoom');
    let zoomed = document.getElementById('zoomed-img');
    if(!overlay){
        return;
    }
    overlay.style.display = 'none';
    if(zoomed){
        zoomed.src = '';
        zoomed.style.transformOrigin = 'center center';
        zoomed.removeEventListener('mousemove', zoomPan);
        zoomed.removeEventListener('mouseleave', resetZoomOrigin);
    }
}

// Reviews Start

function toggleReviewCreate() {
    /* toggles the div for creating/updating/deleting a review */
    let createReviewElem = document.getElementById("create-review");
    createReviewElem.hidden = !createReviewElem.hidden;
}

function updateReviewCreate(rating) {
    /* 
        Makes the create review stars responsive. Ex. pressing 3rd star makes all 
        current and previous stars orange 
    */
    let createReviewLabels = document.getElementsByClassName('create-review-label') ;

    for (let i = 1; i <= 5; i++) {
        // gets the <i> elem containing the icon within the label
        let starElem = createReviewLabels[i-1].children[0];
        if (i <= rating) {
            starElem.classList.add("review-star");
            starElem.classList.remove("review-star-gray");
        }
        else {
            starElem.classList.add("review-star-gray");
            starElem.classList.remove("review-star");
        }
    }
}