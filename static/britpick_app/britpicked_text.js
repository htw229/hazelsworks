
function toggleExpandedBritpick(ele, britpickPk, show) {

    let paragraph = ele.closest('div.paragraph');
    // paragraph.style.backgroundColor = "red";

    let expandedBP = paragraph.getElementsByClassName('britpick expanded ' + britpickPk)[0];
    let expandBPLinks = paragraph.getElementsByClassName('expand-britpick ' + britpickPk);

    if (show) {
        expandedBP.classList.remove("hidden");
        for (i = 0; i < expandBPLinks.length; i++) {
            expandBPLinks[i].classList.add("hidden");
        }
    } else {
        expandedBP.classList.add("hidden");
        for (i = 0; i < expandBPLinks.length; i++) {
            expandBPLinks[i].classList.remove("hidden");
        }
    }

}

function toggleInlineBritpicks(britpickPk, show) {
    let inlineBPs = document.getElementsByClassName("britpick inline " + britpickPk);
    for (i = 0; i < inlineBPs.length; i++) {
        if (show) {
            inlineBPs[i].classList.remove("hidden");
        } else {
            inlineBPs[i].classList.add("hidden");
        }
    }
}


function toggleSimilar(id) {
    let elems = document.getElementsByClassName(id);
    for (i = 0; i < elems.length; i++) {
        if (elems[i].style.display !== "none") {
            elems[i].style.display = "none";
        } else {
            elems[i].style.display = "";
        }

    }
}


// function showSimilar(id) {
//     let elems = document.getElementsByClassName(id)
//     for (i = 0; i < elems.length; i++) {
//         elems[i].style.display = "";
//     }
// }