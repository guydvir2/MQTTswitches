from sys import path

path.append('/home/guy/.local/lib/python3.5/site-packages')
import paho.mqtt.client as mqtt
from threading import Thread
# import datetime


class MQTTClient(Thread):
    def __init__(self, sid=None, host="iot.eclipse.org", username=None, password=None, topics=None,
                 state_topic=None, last_will_topic=None, msg_topic=None, topic_qos=None):

        Thread.__init__(self)
        self.sid = sid
        self.host = host
        self.username = username
        self.password = password
        self.topics = topics
        # self.avail_topic = avail_topic
        self.state_topic = state_topic
        self.msg_topic = msg_topic
        self.topic_qos = topic_qos
        self.client, self.arrived_msg = None, None

        if last_will_topic is None:
            self.last_will_topic = self.topics[0]
        else:
            self.last_will_topic = last_will_topic

    def on_connect(self, client, obj, flags, rc):
        print(">> Connecting to MQTT server %s: %d" % (self.host, rc))
        for topic in self.topics:
            print(">> Subscribe topic: %s" % topic)
            self.client.subscribe(topic, qos=self.topic_qos)
        self.client.publish(topic=self.last_will_topic, payload="online", retain=True)

    def on_message(self, client, obj, msg):
        self.arrived_msg = msg.payload.decode()
        self.call_externalf()

    def call_externalf(self):
        pass

    def pub(self, payload, topic=None, retain=False):
        if topic is None:
            topic = self.topic
        self.client.publish(topic, payload, self.topic_qos, retain)

    def run(self):
        self.client = mqtt.Client(str(self.sid))
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        if self.username is not None and self.password is not None:
            self.client.username_pw_set(self.username, self.password)
        # self.client.will_set(topic=self.last_will_topic, payload='[%s] [%s] Got disconnected from MQTT server' % (
        #     str(datetime.datetime.now())[:-4], self.topics[0]), retain=True)
        self.client.will_set(topic=self.last_will_topic, payload="offline", retain=True)
        self.client.connect(self.host, 1883, 60)
        self.client.loop_forever()


# This class is only for explanation purposes
class AnyOtherClass:
    def __init__(self):
        # following lines as must in every class that ment to use MQTT_class
        self.mqtt = MQTTClient(topics=['HomePi/dvir/test1'], topic_qos=0, host='192.168.2.113')
        self.mqtt.call_externalf = lambda: self.commands(self.mqtt.arrived_msg)
        self.mqtt.start()

    def commands(self, mqtt_msg):
        if mqtt_msg == 'GUY':
            print("YES")


if __name__ == "__main__":
    b = AnyOtherClass()
