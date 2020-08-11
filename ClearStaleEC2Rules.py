import json
import boto3
import os
import re
import time

def lambda_handler(event, context):
    ebClient = boto3.client(service_name='events', region_name='us-west-2')
    ec2Client = boto3.client(service_name='ec2', region_name='us-west-2')
    ec2RuleNames=[]
    ebPaginator = ebClient.get_paginator('list_rules')
    for eachPage in ebPaginator.paginate():
    	for eachRule in eachPage['Rules']:
    		if (re.match("^EC2_Start_at_",eachRule['Name']) or re.match("^EC2_Stop_at_",eachRule['Name'])):
    			ec2RuleNames.append(eachRule['Name'])
    
    allTagsEc2=[]
    tagStr=""
    for eachEC2 in ec2Client.describe_instances( Filters=[{'Name': 'tag-key','Values': ['ec2start','ec2stop']}])['Reservations']:
    	for eachInstance in eachEC2['Instances']:
    		for tag in eachInstance['Tags']:
    			if (tag['Key'] == "ec2start"):
    				tagStr="EC2_Start_at_"+ tag['Value'].split(":")[0] + "_" + tag['Value'].split(":")[1]
    				allTagsEc2.append(tagStr)
    			elif(tag['Key'] == "ec2stop"):
    				tagStr="EC2_Stop_at_"+ tag['Value'].split(":")[0] + "_" + tag['Value'].split(":")[1]
    				allTagsEc2.append(tagStr)
    for eachRule in ec2RuleNames:
    	if(eachRule not in allTagsEc2):
    		ebClient.remove_targets(Rule=eachRule,Ids=['123456'])
    		ebClient.delete_rule(Name=eachRule,Force=True)
    
