# Pass Teachable Machine result with MQTT

Train a model with Teachable Machine, use a webcam to test the model and pass the result to some IOT platform such as HomeAssistant.
In this repository, I use a raspberry pi 4 with [Hass.io](https://www.home-assistant.io/hassio/) with MQTT addon.

## Demo

<https://ping.hass.live>

## Requirement

- a web server (Debian/Ubuntu/CentOS, etc.)
- a phone or laptop with a camera

## Installation

### Install docker (instructions taken from this thread 96 on docker )

`sudo curl -sL get.docker.com | sed 's/9)/10)/' | sh`

### Install hassio dependencies (instructions taken from here 36)

`sudo apt-get install apparmor-utils apt-transport-https avahi-daemon ca-certificates curl dbus jq network-manager socat software-properties-common`

### Install hassio (this part I fiddled with until I got something that worked)

Save hassio installer to file:
`curl -sL "https://raw.githubusercontent.com/home-assistant/hassio-installer/master/hassio_install.sh" >> hassio_install.sh`

Modify install script. Open up hassio_install.sh in your favorite text editor and change it as follows. Where it says **armv7l**, change that section so it looks like this:

``` bash
"armv7l")
        HOMEASSISTANT_DOCKER="$DOCKER_REPO/raspberrypi3-homeassistant"
        HASSIO_DOCKER="$DOCKER_REPO/armhf-hassio-supervisor"
    ;;
```

This link <https://pastebin.com/fc64mDnm> is what mine looked like after I modified it.

Run install script:

``` bash
sudo bash hassio_install.sh
```

After that, hassio should be available.

### Install MQTT.js with WSS support

``` bash
npm install mqtt --save
npm install -g browserify
npm install -g webpack-cli
npm install -g webpack@4
cd node_modules/mqtt
npm install . // install dev dependencies
browserify mqtt.js -s mqtt > browserMqtt.js
webpack mqtt.js ./browserMqtt.js --output-library mqtt
```

Here's what the main part of the js script.

``` bash
<script src="./browserMqtt.js"></script>
<script>
            // var KEY = '/var/www/html/test02/client-key.key';
            // var CERT = '/var/www/html/test02/client-cert.crt';
            // var TRUSTED_CA_LIST = '/var/www/html/test02/cacert.crt';
            // var PORT = '8883';
            // var HOST = '159.210.65.6';
            var options = {
                port: '8081',
                host: '159.210.65.6',
                keyPath: '/var/www/html/test02/client-key.pem',
                certPath: '/var/www/html/test02/client-cert.pem',
                rejectUnauthorized : false,
                //The CA list will be used to determine if server is authorized
                ca: ['/var/www/html/test02/cacert.pem'],
                protocol: 'wss',
                protocolId: 'MQTT',
                // username: 'qqq',
                // password: 'bbb',
                clientId: 'mqttjs_' + Math.random().toString(16).substr(2, 8)
            };

            var client = mqtt.connect(options);

            client.subscribe('messages');
            client.publish('messages', 'Current time is: ' + new Date());
            client.on('message', function(topic, message) {
            console.log(message);
            });

            client.on('connect', function(){
                console.log('Connected');
            });
</script>
```

## Usage

tbd

## Acknowledgments

This repository is based on [kasperkamperman/MobileCameraTemplate](https://github.com/kasperkamperman/MobileCameraTemplate)
