var checkboxspeak = document.getElementById("checkbox-botspeak");

checkboxspeak.addEventListener("change", function() {
    if (this.checked) {
        document.getElementById("label-botspeak").innerHTML = "On";
    } else {
        document.getElementById("label-botspeak").innerHTML = "Off";
    }
});