(function () {
    var listener = function () {
        Array.prototype.forEach.call(document.getElementsByTagName("VIDEO"), function (video) {
            if (video.hasAttribute("autoplay") && video.paused) {
                video.play();
            }
        });
        document.removeEventListener("mousedown", listener, false);
    };
    document.addEventListener("DOMContentLoaded", function() {
        document.addEventListener("mousedown", listener, false);
    }, false);
})();