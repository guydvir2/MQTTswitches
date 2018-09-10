from sys import path
import datetime
from time import sleep

try:
    # Linux
    mod_path = '/home/guy/github/modules'
    path.append(mod_path)
    import scheduler

except ModuleNotFoundError:
    # MAC
    mod_path = '/Users/guy/github/modules'
    path.append(mod_path)
    import scheduler

from mqtt_switch import MQTTClient
from jReader import SchedReader


class MQTTRemoteSchedule:
    def __init__(self, device_topic, scheds_topic, msg_topic, broker='192.168.2.113', qos=0, sched_filename=None,
                 username=None, password=None):

        self.schedule_up, self.schedule_down = None, None

        # ## MQTT parameters
        self.broker = broker
        client_id = device_topic.split('/')[-1] + '_SCHD'
        # ##

        # ## Topics
        # device topic to send command
        self.device_topic = device_topic
        # for group of scheds
        self.scheds_topic = scheds_topic
        # Outgoing notification messages
        self.msg_topic = msg_topic
        # internal msgs to scheduler
        self.int_topic = self.device_topic + "_SCHD"
        # ##

        # ## Read schedule file
        if sched_filename is None:
            sched_filename = device_topic.split('/')[-1] + '.json'
        self.sched_reader = SchedReader(filename=sched_filename)
        if self.sched_reader.data_from_file["topic"] != self.device_topic:
            self.sched_reader.update_value('topic', self.device_topic)
        # Enabled/disabled schedule - defined inside config file
        self.active_schedule_flag = self.sched_reader.data_from_file["enable"]
        # ##

        self.start_mqtt_service(client_id, qos, password=password, username=username)
        self.run_schedule()
        self.schedule_report()
        self.boot_time = datetime.datetime.now()

    # MQTT section
    def start_mqtt_service(self, client_id, qos, password, username):
        self.mqtt_agent = MQTTClient(sid=client_id, topics=[self.device_topic, self.int_topic],
                                     last_will_topic=self.msg_topic,
                                     topic_qos=qos, host=self.broker, password=password, username=username)
        self.mqtt_agent.call_externalf = lambda: self.mqtt_commands(self.mqtt_agent.arrived_msg)
        self.mqtt_agent.start()
        sleep(1)
        self.pub_msg(msg_topic=self.msg_topic, msg='Schedule is active')

    def mqtt_commands(self, msg):
        msg_codes = ['0', '1', '2', '3']
        msg_text = ['STATUS', 'DISABLE', 'ENABLE', 'REPORT']

        if msg.upper() == msg_text[0] or msg == msg_codes[0]:
            msg = "Schedule is [%s], boot time: [%s]" % (self.active_schedule_flag, str(self.boot_time)[:-5])
            self.pub_msg(msg_topic=self.msg_topic, msg=msg)

        elif msg.upper() == msg_text[1] or msg == msg_codes[1]:
            self.active_schedule_flag = False
            msg = "Schedule set to [%s]" % self.active_schedule_flag
            self.pub_msg(msg_topic=self.msg_topic, msg=msg)

        elif msg.upper() == msg_text[2] or msg == msg_codes[2]:
            self.active_schedule_flag = True
            msg = "Schedule set to [%s]" % self.active_schedule_flag
            self.pub_msg(msg_topic=self.msg_topic, msg=msg)

        elif msg.upper() == msg_text[3] or msg == msg_codes[3]:
            report = self.schedule_report()
            for line in report:
                self.pub_msg(msg_topic=self.msg_topic, msg=line[0])

    def pub_msg(self, msg, msg_topic=None):
        if msg_topic == None:
            msg_topic = self.device_topic
        else:
            time_stamp = '[' + str(datetime.datetime.now())[:-4] + ']'
            msg = '%s [%s][SCHD] %s' % (time_stamp, self.device_topic, msg)

        self.mqtt_agent.pub(payload=msg, topic=msg_topic)

    def pub_validated_commad(self, msg):
        # this flag come to enable user to not activate a running Schedule
        if self.active_schedule_flag is True:
            self.pub_msg(msg)
        else:
            self.pub_msg(msg_topic=self.msg_topic, msg="Scheduled task- Disabled by User")

    # Schedule section

    def data_validation(self):
        if self.sched_reader.data_from_file["topic"] == self.device_topic:
            pass
        else:
            print("wrong topic in schedule file")

    def run_schedule(self):
        self.data_validation()

        self.schedule_up = scheduler.RunWeeklySchedule(on_func=lambda: self.pub_validated_commad('up'),
                                                       off_func=lambda: self.pub_validated_commad('off'))
        self.schedule_down = scheduler.RunWeeklySchedule(on_func=lambda: self.pub_validated_commad('down'),
                                                         off_func=lambda: self.pub_validated_commad('off'))

        if self.sched_reader.data_from_file["enable"] is True:
            for current_up_schedule in self.sched_reader.data_from_file["schedule_up"]:
                self.schedule_up.add_weekly_task(new_task=current_up_schedule)
            self.schedule_up.start()

            for current_down_schedule in self.sched_reader.data_from_file["schedule_down"]:
                self.schedule_down.add_weekly_task(new_task=current_down_schedule)
            self.schedule_down.start()

        else:
            print("Schedule is not enabled. \n Quit.")

    def schedule_report(self):
        output = []
        print('Topic: [%s]' % (self.device_topic))
        for i in range(len(self.sched_reader.data_from_file["schedule_up"])):
            schedule_program = "\t\t[UP   #%d]: Start: %s, %s, End: %s, %s" % \
                               (i, self.sched_reader.data_from_file["schedule_up"][i]["start_days"],
                                self.sched_reader.data_from_file["schedule_up"][i]["start_time"],
                                self.sched_reader.data_from_file["schedule_up"][i]["end_days"],
                                self.sched_reader.data_from_file["schedule_up"][i]["end_time"])
            print(schedule_program)
            output.append([schedule_program])
            schedule_program = "\t\t[Down #%d]: Start: %s, %s, End: %s, %s" % \
                               (i, self.sched_reader.data_from_file["schedule_down"][i]["start_days"],
                                self.sched_reader.data_from_file["schedule_down"][i]["start_time"],
                                self.sched_reader.data_from_file["schedule_down"][i]["end_days"],
                                self.sched_reader.data_from_file["schedule_down"][i]["end_time"])
            print(schedule_program)
            output.append([schedule_program])
        print('\n')
        return output
    #
    # def PBit(self):
    #     self.pub_msg('up')
    #     sleep(1)
    #     self.pub_msg('down')
    #     sleep(1)


if __name__ == "__main__":

    topic_prefix = 'HomePi/Dvir/Windows/'
    Home_Devices = ['p']  # , 'fRoomWindow', 'kRoomWindow']
    Home_Devices = [topic_prefix + device for device in Home_Devices]
    for client in Home_Devices:
        MQTTRemoteSchedule(broker='192.168.2.200', device_topic=client, scheds_topic='HomePi/Dvir/Schedules',
                           msg_topic='HomePi/Dvir/Messages', username='guy', password='kupelu9e')
