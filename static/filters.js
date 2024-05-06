/**
 * @fileoverview Sets up and manages controls for filters.
 */

class RangeSlider {
  constructor(sliderId, valueFormatter, queryGenerator, valueTransformer) {
    this.sliderId = sliderId;
    this.leftSlider = document.getElementById("slider-left");
    this.rightSlider = document.getElementById("slider-right");
    this.displayValLeft = document.getElementById("range-left");
    this.displayValRight = document.getElementById("range-right");
    this.sliderTrack = document.getElementById("slider-track");
    this.valueFormatter = valueFormatter;
    this.queryGenerator = queryGenerator;
    this.valueTransformer = valueTransformer;

    this.leftSlider.oninput = () => this.slideLeft();
    this.rightSlider.oninput = () => this.slideRight();
    this.leftSlider.onmouseup = () => this.onChanged();
    this.rightSlider.onmouseup = () => this.onChanged();
    // For mobile browsers
    this.leftSlider.ontouchend = () => this.onChanged();
    this.rightSlider.ontouchend = () => this.onChanged();
    this.updateTrack();
  }

  updateTrack(){
    let sliderMaxValue = this.leftSlider.max;

    let percent1 = (this.leftSlider.value / sliderMaxValue) * 100;
    let percent2 = (this.rightSlider.value / sliderMaxValue) * 100;
    this.sliderTrack.style.background = `linear-gradient(to right, #C6C6C6 ${percent1}% , #c00 ${percent1}% , #c00 ${percent2}%, #C6C6C6 ${percent2}%)`;
  }

  slideLeft(){
    if(parseInt(this.rightSlider.value) - parseInt(this.leftSlider.value) <= 0){
      this.leftSlider.value = parseInt(this.rightSlider.value);
    }
    this.displayValLeft.textContent = this.valueFormatter(this.leftSlider.value);
    this.updateTrack();
  }

  slideRight(){
    if(parseInt(this.rightSlider.value) - parseInt(this.leftSlider.value) <= 0){
      this.rightSlider.value = parseInt(this.leftSlider.value);
    }
    this.displayValRight.textContent = this.valueFormatter(this.rightSlider.value);
    this.updateTrack();
  }

  onChanged() {
    const min = this.leftSlider.value;
    const max = this.rightSlider.value;
    console.log(`Value of slider ${this.sliderId} changed to ${min} - ${max}`);
    sendQuery(this.queryGenerator(min, max));
  }

  set(minValue, maxValue) {
    if (minValue) {
      this.leftSlider.value = this.valueTransformer(minValue);
      this.slideLeft();
    }
    if (maxValue) {
      this.rightSlider.value = this.valueTransformer(maxValue);
      this.slideRight();
    }
    this.updateTrack();
  }
}


function setupMonthSlider(language) {
  const slider = new RangeSlider(
    "#month-range-slider",
    (value) => getMonthName(language, value),
    (minMonth, maxMonth) =>
      getMonthQuery(
        getMonthName(language, minMonth),
        getMonthName(language, maxMonth)
      ),
    (value) => {
      let mappedValue = value - new Date().getMonth() - 1;
      mappedValue = mappedValue >= 0 ? mappedValue : 12 + mappedValue;
      return mappedValue;
    }
  );
  window.onresize = function(event) {
    setupMonthSlider(language);
  };
  return slider;
}

function getMonthName(language, value) {
  let currentDate = new Date();
  var month = (currentDate.getMonth() + parseInt(value)) % 12;
  let firstDayInMonth = new Date();
  firstDayInMonth.setDate(1);
  firstDayInMonth.setMonth(month);
  return new Intl.DateTimeFormat(language, { month: "long" }).format(
    firstDayInMonth
  );
}

