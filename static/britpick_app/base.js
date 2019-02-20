var classVisibilityDict = {};

function toggleClassVisibility(className) {
    let elems = document.getElementsByClassName(className);

    console.log('toggleClassVisibility: ' + className);

    if (!(className in classVisibilityDict) || (classVisibilityDict[className] === true)) {
        classVisibilityDict[className] = false;
    } else {

        classVisibilityDict[className] = true;
    }

    console.log('show: ' + classVisibilityDict[className]);

    for (let i = 0; i < elems.length; i++) {
        if (classVisibilityDict[className] === true) {
            let keepHidden = false;
            for (let j = 0; j < elems[i].classList.length; j++) {
                console.log('other class: ' + elems[i].classList.item(j));
                console.log('classVisibilityDict[elems[i].classList.item(j)] ' + classVisibilityDict[elems[i].classList.item(j)]);
                if (classVisibilityDict[elems[i].classList.item(j)] === false) {
                    keepHidden = true;
                }
            }

            console.log('keepHidden: ' + keepHidden);

            if (elems[i].classList.contains('js-toggle-opposite')) {
                elems[i].classList.add('js-hidden');
            } else if (!keepHidden) {
                elems[i].classList.remove('js-hidden');
            }
        } else {
            if (elems[i].classList.contains('js-toggle-opposite')) {
                elems[i].classList.remove('js-hidden');
            } else {
                elems[i].classList.add('js-hidden');
            }
        }
    }



}