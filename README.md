Predictive ECS Scaling
===

Lambda function created in order to read the Task Defintiion before updating the ECS Service.

## How it works

When the ECS Service is issued an update, the python script goes through the Task Definition, reads the amount of memory needed for the Service Update and the memory available on the Cluster. In case it doesn't have the necessary memory, it launches a new Container Instances based on a running one and updates the Service.

This is specilly interesting when updating Desired Count to an amount higher than 1.

### Example

Container Instances = 1  
Desired Count = 5  
Running Count = 5  
Service Memory Utilization = 75%  
Service AutoScaling monitoring: 80%

An atomic access to a website makes the Desired Count to be updated to 12. The predictiveEcsScaling script will see that the current cluster allows for another 3 containers to be deployed:

Container Instances = 1  
Desired Count = 12  
Running Count = 8  
Service Memory Utilization = 75%  
Service AutoScaling monitoring: 80%

As you can see, the Memory Utilization won't increase until the deploy ends. Based ont hat, the monitoring (CloudWatch) won't be issued. Thus, the Service will go through the "error" state.

Usin the precitiveEcsScaling feature, that "phase" is bypassed since it'll identify the need to launch a new ContainerInstance:

Container Instances = 2  
Desired Count = 12  
Running Count = 8  
Service Memory Utilization = 75%  
Service AutoScaling monitoring: 80% 

Now, as soon as the Container Instance is ready (registered), the other 4 containers will launch. This gives "self healing" features to the ECS cluster. 