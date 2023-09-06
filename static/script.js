"use strict";

window.addEventListener("load", function () {
  console.log("JS loaded");

  // Scroll the bot output to the bottom.
  const botUtterances = document.querySelector("#bot-utterances");
  if (botUtterances) {
    botUtterances.scrollTo(0, botUtterances.scrollHeight);
  }
});

function sendRequestWithSid(params) {
  const sid = document.querySelector("input[name='sid']").getAttribute("value");
  params.append("sid", sid);
  let requestUrl = new URL(
    window.location.pathname + "?" + params.toString(),
    window.location.origin
  );
  window.location = requestUrl;
}

function cancelLastTurn() {
  let searchParams = new URLSearchParams();
  searchParams.set("cancel", "Cancel");
  sendRequestWithSid(searchParams);
}

function sendQuery(query) {
  let searchParams = new URLSearchParams();
  searchParams.set("q", query);
  sendRequestWithSid(searchParams);
}
