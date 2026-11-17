// Loads the mascot image from a handful of small binary parts and
// stitches them back into one WebP image in the browser, then points
// every .brainbox-mascot <img> at it.
//
// Why: the full-resolution mascot file is split into several small
// files on disk (images/mascot-parts/) purely as a workaround for how
// this project's files were transferred during development. This
// script reassembles them client-side; nothing about this affects
// end users or requires any build step.
(function () {
  "use strict";

  var PARTS = [
    "images/mascot-parts/part0.bin",
    "images/mascot-parts/part1.bin",
    "images/mascot-parts/part2.bin",
    "images/mascot-parts/part3.bin",
    "images/mascot-parts/part4.bin",
    "images/mascot-parts/part5.bin",
    "images/mascot-parts/part6.bin"
  ];

  function loadMascot() {
    var targets = document.querySelectorAll(".brainbox-mascot");
    if (!targets.length) return;

    Promise.all(
      PARTS.map(function (url) {
        return fetch(url).then(function (res) {
          if (!res.ok) throw new Error("Failed to fetch " + url);
          return res.arrayBuffer();
        });
      })
    )
      .then(function (buffers) {
        var totalLength = buffers.reduce(function (sum, b) {
          return sum + b.byteLength;
        }, 0);
        var merged = new Uint8Array(totalLength);
        var offset = 0;
        buffers.forEach(function (b) {
          merged.set(new Uint8Array(b), offset);
          offset += b.byteLength;
        });

        var blob = new Blob([merged], { type: "image/webp" });
        var url = URL.createObjectURL(blob);
        targets.forEach(function (img) {
          img.src = url;
        });
      })
      .catch(function (err) {
        // Fail quietly -- the page still works without the mascot image.
        console.error("Mascot image failed to load:", err);
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadMascot);
  } else {
    loadMascot();
  }
})();
