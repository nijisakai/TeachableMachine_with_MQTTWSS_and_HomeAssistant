# Installation of MQTT.js with WSS support

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
