"use strict";

window.addEventListener("load", function () {
  console.log("JS loaded");

  // Scroll the bot output to the bottom.
  const botUtterances = document.querySelector("#bot-utterances");
  if (botUtterances) {
    botUtterances.scrollTo(0, botUtterances.scrollHeight);
  }
});

// Maintains a list of all XHRs that are currently in flight.
let inflightXHRs = new Set();

function sendRequest(
  path,
  args,
  cleanupCallback
) {
  let urlParams = new URLSearchParams(window.location.search);
  const requestUrl = new URL(path + "?" + urlParams, window.location.origin);
  const xhr = new XMLHttpRequest();
  inflightXHRs.add(xhr);

  return new Promise(function (resolve, reject) {
    xhr.open("POST", requestUrl, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    if (!reject) {
      reject = (event) => {
        console.log(
          `Failed request to ${path} with ${JSON.stringify(args)}. Status: ${
            event.target.status
          }`
        );
      };
    }
    xhr.onload = (event) => {
      const xhr = event.target;
      if (xhr.status == 0 || (xhr.status >= 200 && xhr.status < 400)) {
        resolve(event);
      } else {
        reject(event);
      }
    };
    xhr.onerror = reject;
    xhr.onloadend = (event) => {
      if (cleanupCallback) {
        cleanupCallback(event);
      }
      inflightXHRs.delete(event.target);
    };
    xhr.send(JSON.stringify(args));
  });
}

function cancelRequests() {
  inflightXHRs.forEach((xhr) => xhr.abort());
  inflightXHRs.clear();
}

function reload(searchParams) {
  let params = new URLSearchParams(window.location.search);
  for (const [key, value] of Object.entries(searchParams)) {
    params.set(key, value);
  }
  window.location = new URL(
    window.location.pathname + "?" + params.toString(),
    window.location.origin
  );
}

// Hide header on scroll.
var scrollPosition = window.pageYOffset;
window.onscroll = function () {
  var currentPos = window.pageYOffset;
  let header = document.querySelector("header");
  if (scrollPosition > currentPos) {
    header.style.top = "0";
  } else if (currentPos > document.querySelector("header").offsetHeight) {
    header.style.top = "-120px";
  }
  scrollPosition = currentPos;
};

function showLoadingResults() {
  document.querySelector("#results-loading").classList.remove("hidden");
}

function hideLoadingResults() {
  document.querySelector("#results-loading").classList.add("hidden");
}

function onResetClicked() {
  window.location.href = "";
  toggleFirstQuerySent();
}
