function toggleDebug() {
    let debugContainer = document.getElementsByClassName("debug-container")[0];
    if (debugContainer.classList.contains("js-hidden")) {
        debugContainer.classList.remove('js-hidden');
    } else {
        debugContainer.classList.add('js-hidden');
    }
}