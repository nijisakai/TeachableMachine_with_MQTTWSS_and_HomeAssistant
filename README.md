# Pass Teachable Machine result with MQTT

Train a model with Teachable Machine, use a webcam to test the model and pass the result to some IOT platform such as HomeAssistant.
In this repository, I use a raspberry pi 4 with [Hass.io](https://www.home-assistant.io/hassio/) with MQTT addon. 

## Installation

### Install docker (instructions taken from this thread 96 on docker )

`sudo curl -sL get.docker.com | sed 's/9)/10)/' | sh`

### Install hassio dependencies (instructions taken from here 36)

`sudo apt-get install apparmor-utils apt-transport-https avahi-daemon ca-certificates curl dbus jq network-manager socat software-properties-common`

### Install hassio (this part I fiddled with until I got something that worked)

Save hassio installer to file: $ curl -sL "https://raw.githubusercontent.com/home-assistant/hassio-installer/master/hassio_install.sh" >> hassio_install.sh
Modify install script. Open up hassio_install.sh in your favorite text editor and change it as follows. Where it says “armv7l”, change that section so it looks like this:
Copy to clipboard
"armv7l")
        HOMEASSISTANT_DOCKER="$DOCKER_REPO/raspberrypi3-homeassistant"
        HASSIO_DOCKER="$DOCKER_REPO/armhf-hassio-supervisor"
    ;;
This (https://pastebin.com/fc64mDnm) is what mine looked like after I modified it.

Run install script: $ sudo bash hassio_install.sh
After that, hassio should be available.

## Requirement

- nginx server over lan or wan
- a phone or laptop with a camera

## Usage

tbd

## Acknowledgments

This repository is based on [kasperkamperman/MobileCameraTemplate](https://github.com/kasperkamperman/MobileCameraTemplate)