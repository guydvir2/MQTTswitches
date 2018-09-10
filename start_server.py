import MQTTlogger
import Sched_MQTT
import time


def start_logger(topics, server, user, password):
    logger = MQTTlogger.LogMQTTactivity(sid="MQTTlogger", topics=topics, topic_qos=0, mqtt_server=server, username=user,
                                        password=password)
    logger.start()


def start_scheduler(server, user, password, msg_topic, pub_topic):
    topic_prefix = 'HomePi/Dvir/Windows/'
    Home_Devices = ['pRoomWindow', 'fRoomWindow', 'kRoomWindow']
    Home_Devices = [topic_prefix + device for device in Home_Devices]
    for client in Home_Devices:
        Sched_MQTT.MQTTRemoteSchedule(broker=server, device_topic=client, scheds_topic=pub_topic,
                                      msg_topic=msg_topic, username=user, password=password,
                                      sched_filename='/home/guy/github/SmartHome_SoC/MQTTswitches/' + client.split('/')[-1] + '.json')


# ######################### Parameters ###########################
BROKER = '192.168.2.200'
TOPICS2LOG = ['HomePi/Dvir/Windows/All', 'HomePi/Dvir/Messages',
              'HomePi/Dvir/Alarms', 'HomePi/Dvir/Logger']
MSG_TOPIC = 'HomePi/Dvir/Messages'
ADDITIONAL_TOPIC = 'HomePi/Dvir/Schedules'
USER = "guy"
PASSWORD = "kupelu9e"
# #################################################################

# ######### start here ############
start_logger(topics=TOPICS2LOG, server=BROKER, user=USER, password=PASSWORD)
time.sleep(5)
start_scheduler(server=BROKER, user=USER, password=PASSWORD, msg_topic=MSG_TOPIC, pub_topic=ADDITIONAL_TOPIC)
