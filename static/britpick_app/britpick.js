window.onload = load;


function load() {
    let sampleSelect = document.getElementById("id_sample_text");
    sampleSelect.addEventListener("change", selectSampleText);


    let paragraphs = document.getElementsByClassName("britpick-paragraph");
    for (let i = 0; i < paragraphs.length; i++) {
        paragraphs[i].addEventListener("click", function (event) {
            if (event.target.closest(".inline-britpick")) return;
            if (event.target.closest(".expanded-britpick")) return;
            resetBritpickClicks();
        });
    }
}



