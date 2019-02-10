function selectSampleText() {
    let textbox = document.getElementById("id_text");
    let select = document.getElementById("id_sample_text");
    textbox.value = select.options[select.selectedIndex].value;
}