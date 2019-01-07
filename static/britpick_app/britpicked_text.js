function toggleBritpick(id) {

    let inlineBP = document.getElementById('inline-bp-' + id);
    let toggleBP = document.getElementById('toggle-bp-' + id);
    let expandedBP = document.getElementById('expanded-bp-' + id);

    if (expandedBP.style.display !== "none") {
        expandedBP.style.display = "none";
        toggleBP.style.display = "";
        // toggleBP.classList.remove("expanded");
    } else {
        expandedBP.style.display = "inline-block";
        toggleBP.style.display = "none";
        // toggleBP.classList.add("expanded");
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