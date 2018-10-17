#!/usr/bin/python

import sys
import os
import getopt
import boto3
import json


version = '0.4'
"""
Notes:
Version 0.1: Initial Release
Version 0.2: Added support of both 'Status Code Range (sum), 2xx4xx' and 'Status Code Range (sum), 3xx5xx' metrics
             Added '-l/--list' command line option with which a user can provide a list of MediaLive Channel ARNs for
             which the Dashboard will be created. NOTE: All MediaLive Channels in this list must be in the same region
Version 0.3: Added a text widget to contain all the links to the MediaLive/MediaPackage channel consoles of the 
             channels of this dashboard.  
Version 0.4: Switched MediaLive centric widgets to use the MediaLive Channel Name instead of the ARN   
Version 0.5: Added support for the new dual channel MediaPackage implementation.        
"""

dashboard_template = """{
    "widgets": [
        {
            "type": "text",
            "x": 0,
            "y": 0,
            "width": 24,
            "height": 1,
            "properties": {
                "markdown": "# MediaPackage Section Title"
            }
        },
        {
            "type": "text",
            "x": 0,
            "y": 1,
            "width": 12,
            "height": 1,
            "properties": {
                "markdown": "## Ingress"
            }
        },		
        {
            "type": "metric",
            "x": 0,
            "y": 2,
            "width": 12,
            "height": 9,
            "properties": {
                "title": "Ingress Bytes (sum)",
                "view": "timeSeries",
                "stacked": false,
                "metrics": [],
                "region": "",
                "stat": "Sum",
                "period": 60,
                "yAxis": {
                    "left": {
                        "min": 0
                    },
                    "right": {
                        "min": 0
                    }
                }
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 11,
            "width": 12,
            "height": 9,
            "properties": {
                "title": "Ingress Response Times (avg)",			
                "view": "timeSeries",
                "stacked": false,
                "metrics": [],
                "region": "",
                "stat": "Average",
                "period": 60
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 20,
            "width": 12,
            "height": 12,
            "properties": {
                "title": "Status Code Range (sum), 3xx,5xx",	
                "view": "timeSeries",
                "stacked": false,
                "metrics": [],
                "region": "",
                "stat": "Sum",
                "period": 60,
                "yAxis": {
                    "left": {
                        "min": 0
                    },
                    "right": {
                        "min": 0
                    }
                }
            }
        },		
        {
            "type": "text",
            "x": 12,
            "y": 1,
            "width": 12,
            "height": 1,
            "properties": {
                "markdown": "## Egress"
            }
        },		
        {
            "type": "metric",
            "x": 12,
            "y": 2,
            "width": 12,
            "height": 9,
            "properties": {
                "title": "Egress Request Bytes (sum)",		
                "view": "timeSeries",
                "stacked": false,
                "metrics": [],
                "region": "",
                "stat": "Sum",
                "period": 60,
                "yAxis": {
                    "left": {
                        "min": 0
                    },
                    "right": {
                        "min": 0
                    }
                }
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 11,
            "width": 12,
            "height": 9,
            "properties": {
                "title": "Egress Request Count (sum)",		
                "view": "timeSeries",
                "stacked": false,
                "metrics": [],
                "region": "",
                "stat": "Sum",
                "period": 60,
                "yAxis": {
                    "left": {
                        "min": 0
                    }
                }
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 20,
            "width": 12,
            "height": 12,
            "properties": {
                "title": "Status Code Range (sum), 2xx,4xx",
                "view": "timeSeries",
                "stacked": false,
                "metrics": [],
                "region": "",
                "stat": "Sum",
                "period": 60,
                "yAxis": {
                    "left": {
                        "min": 0
                    },
                    "right": {
                        "min": 0
                    }
                }
            }
        },		
        {
            "type": "text",
            "x": 0,
            "y": 32,
            "width": 24,
            "height": 1,
            "properties": {
                "markdown": "# MediaLive Section Title"
            }
        },
        {
            "type": "text",
            "x": 0,
            "y": 33,
            "width": 12,
            "height": 1,
            "properties": {
                "markdown": "## Input"
            }
        },		
        {
            "type": "metric",
            "x": 0,
            "y": 34,
            "width": 12,
            "height": 9,
            "properties": {
                "title": "Input Video Frame Rate (avg)",			
                "view": "timeSeries",
                "stacked": false,
                "metrics": [],
                "region": "",
                "stat": "Average",
                "period": 60,
                "annotations": {
                    "horizontal": [
                        {
                            "label": "30 frames per second",
                            "value": 30
                        },
                        {
                            "label": "30 frames per second",
                            "value": 30,
                            "yAxis": "right"
                        },
                        {
                            "label": "60 frames per second",
                            "value": 60
                        },
                        {
                            "label": "60 frames per second",
                            "value": 60,
                            "yAxis": "right"
                        }
                    ]
                },
                "yAxis": {
                    "left": {
                        "min": 0
                    },
                    "right": {
                        "min": 0
                    }
                }
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 43,
            "width": 12,
            "height": 9,
            "properties": {
                "title": "Network In (sum)",			
                "view": "timeSeries",
                "stacked": false,
                "metrics": [],
                "region": "",
                "stat": "Sum",
                "period": 60,
                "yAxis": {
                    "left": {
                        "min": 0
                    },
                    "right": {
                        "min": 0
                    }
                }
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 52,
            "width": 12,
            "height": 6,
            "properties": {
                "title": "Dropped Frames (sum)",			
                "view": "timeSeries",
                "stacked": false,
                "metrics": [],
                "region": "",
                "stat": "Sum",
                "period": 60,
                "yAxis": {
                    "left": {
                        "min": 0
                    },
                    "right": {
                        "min": 0
                    }
                },
                "legend": {"position": "bottom"}
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 58,
            "width": 12,
            "height": 6,
            "properties": {
                "title": "Fill Milliseconds (sum)",			
                "view": "timeSeries",
                "stacked": false,
                "metrics": [],
                "region": "",
                "stat": "Sum",
                "period": 60,
                "legend": {"position": "bottom"}
            }
        },		
        {
            "type": "metric",
            "x": 0,
            "y": 64,
            "width": 12,
            "height": 6,
            "properties": {
                "title": "SVQ Time (percentage)",			
                "view": "timeSeries",
                "stacked": false,
                "metrics": [],
                "region": "",
                "period": 300,
                "stat": "Average",
                "legend": {"position": "bottom"}
            }
        },
        {
            "type": "text",
            "x": 12,
            "y": 33,
            "width": 12,
            "height": 1,
            "properties": {
                "markdown": "## Output"
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 34,
            "width": 12,
            "height": 9,
            "properties": {
                "title": "Output Video Frame Rate (avg)",			
                "view": "timeSeries",
                "stacked": false,
                "metrics": [],
                "region": "",
                "stat": "Average",
                "period": 60,
                "annotations": {
                    "horizontal": [
                        {
                            "label": "30 frames per second",
                            "value": 30
                        },
                        {
                            "label": "30 frames per second",
                            "value": 30,
                            "yAxis": "right"
                        },
                        {
                            "label": "60 frames per second",
                            "value": 60
                        },
                        {
                            "label": "60 frames per second",
                            "value": 60,
                            "yAxis": "right"
                        }
                    ]
                },
                "yAxis": {
                    "left": {
                        "min": 0
                    },
                    "right": {
                        "min": 0
                    }
                }
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 43,
            "width": 12,
            "height": 9,
            "properties": {
                "title": "Network Out (sum)",			
                "view": "timeSeries",
                "stacked": false,
                "metrics": [],
                "region": "",
                "stat": "Sum",
                "period": 60,
                "yAxis": {
                    "left": {
                        "min": 0
                    },
                    "right": {
                        "min": 0
                    }
                }
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 52,
            "width": 12,
            "height": 12,
            "properties": {
                "title": "Active Output Renditions (avg)",			
                "view": "timeSeries",
                "stacked": true,
                "metrics": [],
                "region": "",
                "stat": "Average",
                "period": 60,
                "yAxis": {
                    "left": {
                        "min": 0
                    }
                }
            }
        },
        {
            "type": "text",
            "x": 12,
            "y": 64,
            "width": 12,
            "height": 6,
            "properties": {
                "markdown": "# Console Links for all channels\nHold down the Control (Ctrl) key when selecting a link 
                to open the console in a new tab within the browser.   \n\n"
            }
        }        
    ]
}"""


# General functions
def usage(app_name):
    """Function that prints out a detailed help page for the script"""
    global version
    print '\npython {0} -a MediaLive_ARN -n Dashboard_Name [Optional parameters]\n'.format(app_name)
    print 'Version:', version
    print '\nThis script creates a CloudWatch Dashboard for a MediaLive/MediaPackage workflow.'
    print "It uses the MediaLive Channel Arn as input and determines the MediaPackage instances from the "
    print "MediaLive channel configuration. It then creates the CloudWatch Dashboard that contains info on the"
    print "MediaLive channel, the two MediaPackage channels, and all of the MediaPackage endpoints."
    print "\nRequired parameters:"
    print "-a, --arn:    MediaLive Channel ARN"
    print "-n, --name:   Name for the CloudWatch Dashboard. "
    print ""
    print "Optional parameters"
    print "-l, --list:   Filename of a file that contains a list of MediaLive Channel ARNs, 1 ARN per line. "
    print "              All MediaLive channels and their corresponding MediaPackage channels will be included in "
    print "              the CloudWatch Dashboard."
    print "              Note: This parameter is ignored if a channel ARN is provided via the '-a/--arn' option"
    print "              Note: All ARNs in the list must be for channels in the same region. All ARNs not in the same"
    print "              region as the first ARN in the list will be ignored."
    print '-h, --help:   Print this help and exit.'
    print ""
    print 'Examples:'
    print ""
    print 'Using MediaLive ARN arn:aws:medialive:us-west-2:0123456789:channel:123456 and create a CloudWatch ' \
          'Dashboard called "My TV Dashboard"'
    print 'python {0} -a arn:aws:medialive:us-west-2:0123456789:channel:123456 ' \
          '-n "My TV Dashboard" '.format(app_name)
    print ""
    print 'Using the MediaLive Channel ARN list defined in the text file "My EML arns.txt" create a CloudWatch' \
          'Dashboard called "Primary Bouquet".'
    print 'python {0} -l "My EML arns.txt" -n "Primary Bouquet"\n'.format(app_name)


def print_mini_help(app_name):
    """Print statement showing how to use the '-h/--help' option to get help on proper usage of the script"""
    print "\nExecute the script with either '-h' or '--help' to obtain detailed help on how to run the script:"
    print 'python {0} -h'.format(app_name)
    print "or"
    print 'python {0} --help\n'.format(app_name)


def is_valid_medialive_channel_arn(mlive_channel_arn):
    """Determine if the ARN provided is a valid / complete MediaLive Channel ARN"""
    if mlive_channel_arn.startswith("arn:aws:medialive:") and "channel" in mlive_channel_arn:
        return True
    else:
        return False


def extract_medialive_region(ml_channel_arn):
    """"Given a MediaLive Channel Arn determine the region the channel is in."""
    region = None
    # arn:aws:medialive:us-west-2:0123456789:channel:123456
    if is_valid_medialive_channel_arn(ml_channel_arn):
        arn_parts = ml_channel_arn.split(":")
        if len(arn_parts) == 7:
            region = arn_parts[3]
    return region


def extract_medialive_channel_id(ml_channel_arn):
    """Given a MediaLive Channel ARN, return the MediaLive Channel ID"""
    ml_channel_id = None
    if is_valid_medialive_channel_arn(ml_channel_arn):
        ml_channel_id = ml_channel_arn.strip().split(":")[-1]
    return ml_channel_id


def load_eml_arn_list(ml_list_file):
    """Load the MediaLive Channel ARNs defined in "ml_list_file" and return as a list.
    All MediaLive Channels must be in the same region to be eligble for inclusion into a CloudWatch Dashboard metric
    widget. Therefore only Channel ARNs in the same region as the first Channel ARN in the list will be returned.
    Additionally, any duplicate ARNs will be discarded as well."""
    first_region = None
    is_first_arn = True
    result = []
    try:
        with open(ml_list_file, "rt") as in_file:
            for line in in_file:
                line = line.strip()
                if is_valid_medialive_channel_arn(line):
                    current_region = extract_medialive_region(line)
                    if is_first_arn:
                        first_region = current_region
                        is_first_arn = False
                    if current_region == first_region:
                        if line not in result:
                            result.append(line)
                        else:
                            print "Skipping duplicate MediaLive ARN '{0}', since it already exists in the " \
                                  "list".format(line)
                    else:
                        print "Ignoring MediaLive ARN '{0}', since it's not in the same region as the first " \
                              "ARN in the list.".format(line)
                else:
                    if line is not "":
                        print "'{0}' is not a valid MediaLive Channel ARN".format(line)
        return result
    except Exception, e:
        print "Error: Processing EML Channel ARN List file '{0}'\n{1}".format(ml_list_file, e.message)


# MediaLive related functions
def create_medialive_client_instance(ml_region):
    """Create a MediaLive Client Instance for the region specified in "ml_region". """
    try:
        medialive = boto3.client('medialive', region_name=ml_region)
        return medialive
    except Exception, e:
        print "Error: Creating a MediaLive Client instance:\n '{0}'".format(e.message)
        exit(-1)


def extract_medialive_channel_info(ml_client, ml_channel_id):
    """Perform a list-channels query against all MediaLive channel in the region specified by the
    MediaLive Channel ID and retrieve the MediaLive Channel Name, and MediaPackage Channel ARNs
    Returns: MediaLive_Channel_Name & a list of MediaPackage channels"""
    mediapackage_channel_list = []
    channel_name = None
    try:
        response = ml_client.describe_channel(
            ChannelId=ml_channel_id
        )
        channel_name = str(response["Name"])
        destinations = response["Destinations"]
        for destination in destinations:
            for output in destination["Settings"]:
                url = str(output["Url"])
                if "mediapackage" in url:
                    mediapackage_channel_list.append(url)
    except Exception, e:
        print "Error:", e.message
    return channel_name, mediapackage_channel_list


def extract_medialive_outputgroup_names(ml_client, ml_channel_id):
    """given the MediaLive Channel ID "ml_channel_id" retrieve a list of all Output Group Names defined in the
    channel configuration."""
    mp_outputgroup_names = []
    try:
        channel_response = ml_client.describe_channel(ChannelId=ml_channel_id)
        outputgroups = channel_response["EncoderSettings"]["OutputGroups"]
        for outputgroup in outputgroups:
            groupname = str(outputgroup["Name"])
            mp_outputgroup_names.append(groupname)
        return mp_outputgroup_names
    except Exception, e:
        print "Error: Unable to perform the describe-channel() query for the MediaLive Channel", ml_channel_id
        print "Error message:", e


# MediaPackage related functions
def create_mediapackage_client_instance(mp_region):
    """Create a MediaPackage Client Instance for the region specified in "mp_region". """
    try:
        mediapackage = boto3.client('mediapackage', region_name=mp_region)
        return mediapackage
    except Exception, e:
        print "Error: Creating a MediaPackage Client instance '{0}'".format(e.message)


def extract_mediapackage_channel_names(mp_client, mediapackage_url_list, ml_region):
    """Using the list-channels query, in the region "ml_region", find the MediaPackage Channel Id for the MediaPackage 
    Channels defined in "mediapackage_url_list"."""
    mp_uids = []
    mp_channel_names = []
    for mediapackage_url in mediapackage_url_list:
        if "mediapackage." + ml_region in mediapackage_url:
            if "/v1/" in mediapackage_url:
                url_parts = mediapackage_url.split("/")
                if len(url_parts) == 7:
                    emp_ch_id = url_parts[5]
                    mp_uids.append(emp_ch_id)
            elif "/v2/" in mediapackage_url:
                url_parts = mediapackage_url.split("/")
                if len(url_parts) == 8:
                    emp_ch_id = url_parts[5]
                    if emp_ch_id not in mp_uids:
                        mp_uids.append(emp_ch_id)
    if len(mp_uids) > 0:
        response = mp_client.list_channels()
        for channel in response["Channels"]:
            channel_arn = channel["Arn"]
            channel_uid = channel_arn.split("/")[-1]
            if channel_uid in mp_uids:
                mp_channel_names.append(channel["Id"])
    return mp_channel_names


def extract_mediapackage_endpoints(mp_client, mp_channel_id_list):
    """Using the list_origin_endpoints query, find all the MediaPackage endpoints for the MediaPackage
    channels defined in "mediapackage_channel_id_list" """
    emp_endpoint_list = {}
    for channel in mp_channel_id_list:
        emp_endpoint_list[str(channel)] = []
    response = mp_client.list_origin_endpoints()
    for endpoint in response['OriginEndpoints']:
        if str(endpoint["ChannelId"]) in mp_channel_id_list:
            emp_endpoint_list[str(endpoint["ChannelId"])].append(str(endpoint['Id']))
    return emp_endpoint_list


# CloudWatch related functions
def create_cloudwatch_client_instance():
    """Create a CloudWatch Client Instance. """
    try:
        cloudwatch = boto3.client('cloudwatch')
        return cloudwatch
    except Exception, e:
        print "Error: Creating a CloudWatch Client instance:\n '{0}'".format(e.message)
        exit(-1)


def extract_cw_metrics_output_names(cw_client, ml_channel_id):
    """Retrieve a list of MediaLive OutputNames for all Outputs defined in the OutputVideoFrameRate CloudWatch Metric 
    of the MediaLive defined by the MediaLive Channel ID "ml_channel_id" """
    output_name_list = []
    try:
        paginator = cw_client.get_paginator('list_metrics')
        for response in paginator.paginate(Dimensions=[{'Name': 'ChannelId', 'Value': ml_channel_id},
                                                       {'Name': 'OutputName'},
                                                       {'Name': 'Pipeline'}],
                                           MetricName='OutputVideoFrameRate',
                                           Namespace='MediaLive'):
            if len(response["Metrics"]) > 0:
                for metric in response["Metrics"]:
                    entry = {}
                    dimensions = metric["Dimensions"]
                    for dimension in dimensions:
                        if dimension["Name"] == "OutputName":
                            entry["OutputName"] = dimension["Value"]
                        elif dimension["Name"] == "ChannelId":
                            entry["ChannelId"] = dimension["Value"]
                        elif dimension["Name"] == "Pipeline":
                            entry["Pipeline"] = dimension["Value"]
                            output_name_list.append(entry)
        return output_name_list
    except Exception, e:
        print "Error while retrieving CloudWatch OutputName information", e.message


def create_cloudwatch_dashboard(cw_client, cw_dashboard_name, cw_dashboard_body):
    """Use put_dashboard to create a new CloudWatch Dashboard named "cw_dashboard_name" that consists of the definition
    as defined in "cw_dashboard_body" """
    try:
        cw_dashboard_name = cw_dashboard_name.replace(" ", "-")
        response = cw_client.put_dashboard(
            DashboardName=cw_dashboard_name,
            DashboardBody=cw_dashboard_body
        )
        result_code = response["ResponseMetadata"]["HTTPStatusCode"]
        if result_code == 200:
            print "Successfully created Dashboard '{0}'".format(cw_dashboard_name)
        else:
            print "HTTP Status Code:", result_code
    except Exception, e:
        print "Error while trying to create new CloudWatch Dashboard:\n", e.message
        exit(-5)


# CloudWatch Dashboard metrics related
def update_ingress_bytes_metric(mp_channel_names):
    """Update the metrics of the "Ingress Bytes (sum)" dashboard widget """
    results = []
    for mp_name in mp_channel_names:
        entry = ["AWS/MediaPackage", "IngressBytes", "Channel", mp_name]
        results.append(entry)
    return results


def update_ingress_resp_times_metric(mp_channel_names):
    """Update the metrics of the "Ingress Response Times (avg)" dashboard widget"""
    results = []
    for mp_name in mp_channel_names:
        entry = ["AWS/MediaPackage", "IngressResponseTime", "Channel", mp_name]
        results.append(entry)
    return results


def update_egress_req_bytes_metric(mp_endpoint_names):
    """Update the metrics of the "Egress Request Bytes (sum)" dashboard widget"""
    results = []
    for mp_name in mp_endpoint_names:
        endpoints = mp_endpoint_names[mp_name]
        for endpoint in endpoints:
            entry = ["AWS/MediaPackage", "EgressBytes", "Channel", mp_name, "OriginEndpoint", endpoint]
            results.append(entry)
    return results


def update_egress_req_count_metric(mp_endpoint_names):
    """Update the metrics of the "Egress Request Count (sum)" dashboard widget"""
    results = []
    for mp_name in mp_endpoint_names:
        endpoints = mp_endpoint_names[mp_name]
        for endpoint in endpoints:
            entry = ["AWS/MediaPackage", "EgressRequestCount", "Channel", mp_name, "OriginEndpoint", endpoint]
            results.append(entry)
    return results


def update_status_code_range_2xx4xx_metric(mp_endpoint_names):
    """Update the metrics of the "Status Code Range (sum)" dashboard widget"""
    results = []
    for mp_name in mp_endpoint_names:
        endpoints = mp_endpoint_names[mp_name]
        for endpoint in endpoints:
            entry = ["AWS/MediaPackage", "EgressRequestCount", "Channel", mp_name, "OriginEndpoint", endpoint,
                     "StatusCodeRange", "2xx"]
            results.append(entry)
            entry = ["AWS/MediaPackage", "EgressRequestCount", "Channel", mp_name, "OriginEndpoint", endpoint,
                     "StatusCodeRange", "4xx", {"yAxis": "right"}]
            results.append(entry)
    return results


def update_status_code_range_3xx5xx_metric(mp_endpoint_names):
    """Update the metrics of the "Status Code Range (sum)" dashboard widget"""
    results = []
    for mp_name in mp_endpoint_names:
        endpoints = mp_endpoint_names[mp_name]
        for endpoint in endpoints:
            entry = ["AWS/MediaPackage", "EgressRequestCount", "Channel", mp_name, "OriginEndpoint", endpoint,
                     "StatusCodeRange", "3xx"]
            results.append(entry)
            entry = ["AWS/MediaPackage", "EgressRequestCount", "Channel", mp_name, "OriginEndpoint", endpoint,
                     "StatusCodeRange", "5xx", {"yAxis": "right"}]
            results.append(entry)
    return results


def update_input_video_frame_rate_metric(ml_channel_id, ml_channel_name):
    """Update the metrics of the "Input Video Frame Rate (avg)" dashboard widget"""
    result = []
    entry = ["MediaLive", "InputVideoFrameRate", "ChannelId", ml_channel_id, "Pipeline", "0",
             {"label": ml_channel_name + "-0"}]
    result.append(entry)
    entry = ["MediaLive", "InputVideoFrameRate", "ChannelId", ml_channel_id, "Pipeline", "1",
             {"yAxis": "right", "label": ml_channel_name + "-1"}]
    result.append(entry)
    return result


def update_network_in_metric(ml_channel_id, ml_channel_name):
    """Update the metrics of the "Network In (sum)" dashboard dashboard widget"""
    result = []
    entry = ["MediaLive", "NetworkIn", "ChannelId", ml_channel_id, "Pipeline", "0", {"label": ml_channel_name + "-0"}]
    result.append(entry)
    entry = ["MediaLive", "NetworkIn", "ChannelId", ml_channel_id, "Pipeline", "1", {"yAxis": "right",
                                                                                     "label": ml_channel_name + "-1"}]
    result.append(entry)
    return result


def update_dropped_frames_metric(ml_channel_id, ml_channel_name):
    """Update the metrics of the "Dropped Frames (sum)" dashboard dashboard widget"""
    result = []
    entry = ["MediaLive", "DroppedFrames", "ChannelId", ml_channel_id, "Pipeline", "0",
             {"label": ml_channel_name + "-0"}]
    result.append(entry)
    entry = ["MediaLive", "DroppedFrames", "ChannelId", ml_channel_id, "Pipeline", "1",
             {"yAxis": "right", "label": ml_channel_name + "-1"}]
    result.append(entry)
    return result


def update_fill_msec_metric(ml_channel_id, ml_channel_name):
    """Update the metrics of the "Fill Milliseconds (sum)" dashboard dashboard widget"""
    result = []
    entry = ["MediaLive", "FillMsec", "ChannelId", ml_channel_id, "Pipeline", "0", {"label": ml_channel_name + "-0"}]
    result.append(entry)
    entry = ["MediaLive", "FillMsec", "ChannelId", ml_channel_id, "Pipeline", "1", {"yAxis": "right",
                                                                                    "label": ml_channel_name + "-1"}]
    result.append(entry)
    return result


def update_svq_time_metric(ml_channel_id, ml_channel_name):
    """Update the metrics of the "SVQ Time (percentage)" dashboard dashboard widget"""
    result = []
    entry = ["MediaLive", "SvqTime", "ChannelId", ml_channel_id, "Pipeline", "0", {"label": ml_channel_name + "-0"}]
    result.append(entry)
    entry = ["MediaLive", "SvqTime", "ChannelId", ml_channel_id, "Pipeline", "1", {"yAxis": "right",
                                                                                   "label": ml_channel_name + "-1"}]
    result.append(entry)
    return result


def update_output_frame_video_rate_metric(ml_output_names):
    """Update the metrics of the "Output Video Frame Rate (avg)" dashboard dashboard widget"""
    result = []
    for output in ml_output_names:
        if output["Pipeline"] == "0":
            entry = ["MediaLive", "OutputVideoFrameRate", "ChannelId", output["ChannelId"], "OutputName",
                     output["OutputName"], "Pipeline", "0"]
            result.append(entry)
        elif output["Pipeline"] == "1":
            entry = ["MediaLive", "OutputVideoFrameRate", "ChannelId", output["ChannelId"], "OutputName",
                     output["OutputName"], "Pipeline", "1", {"yAxis": "right"}]
            result.append(entry)
    return result


def update_network_output_metric(ml_channel_id, ml_channel_name):
    """Update the metrics of the "Network Out (sum)" dashboard dashboard widget"""
    result = []
    entry = ["MediaLive", "NetworkOut", "ChannelId", ml_channel_id, "Pipeline", "0", {"label": ml_channel_name + "-0"}]
    result.append(entry)
    entry = ["MediaLive", "NetworkOut", "ChannelId", ml_channel_id, "Pipeline", "1", {"yAxis": "right",
                                                                                      "label": ml_channel_name + "-1"}]
    result.append(entry)
    return result


def update_active_output_renditions_metric(ml_channel_id, ml_channel_name, ml_channelgroup_names):
    """Update the metrics of the "Active Output Renditions (avg)" dashboard dashboard widget"""
    results = []
    for groupname in ml_channelgroup_names:
        entry = ["MediaLive", "ActiveOutputs", "OutputGroupName", groupname, "ChannelId", ml_channel_id,
                 "Pipeline", "0", {"label": ml_channel_name + "-0"}]
        results.append(entry)
        entry = ["MediaLive", "ActiveOutputs", "OutputGroupName", groupname, "ChannelId", ml_channel_id,
                 "Pipeline", "1", {"yAxis": "right", "label": ml_channel_name + "-1"}]
        results.append(entry)
    return results


def update_console_links_markdown(region, ml_channel_name, ml_channel_id, mp_channel_names):
    """Update the markdown of the text widget to show the list of console links for the specific MediaLive and
    MediaPackage channels"""
    result = "MediaLive: [{0} - {1}](https://{2}.console.aws.amazon.com/medialive/home?region={2}#/" \
             "channels/{1}) MediaPackage: ".format(ml_channel_name, ml_channel_id, region)
    mp_name_count = len(mp_channel_names)
    index = 1
    for mp_name in mp_channel_names:
        tmp = " [{0}](https://{1}.console.aws.amazon.com/mediapackage/home?region={1}#/channels" \
              "/{0})".format(mp_name, region)
        if index < mp_name_count:
            tmp += " , "
        index += 1
        result += tmp
    result += "   \n"
    return result


def process_all_medialive_channels(ml_channel_list, cw_dashboard_name):
    """Given a list of all MediaLive Channel ARNs process them one at time and update the CloudWatch Dashboard 
    template"""
    global dashboard_template
    eml_region = extract_medialive_region(ml_channel_list[0])
    if eml_region is None:
        print "Error: Unable to extract the Region from the MediaLive Channel ARN '{0}'.".format(ml_channel_list[0])
        exit(-3)
    eml_client = create_medialive_client_instance(eml_region)
    cw_client = create_cloudwatch_client_instance()
    emp_client = create_mediapackage_client_instance(eml_region)

    dashboard_json = json.loads(dashboard_template, strict=False)

    # Update the titles of the 2 sections within the dashboard
    for widget in dashboard_json["widgets"]:
        if widget["type"] == "text":
            text_title = widget["properties"]["markdown"]
            if "MediaPackage Section Title" in text_title:
                widget["properties"]["markdown"] = "# {0}: Packaging and Origination".format(cw_dashboard_name)
            if "MediaLive Section Title" in text_title:
                widget["properties"]["markdown"] = "# {0}: Encoding".format(cw_dashboard_name)

    for ml_channel_arn in ml_channel_list:
        print "Retrieving information from MediaLive channel", ml_channel_arn
        eml_channel_id = extract_medialive_channel_id(ml_channel_arn)
        if eml_channel_id is None:
            print "Error: Verify the MediaLive Channel ARN"
            exit(-4)
        eml_channel_name, emp_channel_arn_list = extract_medialive_channel_info(eml_client, eml_channel_id)
        if eml_channel_name is None or emp_channel_arn_list == []:
            print "Error: Retrieving MediaLive Name and\or MediaPackage Destinations from the MediaLive Channel " \
                  "configuration."
            exit(-3)
        print "MediaLive Channel Name: ", eml_channel_name
        eml_outputgroup_names = extract_medialive_outputgroup_names(eml_client, eml_channel_id)
        eml_output_names = extract_cw_metrics_output_names(cw_client, eml_channel_id)

        print "Retrieving information from the MediaPackage channels"
        emp_channel_names = extract_mediapackage_channel_names(emp_client, emp_channel_arn_list, eml_region)
        emp_endpoint_names = extract_mediapackage_endpoints(emp_client, emp_channel_names)

        for widget in dashboard_json["widgets"]:
            if widget["type"] == "metric":
                metrics = []
                metric_title = widget["properties"]["title"]
                if "Ingress Bytes (sum)" in metric_title:
                    metrics += update_ingress_bytes_metric(emp_channel_names)
                elif "Ingress Response Times" in metric_title:
                    metrics += update_ingress_resp_times_metric(emp_channel_names)
                elif "Egress Request Bytes (sum)" in metric_title:
                    metrics += update_egress_req_bytes_metric(emp_endpoint_names)
                elif "Egress Request Count (sum)" in metric_title:
                    metrics += update_egress_req_count_metric(emp_endpoint_names)
                elif "Status Code Range (sum), 2xx,4xx" in metric_title:
                    metrics += update_status_code_range_2xx4xx_metric(emp_endpoint_names)
                elif "Status Code Range (sum), 3xx,5xx" in metric_title:
                    metrics += update_status_code_range_3xx5xx_metric(emp_endpoint_names)
                elif "Active Output Renditions (avg)" in metric_title:
                    metrics += update_active_output_renditions_metric(eml_channel_id, eml_channel_name,
                                                                      eml_outputgroup_names)
                elif "Output Video Frame Rate (avg)" in metric_title:
                    metrics += update_output_frame_video_rate_metric(eml_output_names)
                elif "Input Video Frame Rate (avg)" in metric_title:
                    metrics += update_input_video_frame_rate_metric(eml_channel_id, eml_channel_name)
                elif "Network In (sum)" in metric_title:
                    metrics += update_network_in_metric(eml_channel_id, eml_channel_name)
                elif "Dropped Frames (sum)" in metric_title:
                    metrics += update_dropped_frames_metric(eml_channel_id, eml_channel_name)
                elif "Network Out (sum)" in metric_title:
                    metrics += update_network_output_metric(eml_channel_id, eml_channel_name)
                elif "SVQ Time (percentage)" in metric_title:
                    metrics += update_svq_time_metric(eml_channel_id, eml_channel_name)
                elif "Fill Milliseconds (sum)" in metric_title:
                    metrics += update_fill_msec_metric(eml_channel_id, eml_channel_name)
                else:
                    print "Unsupported metric '{0}' found in the dashboard template".format(metric_title)
                if len(metrics) > 0:
                    widget["properties"]["metrics"] += metrics
                    widget["properties"]["region"] = eml_region
            if widget["type"] == "text":
                markdown = widget["properties"]["markdown"]
                if "Console Links for all channels" in markdown:
                    tmp = update_console_links_markdown(eml_region, eml_channel_name, eml_channel_id, emp_channel_names)
                    widget["properties"]["markdown"] = markdown + tmp

    dashboard_template = json.dumps(dashboard_json, indent=4, sort_keys=True)
    create_cloudwatch_dashboard(cw_client, cw_dashboard_name, dashboard_template)


def main(argv=None):
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ha:n:l:', ['help', 'arn=', 'name=', 'list='])
    except getopt.GetoptError, err:
        print str(err)
        usage(sys.argv[0])
        exit(-1)
    if len(args) > 0:
        print "\nError in the command line options. Please validate that the fields were defined correctly."
        print "If the dashboard name consist of more than 1 word or contains spaces then please encapsulate the"
        print 'name in "", e.g. -n "My Dashboard name" '
        print_mini_help(sys.argv[0])
        exit()
    if len(sys.argv) == 1:
        usage(sys.argv[0])
        exit()
    medialive_channel_arn = None
    dashboard_name = None
    eml_list_filename = None
    eml_channel_arn_list = []
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(sys.argv[0])
            sys.exit(0)
        elif opt in ("-a", "--arn"):
            medialive_channel_arn = arg
            if not is_valid_medialive_channel_arn(medialive_channel_arn):
                print "Error: Invalid MediaLive Channel ARN '{0}'".format(medialive_channel_arn)
                exit(-2)  # without a valid MediaLive Channel ARN there is no reason to continue.
        elif opt in ("-n", "--name"):
            dashboard_name = arg
        elif opt in ("-l", "--list"):
            eml_list_filename = arg
            if not os.path.isfile(eml_list_filename):
                print "Error: File '{0}' doesn't exists or is not in the folder provided.".format(eml_list_filename)
                eml_list_filename = None
        else:
            assert False, "Unhandled option '{0}'".format(opt)

    if medialive_channel_arn is not None:
        eml_channel_arn_list = [medialive_channel_arn]
    elif medialive_channel_arn is None and eml_list_filename is not None:
        eml_channel_arn_list = load_eml_arn_list(eml_list_filename)
        arn_count = len(eml_channel_arn_list)
        print "\nFound {0} valid MediaLive Channel ARNs in the file {1}".format(arn_count, eml_list_filename)
        if arn_count == 0:
            print "\nMust provide a MediaLive Channel ARN or a file containing a list of MediaLive Channel ARNs"
            print_mini_help(sys.argv[0])
            exit(-1)  # Must have a MediaLive Channel ARN to continue
    elif medialive_channel_arn is None and len(eml_channel_arn_list) == 0:
        print "\nMust provide a MediaLive Channel ARN or a file containing a list of MediaLive Channel ARNs"
        print_mini_help(sys.argv[0])
        exit(-1)  # Must have a MediaLive Channel ARN to continue

    if dashboard_name is None:
        print '\nPlease provide a name for the Dashboard. Note to encapsulate the name in "" if it contains spaces.'
        exit()

    process_all_medialive_channels(eml_channel_arn_list, dashboard_name)


if __name__ == "__main__":
    sys.exit(main())
