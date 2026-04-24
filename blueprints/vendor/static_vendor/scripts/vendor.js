const parser = new DOMParser();

const specElem = document.getElementById("vendor-specs");
const colorElem = document.getElementById("vendor-colors");
const imageElem = document.getElementById("vendor-images");

const specHTML = specElem.children[1].outerHTML;
const colorHTML = colorElem.children[0].outerHTML;
const imageHTML = imageElem.children[1].outerHTML;


function addElem(elem, html) {
    // Function to add an element to a html field
    // e.g. addElem(specElem, specHTML) to add to the specElem
    let child = parser.parseFromString(html, 'text/html').body.firstChild;
    elem.append(child);
}