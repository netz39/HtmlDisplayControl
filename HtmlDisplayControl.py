#! /usr/bin/python3


import signal
import sys

import argparse
import syslog
import webbrowser

import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    syslog.syslog("MQTT connected, result code: {}".format(rc))
    
    global URI_TOPIC
    client.subscribe(URI_TOPIC)
    
    return


def on_disconnect(client, userdata, rc):
    syslog.syslog("MQTT disconnected, result code: {}".format(rc))
    
    return


def on_log(client, userdata, level, buf):
    if level <= mqtt.MQTT_LOG_WARNING:
        syslog.syslog(level, buf)
    
    return


def on_message(client, userdata, msg):
    if msg.payload is not None:
        uri = msg.payload.decode("utf-8")
        
        syslog.syslog(syslog.LOG_NOTICE, "Received URI {}.".format(uri))
        
        webbrowser.open(uri)
    
    return


def sigint_handler(signal, frame):
    global RUN
    
    if RUN:
        msg = "SIGINT received, marking for shutdown."
        print(msg)
        syslog.syslog(syslog.LOG_INFO, msg)
        RUN=False
    else:
        msg = "SIGINT received for the second time. Immediate exit!"
        print(msg)
        syslog.syslog(syslog.LOG_WARN, msg)
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Open URIs provided via MQTT in a web browser")
    parser.add_argument("--broker", help="MQTT Broker")
    parser.add_argument("--topic", help="URI topic")
    args = parser.parse_args()
    
    if args.broker is None:
        print("No broker has been provided, aborting!")
        sys.exit(1)
    
    if args.topic is None:
        print("No topic has been provided, aborting!")
        sys.exit(1)
    
    BROKER = args.broker
    
    global URI_TOPIC
    URI_TOPIC = args.topic
    
    syslog.openlog(facility=syslog.LOG_DAEMON)
    syslog.syslog(syslog.LOG_INFO, "Html Display client started")
    
    global RUN
    RUN=True
    signal.signal(signal.SIGINT, sigint_handler)
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_log = on_log
    client.on_message = on_message
    
    client.connect(BROKER, 1883, 60)
    
    while RUN:
        client.loop()
    
    client.disconnect()
    
    syslog.syslog(syslog.LOG_INFO, "Html Display client finished.")
    syslog.closelog()


# kate: space-indent on; indent-width 4; mixedindent off; indent-mode python; indend-pasted-text false; remove-trailing-space off
