// State and setup
var running = false;
var canvas;
var domInputArray = [];
var pointList = [(10,10)];

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

function setup() {
  canvas = createCanvas(displayWidth, displayHeight);
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
  readyButton = createButton('Press anywhere to continue');
  readyButton.id("readybutton");
  readyButton.position(0, 0);
  readyButton.mousePressed(init);
}

function init(){

  readyButton.remove();

  running = true;
  startExp(expCount)
}

function startExp(expID){
  fill(255,0,0);
  ellipse(20, 20, 20, 20);
}



function draw() {
  // if (mouseIsPressed) {
  //   fill(0);
  // } else {
  //   fill(255);
  // }
  // ellipse(mouseX, mouseY, 80, 80);
}

function mousePressed() {
  touchTry();
}

function touchStarted() {
  touchTry();
}


function touchTry(){
  if(!running){
    return;
  }
  ellipse(mouseX, mouseY, 80, 80);
}