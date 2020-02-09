const URL = "../my_model/";

let model, labelContainer, maxPredictions;

// Load the image model and setup the webcam
async function initwebcam() {
  const modelURL = URL + "model.json";
  const metadataURL = URL + "metadata.json";

  // load the model and metadata
  // Refer to tmImage.loadFromFiles() in the API to support files from a file picker
  // or files from your local hard drive
  // Note: the pose library adds "tmImage" object to your window (window.tmImage)
  model = await tmImage.load(modelURL, metadataURL);
  maxPredictions = model.getTotalClasses();

  labelContainer = document.getElementById("label-container");
  for (let i = 0; i < maxPredictions; i++) { // and class labels
    labelContainer.appendChild(document.createElement("div"));
  }

  window.requestAnimationFrame(loop);
}

async function loop() {
  await predict();
  window.requestAnimationFrame(loop);
}

// run the webcam image through the image model

async function predict() {
  const name1 = document.getElementById("name1")
  const long1 = document.getElementById("long1")
  const name2 = document.getElementById("name2")
  const long2 = document.getElementById("long2")
  const prediction = await model.predict(video);
  for (let i = 0; i < maxPredictions; i++) {
    // const classPrediction =
    //   prediction[i].className + ": " + prediction[i].probability.toFixed(2);
    // labelContainer.childNodes[i].innerHTML = classPrediction;
    // console.log(classPrediction);
    name1.innerHTML = prediction[0].className
    name2.innerHTML = prediction[1].className
    long1.innerHTML = prediction[0].probability.toFixed(2)
    long2.innerHTML = prediction[1].probability.toFixed(2)
    long1.style.width = "calc(250px * " + prediction[0].probability.toFixed(2) + ")"
    long2.style.width = "calc(250px * " + prediction[1].probability.toFixed(2) + ")"
  }
}