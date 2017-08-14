Predictive ECS Scaling
===

Lambda function created in order to read the Task Definition before updating the ECS Service.

## How it works

When the ECS Service is issued an update, the python script goes through the Task Definition, reads the amount of memory needed for the Service to update and the memory available on the Cluster. In case it doesn't have the necessary memory, it launches a new Container Instances based on a running one and updates the Service.

This is specially interesting when updating Desired Count to an amount higher than 1.

### Example

Container Instances = 1  
Desired Count = 5  
Running Count = 5  
Service Memory Utilization = 75%  
Service AutoScaling monitoring: 80%

Lets assuma that an atomic access to a website makes the Desired Count to be updated to 12. The predictiveEcsScaling script will see that the current cluster allows for another 3 containers to be deployed:

Container Instances = 1  
Desired Count = 12  
Running Count = 8  
Service Memory Utilization = 75%  
Service AutoScaling monitoring: 80%

As you can see, the Memory Utilization won't increase until the deploy ends. Based on that, the monitoring (CloudWatch) won't be issued until the Service starts to monitored memory. Thus, the Service will go through the "error" state (not enough memory to launch new contaienrs). The cluster will stay in this state until a new Container Instance is launched and/or a new alarm is issue in CloudWatch (Cluster MemoryUtilization for example). This could take minutes.

Using the precitiveEcsScaling feature, that "error phase" is bypassed (actually it'll still exist, but, for a shorter period - read below) since it'll identify the need to launch a new ContainerInstance:

Container Instances = 2  
Desired Count = 12  
Running Count = 8  
Service Memory Utilization = 75%  
Service AutoScaling monitoring: 80% 

Now, as soon as the Container Instance is ready (registered), the other 4 containers will launch. 

### Use

predictiveEcsScaling.py update <clusterName> <serviceName> <desiredCount>

### In Dev

Normalization features to correctly scale the containers x ContainerInstance ratio
Use the "correct" EC2 according to cluster needs
Application "learning" features

#### Obs:

This was created by an enthusiast and gives "self healing" features to the an ECS cluster using an Automatic Scaling feature that I believe it would be great.  
I hope this helps anyone and please feel free to give me any feedback (I'm 100% sure that I need it) or improvement.  
Feel free to provide me with any ideas of future implementations as well as discussing them.