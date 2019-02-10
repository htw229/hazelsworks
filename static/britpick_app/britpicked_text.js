

function toggleExpandedBritpick(ele, britpickPK, show) {

    let paragraph = ele.closest('div.britpick-paragraph');

    let expandedBritpick = paragraph.getElementsByClassName('expanded-britpick ' + britpickPK)[0];
    let expandButtons = paragraph.getElementsByClassName('inline-britpick-open-expanded ' + britpickPK);

    if (show) {
        expandedBritpick.classList.remove("js-hidden");
        for (let i = 0; i < expandButtons.length; i++) {
            expandButtons[i].classList.add("js-hidden");
        }
    } else {
        expandedBritpick.classList.add("js-hidden");
        for (let i = 0; i < expandButtons.length; i++) {
            expandButtons[i].classList.remove("js-hidden");
        }
    }

}

function expandAllBritpicks() {
    let expandedBritpicks = document.getElementsByClassName('expanded-britpick');
    for (let i = 0; i < expandedBritpicks.length; i++) {
        expandedBritpicks[i].classList.remove("js-hidden");
    }
}

function collapseAllBritpicks() {
    let expandedBritpicks = document.getElementsByClassName('expanded-britpick');
    for (let i = 0; i < expandedBritpicks.length; i++) {
        expandedBritpicks[i].classList.add("js-hidden");
    }
}

function clickParagraph(elem, pk) {

}


function clickInlineBritpick(elem, pk) {
    toggleBritpickClicks(pk);

    // let p = getParagraphContainer(elem);
    // let inlineBPs = p.getElementsByClassName("inline-britpick " + pk);
    // addClass(inlineBPs, "js-clicked");
    // let expandedBPs = p.getElementsByClassName("expanded-britpick " + pk);
    // addClass(expandedBPs, "js-clicked");
}

function clickExpandedBritpick(elem, pk) {
    toggleBritpickClicks(pk);

    // let p = getParagraphContainer(elem);
    // let inlineBPs = p.getElementsByClassName("inline-britpick " + pk);
    // addClass(inlineBPs, "js-clicked");
    // let expandedBPs = p.getElementsByClassName("expanded-britpick " + pk);
    // addClass(expandedBPs, "js-clicked");
}







function getParagraphContainer(elem) {
    return elem.closest('div.britpick-paragraph');
}


function toggleBritpickClicks(pk) {
    resetBritpickClicks();

    let inlineBPs = document.getElementsByClassName("inline-britpick " + pk);
    toggleClass(inlineBPs, "js-clicked");
    let expandedBPs = document.getElementsByClassName("expanded-britpick " + pk);
    toggleClass(expandedBPs, "js-clicked");
}


function toggleBritpickHighlights(pk) {
    resetBritpickHighlights();

    let inlineBPs = document.getElementsByClassName("inline-britpick " + pk);
    toggleClass(inlineBPs, "js-highlight");
    let expandedBPs = document.getElementsByClassName("expanded-britpick " + pk);
    toggleClass(expandedBPs, "js-highlight");
}

function resetBritpickHighlights() {
    let inlineBPs = document.getElementsByClassName("inline-britpick");
    removeClass(inlineBPs, "js-highlight");
    let expandedBPs = document.getElementsByClassName("expanded-britpick");
    removeClass(expandedBPs, "js-highlight");
}

function resetBritpickClicks() {
    let inlineBPs = document.getElementsByClassName("inline-britpick");
    removeClass(inlineBPs, "js-clicked");
    let expandedBPs = document.getElementsByClassName("expanded-britpick");
    removeClass(expandedBPs, "js-clicked");
}



function toggleInlineBritpicks(britpickPK, show) {
    let inlineBPs = document.getElementsByClassName("britpick inline " + britpickPK);
    for (let i = 0; i < inlineBPs.length; i++) {
        if (show) {
            inlineBPs[i].classList.remove("js-hidden");
        } else {
            inlineBPs[i].classList.add("js-hidden");
        }
    }
}

// mouseover inline britpick -> toggle highlights on, show text ("click to expand")
// mouseout inline britpick -> toggle highlights off (if unclicked)

// click on inline britpick -> toggle expanded and toggle highlights

// click not anywhere -> toggle highlights off

// mouseover expanded britpick -> toggle highlights on
// mouseout expanded britpick -> toggle highlights off (if unclicked)

// click on expanded britpick -> toggle highlights
// click on expanded britpick togglebar -> hide expanded and toggle highlights off



//

function toggleBritpickHighlight(ele, britpickPK, toggle=true, highlight=true, clicked=false) {
    let paragraph = ele.closest('div.britpick-paragraph');

    let expandedBritpicks = paragraph.getElementsByClassName('expanded-britpick ' + britpickPK);
    toggleClass(expandedBritpicks, "js-highlight", toggle, highlight);

    let inlineBritpicks = paragraph.getElementsByClassName('inline-britpick ' + britpickPK);
    toggleClass(inlineBritpicks, "js-highlight");
}


function toggleBritpickClickHighlight(elem, pk) {
    let paragraph = elem.closest('div.britpick-paragraph');
    let expandedBritpicks = paragraph.getElementsByClassName('expanded-britpick ' + britpickPK);

    if (expandedBritpicks[0].classList.contains("js-clicked")) {

    }


}

function toggleBritpickMouseoverHighlight(elem, pk, showhighlight) {

}

function addClass(elems, classname) {
    for (let i = 0; i < elems.length; i++) {
        elems[i].classList.add(classname);
    }
}

function removeClass(elems, classname) {
    for (let i = 0; i < elems.length; i++) {
        elems[i].classList.remove(classname);
    }
}

function toggleClass(elems, classname) {
    for (let i = 0; i < elems.length; i++) {
        elems[i].classList.toggle(classname);
    }
}

// function toggleClass(elems, classname, toggle=true, addclass, removeclass) {
//     for (let i = 0; i < elems.length; i++) {
//         if (toggle === true) {
//             elems[i].classList.toggle(classname);
//         } else if (addclass === true) {
//             elems[i].classList.add(classname);
//         } else if (removeclass === true) {
//             elems[i].classList.remove(classname);
//         }
//
//     }
// }

function toggleSimilar(id) {
    let elems = document.getElementsByClassName(id);
    for (let i = 0; i < elems.length; i++) {
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