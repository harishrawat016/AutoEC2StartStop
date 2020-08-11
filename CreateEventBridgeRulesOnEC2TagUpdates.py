import boto3
import os
import re
import time
from pprint import pprint

def lambda_handler(event, context):
	ebClient = boto3.client(service_name='events', region_name='us-west-2')
	ec2Client = boto3.client(service_name='ec2', region_name='us-west-2')
	ec2rsc = boto3.resource(service_name='ec2', region_name='us-west-2')
	
	def createEB_Rule(tag,action):
		hrs = tag['Value'].split(":")[0]
		mins = tag['Value'].split(":")[1]
		cronjob = "cron(" + mins + "\t"+ hrs + "\t?\t*\t*\t*)"
		arnLambda = "arn:aws:lambda:us-west-2:578225969089:function:AutoScheduled-EC2StartStop"
		if(action == 'ec2stop'):
			ruleName = "EC2_Stop_at_" + hrs +"_"+ mins
			inputEvents = '{"hrs": "'+ hrs + '","mins":"' + mins + '","action":"' + action +'"}'
		elif(action == 'ec2start'):
			ruleName = "EC2_Start_at_" + hrs +"_"+ mins
			inputEvents = '{"hrs": "'+ hrs + '","mins":"' + mins + '","action":"' + action +'"}'
		if (ruleName not in ec2RuleNames):
			ebClient.put_rule(Name=ruleName,ScheduleExpression=cronjob)
			ebClient.put_targets(Rule=ruleName,Targets=[{'Id':'123456','Arn':arnLambda,'Input': inputEvents}])
	
	ec2RuleNames=[]
	ebPaginator = ebClient.get_paginator('list_rules')
	for eachPage in ebPaginator.paginate():
		for eachRule in eachPage['Rules']:
			if (re.match("^EC2_",eachRule['Name'])):
				hrsTemp = eachRule['Name'].split("_")[-2]
				minsTemp = eachRule['Name'].split("_")[-1]
				cronjobTemp = "cron(" + minsTemp + "\t"+ hrsTemp + "\t?\t*\t*\t*)"
				if (cronjobTemp != eachRule['ScheduleExpression'] ):
					ebClient.remove_targets(Rule=eachRule['Name'],Ids=['123456'])
					ebClient.delete_rule(Name=eachRule['Name'],Force=True)
				else:	
					ec2RuleNames.append(eachRule['Name'])
	
	for eachEC2 in ec2Client.describe_instances( Filters=[{'Name': 'tag-key','Values': ['ec2start','ec2stop']}])['Reservations']:
		for eachInstance in eachEC2['Instances']:
			for tag in eachInstance['Tags']:
				if (tag['Key'] == "ec2stop"):
					createEB_Rule(tag,'ec2stop')
				elif (tag['Key'] == "ec2start"):
					createEB_Rule(tag,'ec2start')