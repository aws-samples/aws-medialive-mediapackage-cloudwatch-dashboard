Automated Way to Create an AWS Media Services-Centric CloudWatch Dashboard
==========================================================================

This repository is part of a AWS Media Blog post, called [Automated Way to Create an AWS Media Services-Centric CloudWatch Dashboard] (https://aws-preview.aka.amazon.com/blogs/media/automated-way-to-create-an-aws-media-services-centric-cloudwatch-dashboard/)

This blog post describes two methods for automating the creation of CloudWatch dashboards that present widgets in a consistent, user-friendly layout optimized for media workflows. One method uses a Python script and the other applies an AWS CloudFormation template that utilizes the Python script. If you already have a working environment for the AWS SDK for Python (Boto3), the Python script will be easiest to use. This is also true if you have a large number of dashboards to create. If you don’t use the AWS SDK for Python, then the CloudFormation template will be the easiest solution for you. Both approaches are designed for media workflows that incorporate the AWS Elemental MediaLive and AWS Elemental MediaPackage services and will generate a dashboard with widgets that present key metrics from those services during operation. Please note there are many different ways to achieve the same result programmatically.

Assumptions
-----------

For sake of simplicity, these examples make several assumptions. The assumptions for running the Python script directly are:

The Python modules boto3 and awscli are installed, and "aws configure" was run to define the access key and secret access key to be used by boto3 to interact with the AWS services.
The user that runs the script has an IAM policy that allows the user to run list/describe commands for MediaLive, MediaPackage, and CloudWatch, and has permission to create the dashboard instance in the user’s account.
Assumptions for both the Python script and the CloudFormation Template are:

Even though dashboards are not regional, an instance of a given dashboard widget can only present data for a single region. Therefore, this script requires that the MediaLive channels used to create the dashboard all be in the same region.
The MediaLive Channel was started at least once. This is required for the OutputVideoFrameRate CloudWatch Metric to be populated with the names of the outputs of the MediaLive channel.
MediaPackage Channels receiving content from the MediaLive Channel are in the same region as the MediaLive channel.
The CloudWatch Dashboard is created in the same region as the MediaLive Channel

Execution of the python script
------------------------------

The script has a comprehensive help function that can be accessed by the command line option “-h” or “–help”, e.g.

```python create_CW_dashboard.py -h```  

The script takes as input either a single MediaLive Channel ARN, or a file consisting of a list of MediaLive Channel ARNs, as well as the name of the dashboard.

```python create_CW_dashboard.py --arn <MediaLive_Ch_ARN> --name <Dashboard_Name>```

or

```python create_CW_dashboard.py --list <MediaLive_Ch_ARN_LIST_file> --name <Dashboard_Name>```

The MediaLive ARN list file <MediaLive_Ch_ARN_LIST_file> should be a text file that has a single MediaLive Channel ARN per line, e.g.

arn:aws:medialive:us-west-2:0123456789:channel:123456
arn:aws:medialive:us-west-2:0123456789:channel:234567
arn:aws:medialive:us-west-2:0123456789:channel:345678

The script ignores duplicate entries and empty lines in the list file.

Execution of the CloudFormation Template
----------------------------------------

The CloudFormation template creates a Lambda function that will then, in turn, create the CloudWatch dashboard. The Lambda runs a version of the Python script mentioned above. Use the  CloudFormation console to create a stack instance in the region you want the dashboard to reside.

## Structure of the Dashboard


The dashboard is broken up into two sections, namely the Packaging & Origin section (i.e. MediaPackage related) and the Encoding section (MediaLive related).

### Packaging & Origin Section

This section consists of six metrics related to the MediaPackage service:

1. Ingress Bytes: Number of bytes that the MediaPackage Channel ingests.
1. Egress Request Bytes: Number of bytes that MediaPackage successfully outputs for each request.
1. Ingress Response Time: The time that it takes the MediaPackage to process each ingest request.
1. Egress Request Count: Number of content requests that MediaPackage receives.
1. Status Codes for 2xx and 4xx: For each MediaPackage Endpoint graphs the sum of all 2xx Status Codes and 4xx Status Codes.
1. Status Codes for 3xx and 5xx: For each MediaPackage Endpoint graphs the sum of all 3xx Status Codes and 5xx Status Codes.

### Encoding Section
The Encoding section of the dashboard is relate to the metrics of the MediaLive channel:

1. Input Video Frame Rate: The input video frame rate averaged over the last ten seconds.
1. Output Video Frame Rate: This metric graphs the output video frame rate of each output in the MediaLive channel, averaged over the last ten seconds.
1. Network In: A graph of the sum of the input bit rate
1. Network Out: A graph of the sum of all the outputs of the MediaLive channel
1. Active Output Renditions: Sum of the number of active outputs of the MediaLive channel
1. Dropped Frames: The Dropped Frame metric indicates the cumulative number of dropped input frames since the start of the channel. A frame drop indicates that the system is unable to keep up in real time.
1. Fill Milliseconds: This metric is the number of consecutive milliseconds of “fill” frames (e.g. repeated frames, black frames and/or slate) inserted by the MediaLive due to the input not being present.  Once the input returns it will go back to zero.
1. SVQ Time: This metric defines the percentage of time, averaged over the last 10 seconds, the encoder has had to reduce quality optimizations to speed up the encode process, in order to keep the MediaLive running in real time.



For more detailed information, please read the blog post. 


## License

This library is licensed under the Apache 2.0 License. 