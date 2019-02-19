function toggleClassVisibility(className) {
    let elems = document.getElementsByClassName(className);
    for (let i = 0; i < elems.length; i++) {
        if (elems[i].classList.contains("js-hidden")) {
            elems[i].classList.remove('js-hidden');
        } else {
            elems[i].classList.add('js-hidden');
        }
    }
}