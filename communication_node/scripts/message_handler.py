#!/usr/bin/env python
# coding=utf-8
"""Message Handler.

# Authors:  MohammadHossein GohariNejad <hoseingohari76@gmail.com>
#           Sajjad Azami <sajjadaazami@gmail.com>
# License:  BSD 3 clause

Plays the server role in communication_node

Relations
----------
subscribes from /message_server topic,
publishes on corresponding nodes /ns/message_status topic

"""
import os
import signal
import sys
from time import gmtime,strftime
import rospy
from communication_node.msg import *
from nav_msgs.msg import *

debuger_mode=False;
information_logger=None;
rate=None
message_handlers_list=[]



class message_handle:
    """
    this class is wrapper around a ros publisher and a ros subscriber
    and a callback function for the ros rossubscirber
    for each data type given to the this script through launch file or
    parameter server this script will create an object to
    handle messages of that type
    """

    def __init__(self,sub_topic="",pub_topic="",data_type=None,tag="",alt_type=None):
            """this is the constructor function for message_handle class
            :parameter
            sub_topic : string, the prefix for the subscribing topic
            pub_topic : string, the topic for publishing the messages to
            data_type : type, the type of the message that's going to be handled
            tag       : string, tag for the data type
            alt_type  : type, alternative type for publishing message

            Relations
            ----------
            subscribes from /"sub_topic"+"tag"
            """
            self.sub_topic=sub_topic;
            self.pub_topic=pub_topic;
            self.data_type=data_type;
            self.alt_type=alt_type;
            self.tag=tag;
            self.subscriber=rospy.Subscriber(self.sub_topic+self.tag,self.data_type, self.callback_function,queue_size=20);
            self.message_publisher=None;

    def callback_function(self,data):
            """this is the callback function for self.subscriber
            :parameter
            data : self.data_type, this is the data received by the Subscriber

            Relations
            ----------
            publishes to "data.source"+"self.pub_topic"
            """
            global information_logger
            global propagation_parameters
            # TODO handle for different message types
            # TODO prop_model = data.prop_model
            if(self.tag!="map"and self.tag!="Odom"):
                print("new "+self.tag+" received")
            robots_list=rospy.get_param("/robots_list")
            if ((data.source not in robots_list )or(data.destination not in robots_list) ):
                return;
            connection_list=[];
            connection_list=(rospy.get_param("/connection_list_"+data.source));
            source_index=robots_list.index(data.destination);
            if (connection_list[1+source_index]==1):
                    if (self.alt_type!=None):
                       self.message_publisher = rospy.Publisher(data.source +"/g_map", self.alt_type, queue_size=10)
                       i=0
                       while not ( rospy.is_shutdown() or i>1):
                                 self.message_publisher.publish(data.data)
                                 print("from",data.source," to",data.destination);
                                 i+=1
                                 rate.sleep()
                       i=0
                    else:
                       self.message_publisher = rospy.Publisher(data.destination + self.pub_topic, self.data_type, queue_size=10)
                       i=0
                       while not ( rospy.is_shutdown() or i>1):
                                 self.message_publisher.publish(data)
                                 print("from",data.source," to",data.destination);
                                 #print("sent messagne",self.tag)
                                 i+=1
                                 rate.sleep()
                       i=0

                    #print "communication is possible"

def listener():
    global information_logger
    global rate
    global debuger_mode
    global message_handlers_list;
    global propagation_models;
    rospy.init_node('communication_node_message_handler')
    rate=rospy.Rate(50)
    message_list=[["/message_server_","/inbox_Goal",Data_Goal,"Goal",None],["/message_server_","/inbox_Map",Data_Map,"map",None]];
    for i in range (0,len(message_list)):
        message_handlers_list.append(message_handle(message_list[i][0],message_list[i][1],message_list[i][2],message_list[i][3],message_list[i][4]));
    rospy.spin()


listener()
