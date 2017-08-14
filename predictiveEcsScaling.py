#!/usr/bin/env python2.7

import boto3
import json
import sys, getopt
import base64

client = boto3.client('ecs')

option = str(sys.argv[1])
cluster = str(sys.argv[2])
service_name = str(sys.argv[3])
desired = str(sys.argv[4])

def update_service():
    response = client.update_service(
        cluster=cluster,
        service=service_name,
        desiredCount=int(desired)
    )

    print option, service_name, desired

def getNecessaryMemory():
    #print desired
    describe_services = client.describe_services(
    cluster='clusterForStandardHttpd',
    services=[
        '0ScaledTest',
    ]
    )
    task_definition = client.describe_task_definition(
        taskDefinition='Running:17'
    )
    needed_memory = int(task_definition['taskDefinition']['containerDefinitions'][0]['memory'])
    desired_count = describe_services['services'][0]['desiredCount']
    necessary_memory = int(int(desired) * int(needed_memory))
    return necessary_memory

container_instance_arns = client.list_container_instances(cluster='clusterForStandardHttpd', status='ACTIVE')['containerInstanceArns']

def getAvailableMemory():
    memory = 0

    if container_instance_arns:
        instances = (client.describe_container_instances(cluster='clusterForStandardHttpd', containerInstances=container_instance_arns))

        # for i = 0, i < instances[size]; i ++)
        for instance in instances['containerInstances']:
            av = instance['remainingResources'][1]['integerValue']
            #print instance['remainingResources'][1]['integerValue']
            memory = memory + int(av)
        #print "Added memory value:"
        return memory

def getInstanceUserdata(instance):
    client = boto3.client('ec2')

    response = client.describe_instance_attribute(
        Attribute='userData',

        #    Attribute='instanceType'|'kernel'|'ramdisk'|'userData'|'disableApiTermination'|'instanceInitiatedShutdownBehavior'|'rootDeviceName'|'blockDeviceMapping'|'productCodes'|'sourceDestCheck'|'groupSet'|'ebsOptimized'|'sriovNetSupport'|'enaSupport',
        InstanceId=instance
    )

    #print(response)['UserData']['Value']
    return(base64.b64decode((response)['UserData']['Value']))

#def getInstanceData(instance, userData):
def getInstanceData(instance):
    clientec2 = boto3.client('ec2')
    response = clientec2.describe_instances(
        InstanceIds=[
            instance,
        ]

    )

    instance = response['Reservations'][0]['Instances'][0]
    imageid = (instance['ImageId'])
    instancetype = (instance['InstanceType'])
    keyname = (instance['KeyName'])
    securitygroupname = (instance['SecurityGroups'][0]['GroupName'])
    iaminstanceprofile = (instance['IamInstanceProfile']['Arn'])
    #if imageid & instancetype & keyname & securitygroupname:
    #    createinstance(imageid, instancetype, keyname, securitygroupname)
    #else:
    #    print "something is missing"
    return imageid, instancetype, keyname, securitygroupname, iaminstanceprofile

def createinstance(a,b,c,d,e,f):
    ec2create = boto3.resource('ec2', region_name="us-east-1")
    ec2create.create_instances(

        ImageId=str(a),
        MinCount=1,
        MaxCount=1,
        InstanceType=str(b),
        KeyName=str(c),

        Monitoring={
            'Enabled': False
        },

        SecurityGroups=[
            str(d)
        ],
        UserData=str(f),

        IamInstanceProfile = {'Arn' : str(e)}

    )

#create a getRunningInstanceId to gather information about the ContainerInstane and something to be based on
def getRunningInstanceId():
    cluster_arn_list = client.list_clusters()['clusterArns']
    cluster_list = client.describe_clusters(clusters=cluster_arn_list)['clusters']

    for cluster in cluster_list:
        cluster_arn = cluster['clusterArn']
        container_instance_list = client.list_container_instances(cluster=cluster_arn)
        container_instance_arns = container_instance_list['containerInstanceArns']
        if container_instance_arns:
            instances = (
            client.describe_container_instances(cluster=cluster_arn, containerInstances=container_instance_arns))

    return instances['containerInstances'][0]['ec2InstanceId']

print "Printing Running Instance ID:"
runningInstanceId = getRunningInstanceId()
print runningInstanceId

print getInstanceUserdata(runningInstanceId)
a,b,c,d,e = getInstanceData(runningInstanceId)
f = getInstanceUserdata(runningInstanceId)
print getInstanceData(runningInstanceId)
print "Necessary memory for update: "
necessary = getNecessaryMemory()
print necessary
print "Available memory: "
available = getAvailableMemory()
print available
print "Is it necessary to create a new instance?"
if int(necessary) > int(available):
    print "yes"
    print "creating instance"
    createinstance(a,b,c,d,e,f)
else:
    print "no"
update_service()


#i-096b8c250ff35f515
