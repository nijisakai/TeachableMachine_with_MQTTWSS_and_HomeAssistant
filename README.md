# Pass Teachable Machine result with MQTT

Train a model with Teachable Machine, use a webcam to test the model and pass the result to some IOT platform such as HomeAssistant.
In this repository, I use a raspberry pi 4 with [Hass.io](https://www.home-assistant.io/hassio/) with MQTT addon.

## Demo

<https://ping.hass.live><br>
<https://www.bilibili.com/video/BV1eE411j7om/>

## Requirement

- an **x86** web server (Debian/Ubuntu/CentOS, etc. /WSL)
- a phone or laptop with a camera

## Installation

### Pre-Installation on web server

``` bash
sudo apt update
sudo apt upgrade -y
sudo apt install net-tools curl git openssh-server nginx npm
```

### Install Docker on Raspberry Pi 4 64 bit Ubuntu 20.10/Official Debian

<https://dev.to/rohansawant/installing-docker-and-docker-compose-on-the-raspberry-pi-in-5-simple-steps-3mgl>

``` bash
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker pi
sudo apt-get install -y libffi-dev libssl-dev
sudo apt-get install -y python3 python3-pip
sudo apt-get remove python-configparser
sudo pip3 -v install docker-compose
```

### Install Hass.IO on Raspberry Pi

<https://bbs.hassbian.com/forum.php?mod=viewthread&tid=4520&highlight=hassio>

``` bash
su root
wget https://code.aliyun.com/neroxps/hassio_install/raw/master/install.sh
chmod a+x install.sh
./install.sh
```

### Install MQTT.js with WSS support on web server

``` bash
npm install mqtt --save
npm install -g browserify
npm install webpack webpack-cli --save-dev -g
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

This camera part code is from [kasperkamperman/MobileCameraTemplate](https://github.com/kasperkamperman/MobileCameraTemplate)
