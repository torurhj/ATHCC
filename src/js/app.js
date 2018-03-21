// State and setup
var running = false;
var canvas;
var domInputArray = [];
var pointList = [];
var inTouch = false;
var randPoints = 70;
var delaybetween = 400;

// input data
var inputName;
var inputAge;
var inputGender;
var inputThumb;
var inputHand;

// state data
var timeStart;
var timeEnd;
var targetX;
var targetY;
var touchX;
var touchY;
var expCount = 0;


var dspWidth;
var dspHeight;


// var fs=false;
// document.addEventListener('touchmove', function (event) {
//   if (event.scale !== 1) { event.preventDefault(); }
// }, false);

var tblock = function (e) {
    if (e.touches.length > 1) {
        e.preventDefault()
    }

    return false;
}

document.addEventListener("touchmove", tblock, true);

// var lastTouchEnd = 0;
// document.addEventListener('touchend', function (event) {
//   var now = (new Date()).getTime();
//   if (now - lastTouchEnd <= 300) {
//     event.preventDefault();
//   }
//   lastTouchEnd = now;
// }, false);

function getRandomArbitrary(min, max) {
    return Math.random() * (max - min) + min;
}

function initArray(){
  // insert 2 normal points
  var xMax = dspWidth;
  var yMax = dspHeight;
  // alert(xMax);
  // alert(window.innerWidth);
  var x_grid = [
    0,
    Math.floor(xMax*(1/5)),
    Math.floor(xMax*(2/5)),
    Math.floor(xMax*(3/5)),
    Math.floor(xMax*(4/5)),
    ];
  var y_grid = [0,
    Math.floor(yMax*(1/9)),
    Math.floor(yMax*(2/9)),
    Math.floor(yMax*(3/9)),
    Math.floor(yMax*(4/9)),
    Math.floor(yMax*(5/9)),
    Math.floor(yMax*(6/9)),
    Math.floor(yMax*(7/9)),
    Math.floor(yMax*(8/9)),
    ];
  for (var xc = 0; xc < x_grid.length; xc++) {
    for (var yc = 0; yc < y_grid.length; yc++) {
      pointList.push(
        {x:Math.floor(x_grid[xc] + (xMax * (1/5)/2))
        ,y:Math.floor(y_grid[yc] + (yMax * (1/9)/2))})
    }
  }

  for (var x = 0; x < randPoints; x++) {
    pointList.push(
        {x:getRandomArbitrary(0,dspWidth)
        ,y:getRandomArbitrary(0,dspHeight)})
  }
}

function setup() {
  dspWidth = displayWidth ;//* displayDensity();
  dspHeight = displayHeight;// * displayDensity();
  initArray();
  canvas = createCanvas(dspWidth, dspHeight);
  canvas.parent('sketch-holder');
  // Name input -------------------------

  textName = createElement('h1', 'Name:');
  textName.position(20, 5);

  inputName = createInput();
  inputName.position(20, textName.y+textName.height);
  domInputArray.push(textName,inputName)

  // Age input ---------------------------
  textAge = createElement('h1', 'Age:');
  textAge.position(20, inputName.y+inputName.height);

  inputAge = createInput([0],['number']);
  inputAge.position(20, textAge.y+textAge.height);
  domInputArray.push(textAge,inputAge)

  // Gender input ---------------------------
  textGender = createElement('h1', 'Gender:');
  textGender.position(20, inputAge.y+inputAge.height);

  inputGender = createSelect();
  inputGender.position(20, textGender.y+textGender.height);
  inputGender.option('Man');
  inputGender.option('Woman');
  domInputArray.push(textGender,inputGender)

  // Thumblenght input ---------------------------
  textThumb = createElement('h1', 'Thumb size:');
  textThumb.position(20, inputGender.y+inputGender.height);

  inputThumb = createInput([0],['number']);
  inputThumb.position(20, textThumb.y+textThumb.height);
  domInputArray.push(textThumb,inputThumb)

  // prefered hand input ---------------------------
  textHand = createElement('h1', 'Preferred hand:');
  textHand.position(20, inputThumb.y+inputThumb.height);

  inputHand = createSelect();
  inputHand.position(20, textHand.y+textHand.height);
  inputHand.option('Left');
  inputHand.option('Right');
  domInputArray.push(textHand,inputHand)


  submitButton = createButton('submit');
  submitButton.position(40, inputHand.y+inputHand.height+ 20);
  submitButton.mousePressed(getReady);
  domInputArray.push(submitButton)

  fillscreenButton = createButton('Set fullscreen');
  fillscreenButton.position(40, submitButton.y+submitButton.height+ 20);
  fillscreenButton.mousePressed(fullscreen);
  domInputArray.push(fillscreenButton)
}

function getReady(){
  var arrayLength = domInputArray.length;
  for (var i = 0; i < arrayLength; i++) {
    domInputArray[i].remove();
    //Do something
  }
  setTimeout(function() {
    readyButton = createButton('Press anywhere to continue');
    readyButton.id("readybutton");
    readyButton.position(0, 0);
    readyButton.mousePressed(initExp);
    }, 200);
}

function initExp(){
  setTimeout(function() {
    readyButton.remove();
    running = true;
    startExp(expCount);
    }, delaybetween);
}

function startExp(expID){
  if (pointList.length <= expID){
    running = false;
    textSize(28);
    text('Thank you for participating', 10, 300);
    fill(0, 102, 153);
    return;
  }
  targetX = pointList[expID].x;
  targetY = pointList[expID].y;
  timeStart = Date.now();
  fill(255,0,0);
  ellipse(targetX, targetY, 10, 10);
}

function endExp(expID){
  touchX = mouseX;
  touchY = mouseY;
  timeEnd = Date.now();
  expCount++;
  clear();
  sendData();
  setTimeout(function() { startExp(expCount)}, delaybetween);
}


function sendData(){
  $.ajax({
    type: "POST",
    data:
      {touchX:Math.floor(touchX),
       touchY:Math.floor(touchY),
       targetX:Math.floor(targetX),
       targetY:Math.floor(targetY),
       timeStart:timeStart,
       timeEnd:timeEnd,
       expID:expCount,
       totalX: dspWidth,
       totalY: dspHeight,
       name:inputName.value(),
       age:inputAge.value(),
       hand:inputHand.value(),
       thumb:inputThumb.value(),
       gender:inputGender.value()
      },
    url: "submit.php",
    success: function(data){
      // alert(data);
  }});
}

function touchStarted() {
  touchTry();
  if(running){
    return false;
  }
}



function touchTry(){
  if(!running){
    return;
  }
  endExp(expCount)
}




// function sleep(milliseconds) {
//   var start = new Date().getTime();
//   for (var i = 0; i < 1e7; i++) {
//     if ((new Date().getTime() - start) > milliseconds){
//       break;
//     }
//   }
// }