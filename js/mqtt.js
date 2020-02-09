var wsbroker = "192.168.123.45";  //mqtt websocket enabled brokers
var wsport = 1884; // or for above

var client = new Paho.MQTT.Client(wsbroker, wsport,
  "myclientid_" + parseInt(Math.random() * 100, 10));

  client.onConnectionLost = function (responseObject) {
  console.log("connection lost: " + responseObject.errorMessage);
};

client.onMessageArrived = function (message) {
  console.log(message.destinationName, ' -- ', message.payloadString);
};

var options = {
  timeout: 3,
  userName: "mqttuser",
  password: "bnubnu",
  onSuccess: function () {
    console.log("mqtt connected");
    console.log(client.host + ":" + client.port);
    console.log(client);
    console.log('hahahahaha');
  },
  onFailure: function (message) {
    console.log("Connection failed: " + message.errorMessage);
  }
};

function init() {
  client.connect(options);
}

function publish(face1State,face2State) {
  var topic = "mytopic01";
  var qos = 0;
  var message1 = face1State;
  var message2 = face2State;
  var retain = false;
  
  message = "{\"list01\":\""+name1.innerHTML+"\",\"score01\":"+long1.innerHTML+",\"list02\":\""+name2.innerHTML+"\",\"score02\":"+long2.innerHTML+"}";

  logMessage("INFO", "Publishing Message: [Topic: ", topic, ", Payload: ", message, ", QoS: ", qos, ", Retain: ", retain, "]");
  message = new Paho.MQTT.Message(message);
  message.destinationName = topic;
  message.qos = Number(qos);
  message.retained = retain;
  client.send(message);
  console.log(message); 
}

function logMessage(type, ...content) {

  var date = new Date();
  var timeString = date.toUTCString();
  var logMessage = timeString + " - " + type + " - " + content.join("");
  console.log(logMessage);
}