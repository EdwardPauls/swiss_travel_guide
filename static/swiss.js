/**
 * @fileoverview JS for the swiss bot.
 */

window.onload = (event) => {
  if (!data) {
    return;
  }
  for (const city of data.cities) {
    args = {
        origin : data.origin,
        destinations : [city.name],
        preferences : data.preferences,
    };
    sendRequest(
      SUMMARY_BACKEND,
      args,
      (event) => {
        const xhr = event.target;
        createCitySummary(city.id, JSON.parse(xhr.responseText).cities[0]);
      },
      (event) => {
        console.log("Failed summary request for " + city.name);
      }
    );
    sendRequest(
      CARDS_BACKEND,
      args,
      (event) => {
        const xhr = event.target;
        createCityCards(city.id, JSON.parse(xhr.responseText).locations);
      },
      (event) => {
        console.log("Failed summary request for " + city.name);
      }
    );
  }
}

function sendRequest(backend, args, successCallback, errorCallback) {
  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/proxy', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.onload = successCallback;
  xhr.onerror = errorCallback;
  xhr.send(JSON.stringify({
    backend : backend,
    args : args
  }));
}

function createCitySummary(cityId, cityData) {
  const cityElement = document.querySelector('#city-' + cityId);
  const citySummary = document.createElement('div');
  citySummary.setAttribute('class', 'city-summary');
  citySummary.appendChild(document.createTextNode(cityData.summary));
  cityElement.prepend(citySummary); // Has to be the first child.

  // Remove the spinner and add the new nodes.
  document.querySelector('#spinner-' + cityId).remove();
}

function createCityCards(cityId, cards) {
  if (!cards) {
    return;
  }

  const cityElement = document.querySelector('#city-' + cityId);
  const cityCardList = document.createElement('div');
  cityCardList.setAttribute('class', 'city-card-list');

  const cityCardListTitle = document.createElement('span');
  cityCardListTitle.setAttribute('class', 'city-card-list-title');
  cityCardListTitle.appendChild(document.createTextNode('Locations'));

  for (const card of cards) {
    const cityCard = document.createElement('div');
    cityCard.setAttribute('class', 'city-card');

    const cityCardName = document.createElement('div');
    cityCardName.setAttribute('class', 'city-card-name');
    cityCardName.appendChild(document.createTextNode(card.name));
    cityCard.appendChild(cityCardName);

    if (card.image) {
      const cityCardImage = document.createElement('img');
      cityCardImage.setAttribute('class', 'city-card-image');
      cityCardImage.setAttribute('src', 'data:image/png;base64,' + card.image);
      cityCard.appendChild(cityCardImage);
    }

    if (card.text) {
      const cityCardText = document.createElement('div');
      cityCardText.setAttribute('class', 'city-card-text');
      cityCardText.appendChild(document.createTextNode(card.text));
      cityCard.appendChild(cityCardText);
    }

    cityCardList.appendChild(cityCard);
  }
  cityElement.appendChild(cityCardList);
}

function originChanged() {
  const originSelect = document.querySelector('#origin-select');
  const selectedIndex = originSelect.selectedIndex;
  const origin = originSelect.options[selectedIndex].text;
  sendQuery('I am traveling from ' + origin);
}
