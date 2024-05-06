/**
 * @fileoverview JS for the swiss bot.
 */

/**
 * Application state.
 */
let cityList = null;
let currentSid = null;
let preferences = null;
let first_query_sent = false;

const ENABLE_SUGGESTION_CARDS = true;
const ORIGIN_VALUE_GENEVA = "Geneva";

window.onload = (event) => {
  setLanguage();
  preferences = parsePreferences();

  if (ENABLE_SUGGESTION_CARDS) {
    setupForm();
  } else {
    sendQuery(getInitialQuery());
  }
};

const ENTER_BUTTON_KEY_CODE = 13;

function submitOnEnter(event) {
  if (event.keyCode === ENTER_BUTTON_KEY_CODE) {
    submitForm(event);
  }
  event.stopPropagation();
}

function toggleFirstQuerySent() {
  first_query_sent = !first_query_sent;
  document.querySelector("#text-find-my-trip").classList.toggle("invisible");
  document.querySelector("#text-modify-suggestions").classList.toggle("invisible");
}

function setupForm() {
  document.querySelector("textarea[name='q']").addEventListener("keydown", submitOnEnter);
}

const INITIAL_CITY_COUNT = 4;
const INVALID_QUERY_ERROR = "INVALID_QUERY";

class CityList {
  constructor(listElement, botState, cities) {
    this.listElement = listElement;
    this.showMoreButton = document.querySelector("#load-more-button");
    this.showMoreButton.onclick = (event) => {
      this.loadMoreCities(4);
    };
    this.botState = botState;
    this.cities = cities;
    this.citiesShown = 0;
    this.pendingItineraryRequests = {};
    this.loadMoreCities(INITIAL_CITY_COUNT);
  }

  loadMoreCities(count) {
    const lastCityShown = this.citiesShown;
    this.citiesShown += count;
    for (
      let i = lastCityShown;
      i < Math.min(this.citiesShown, this.cities.length);
      ++i
    ) {
      this.loadCity(i);
    }
    if (this.citiesShown < this.cities.length) {
      this.showMoreButton.classList.remove("hidden");
    } else {
      this.showMoreButton.classList.add("hidden");
    }
  }

  showPopup(index) {
    const city = this.cities[index];
    const cityOverlay = city.element.querySelector(".overlay");
    cityOverlay.classList.toggle("visible");
    document.querySelector("body").classList.toggle("disabled");
    selectTab(cityOverlay, 0);
    this.cityInPopup = city;
    if (!preferences.disableOnDemandItineraries) {
      this.loadItinerary(index, this.botState.duration);
    }
    this.loadEvents(index);
  }

  loadCity(index) {
    let city = this.cities[index];
    city.element = this.listElement.querySelector(
      `.result-list-item:nth-child(${index + 1})`
    );
    city.element.classList.remove("hidden");
    city.placeContentByQuery = {};

    this.loadSummary(index);
    if (preferences.disableOnDemandItineraries) {
      this.loadItinerary(index, this.botState.duration);
    }

    const onclickHandler = (event) => {
      gtag("event", "select_content", {
        content_type: "click_city",
        content_id: city.name,
      });
      this.showPopup(index);
      event.stopPropagation();
    };
    city.element.querySelector(".tile-splitted").onclick = onclickHandler;
    city.element.querySelector(".popup-link-box").onclick = onclickHandler;
  }

  loadSummary(index) {
    const city = this.cities[index];
    sendRequest("/city_summary", {
      origin: this.botState.origin,
      city: city.name,
      preferences: this.botState.preferences,
    }).then((event) => {
      const xhr = event.target;
      const cityData = JSON.parse(xhr.responseText).city;
      const cityElement = document.querySelector("#city-" + city.id);
      const cityDescription = cityElement.querySelector(".city-description");
      const citySummary = document.createElement("span");
      citySummary.classList.add("city-summary");
      citySummary.innerText = cityData.summary;
      cityDescription.prepend(citySummary);
      cityDescription.querySelector(".loading-box").remove();
    });
  }

  async loadItinerary(index, days) {
    let city = this.cities[index];
    if (city.hasItinerary) {
      return;
    }
    if (!days) {
      days = 3;
    }
    let daySelector = city.element.querySelector("#itinerary-days-select");
    daySelector.value = days;
    daySelector.onchange = (event) => {
      city.hasItinerary = false;
      this.loadItinerary(index, event.target.value);
    };
    city.element
      .querySelectorAll(".itinerary-loading-box")
      .forEach((loadingEl) => {
        loadingEl.removeAttribute("hidden");
      });
    city.element
      .querySelector(".city-itinerary-error")
      .setAttribute("hidden", "true");
    city.element.querySelector(".city-itinerary").innerHTML = "";

    const params = {
      id: city.id,
      preferences: this.botState.preferences,
      num_days: days,
      validation_type: preferences.validationType,
    };
    let existingRequest = this.pendingItineraryRequests[index];
    if (existingRequest) {
      existingRequest.abort();
    }

    city.itineraryQueries = {};
    sendRequest("/city_itinerary", params)
      .then((event) => {
        const xhr = event.target;
        const response = xhr.responseText;
        const ndJsonResponses = response.split("\n");
        for (const jsonResponse of ndJsonResponses) {
          if (!jsonResponse) {
            continue;
          }
          let day_response = JSON.parse(jsonResponse);
          if (day_response.error) {
            populateItineraryError(city.element);
            return;
          }
          day_response.queries.forEach(
            (query) => (city.itineraryQueries[query.id] = query)
          );

          populateItinerary(city.element, day_response.itinerary);
        }
        hideLoadingItinerary(city.element);
        city.loadedItinerary = true;
        this.updatePlaceListeners(city);
      })
      .catch((event) => {
        console.log(event);
        populateItineraryError(city.element);
      });
  }

  updatePlaceListeners(city) {
    city.element.querySelectorAll(".place-item").forEach((placeItem) => {
      placeItem.onclick = (event) => {
        gtag("event", "select_content", {
          content_type: "place",
          content_id: "place",
        });
        onPlaceCardOpened(placeItem, city);
        event.stopPropagation();
      };
    });
  }

  loadEvents(index) {
    const city = this.cities[index];
    sendRequest("/city_events", {
      id: city.id,
      city: city.name,
      country: city.country,
      preferences: this.botState.preferences,
      start_month: this.botState.start_month,
      end_month: this.botState.end_month,
    }).then((event) => {
      const xhr = event.target;
      const response = JSON.parse(xhr.responseText);
      populateEvents(city, response.events);
    });
  }
}

function sendQuery(query) {
  showLoadingResults();
  cancelRequests();
  const urlParams = new URLSearchParams(window.location.search);
  const queryType =  urlParams.get("mdiq") || "default";
  const querySubType = urlParams.get("utm_content") || "default";
  let validation = sendRequest("/validation",
    { q: query, query_type: queryType, query_subtype: querySubType,
  }).then((event) => {
      return isSuccessfulValidation(event)
        ? Promise.resolve()
        : Promise.reject(INVALID_QUERY_ERROR);
  });
  if (ENABLE_SUGGESTION_CARDS && !first_query_sent
      && getOriginValue() == ORIGIN_VALUE_GENEVA ) {
    query += '. ' + getSelectedOriginQuery();
  }

  let swiss = sendRequest("/swiss", { q: query, sid: currentSid});
  if (ENABLE_SUGGESTION_CARDS) {
    document.querySelector("textarea[name='q']").value = "";
    updateFollupUpPlaceHolderText();
    hideSuggestionCards();
  } else {
    document.querySelector("input[name='q']").value = "";
  }


  Promise.all([swiss, validation])
    .then((responses) => {
      onQuerySuccess(responses[0]);
    })
    .catch((error) => {
      console.log(error);
      if (error == INVALID_QUERY_ERROR) {
        displayQueryError(getValidationFailedError());
      } else {
        displayQueryError(getQueryError());
      }
    });
}

function isSuccessfulValidation(event) {
  const xhr = event.target;
  const response = JSON.parse(xhr.responseText);
  return response["is_valid"];
}

function onQuerySuccess(event) {
  if (ENABLE_SUGGESTION_CARDS) {
    if (!first_query_sent) {
      toggleFirstQuerySent();
    }
  }
  const xhr = event.target;
  const response = JSON.parse(xhr.responseText);
  document.querySelector("#bot-response").innerHTML = response.utterance_html;
  document.querySelector("#filters").innerHTML = response.filters_html;
  currentSid = response.sid;
  handleResponse(response.language, response.state);
}

function displayQueryError(error) {
  hideLoadingResults();
  const utteranceEl = document.querySelector(".utterance-bubble");
  utteranceEl.innerHTML = error;
}

function listCities(botState) {
  monthSlider.set(botState.start_month, botState.end_month);
  setOrigin(botState.origin);
  sendRequest(
    "/cities",
    {
      origin: botState.origin,
      preferences: botState.preferences,
      min_price: botState.min_price,
      max_price: botState.max_price,
      region: botState.region,
      duration: botState.duration,
      direct: botState.direct,
    },
    (event) => {
      hideLoadingResults();
    }
  ).then((event) => {
    const xhr = event.target;
    const response = JSON.parse(xhr.responseText);
    if (response.cities.length > 0) {
      const cityListElement = document.querySelector("#cities-container");
      cityListElement.innerHTML = response.html;
      cityList = new CityList(cityListElement, botState, response.cities);
    } else {
      displayQueryError(getCitiesNotFoundError());
    }
  })
  .catch((error) => {
    console.log(error);
    displayQueryError(getCitiesNotFoundError());
  });
}

function showItinerary(botState) {
  monthSlider.set(botState.start_month, botState.end_month);
  sendRequest(
    "/city_lookup",
    {
      cities: [botState.city],
      origin: botState.origin,
    },
    (event) => {
      hideLoadingResults();
    }
  )
    .then((event) => {
      const xhr = event.target;
      const response = JSON.parse(xhr.responseText);
      const cityListElement = document.querySelector("#cities-container");
      cityListElement.innerHTML = response.html;
      if (response.cities) {
        cityList = new CityList(cityListElement, botState, response.cities);
        cityList.showPopup(0);
      }
    })
    .catch((error) => {
      console.log(error);
      displayQueryError(getQueryError());
    });
}

function handleResponse(language, data) {
  monthSlider = setupMonthSlider(language);
  if (data.error) {
    console.log("Backend error: " + data.error);
    return;
  }
  if (!data.intent) {
    return;
  }
  if (data.intent == "list_cities") {
    listCities(data.list_cities);
  } else if (data.intent == "show_itinerary") {
    showItinerary(data.show_itinerary);
  }
}

function submitForm(submitEvent) {
  event.preventDefault();
  const inputText = getInputTextEl();
  const query = inputText.value;
  if (query) {
    sendQuery(query);
  }
}

function getInputTextEl() {
  if (ENABLE_SUGGESTION_CARDS) {
    return document.querySelector("textarea[name='q']");
  } else {
    return document.querySelector("input[name='q']");
  }
}

function onDisclaimerClosed(e) {
  const el = e.target.closest(".disclaimer-overlay");
  el.classList.remove("visible");
  el.classList.add("hidden");
  e.stopPropagation();
}

function onDisclaimerOpened(e) {
  const disclaimerElement = document.querySelector(".disclaimer-overlay");
  disclaimerElement.classList.remove("hidden");
  disclaimerElement.classList.add("visible");
  e.stopPropagation();
}

function hideAllPlaceCards() {
  document.querySelectorAll(".place-card.visible").forEach((el) => {
    el.classList.remove("visible");
    el.classList.add("hidden");
  });

  document.querySelectorAll(".activity-active").forEach((el) => {
    el.classList.remove("activity-active");
  });
}

function onCityPopupClicked(e) {
  hideAllPlaceCards();
  e.stopPropagation();
}

function onPopupCloseClicked(e) {
  hideAllPlaceCards();
  const cityOverlay = e.target.closest(".overlay");
  cityOverlay.classList.remove("visible");
  document.querySelector("body").classList.remove("disabled");
  e.stopPropagation();
}

function onPlaceCardClosedClicked(e) {
  const placeCard = e.target.closest(".place-card");
  placeCard.classList.remove("visible");
  placeCard.classList.add("hidden");

  const activityEl = placeCard.parentNode.querySelector(".activity-active");
  activityEl.classList.remove("activity-active");

  const notFound = placeCard.querySelector(".place-not-found");
  if (notFound) {
    activityEl.classList.remove("itinerary-activity");
  }
  e.stopPropagation();
}

function onTabButtonClicked(e) {
  let index = 0;
  for (const c of e.target.parentNode.children) {
    if (c == e.target) {
      break;
    }
    index++;
  }

  gtag("event", "select_content", {
    content_type: "tab",
    content_id: "tab-" + index,
  });

  const cityOverlay = e.target.closest(".overlay");
  selectTab(cityOverlay, index);
  e.stopPropagation();
}

function selectTab(overlayElement, index) {
  overlayElement
    .querySelectorAll(".selected")
    .forEach((el) => el.classList.remove("selected"));

  const buttonContainer = overlayElement.querySelector(".tab-button-container");
  const button = buttonContainer.querySelectorAll(".tab-button")[index];
  button.classList.add("selected");

  const tabContainer = overlayElement.querySelector(".tab-container");
  const tab = tabContainer.querySelectorAll(".tab")[index];
  tab.classList.add("selected");
}

function setOrigin(origin) {
  if (origin) {
    document.querySelector("#origin-select").value = origin;
  }
}

function originChanged() {
  gtag("event", "select_content", {
    content_type: "origin_changed",
    content_id: "origin_changed",
  });
  if (first_query_sent) {
    sendQuery(getSelectedOriginQuery());
  } else {
    const origin = getOriginValue();
    const zurichCards = document.querySelector(".suggestion-cards-zurich");
    const genevaCards = document.querySelector(".suggestion-cards-geneva");
    if (origin == 'Geneva') {
      genevaCards.classList.remove("hidden");
      zurichCards.classList.add("hidden");
    } else {
      genevaCards.classList.add("hidden");
      zurichCards.classList.remove("hidden");
    }
  }
}

function getOriginValue() {
  const originSelect = document.querySelector("#origin-select");
  return originSelect.options[originSelect.selectedIndex].value;
}

function getSelectedOriginQuery() {
  const originSelect = document.querySelector("#origin-select");
  const textValue = originSelect.options[originSelect.selectedIndex].text;
  return getOriginQuery(textValue);
}

function parsePreferences() {
  const urlParams = new URLSearchParams(window.location.search);
  let preferences = {};
  preferences.disableItineraries = urlParams.has("disable_itineraries");
  // Expected values: [basic|advanced|none], if not provided displays default
  // behavior.
  preferences.validationType = urlParams.get("itinerary_validation");
  preferences.disableOnDemandItineraries = urlParams.has(
    "disable_ondemand_itineraries"
  );
  preferences.disableEvents = urlParams.has("disable_events");
  return preferences;
}

function resetItineraryList(cityElement) {
  const cityItinerary = cityElement.querySelector(".city-itinerary");
  cityItinerary.innerHTML += "";
}

function populateItinerary(cityElement, html) {
  const itineraryError = cityElement.querySelector(".city-itinerary-error");
  itineraryError.setAttribute("hidden", "true");
  const cityItinerary = cityElement.querySelector(".city-itinerary");
  cityItinerary.innerHTML += html;
}

function hideLoadingItinerary(cityElement) {
  cityElement
    .querySelectorAll(".itinerary-loading-box")
    .forEach((loadingBox) => {
      loadingBox.setAttribute("hidden", "true");
    });
}

function populateItineraryError(cityElement) {
  cityElement
    .querySelectorAll(".itinerary-loading-box")
    .forEach((loadingBox) => {
      loadingBox.setAttribute("hidden", "true");
    });
  const itineraryError = cityElement.querySelector(".city-itinerary-error");
  itineraryError.removeAttribute("hidden");
}

function populateEvents(city, html) {
  const cityElement = document.querySelector("#city-" + city.id);
  const loadingBox = cityElement.querySelector(".events-loading-box");
  if (loadingBox) {
    loadingBox.setAttribute("hidden", "true");
  }
  const cityEvents = cityElement.querySelector(".city-events");
  cityEvents.innerHTML = html;
  const eventItem = cityEvents.querySelector(".event-item");
  if (!eventItem) {
    console.log("Did not find events for " + city.name + ", hiding tab");
  } else {
    showEventsTab(city.id);
    console.log("got events for city: " + city.name);
  }
}

function showEventsTab(cityId) {
  const cityElement = document.querySelector("#city-" + cityId);
  cityElement
    .querySelector("#events-tab-header")
    .classList.remove("tab-no-results");
}

function onPlaceCardOpened(placeCardEl, city) {
  showPlaceCard(placeCardEl);
  let query = placeCardEl.innerText.trim();
  let placeCardId = placeCardEl.id;
  let floatingCard = placeCardEl.parentNode.querySelector(
    ".place-floating-card"
  );

  // If validation is enabled there might be a place_id already fetched.
  let itineraryQuery = city.itineraryQueries[placeCardId];
  const placeId = itineraryQuery ? itineraryQuery["place_id"] : null;
  if (city.placeContentByQuery[query]) {
    floatingCard.innerHTML = city.placeContentByQuery[query];
  } else {
    sendRequest("/places", {
      queries: [{ query: query, place_id: placeId }],
      city_id: city.id,
    }).then((event) => {
      const xhr = event.target;
      floatingCard.innerHTML = xhr.responseText;
      city.placeContentByQuery[query] = xhr.responseText;
    });
  }
}

function showPlaceCard(placeCardEl) {
  hideAllPlaceCards();
  placeCardEl.classList.add("activity-active");
  let placeDetails = placeCardEl.parentNode.querySelector(
    ".place-floating-card"
  );
  placeDetails.classList.remove("hidden");
  placeDetails.classList.add("visible");
}

function populatePlaces(cityElement, html) {
  const placesElement = document.createElement("div");
  placesElement.innerHTML = html;
  placesElement
    .querySelectorAll(".place-card-container")
    .forEach((placeContainer) => {
      placeCard = placeContainer.querySelector(".place-card");
      let placeCardId = placeCard.id;
      const placeTextId = placeCardId.replace("place-", "");
      const textEl = document.querySelector("#" + placeTextId);
      if (textEl) {
        textEl.classList.add("itinerary-activity");
        textEl.innerHTML = textEl.innerHTML + placeContainer.innerHTML;
      } else {
        console.log("Did not find place element for id: " + placeTextId);
      }
    });

  cityElement.querySelectorAll(".loading-activity").forEach((el) => {
    el.remove();
  });
  cityElement.querySelectorAll(".place-loading-text").forEach((el) => {
    el.remove();
  });
}

function languageChanged() {
  reload({ l: document.querySelector("#language-select").value });
}

function setLanguage() {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has("l")) {
    const language = urlParams.get("l");
    let languageSelect = document.querySelector("#language-select");
    languageSelect.value = language;
  }
}

function onShowFiltersClick() {
  const showFiltersArrow = document.querySelector("#show-filters-arrow");
  const filtersSection = document.querySelector(".df-filters-section");
  showFiltersArrow.classList.toggle("down");
  showFiltersArrow.classList.toggle("up");
  filtersSection.classList.toggle("show");

  document.querySelectorAll(".filters-button").forEach((el) => {
    el.classList.toggle("show");
    el.classList.toggle("remove");
  });
}

function onBookClicked(url) {
  gtag("event", "select_content", {
    content_type: "book",
    content_id: url,
  });
  window.open(url, '_blank');
}

function getQueryError() {
  return document.querySelector("#metadata-query-error").innerHTML;
}

function getInitialQuery(cohort) {
  const urlParams = new URLSearchParams(window.location.search);
  const queryType =  urlParams.get("mdiq") || "default";
  return document.querySelector(`#mdiq-${queryType}`).innerHTML;
}

function getUserProfile() {
  const urlParams = new URLSearchParams(window.location.search);
  return  urlParams.get("profile") || "default";
}

function getValidationFailedError() {
  return document.querySelector("#metadata-invalid-query").innerHTML;
}

function getCitiesNotFoundError() {
  return document.querySelector("#metadata-cities-not-found").innerHTML;
}

function getOriginQuery(origin) {
  return document
    .querySelector("#metadata-origin-query")
    .innerHTML.replace("${origin}", origin);
}

function getMonthQuery(minMonth, maxMonth) {
  return document
    .querySelector("#metadata-month-query")
    .innerHTML.replace("${minMonth}", minMonth)
    .replace("${maxMonth}", maxMonth);
}

function getRemovePreferenceQuery(preference) {
  return document
    .querySelector("#metadata-remove-preference-query")
    .innerHTML.replace("${preference}", preference);
}

function getRemoveRegionQuery(region) {
  return document
    .querySelector("#metadata-remove-region-query")
    .innerHTML.replace("${region}", region);
}

function hideSuggestionCards() {
  document.querySelector("#suggestion-cards-section").classList.add("hidden");
}

function updateFollupUpPlaceHolderText() {
  const textArea = document.querySelector("textarea[name='q']");
  const followupPlaceholder =
  document.querySelector("#metadata-placeholder-follow-up").innerHTML;
  textArea.placeholder = followupPlaceholder;
}

function onSuggestionCardClicked(query) {
  const textArea = document.querySelector("textarea[name='q']");
  textArea.value = query;
  textArea.focus();
}
