import boto3
import os
import re
import time
import json
from pprint import pprint

def lambda_handler(event, context):
    hrs = event['hrs']
    mins = event['mins']
    action = event['action']
    ec2Client = boto3.client(service_name='ec2', region_name='us-west-2')
    if(action == "ec2start"):
    	tagName = "tag:ec2start"
    elif(action == "ec2stop"):
    	tagName = "tag:ec2stop"
    tagValue = hrs+":"+mins
    tagFilter = {'Name': tagName, 'Values':[tagValue]}
    targetIDs=[]
    ec2Paginator = ec2Client.get_paginator('describe_instances')
    ec2Instances = ec2Paginator.paginate(Filters=[tagFilter])
    for eachInstance in ec2Instances:
    	for eachReservation in eachInstance['Reservations']:
    		for instance in eachReservation['Instances']:
    			targetIDs.append(instance['InstanceId'])
    if(action == "ec2start"):
    	ec2Client.start_instances(InstanceIds=targetIDs)
    elif(action == "ec2stop"):
    	ec2Client.stop_instances(InstanceIds=targetIDs,Force=True)

    
