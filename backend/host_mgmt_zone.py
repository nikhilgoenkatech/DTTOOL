import os
import io
import sys  
import json
import time
import pandas
import logging
import certifi
import smtplib
import datetime
import requests
import traceback
import xlsxwriter
import statistics
from email import encoders
from pandas import ExcelWriter
from matplotlib import pyplot as plt
from backend.constant_host_unit import *
from backend.err_code import *
from django_pandas.io import read_frame
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from advancedConfig.models import featureAdoptionCount, applicationDetails, problemDetails
sys.path.append("")

hostList = [] 

class app:
  def __init__(self):
   self.name = ""
   self.type = ""
   self.entityId = ""
   self.dem = 0
   self.consumption = 0
   self.key_requests = 0
   self.apdex_satisfied = 0
   self.overall_apdex = 0
   self.apdex_tolerated = 0
   self.conversion_goals = 0
   self.apdex_frustrated = 0 

class tenant_data:
  def __init__(self):
    self.tenant_dict = {}
    self.index_list = []
    #self.index_list = ["Applications", "Synthetic Browsers", "HTTP Browsers", "Host Groups","Process Groups", "Tags","Alerting Profiles","Management Zones","Naming Rules","Problem Notifications","Cloud Platform Integration","Key User Requests","API Token","Request Attributes"]

    self.tenant_license_dict = {}
    self.license_index_list = ["Host Units Consumption", "DEM Units Consumption"]

class problem_data:
  def __init__(self):
    self.service = 0
    self.resource = 0
    self.total_prb = 0
    self.prb_resolved = 0 
    self.error_event = 0
    self.performance = 0
    self.application = 0
    self.environment = 0
    self.infrastructure = 0
    self.availability_event = 0

class mgmt_zone_data:
  def __init__(self):
    self.dem = 0
    self.tag = 0
    self.req_attr = 0
    self.problems = 0
    self.host_units = 0
    self.host_group = 0
    self.api_tokens = 0
    self.syn_browser = 0
    self.http_browser = 0
    self.applications = 0
    self.process_group= 0
    self.naming_rules = 0
    self.cloud_integration = 0
    self.key_usr_actions = 0
    self.alerting_profile = 0
    self.problem_notification = 0
    self.configured_mgmt_zones = 0

class email_details:
  def __init__(self):
    self.smtpserver = ""
    self.username = ""
    self.password = ""
    self.port = 0
    self.senders_list = ""
    self.receivers_list = ""

class tenantInfo:
   def __init__(self):
     self.tenant_url = ""
     self.tenant_token = ""
     self.name = ""
#------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to initialize the email server
# Returns the smtp_server initialized 
#------------------------------------------------------------------------------
def initialize_email_server(err_msg, logger, smtp_server_details):
  try:
    logger.info("In initialize_email_server")

    smtp_server = smtplib.SMTP(smtp_server_details.smtpserver,smtp_server_details.port)
    smtp_server.ehlo()
    smtp_server.starttls()
    smtp_server.login(smtp_server_details.username, smtp_server_details.password)

  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"initialize_email_server")
    logger.error("Received exception while running initialize_email_server", exc_info=e)

  finally:
    logger.info("Execution sucessfull: initialize_email_server")
    return err_msg, smtp_server

#------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to send an email using the smtp_server initialized
# Returns: nothing 
#------------------------------------------------------------------------------

def send_email(err_msg, logger, smtp_server, content, smtp_server_details):
  try:
    logger.info("In send_email")
    logger.debug ("send_email: smtp_server = %s", smtp_server)
    logger.debug ("sender_list = %s", smtp_server_details.senders_list)
    logger.debug ("receiver_list = %s", smtp_server_details.receivers_list)
    content["From"] = smtp_server_details.senders_list
    content["To"] = smtp_server_details.receivers_list
    #smtp_server.sendmail(smtp_server_details.senders_list, (smtp_server_details.receivers_list).split(','), content.as_string())
    print (smtp_server_details.receivers_list)
    print (smtp_server_details.senders_list)
    smtp_server.sendmail(smtp_server_details.senders_list, (smtp_server_details.receivers_list).split(';'), content.as_string())

  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"send_email")
    logger.error("Received exception while running send_email", exc_info=e)
  finally:
    return err_msg

#------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to make API call using the token defined in constant.py
# Returns the json object returned using the API call
#------------------------------------------------------------------------------
def dtApiSpecificQuery(err_msg, logger, endpoint, tenant_info, URL="", item_id = ""):
  try:
    logger.info("In dtApiSpecificQuery")
    logger.debug ("dtApiSpecificQuery: endpoint = %s", endpoint)

    if URL == "":
      URL = tenant_info.tenant_url

    if item_id != "":
      endpoint = endpoint.replace("ID",item_id)

    query = str(URL) + str(endpoint)
    get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(tenant_info.tenant_token)}
    populate_data = requests.get(query, headers = get_param)

    if populate_data.status_code == 401:
      data = {} 
      err_msg = AUTHENTICATION_ERR
    else:
      data = populate_data.json()

  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"dtApiSpecificQuery")
    logger.error("Received exception while running dtApiSpecificQuery", exc_info = e)

  finally:
    logger.info("Execution sucessfull: dtApiSpecificQuery")
    return data, err_msg


#------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to make API call using the token defined in constant.py
# Returns the json object returned using the API call 
#------------------------------------------------------------------------------
def dtApiQuery(err_msg, logger, endpoint, tenant_info, URL=""):
  try:
    data = {}
    logger.info("In dtApiQuery")
    logger.debug ("dtApiQuery: endpoint = %s", endpoint)

    if URL == "":
      URL = tenant_info.tenant_url

    query = str(URL) + str(endpoint)
    get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(tenant_info.tenant_token)}
    populate_data = requests.get(query, headers = get_param)
    if populate_data.status_code >=200 and populate_data.status_code <= 400:
      data = populate_data.json() 

    elif populate_data.status_code == 401:
      err_msg = AUTHENTICATION_ERR 

  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"dtApiQuery")
    logger.error("Received exception while running dtApiQuery ", exc_info = e) 

  finally:
    logger.info("Execution sucessfull: dtApiQuery - " + err_msg)
    return data, err_msg

#---------------------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to print the entire structure of app_mgmt_zone (will be used for debugging) 
#---------------------------------------------------------------------------------------------
def pretty_print(err_msg, logger, app_mgmt_zone):
  try:
    logger.info("In pretty_print")
    for mgmt_zone_name in app_mgmt_zone.keys():
        for i in range(len(app_mgmt_zone[mgmt_zone_name])):
          print (mgmt_zone_name + " " + str(len(app_mgmt_zone[mgmt_zone_name])) + "." + app_mgmt_zone[mgmt_zone_name][i].name + "\t" + str(app_mgmt_zone[mgmt_zone_name][i].consumption) + "\t" + str(app_mgmt_zone[mgmt_zone_name][i].dem) + "\n")
  except Exception as e:
    logger.fatal("Received exception while running pretty_print", str(e), exc_info=True)


def form_list(err_msg, logger, html, table_list, tenant_info, mgmt_zone, app_mgmt_zone):
    try:
      logger.info("In form_list: ")
      logger.debug("In form_list%s: ", table_list)

      for key in mgmt_zone.keys():
        try:
          total_consumption = 0
          for i in range(len(app_mgmt_zone[key])):
            total_consumption = total_consumption + app_mgmt_zone[key][i].dem
        except KeyError:
          total_consumption = 0.0
        finally:
          try:
            obj = mgmt_zone[key]
          except KeyError:
            mgmt_zone[key].dem = 0.0
          finally:
            mgmt_zone[key].dem = total_consumption 
 
      for key in app_mgmt_zone.keys():
        total_consumption = 0
        for i in range(len(app_mgmt_zone[key])):
          total_consumption = float(total_consumption) + app_mgmt_zone[key][i].dem

        try:
          host_units = mgmt_zone[key].host_units
        except KeyError:
          host_units = "0.0"
        finally:
          try:
            obj = mgmt_zone[key]
          except KeyError:
            obj = mgmt_zone_data()
            obj.dem = 0.0
            mgmt_zone[key] = obj 
          finally:
            mgmt_zone[key].dem = total_consumption
 

      #html = html.format(tenant_name=tenant_info.name, table=tabulate(table_list, headers="firstrow", tablefmt = "html"))
    except Exception as e:
      err_msg = EXCEPTION_RCVD.format(e,"form_list")
      logger.error ("Received error while executing form_list", exc_info=e)
     
    finally:
      return table_list, err_msg

#------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to create the html header 
# Returns: hmtl 
#------------------------------------------------------------------------------
def html_header(err_msg, logger):
    try:
      logger.info("In html_header: ")
      html = """
      <img border="10" src="cid:header">
      <br></br>Dear Team,<br></br>
      Please find below the licensing consumption information for the configured tenants.<br></br>

      <img border="10" height="450" width="900" src="cid:license">
      <br></br>
      <font size=2>*Please note the DEM-unit consumption is for the past 3-months. Host-units consumption is pulled from the running-hosts.</font><br></br>

      <br></br>
      To optimize license usage, configure some of the Dynatrace features that can help in your journey to achieve complex use-cases like AIOps or simpler day-to-day monitoring tasks. 

      <br></br>
      <br></br>
      <a href="https://www.dynatrace.com/support/help/shortlink/rum-application-concept"><b><u>Applications</a></b></u>: Applications count would highlight if the Real User Monitoring has been enabled on your applications.<br></br>
      <a href="https://www.dynatrace.com/support/help/shortlink/synthetic-hub"><b><u>Synthetic Browsers</a></b></u>: Configuring Synthetic Browsers will help to monitor your application performance from AWS instance hosted in different geographical locations.<br></br>
      <a href="https://www.dynatrace.com/support/help/shortlink/synthetic-hub#http-monitors"><b><u>HTTP Browsers</a></b></u>: HTTP monitors will try to reach the end point and collect results.<br></br>
      <a href="https://www.dynatrace.com/support/help/shortlink/host-groups"><b><u>Host Groups</a></b></u>: Setting up Host-group would help to organize the environment better.<br></br>
      <a href="https://www.dynatrace.com/support/help/shortlink/processes-hub"><b><u>Process Groups</a></b></u>: Setting up process-group will provide fine tuning to the automatically identified process groups.<br></br>
      <a href="https://www.dynatrace.com/support/help/shortlink/tags-and-metadata-hub"><b><u>Tags</a></b></u>: Tags help to maintain large environments and view in a way to suit your team(s).<br></br>
      <a href="https://www.dynatrace.com/support/help/shortlink/alerting-profiles"><b><u>Alerting Profiles</a></b></u>: Alerting profiles will enable to configure problem notifications based on different severity/teams.<br></br>
      <a href="https://www.dynatrace.com/support/help/shortlink/management-zones-hub"><b><u>Management Zones</a></b></u>: Management zones allow to create logical boundaries to view and slice data for different teams.<br></br>
      <a href="https://www.dynatrace.com/support/help/shortlink/request-attributes-naming-rules"><b><u>Naming Rules</a></b></u>: Naming rules enables to better refine request identities across services.<br></br>
      <a href="https://www.dynatrace.com/support/help/shortlink/third-party-integrations-hub"><b><u>Problem Notification</a></b></u>: Problem notification would enable to push problem to 3rd party platform like slack, email, etc..<br></br>
      <a href="https://www.dynatrace.com/support/help/shortlink/section-cloud-platforms"><b><u>Cloud Platform Integration</a></b></u>: Dynatrace support cloud integration with varios cloud technologies - configuring any cloud technologies would give additional visibility into them.<br></br>
      <a href="https://www.dynatrace.com/support/help/shortlink/key-requests"><b><u>Key User Requests</a></b></u>: Configuring a request as key-request enables to quickly access the request, have them pinned to dashboard and additional data retention.<br></br>
      <a href="https://www.dynatrace.com/support/help/shortlink/section-api"><b><u>API Tokens</a></b></u>: Dynatrace API is gateway to pull/push data into Dynatrace to automate your monitoring tasks or export into 3rd party reporting.<br></br>
      <a href="https://www.dynatrace.com/support/help/shortlink/request-attributes" style="color:blue"><b><u>Request Attributes</a></b></u>: Request-attributes are key/value pairs that can be fetched at request-level. Request attributes once configured can help developers/business users additional data.<br></br>
   
      <br></br>
      Please find below the feature adoption for your configured tenants:
      <br></br>
 
      <img border="10" height="450" width="900" src="cid:image1">
      <br></br>
      <br></br>
      Share the report with Dynatrace-PS team to get deeper analysis and the next steps.
      <br></br>
      """
    except Exception as e:
      err_msg = EXCEPTION_RCVD.format(e,"html_header_pdf")
      logger.error ("Received error while executing html_header_pdf %s", exc_info=e)

    finally:
      logger.info("Succesfully completed html_header")
      return html, err_msg

def html_footer(err_msg, logger, html, content):
    try:
      logger.info("In html_footer : ")
      logger.debug("In html_footer %s: ", content)

      html = html + """ 
      <center>
      <p style="text-align:left;">Regards, </p>
      <p style="text-align:left;">Dynatrace Team </p>
      <img border="10" src="cid:footer">
      </body>
      """

      content.attach(MIMEText(html, "html"))
      msgAlternative = MIMEMultipart('alternative')
      content.attach(msgAlternative)

      fp = open('Email_Template_01.jpg','rb')
      msgImage = MIMEImage(fp.read())
      fp.close()

      msgImage.add_header('Content-ID', '<header>')
      content.attach(msgImage)

      fp = open('Email_Template_03.jpg','rb')
      msgImage = MIMEImage(fp.read())
      fp.close()

      msgImage.add_header('Content-ID', '<footer>')
      content.attach(msgImage)
      fp = open('image1.png','rb')
      msgImage = MIMEImage(fp.read())
      fp.close()

      msgImage.add_header('Content-ID', '<image1>')
      content.attach(msgImage)

      fp = open('license.png','rb')
      msgImage = MIMEImage(fp.read())
      fp.close()

      msgImage.add_header('Content-ID', '<license>')
      content.attach(msgImage)

      cwd = os.getcwd()
      for file in os.listdir(cwd):
        if file.endswith(".xlsx"):
          filename = os.path.join(cwd, file)
          part = MIMEBase('application', "octet-stream")
          part.set_payload(open(filename, "rb").read())
          encoders.encode_base64(part)
          part.add_header('Content-Disposition', 'attachment; filename=%s"' % file)
          content.attach(part)

    except Exception as e:
      err_msg = EXCEPTION_RCVD.format(e,"html_footer")
      logger.error ("Received error while executing html_footer %s", exc_info=e)
     
    finally:
      return content, err_msg
#-----------------------------------------------------------------------
# Function to fetch problem in the last month
#------------------------------------------------------------------------
def fetch_problems(err_msg, logger, problem_mgmt_zone, tenant_info):
  try:
    logger.info("In fetch_problems")
    problem_rsp, err_msg = dtApiQuery(err_msg, logger, PROBLEMS, tenant_info)

    if err_msg == "":
      if problem_rsp != None:
        problem_list = problem_rsp["result"]["problems"]
    

      total_prb = 0
      service = 0
      resource = 0
      availability = 0
      error_event = 0
      performance = 0
      application = 0
      environment = 0
      infrastructure = 0 
      total_prb_resolved = 0 
      mean_rsp_time=[]

      for i in range(len(problem_list)):
        severity = problem_list[i]["severityLevel"]
        if severity == "AVAILABILITY":
          availability = availability + 1 
        elif severity == "PERFORMANCE":
          performance = performance + 1
        elif severity == "ERROR":
          error_event = error_event + 1
        elif severity == "RESOURCE_CONTENTION":
          resource = resource + 1

        impact_level = problem_list[i]["impactLevel"]
        if impact_level == "SERVICE":
          service = service + 1 
        elif impact_level == "APPLICATION":
          application = application + 1
        elif impact_level == "INFRASTRUCTURE":
          infrastructure = infrastructure + 1
        elif impact_level == "ENVIRONMENT":
          environment = environment + 1
        
        start_time = problem_list[i]["startTime"]
        end_time = problem_list[i]["endTime"]

        if end_time != -1:
          total_prb_resolved = total_prb_resolved + 1
          resolution_time = end_time - start_time
          mean_rsp_time.append(resolution_time)

      median_rsp_time = statistics.mean(mean_rsp_time)
      print ("\n\n\nStatistics = " + str(median_rsp_time))

      problem_mgmt_zone["Tenant"] = tenant_info.name
      problem_mgmt_zone["Total Problems"] = len(problem_list) 
      problem_mgmt_zone["Problems Resolved"] = total_prb_resolved 
      problem_mgmt_zone["Severity - Resource"] = resource 
      problem_mgmt_zone["Severity - Error"] = error_event
      problem_mgmt_zone["Severity - Performance"] = performance
      problem_mgmt_zone["Severity - Availability"] = availability
      problem_mgmt_zone["Impact - Environment"] = environment 
      problem_mgmt_zone["Impact - Service"] = service
      problem_mgmt_zone["Impact - Application"] = application
      problem_mgmt_zone["Impact - Infrastructure"] = infrastructure 
      problem_mgmt_zone["Mean Response Time"] = median_rsp_time 
    else:
      err_msg = err_msg.format("Problem","Problem feed")

  except Exception:
    err_msg = EXCEPTION_RCVD.format(e,"fetch_problems")
    logger.error("Exception caused while fetch_problems", exc_info=e)

  finally:
    return problem_mgmt_zone, err_msg 

#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the excel file
#------------------------------------------------------------------------
def func(err_msg, logger, totalHostUnits, smtp_server, smtp_server_details, html, tenant_info, table_list, email_body, mgmt_zone, app_mgmt_zone, problem_mgmt_zone, featureObj):
  try:
    logger.info("In func")
    logger.debug("func: totalHostUnits = %s", totalHostUnits)  
    logger.debug("func: smtp_server = %s", smtp_server)
    logger.debug("func: smtp_server = %s", smtp_server_details)

    hosts, err_msg = dtApiQuery(err_msg, logger, INFRA_API, tenant_info)
    print (hosts)
    print (err_msg)
    host_group = 0

    logger.debug(hosts)
    for host in hosts:
      logger.debug(host)
      key = ""

      #Management Zone
      try:
        zones = host['managementZones']
        for zone in zones:
          key = key + zone['name'] + ","
        key = key[:-1]
      except KeyError:
        key = "No management zone"

      try:
        if host['hostGroup']:
          host_group = host_group + 1
      except KeyError:
          print ("No Host group - " + host['displayName'])
          pass

      try:
        obj = mgmt_zone[key]
        obj.host_units = obj.host_units + float(host['consumedHostUnits']) 
        mgmt_zone[key] = obj 

      except KeyError:
        obj = mgmt_zone_data()
        obj.host_units = float(host['consumedHostUnits']) 
        mgmt_zone[key] = obj 
    
      #print "Host -> ", host['displayName'] +  " -> " + str(key) + " -> " + str(mgmt_zone[key])

    #First fetch all the applications
    try:
      obj = mgmt_zone["No management zone"]
    except KeyError:
      obj = mgmt_zone_data()
    finally:
      obj.host_group = host_group 
      mgmt_zone["No management zone"] = obj

    app_mgmt_zone, mgmt_zone, err_msg = fetch_application(err_msg, logger, app_mgmt_zone, tenant_info, FETCH_APPLICATIONS, mgmt_zone, featureObj)
    if err_msg != "":
      return problem_mgmt_zone, app_mgmt_zone, mgmt_zone, table_list, html, err_msg
     
    #Now fetch all the synthetic applications 
    app_mgmt_zone, mgmt_zone, err_msg = fetch_syn_application(err_msg, logger, app_mgmt_zone, tenant_info, FETCH_SYN_APPLICATIONS, mgmt_zone)
    if err_msg != "":
      return problem_mgmt_zone, app_mgmt_zone, mgmt_zone, table_list, html, err_msg

    app_mgmt_zone, err_msg = populate_consumption(err_msg, logger, mgmt_zone, app_mgmt_zone, tenant_info, APP_BILLING_API)
    if err_msg != "":
      return problem_mgmt_zone, app_mgmt_zone, mgmt_zone, table_list, html, err_msg

    app_mgmt_zone, err_msg = populate_consumption(err_msg, logger, mgmt_zone, app_mgmt_zone, tenant_info, SYN_BILLING_API, 1)
    if err_msg != "":
      return problem_mgmt_zone, app_mgmt_zone, mgmt_zone, table_list, html, err_msg

    app_mgmt_zone, err_msg = populate_consumption(err_msg, logger, mgmt_zone, app_mgmt_zone, tenant_info, HTTP_BILLING_API, 2)
    if err_msg != "":
      return problem_mgmt_zone, app_mgmt_zone, mgmt_zone, table_list, html, err_msg
   
    problem_mgmt_zone, err_msg = fetch_problems(err_msg, logger, problem_mgmt_zone, tenant_info)
    if err_msg != "":
      return problem_mgmt_zone, app_mgmt_zone, mgmt_zone, table_list, html, err_msg
 
    #pretty_print(err_msg, logger, app_mgmt_zone)        
    table_list, err_msg = form_list(err_msg, logger, html, table_list, tenant_info, mgmt_zone, app_mgmt_zone)
    if err_msg != "":
      return problem_mgmt_zone, app_mgmt_zone, mgmt_zone, table_list, html, err_msg
    
  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"func")
    logger.fatal("Received exception while running func", exc_info=e)

  finally:
    logger.info("Successful execution: func")
    return problem_mgmt_zone, app_mgmt_zone, mgmt_zone, table_list, html, err_msg

#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to fetch all the synthetic browsers and append it to the directory "app_mgmt_zone" 
#------------------------------------------------------------------------
def populate_consumption(err_msg, logger, mgmt_zone, app_mgmt_zone, tenant_info, query, syn = 0):
  consumption_details = {}
  try:
    logger.info("In populate_consumption")
    logger.debug("populate_consumption = %s", query)
   
    url = (tenant_info.tenant_url).replace("v1","v2")
    applications, err_msg = dtApiQuery(err_msg, logger, query, tenant_info, url)
    if err_msg == "":
      logger.debug("Applications")
      logger.debug(applications)

      if syn == 0:
        apps = applications['result'][0]['data']
        print (apps)
      elif syn == 1:
        apps = applications['result'][0]['data']
      elif syn == 2:
        apps = applications['result'][0]['data']

      for billing in apps:
        dimensions = billing['dimensions']
        if syn == 0:
          if dimensions[1] == "Billed":
            consumption_details[dimensions[0]] = billing['values'][0]
        elif syn >= 0:
            consumption_details[dimensions[0]] = billing['values'][0]
            logger.debug(billing['values'][0])
      
      for key in consumption_details.keys():
        for mgmt_zone_name in app_mgmt_zone.keys():
          for i in range(len(app_mgmt_zone[mgmt_zone_name])):
            if key == app_mgmt_zone[mgmt_zone_name][i].entityId:
              app_mgmt_zone[mgmt_zone_name][i].consumption = app_mgmt_zone[mgmt_zone_name][i].consumption + consumption_details[key]

              if app_mgmt_zone[mgmt_zone_name][i].type == "Synthetic":
                app_mgmt_zone[mgmt_zone_name][i].dem = float(app_mgmt_zone[mgmt_zone_name][i].consumption * 1.0)

              elif app_mgmt_zone[mgmt_zone_name][i].type == "HTTP":
                app_mgmt_zone[mgmt_zone_name][i].dem = float(app_mgmt_zone[mgmt_zone_name][i].consumption * 0.1)

              else: 
                app_mgmt_zone[mgmt_zone_name][i].dem = float(app_mgmt_zone[mgmt_zone_name][i].consumption * 0.25)
    else:
      err_msg = err_msg.format("Billing","Read API V2")

  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"populate_consumption")
    logger.fatal("Received exception while running populate_consumption", exc_info=e)
    
  finally:
    for k in app_mgmt_zone.keys():
      logger.debug(k)
      logger.debug(str(app_mgmt_zone[k]))
    logger.info("Successful execution: populate_consumption")
    return app_mgmt_zone, err_msg


#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to fetch all the synthetic browsers and append it to the directory "app_mgmt_zone" 
#------------------------------------------------------------------------
def fetch_syn_application(err_msg, logger, app_mgmt_zone, tenant_info, query, mgmt_zone):
  try:
    logger.info("In fetch_syn_application")
    logger.debug("fetch_syn_application = %s", query)
   
    #print query
    applications, err_msg = dtApiQuery(err_msg, logger, query, tenant_info)
    if err_msg == "":
      application = applications['monitors']

      for i in range(len(application)):
        appInfo = app()
        appInfo.name = application[i]['name']

        #For custom-type application, applicationType is not populated, hence the check
        try:
          if application[i]['type'] is not "HTTP":
            appInfo.type = "Synthetic"
          else:
            appInfo.type = "HTTP"
        except KeyError:
          appInfo.type = "Synthetic"
            
        appInfo.entityId = application[i]['entityId']
 
        #Management Zone
        key = ""
        try:
          zones = application[i]['managementZones']
          for zone in zones:
            key = key + zone['name'] + ","
          key = key[:-1]
        except KeyError:
          key = "No management zone"

        try:
          obj = mgmt_zone[key]
        except KeyError:
          obj = mgmt_zone_data()
        finally:
          obj.syn_browser = obj.syn_browser + 1
          mgmt_zone[key] = obj


        if key in app_mgmt_zone.keys():
          app_mgmt_zone[key].append(appInfo)
        else:
          app_mgmt_zone[key] = [appInfo]
    else:
      err_msg = err_msg.format("Synthetic Browsers", "") 
    
  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"fetch_sync_application")
    logger.fatal("Received exception while running fetch_syn_application ", exc_info=e)

  finally:
    logger.info("Successful execution: fetch_sync_application")
    return app_mgmt_zone, mgmt_zone, err_msg

#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the excel file
#------------------------------------------------------------------------

def fetch_application(err_msg, logger, app_mgmt_zone, tenant_info, query, mgmt_zone, featureObj):
  try:
    logger.info("In fetch_application")
    logger.debug("fetch_application = %s", query)
   
    #print query
    applications, err_msg = dtApiQuery(err_msg, logger, query, tenant_info)
    
    if err_msg == "":
      for application in applications:
        appInfo = app()
        appInfo.name = application['displayName']

        #For custom-type application, applicationType is not populated, hence the check
        try:
          appInfo.type = application['applicationType']
        except KeyError:
          appInfo.type = "Not available"

        appInfo.entityId = application['entityId']
 
        #Management Zone
        key = ""
        try:
          zones = application['managementZones']
          for zone in zones:
            key = key + zone['name'] + ","
          key = key[:-1]
        except KeyError:
          key = "No management zone"
        
        if featureObj.key_usr_actions == True:
          user_action_count, err_msg = get_key_requests_data(err_msg, logger, tenant_info, KEY_REQUESTS, application['displayName'])
          if err_msg != "":
            return app_mgmt_zone, mgmt_zone, err_msg
          appInfo.key_requests = user_action_count

          apdex_data, err_msg = get_apdex_data(err_msg, logger, tenant_info, APDEX_API, application['displayName'])
          if err_msg != "":
            return app_mgmt_zone, mgmt_zone, err_msg

          if apdex_data != None :
            for i in range(len(apdex_data)):
              if apdex_data[i][0] == "SATISFIED":
                appInfo.apdex_satisfied = apdex_data[i][1]
              elif apdex_data[i][0] == "TOLERATED": 
                appInfo.apdex_tolerated = apdex_data[i][1] 
              elif apdex_data[i][0] == "FRUSTRATED": 
                appInfo.apdex_frustrated = apdex_data[i][1] 
          try:
            appInfo.overall_apdex = (((appInfo.apdex_satisfied) + (0.5 * appInfo.apdex_tolerated))/(appInfo.apdex_satisfied + appInfo.apdex_tolerated + appInfo.apdex_frustrated))
          except ZeroDivisionError:
            appInfo.overall_apdex = 0
          conversion_goal, err_msg = get_conversion_goal(err_msg, logger, tenant_info, CONVERSION_GOAL, application["entityId"])

          if err_msg != "":
            return app_mgmt_zone, mgmt_zone, err_msg

          appInfo.conversion_goals = conversion_goal
          print (application["displayName"] + " " + str(conversion_goal))

          try:
            obj = mgmt_zone[key]
          except KeyError:
            obj = mgmt_zone_data()
          finally:
            obj.applications = obj.applications + 1
            obj.key_usr_actions = obj.key_usr_actions + user_action_count
            mgmt_zone[key] = obj

          if key in app_mgmt_zone.keys():
            app_mgmt_zone[key].append(appInfo)
          else:
            app_mgmt_zone[key] = [appInfo]
    else:
        err_msg = err_msg.format("applications","Applications") 
        return app_mgmt_zone, mgmt_zone, err_msg

  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"fetch_application")
    logger.fatal("Received exception while running fetch_application ", exc_info=e)

  finally:
    logger.info("Successful execution: fetch_application")
    return app_mgmt_zone, mgmt_zone, err_msg
#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the excel file
#------------------------------------------------------------------------
def parse_config(filename):
  try:
    stream = open(filename)
    data = json.load(stream)
  except Exception:
    err_msg = EXCEPTION_RCVD.format(e,"parse_config")
    logger.error("Exception encountered in parse_config function : %s ", exc_info=e)
  finally:
    return data

#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the excel file
#------------------------------------------------------------------------
def populate_smtp_variable(err_msg, logger, SMTPObj, EmailObj, smtp_server_details):
  try:
    logger.debug("In populate_smtp_variable")

    for smtp in SMTPObj:
      smtp_server_details.username = smtp.smtp_user
      smtp_server_details.password = smtp.smtp_password
      smtp_server_details.smtpserver = smtp.smtp_server
      smtp_server_details.port = int(smtp.smtp_port)

    print ("Printing....")
    print (EmailObj)
    for email in EmailObj:
      print (email.senders_email)
      print (email.receivers_email)
      smtp_server_details.senders_list = email.senders_email
      smtp_server_details.receivers_list = email.receivers_email 

  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"populate_smtp_variable")
    logger.error("Exception encountered while executing populate_smtp_variable %s ", exc_info=e)
  finally:
    return err_msg, smtp_server_details

#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the excel file
#------------------------------------------------------------------------
def populate_tenant_details(err_msg, logger, tenant, tenant_info):
  try:
    logger.info("In populate_tenant_details")
    logger.info("In populate_tenant_details %s ", tenant)

    tenant_info.tenant_url = tenant.tenant_URL 
    tenant_info.tenant_token = tenant.tenant_API_token
    tenant_info.name = tenant.tenant_name

  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"populate_tenant_details")
    logger.error("Exception encountered while executing populate_tenant_details %s ", exc_info=e)

  finally:
    return tenant_info, err_msg 

#-----------------------------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the management_zone properties for that feature flag 
#-----------------------------------------------------------------------------------------------------
def get_problem_notifications_data(err_msg, logger, tenant_info, feature_name, FIRST_API_CALL, SPECIFIC_ID_API_CALL, mgmt_zone, mgmt_zone_struct, alerting_profile_struct):
  try:
    logger.info("In get_problem_notifications_data")
    config_URL = (tenant_info.tenant_url).replace("v1","config/v1") 
    data_set, err_msg = dtApiQuery(err_msg, logger, FIRST_API_CALL, tenant_info, config_URL)

    if err_msg != "":
      err_msg = err_msg.format("Problem Notications","Access Problem")
      return mgmt_zone, err_msg

    value_set = data_set['values']
    for item in value_set:
      data_id = item['id']
      data, err_msg = dtApiSpecificQuery(err_msg, logger, SPECIFIC_ID_API_CALL, tenant_info, config_URL, data_id)
      alerting_profile_id = data["alertingProfile"]
      for keys in alerting_profile_struct.keys():
        alerting_profile_list = alerting_profile_struct[keys]
        if alerting_profile_id in alerting_profile_list:
          management_zone_name = keys
          break
      try:
        obj = mgmt_zone[management_zone_name]
        obj.problem_notification = obj.problem_notification + 1
        mgmt_zone[management_zone_name] = obj
      except KeyError:
        obj = mgmt_zone_data()
        obj.problem_notification = obj.problem_notification + 1
        mgmt_zone[management_zone_name] = obj

  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"get_problem_notifications_data")
    logger.error("Exception caused during fetching get_problem_notifications_data", exc_info=e)

  finally:     
    logger.info("Successful execution get_problem_notifications_data")
    return mgmt_zone, err_msg


#-----------------------------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the management_zone properties for that feature flag 
#-----------------------------------------------------------------------------------------------------
def get_alerting_profile_data(err_msg, logger, tenant_info, feature_name, FIRST_API_CALL, SPECIFIC_ID_API_CALL, mgmt_zone, mgmt_zone_struct, alerting_profile_struct):
  try:
    logger.info("In get_alerting_profile_data")
    config_URL = (tenant_info.tenant_url).replace("v1","config/v1") 
    data_set, err_msg = dtApiQuery(err_msg, logger, FIRST_API_CALL, tenant_info, config_URL)
    if err_msg != "":
      err_msg = err_msg.format("Alerting Profile","Topology")
      return mgmt_zone, alerting_profile_struct, err_msg

    value_set = data_set['values']
    for item in value_set:
      data_id = item['id']
      data, err_msg = dtApiSpecificQuery(err_msg, logger, SPECIFIC_ID_API_CALL, tenant_info, config_URL, data_id)
      zone_id = data["managementZoneId"]
      try:
        key = mgmt_zone_struct[zone_id]
      except KeyError:
        key = "No management zone"
      finally:
        try:
          obj = mgmt_zone[key]
          obj.alerting_profile = obj.alerting_profile + 1
          mgmt_zone[key] = obj
        except KeyError:
          obj = mgmt_zone_data()
          obj.alerting_profile = obj.alerting_profile + 1
          mgmt_zone[key] = obj
        #Push the info in alerting_profile_struct too
        try:
          alerting_list = alerting_profile_struct[key]
          alerting_list.append(data_id)
          alerting_profile_struct[key] = alerting_list
        except KeyError:
          alerting_list = []
          alerting_list.append(data_id)
          alerting_profile_struct[key] = alerting_list

  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"get_alerting_profile_data")
    logger.error("Exception caused during fetching get_alerting_profile_data", exc_info=e)

  finally:     
    logger.info("Successful execution get_alerting_profile_data")
    return mgmt_zone, alerting_profile_struct, err_msg


#-----------------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the management_zone properties for that feature flag
#------------------------------------------------------------------------------------------
def get_naming_data(err_msg, logger, tenant_info, feature_name, API_CALL, mgmt_zone):
  try:
    logger.info("In get_naming_data")
    logger.info("In get_naming_data = " + str(API_CALL))
    config_URL = (tenant_info.tenant_url).replace("v1","config/v1")
    data, err_msg = dtApiQuery(err_msg, logger, API_CALL, tenant_info, config_URL)
    if err_msg != "":
      err_msg = err_msg.format("Naming Rules","Topology")
      return mgmt_zone, err_msg

    key = "No management zone"
    try:
      obj = mgmt_zone[key]
    except KeyError:
      obj = mgmt_zone_data()
    finally:
      naming_rules = len(data['values'])
      print ("Naming Rules - " + str(naming_rules))
      obj.naming_rules = naming_rules
      mgmt_zone[key] = obj
  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"get_naming_data")
    logger.error("Exception caught in get_naming_data", exc_info=e)

  finally:
    logger.info("Successful execution of get_naming_data")
    return mgmt_zone, err_msg

#-----------------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the management_zone properties for that feature flag
#------------------------------------------------------------------------------------------
def get_conversion_goal(err_msg, logger, tenant_info, API_CALL, entityId):
  try:
    logger.info("In get_conversion_goal")
    logger.info("In get_conversion_goal = " + str(API_CALL))
    config_URL = (tenant_info.tenant_url).replace("v1","config/v1")
    API_CALL = API_CALL.replace("ENTITY_ID",entityId)
    data, err_msg = dtApiQuery(err_msg, logger, API_CALL, tenant_info, config_URL)

    if err_msg != "":
      err_msg = err_msg.format("Conversion Goals","User Session")

  except Exception as e: 
    err_msg = EXCEPTION_RCVD.format(e,"get_conversion_goal")
    logger.exception("Exception caught in get_conversion_goal", exc_info=e)

  finally:
    logger.info("Successful execution of get_conversion_goal")

    if data != None:
      try:
        return len(data["conversionGoals"]), err_msg
      except KeyError:
        return 0, err_msg
    else:
      return 0, err_msg 

#-----------------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the management_zone properties for that feature flag
#------------------------------------------------------------------------------------------
def get_apdex_data(err_msg, logger, tenant_info, API_CALL, application_name):
  try:
    values = 0
    logger.info("In get_apdex_data")
    logger.info("In get_apdex_data = " + str(API_CALL))
    API_CALL = API_CALL.replace("APP_NAME", application_name)
    end_time = int(time.mktime(datetime.datetime.now().timetuple()))
    start_time = str(int(end_time) - 604800)
 
    start_time = int(start_time) * 1000 
    end_time = int(end_time) * 1000 
    API_CALL = API_CALL.replace("STARTTIME", str(start_time))
    API_CALL = API_CALL.replace("ENDTIME", str(end_time))
    data, err_msg = dtApiQuery(err_msg, logger, API_CALL, tenant_info)

    if err_msg != "":
      err_msg = err_msg.format("apdex","User Sessions")
      return values, err_msg 

  except Exception as e: 
    err_msg = EXCEPTION_RCVD.format(e,"get_apdex_data")
    logger.exception("Exception caught in get_apdex_data", exc_info=e)

  finally:
    logger.info("Successful execution of get_apdex_data")
    if data != None:
      values = data['values']
      return values, err_msg
    else:
      return values, err_msg

#-----------------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the management_zone properties for that feature flag
#------------------------------------------------------------------------------------------
def get_key_requests_data(err_msg, logger, tenant_info, API_CALL, application_name):
  try:
    logger.info("In get_key_requests_data")
    logger.info("In get_key_requests_data = " + str(API_CALL))
    values = 0
    API_CALL = API_CALL.replace("APP_NAME", application_name)
    data, err_msg = dtApiQuery(err_msg, logger, API_CALL, tenant_info)

    if err_msg != "":
      print ("Receveid Exception" + err_msg)
      err_msg = err_msg.format("Key Requests","User Sessions")
      return values, err_msg 

    elif data != None:
      values = data['values'][0][0]
  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"get_key_requests")
    logger.exception("Exception caught in get_key_requests", exc_info=e)

  finally:
    logger.info("Successful execution of get_key_requests")
    return values, err_msg 

#-----------------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the management_zone properties for that feature flag
#------------------------------------------------------------------------------------------
def get_mgmt_zone_details(err_msg, logger, tenant_info, feature_name, API_CALL, mgmt_zone_struct, mgmt_zone):
  try:
    logger.info("In get_mgmt_zone_details")
    logger.info("In get_mgmt_zone_details = " + str(API_CALL))
    config_URL = (tenant_info.tenant_url).replace("v1","config/v1") 
    data, err_msg = dtApiQuery(err_msg, logger, API_CALL, tenant_info, config_URL)
    if err_msg != "":
      err_msg = err_msg.format("Managemnt zone","Topology")
      return mgmt_zone_struct, mgmt_zone, err_msg

    zone_count = 0
    for j in range(len(data['values'])):
      try:
        key = data['values'][j]['id']
        zone_name = data['values'][j]['name']
        mgmt_zone_struct[key] = zone_name
        zone_count = zone_count + 1
      except KeyError:
        break
      except Exception as e:
        err_msg = EXCEPTION_RCVD.format(e,"get_mgmt_zone_details")
        logger.error("Exception caught while trying to read the API values", exc_info=e)
        
            
  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"get_mgmt_zone_details")
    logger.error("Exception caught in get_mgmt_zone_details", exc_info=e)

  finally:
    key = "No management zone"
    try:
      obj = mgmt_zone[key]
      obj.configured_mgmt_zones = zone_count 
      mgmt_zone[key] = obj
    except KeyError:
      obj = mgmt_zone_data()
      obj.configured_mgmt_zones = zone_count 
      mgmt_zone[key] = obj
    finally:
      logger.info("Succesful execution of get_mgmt_zone_details")
      return mgmt_zone_struct, mgmt_zone, err_msg

#-----------------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the management_zone properties for that feature flag
#------------------------------------------------------------------------------------------
def get_tag_data(err_msg, logger, tenant_info, feature_name, API_CALL, mgmt_zone):
  try:
    logger.info("In get_tag_data")
    logger.info("In get_tag_data = " + str(API_CALL))
    config_URL = (tenant_info.tenant_url).replace("v1","config/v1") 
    data, err_msg = dtApiQuery(err_msg, logger, API_CALL, tenant_info, config_URL)

    if err_msg != "":
      err_msg = err_msg.format("Tag","Topology")
      return mgmt_zone, err_msg

    key = "No management zone"
    try:
      obj = mgmt_zone[key]
    except KeyError:
      obj = mgmt_zone_data()
    finally:
      no_tags = len(data['values'])
      print ("Tag count - " + str(no_tags))
      obj.tag = no_tags
      mgmt_zone[key] = obj
  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"get_tag_data")
    logger.error("Exception caught in get_tag_data", exc_info=e)

  finally:
    logger.info("Successful execution of get_tag_data")
    return mgmt_zone, err_msg

#-----------------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the management_zone properties for that feature flag 
#------------------------------------------------------------------------------------------
def get_PG_data(err_msg, logger, tenant_info, feature_name, API_CALL, mgmt_zone):
  try:
    logger.info("In get_PG_data")
    logger.info("In get_PG_data = " + str(API_CALL))
    data, err_msg = dtApiQuery(err_msg, logger, API_CALL, tenant_info)

    if err_msg != "":
      print("IT FAILED!!!")
      print(err_ms)
      err_msg = err_msg.format("Process Group","Process & Topology")
      return mgmt_zone, err_msg

  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"get_PG_data")
    logger.error("Exception encountered during execution of get_PG_data", exc_info=e)

  for items in data:
    try:
      key = ""
      zone = items['managementZones']
      for j in range(len(zone)):
        try:
          key = key + zone[j]['name'] + ","
          print (items['displayName'] + " " + "key is " + key + " ") 
        except KeyError:
          logger.error("No management name found for PG - ")
          key = "No management zone,"

      key = key[:-1]
      try:
        obj = mgmt_zone[key]
      except KeyError:
        obj = mgmt_zone_data()
      finally:
        obj.process_group = obj.process_group + 1
        mgmt_zone[key] = obj
        
    except KeyError:
      logger.error("No management zone assigned to PG - ")

  return mgmt_zone, err_msg 
 
#-----------------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the management_zone properties for that feature flag 
#------------------------------------------------------------------------------------------
def get_api_tokens_data(err_msg, logger, tenant_info, feature_name, API_CALL, mgmt_zone):
  try:
    logger.info("In get_api_tokens_data")
    logger.info("In get_api_tokens_data = " + str(API_CALL))
    data, err_msg = dtApiQuery(err_msg, logger, API_CALL, tenant_info) 

  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"get_api_tokens_data")
    logger.error("Exception encountered during execution of get_api_tokens_data: ", exc_info=e)

  finally:
    if err_msg == "":
      print("Managed to sneak in")
      key = "No management zone"
      no_tokens = len(data['values'])
      print ("Tokens count - " + str(no_tokens))
      try:
        obj = mgmt_zone[key]
      except KeyError:
        obj = mgmt_zone_data()
      finally:
        obj.api_tokens = no_tokens  
        mgmt_zone[key] = obj
    elif err_msg != "":
      err_msg = err_msg.format("API Tokens","Token Management")
    
    logger.info("Succesful execution of get_api_tokens_data")
    return mgmt_zone, err_msg 

#-----------------------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the management_zone properties for that feature flag
#------------------------------------------------------------------------------------------
def get_request_attribute_data(err_msg, logger, tenant_info, feature_name, API_CALL, mgmt_zone):
  try:
    logger.info("In get_request_attribute_data")
    logger.info("In get_request_attribute_data = " + str(API_CALL))
    config_URL = (tenant_info.tenant_url).replace("v1","config/v1") 
    data, err_msg = dtApiQuery(err_msg, logger, API_CALL, tenant_info, config_URL)

    if err_msg != "":
      err_msg = err_msg.format("Request Attributes","Topology")
      return mgmt_zone, err_msg

  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"get_request_attribute_data")
    logger.error("Exception encountered during execution of get_request_attribute_data: ", exc_info=e)

  finally:
    key = "No management zone"
    no_req_attr = len(data['values'])
    print ("Request attribute count - " + str(no_req_attr))
    try:
      obj = mgmt_zone[key]
    except KeyError:
      obj = mgmt_zone_data()
    finally:
      obj.req_attr = no_req_attr
      mgmt_zone[key] = obj

    logger.info("Succesful execution of get_request_attribute_data")
    return mgmt_zone, err_msg

def populate_report_excel(err_msg, logger, df, absolute_df, app_dir_list, prb_dir_list, column_list, absolute_column_list):
    try:
      logger.info("In populate_report_excel")

      number_rows = len(df.index) + 1
      
      writer = pandas.ExcelWriter('Health_Report_Dynatrace.xlsx', engine='xlsxwriter')
      df.to_excel(writer, sheet_name='Management Zone Delta', index=False, columns=column_list)
      
      workbook  = writer.book
      worksheet = writer.sheets['Management Zone Delta']
      format1 = workbook.add_format({'bg_color': '#FFFF00',
                                     'font_color': '#000000'})
    
      worksheet.conditional_format("$A$1:$Z$%d" % (number_rows),
                                   {"type": "formula",
                                    "criteria": '=INDIRECT("E"&ROW())=1',
                                    "format": format1
                                   })

      worksheet.conditional_format("$A$1:$Z$%d" % (number_rows),
                                   {"type": "icon_set",'icon_style': '3_arrows',
                                    'icons': [
                  {'criteria': '>=', 'type': 'number', 'value': 0.001},
                  {'criteria': '<=', 'type': 'number', 'value': -0.001}
                                                         ]}
                                            )

      logger.debug(absolute_df.columns)
      logger.debug(absolute_column_list)
      print(absolute_df.columns)
      print(absolute_column_list)
      absolute_df.to_excel(writer, sheet_name='Management Zone Absolute Values', index=False, columns=absolute_column_list)

      app_df = pandas.DataFrame(app_dir_list)
      app_df.to_excel(writer, sheet_name='App Dev - Application Health', index=False, columns=['Tenant','Application name','Conversion Goals','Key Requests Count', 'Application Apdex','Satisfied Apdex Users Action','Tolerated Apdex Users Action','Frustrated Apdex Users Action'])
 
      prb_df = pandas.DataFrame(prb_dir_list)
      prb_df.to_excel(writer, sheet_name='Operation - Problem Health', index=False, columns=['Tenant','Total Problems','Problems Resolved','Severity - Resource','Severity - Error','Severity - Performance','Severity - Availability','Impact - Environment','Impact - Service','Impact - Application','Impact - Infrastructure','Mean Response Time'])

      workbook.close()
    except Exception as e:
      err_msg = EXCEPTION_RCVD.format(e,"populate_report_excel")
      logger.error("Received an exception in populate_report_excel", exc_info=e)
    finally:
      logger.info("Succesful execution of populate_report_excel")
      return err_msg

#Push_feature adoption data in the models
def push_absolute_data(err_msg, logger, zone, tenant_name, obj, absolute_list, featureAdoptionObj):
    try:
      dir_data = {}
      absolute_column_list = []
      logger.info("In push_absolute_data zone = %s", zone)
      logger.info("In push_absolute_data zone = %s", tenant_name)


      dir_data["Host Units Consumption"] = obj.host_units
      dir_data["DEM Units Consumption"] = obj.dem
      dir_data["Tenant"] = tenant_name
      dir_data["Management Zone"] = zone

      absolute_column_list.append("Tenant")
      absolute_column_list.append("Management Zone")
      absolute_column_list.append("Host Units Consumption")
      absolute_column_list.append("DEM Units Consumption")

      if (featureAdoptionObj.application == True):
        dir_data["Applications"] = obj.applications
        absolute_column_list.append("Applications")

      if (featureAdoptionObj.synthetic == True):
        dir_data["Synthetic Browsers"] = obj.syn_browser
        absolute_column_list.append("Synthetic Browsers")

      if (featureAdoptionObj.http_monitors == True):
        dir_data["HTTP Browsers"] = obj.http_browser
        absolute_column_list.append("HTTP Browsers")

      if (featureAdoptionObj.host_group == True):
        dir_data["Host Groups"] = obj.host_group
        absolute_column_list.append("Host Groups")

      if (featureAdoptionObj.process_group == True):
        dir_data["Process Groups"] = obj.process_group
        absolute_column_list.append("Process Groups")

      if (featureAdoptionObj.tagging == True):
        dir_data["Tags"] = obj.tag
        absolute_column_list.append("Tags")

      if (featureAdoptionObj.alerting_profile == True):
        dir_data["Alerting Profiles"] =  obj.alerting_profile
        absolute_column_list.append("Alerting Profiles")

      if (featureAdoptionObj.naming_rules == True):
        dir_data["Management Zones"] =  obj.configured_mgmt_zones
        absolute_column_list.append("Management Zones")

      if (featureAdoptionObj.naming_rules== True):
        dir_data["Naming Rules"] =  obj.naming_rules
        absolute_column_list.append("Naming Rules")

      if (featureAdoptionObj.problem_notifications == True):
        dir_data["Problem Notifications"] =  obj.problem_notification
        absolute_column_list.append("Problem Notifications")

      if (featureAdoptionObj.cloud_platform == True):
        dir_data["Cloud Platform Integration"] =  obj.cloud_integration
        absolute_column_list.append("Cloud Platform Integration")

      if (featureAdoptionObj.key_usr_actions == True):
        dir_data["Key User Requests"] =  obj.key_usr_actions
        absolute_column_list.append("Key User Requests")

      if (featureAdoptionObj.api == True):
        dir_data["API Token"] =  obj.api_tokens
        absolute_column_list.append("API Token")

      if (featureAdoptionObj.request_attribute == True):
        dir_data["Request Attributes"] =  obj.req_attr
        absolute_column_list.append("Request Attributes")

      absolute_list.append(dir_data)

    except Exception as e:
      err_msg = EXCEPTION_RCVD.format(e,"push_absolute_data")
      logger.error("Exception encountered in push_absolute_data zone = ", exc_info=e)

    finally:
      logger.info("Successful execution push_absolute_data zone")
      return absolute_list, absolute_column_list

#Push_feature adoption data in the models
def push_data(err_msg, logger, zone, tenant_name, obj, dir_list, featureAdoptionObj, create_flag = 0):
    try:
      dir_data = {}
      column_list = [] 
      logger.info("In push_data zone = %s", zone)
      logger.info("In push_data zone = %s", tenant_name)
     
      column_list.append("Tenant")
      column_list.append("Management Zone")
      column_list.append("Host Units Consumption")
      column_list.append("DEM Units Consumption")
      column_list.append("New_Entry")
      column_list.append("Management Zones")

      if create_flag == 1:
        logger.debug("pushing new entry")
        logger.debug("zone " + zone)
        logger.debug("tenant_name:" + tenant_name)
        feature_obj = featureAdoptionCount.objects.create(mgmt_zone=zone, tenant=tenant_name, host_units_consumption=int(obj.host_units), dem_units_consumption=int(obj.dem), application_count=int(obj.applications), syn_browser_count=int(obj.syn_browser), http_browser_count=int(obj.http_browser), host_group_count=int(obj.host_group), process_group_count=int(obj.process_group), tag_count=int(obj.tag), alerting_profile_count=int(obj.alerting_profile), mgmt_zone_count=int(obj.configured_mgmt_zones), naming_rule_count=int(obj.naming_rules), problem_notifications_count=int(obj.problem_notification), cloud_platform_count=int(obj.cloud_integration), key_usr_req_count=int(obj.key_usr_actions), api_token_count=int(obj.api_tokens), request_attr_count=int(obj.req_attr)) 

        dir_data["Tenant"] = tenant_name 
        dir_data["Management Zone"] = zone
        dir_data["Host Units Consumption"] = obj.host_units
        dir_data["DEM Units Consumption"] = obj.dem
        dir_data["Management Zones"] =  obj.configured_mgmt_zones
        dir_data["New_Entry"] = 1 

        if featureAdoptionObj.application == True:
          dir_data["Applications"] = obj.applications
          column_list.append("Applications")

        if featureAdoptionObj.synthetic == True:
          dir_data["Synthetic Browsers"] = obj.syn_browser
          column_list.append("Synthetic Browsers")

        if featureAdoptionObj.http_monitors == True:
          dir_data["HTTP Browsers"] = obj.http_browser
          column_list.append("HTTP Browsers")

        if featureAdoptionObj.host_group == True:
          dir_data["Host Groups"] = obj.host_group
          column_list.append("Host Groups")

        if featureAdoptionObj.process_group == True:
          dir_data["Process Groups"] = obj.process_group
          column_list.append("Process Groups")

        if featureAdoptionObj.tagging == True:
          dir_data["Tags"] = obj.tag
          column_list.append("Tags")

        if featureAdoptionObj.alerting_profile == True:
          dir_data["Alerting Profiles"] =  obj.alerting_profile
          column_list.append("Alerting Profiles")

        if featureAdoptionObj.naming_rules == True:
          dir_data["Naming Rules"] =  obj.naming_rules
          column_list.append("Naming Rules")

        if featureAdoptionObj.problem_notifications == True:
          dir_data["Problem Notifications"] =  obj.problem_notification
          column_list.append("Problem Notifications")

        if featureAdoptionObj.cloud_platform == True:
          dir_data["Cloud Platform Integration"] =  obj.cloud_integration
          column_list.append("Cloud Platform Integration")

        if featureAdoptionObj.key_usr_actions == True:
          dir_data["Key User Requests"] =  obj.key_usr_actions
          column_list.append("Key User Requests")

        if featureAdoptionObj.api == True:
          dir_data["API Token"] =  obj.api_tokens
          column_list.append("API Token")

        if featureAdoptionObj.request_attribute == True:
          dir_data["Request Attributes"] =  obj.req_attr
          column_list.append("Request Attributes")

        dir_list.append(dir_data) 

      else:

        feature_obj = featureAdoptionCount.objects.filter(mgmt_zone=zone, tenant=tenant_name)
        old_val = feature_obj.all().values_list("tenant","mgmt_zone","host_units_consumption","dem_units_consumption","application_count","syn_browser_count","http_browser_count","host_group_count","process_group_count","tag_count","alerting_profile_count","mgmt_zone_count","naming_rule_count","problem_notifications_count","cloud_platform_count","key_usr_req_count","api_token_count","request_attr_count")

        items = old_val[0]
        dir_data["Tenant"] = items[0]
        dir_data["New_Entry"] = 0
        dir_data["Host Units Consumption"] = obj.host_units - items[2] 
        dir_data["DEM Units Consumption"] = obj.dem  - items[3]
        dir_data["Management Zone"] = items[1]
        dir_data["Management Zones"] =  obj.configured_mgmt_zones - items[11]

        if featureAdoptionObj.application == True:
          dir_data["Applications"] = obj.applications - items[4]
          column_list.append("Applications")

        if featureAdoptionObj.synthetic == True:
          dir_data["Synthetic Browsers"] = obj.syn_browser - items[5]
          column_list.append("Synthetic Browsers")

        if featureAdoptionObj.http_monitors == True:
          dir_data["HTTP Browsers"] = obj.http_browser - items[6]
          column_list.append("HTTP Browsers")

        if featureAdoptionObj.host_group == True:
          dir_data["Host Groups"] = obj.host_group - items[7]
          column_list.append("Host Groups")

        if featureAdoptionObj.process_group == True:
          dir_data["Process Groups"] = obj.process_group - items[8]
          column_list.append("Process Groups")

        if featureAdoptionObj.tagging == True:
          dir_data["Tags"] = obj.tag - items[9]
          column_list.append("Tags")

        if featureAdoptionObj.alerting_profile == True:
          dir_data["Alerting Profiles"] =  obj.alerting_profile - items[10]
          column_list.append("Alerting Profiles")

        if featureAdoptionObj.naming_rules == True:
          dir_data["Naming Rules"] =  obj.naming_rules - items[12]
          column_list.append("Naming Rules")

        if featureAdoptionObj.problem_notifications == True:
          dir_data["Problem Notifications"] =  obj.problem_notification - items[13]
          column_list.append("Problem Notifications")

        if featureAdoptionObj.cloud_platform == True:
          dir_data["Cloud Platform Integration"] =  obj.cloud_integration - items[14]
          column_list.append("Cloud Platform Integration")

        if featureAdoptionObj.key_usr_actions == True:
          dir_data["Key User Requests"] =  obj.key_usr_actions - items[15]
          column_list.append("Key User Requests")

        if featureAdoptionObj.api == True:
          dir_data["API Token"] =  obj.api_tokens - items[16]
          column_list.append("API Token")

        if featureAdoptionObj.request_attribute == True:
          dir_data["Request Attributes"] =  obj.req_attr - items[17]
          column_list.append("Request Attributes")

        dir_list.append(dir_data) 
        feature_obj.update(tenant=str(tenant_name),mgmt_zone=zone,host_units_consumption=float(obj.host_units), dem_units_consumption=float(obj.dem), application_count=int(obj.applications), syn_browser_count=int(obj.syn_browser), http_browser_count=int(obj.http_browser), host_group_count=int(obj.host_group), process_group_count=int(obj.process_group), tag_count=int(obj.tag), alerting_profile_count=int(obj.alerting_profile), mgmt_zone_count=int(obj.configured_mgmt_zones), naming_rule_count=int(obj.naming_rules), problem_notifications_count=int(obj.problem_notification), cloud_platform_count=int(obj.cloud_integration), key_usr_req_count=int(obj.key_usr_actions), api_token_count=int(obj.api_tokens), request_attr_count=int(obj.req_attr)) 

    except Exception as e:
      err_msg = EXCEPTION_RCVD.format(e,"push_data")
      logger.error("Exception encountered in push_data zone = ", exc_info=e)

    finally:
      logger.info("Successful execution push_data zone")
      return dir_list, feature_obj, column_list

def html_body_health_rpt(err_msg, logger, html, mgmt_zone, dir_list, absolute_list, tenant_name, featureAdoptionObj):
    logger.debug("In html_body_health_rpt")
    zones = mgmt_zone.keys()

    for zone in zones:
      string = ""
      obj = mgmt_zone[zone]
      host_units = str(obj.host_units)
      dem_units = str(obj.dem)
      host_groups = str(obj.host_group)
      process_groups = str(obj.process_group)
      tagging = str(obj.tag)
      alerting_profile = str(obj.alerting_profile)
      management_zone = str(obj.configured_mgmt_zones)
      naming_rule = str(obj.naming_rules)
      problem_notifications = str(obj.problem_notification)
      cloud_integration = str(obj.cloud_integration)
      key_usr_action = str(obj.key_usr_actions)
      api_token = str(obj.api_tokens)
      req_attrs = str(obj.req_attr)
      
      try:
        feature_obj = featureAdoptionCount()
        feature_obj = featureAdoptionCount.objects.filter(mgmt_zone=zone, tenant=tenant_name)
        logger.info("Print feature_obj")       
        logger.info(feature_obj)       
 
        if len(feature_obj) == 0:
          create_flag = 1
          dir_list, feature_obj, column_list = push_data(err_msg, logger, zone, tenant_name, obj, dir_list, featureAdoptionObj, create_flag)
        else:
          create_flag = 0
          dir_list, feature_obj, column_list = push_data(err_msg, logger, zone, tenant_name, obj, dir_list, featureAdoptionObj, create_flag)

      except Exception as e:
        err_msg = EXCEPTION_RCVD.format(e,"html_body_health_rpt")
        logger.fatal("Exception encountered while executing html_body_health_rpt: ", exc_info=e )
      absolute_list, absolute_column_list = push_absolute_data(err_msg, logger, zone, tenant_name, obj, absolute_list, featureAdoptionObj)

    return dir_list, absolute_list, html, err_msg, column_list, absolute_column_list

#Push application data
def populate_application_worksheet_excel(err_msg, logger, app_dir_list):
    logger.info("In populate_application_worksheet_excel")

    try:
      file_name = 'Health_Report_Dynatrace.xlsx'

      writer = pandas.ExcelWriter(file_name, engine='xlsxwriter')
      if os.path.exists(file_name):
        logger.info("Found file ")
        book = xlsxwriter.Workbook(file_name)
        writer.book = book 

    except Exception as e:
      err_msg = EXCEPTION_RCVD.format(e,"populate_application_worksheet_excel")
      logger.fatal("Exception encountered while executing populate_application_worksheet_excel: ", exc_info=e )

    finally:
      logger.info("Succesfully executed populate_application_worksheet_excel")
      writer.save()
      writer.close()

#Push Problem Data in DB
def push_prb_data(err_msg, logger, problem_mgmt_zone, prb_dir_list, tenant_name):
    logger.info("In push_prb_data")

    try:
       create_flag = 0
       prb_obj = problemDetails()
       prb_obj = problemDetails.objects.filter(tenant=tenant_name)

       resource = problem_mgmt_zone["Severity - Resource"]
       error_event = problem_mgmt_zone["Severity - Error"]
       performance = problem_mgmt_zone["Severity - Performance"]
       availability = problem_mgmt_zone["Severity - Availability"]
       environment = problem_mgmt_zone["Impact - Environment"]
       service = problem_mgmt_zone["Impact - Service"]
       application = problem_mgmt_zone["Impact - Application"]
       infrastructure = problem_mgmt_zone["Impact - Infrastructure"]
       median_rsp_time = problem_mgmt_zone["Mean Response Time"]
       total_problem = problem_mgmt_zone["Total Problems"]
       prb_resolved = problem_mgmt_zone["Problems Resolved"]

       if len(prb_obj) == 0:
         create_flag = 1
         prb_obj = problemDetails.objects.create(tenant=tenant_name, availability_severity=availability,performance_severity=performance,error_severity=error_event,resource_severity=resource,impact_service=service,impact_app=application,impact_environment=environment,impact_infra=infrastructure,mean_rsp_time=median_rsp_time,total_prb=total_problem,total_prb_resolved=prb_resolved)
       else:
         create_flag = 0
         old_val = prb_obj.all().values_list("tenant","availability_severity","performance_severity","error_severity","resource_severity","impact_service","impact_app","impact_environment","impact_infra","mean_rsp_time","total_prb","total_prb_resolved")
         prb_dir_list.append(problem_mgmt_zone)

    except Exception as e:
       err_msg = EXCEPTION_RCVD.format(e,"push_prb_data")
       logger.error("Caught an exception while executing push_prb_data", exc_info=e)

    finally:
       return prb_dir_list, err_msg

#Populate "Application" Worksheet
def push_app_data(err_msg, logger, app_mgmt_zone, app_dir_list, tenant_name): 
    logger.info("In push_app_data")

    try:
       for zone in app_mgmt_zone.keys():
         appInfo = app_mgmt_zone[zone]
         for app in appInfo:
           create_flag = 0 
           app_obj = applicationDetails()
           app_obj = applicationDetails.objects.filter(entityId=app.entityId)

           if len(app_obj) == 0:
             create_flag = 1
             app_obj = applicationDetails.objects.create(entityId=app.entityId,application_displayName=app.name,satisfied_apdex_actions=app.apdex_satisfied,tolerated_apdex_actions=app.apdex_tolerated,frustrated_apdex_actions=app.apdex_frustrated,conversion_goals=app.conversion_goals,key_user_action=app.key_requests,overall_apdex=app.overall_apdex) 
           else:
             create_flag = 0
             app_obj = applicationDetails.objects.filter(entityId=app.entityId)
             old_val = app_obj.all().values_list("entityId","application_displayName","satisfied_apdex_actions","tolerated_apdex_actions","frustrated_apdex_actions","conversion_goals","key_user_action","overall_apdex")

           app_dir = {}
           app_dir["Tenant"] = tenant_name
           app_dir["Application name"] = app.name
           app_dir["Conversion Goals"] = app.conversion_goals
           app_dir["Key Requests Count"] = app.key_requests

           app_dir["Application Apdex"] = app.overall_apdex
           app_dir["Satisfied Apdex Users Action"] = app.apdex_satisfied
           app_dir["Tolerated Apdex Users Action"] = app.apdex_tolerated
           app_dir["Frustrated Apdex Users Action"] = app.apdex_frustrated

           app_dir_list.append(app_dir)
    except Exception as e:
       err_msg = EXCEPTION_RCVD.format(e,"push_app_data")
       logger.error("Caught an exception while executing push_app_data", exc_info=e)

    finally:
       return app_dir_list, err_msg

#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to validate API call
#------------------------------------------------------------------------
def make_api_call(tenant_url, tenant_token):
  try:
    endpoint = INFRA_API 
    query = str(tenant_url) + str(endpoint)
    get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(tenant_token)}
    populate_data = requests.get(query, headers = get_param)
  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"make_api_call")
    print("Exception encountered while running make_api_call")
  finally:
    return populate_data.content

def generate_tenant_data(err_msg, logger, tenant_level_values, tenant, mgmt_zone, html, featureAdoptionObj):
  try:
    logger.info("In generate_tenant_data")
    intermediate_list = []

    license_dir_data = {}
    license_dir_data["Host Units Consumption"] = 0 
    license_dir_data["DEM Units Consumption"] = 0

    dir_data = {}
    dir_data["Applications"] = 0
    dir_data["Synthetic Browsers"] = 0
    dir_data["HTTP Browsers"] = 0
    dir_data["Host Groups"] = 0
    dir_data["Process Groups"] = 0
    dir_data["Tags"] = 0
    dir_data["Alerting Profiles"] = 0
    dir_data["Management Zones"] = 0 
    dir_data["Naming Rules"] = 0
    dir_data["Problem Notifications"] = 0
    dir_data["Cloud Platform Integration"] = 0
    dir_data["Key User Requests"] = 0
    dir_data["API Token"] = 0
    dir_data["Request Attributes"] = 0

    for zone in mgmt_zone:
      obj = mgmt_zone[zone]
      license_dir_data["Host Units Consumption"] = license_dir_data["Host Units Consumption"] + obj.host_units
      license_dir_data["DEM Units Consumption"] = license_dir_data["DEM Units Consumption"] + obj.dem

      dir_data["Synthetic Browsers"] = dir_data["Synthetic Browsers"] + obj.syn_browser
      dir_data["HTTP Browsers"] = dir_data["HTTP Browsers"] + obj.http_browser
      dir_data["Host Groups"] = dir_data["Host Groups"] + obj.host_group
      dir_data["Process Groups"] = dir_data["Process Groups"] + obj.process_group
      dir_data["Tags"] = dir_data["Tags"] + obj.tag
      dir_data["Alerting Profiles"] = dir_data["Alerting Profiles"] + obj.alerting_profile
      dir_data["Management Zones"] = dir_data["Management Zones"] + 1 
      dir_data["Naming Rules"] = dir_data["Naming Rules"] + obj.naming_rules
      dir_data["Problem Notifications"] = dir_data["Problem Notifications"] + obj.problem_notification
      dir_data["Cloud Platform Integration"] = dir_data["Cloud Platform Integration"] + obj.cloud_integration 
      dir_data["Key User Requests"] = dir_data["Key User Requests"] + obj.key_usr_actions 
      dir_data["API Token"] = dir_data["API Token"] + obj.api_tokens
      dir_data["Request Attributes"] = dir_data["Request Attributes"] + obj.req_attr

    if (featureAdoptionObj.application == True):
      intermediate_list.append(dir_data["Applications"])

    if (featureAdoptionObj.synthetic == True):
      intermediate_list.append(dir_data["Synthetic Browsers"])

    if (featureAdoptionObj.http_monitors == True):
      intermediate_list.append(dir_data["HTTP Browsers"])

    if (featureAdoptionObj.host_group == True):
      intermediate_list.append(dir_data["Host Groups"])

    if (featureAdoptionObj.process_group == True):
      intermediate_list.append(dir_data["Process Groups"])

    if (featureAdoptionObj.tagging == True):
      intermediate_list.append(dir_data["Tags"])

    if (featureAdoptionObj.alerting_profile == True):
      intermediate_list.append(dir_data["Alerting Profiles"])

    intermediate_list.append(dir_data["Management Zones"])

    if (featureAdoptionObj.naming_rules == True):
      intermediate_list.append(dir_data["Naming Rules"])

    if (featureAdoptionObj.problem_notifications == True):
      intermediate_list.append(dir_data["Problem Notifications"])

    if (featureAdoptionObj.cloud_platform == True):
      intermediate_list.append(dir_data["Cloud Platform Integration"])

    if (featureAdoptionObj.key_usr_actions == True):
      intermediate_list.append(dir_data["Key User Requests"])

    if (featureAdoptionObj.api == True):
      intermediate_list.append(dir_data["API Token"])

    if (featureAdoptionObj.request_attribute == True):
      intermediate_list.append(dir_data["Request Attributes"])

    license_tmp_list = [license_dir_data["Host Units Consumption"],license_dir_data["DEM Units Consumption"]]

    tenant_level_values.tenant_dict[tenant] = intermediate_list 
    tenant_level_values.tenant_license_dict[tenant] = license_tmp_list

  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"generate_tenant_data")
    logger.error("Received exception while running generate_tenant_data ", exc_info=e)

  finally:
    logger.info("Succesfully completed generate_tenant_data")
    return html, tenant_level_values, err_msg

def generate_bar_graph_html(err_msg, logger, html, tenant_level_values, featureAdoptionObj):
  try:
    logger.info("In generate_bar_graph_html")

    ax1 = plt.subplot2grid((6,12),(0,0),rowspan=6, colspan=5)
    ax2 = plt.subplot2grid((6,12),(0,5),rowspan=6, colspan=7)

    if (featureAdoptionObj.application == True):
      tenant_level_values.index_list.append("Applications")

    if (featureAdoptionObj.synthetic == True):
      tenant_level_values.index_list.append("Synthetic Browsers")

    if (featureAdoptionObj.http_monitors == True):
      tenant_level_values.index_list.append("HTTP Browsers")

    if (featureAdoptionObj.host_group == True):
      tenant_level_values.index_list.append("Host Groups")

    if (featureAdoptionObj.process_group == True):
      tenant_level_values.index_list.append("Process Groups")

    if (featureAdoptionObj.tagging == True):
      tenant_level_values.index_list.append("Tags")

    if (featureAdoptionObj.alerting_profile == True):
      tenant_level_values.index_list.append("Alerting Profiles")

    tenant_level_values.index_list.append("Management Zones")

    if (featureAdoptionObj.naming_rules == True):
      tenant_level_values.index_list.append("Naming Rules")

    if (featureAdoptionObj.problem_notifications == True):
      tenant_level_values.index_list.append("Problem Notifications")

    if (featureAdoptionObj.cloud_platform == True):
      tenant_level_values.index_list.append("Cloud Platform Integration")

    if (featureAdoptionObj.key_usr_actions == True):
      tenant_level_values.index_list.append("Key User Requests")

    if (featureAdoptionObj.api == True):
      tenant_level_values.index_list.append("API Token")

    if (featureAdoptionObj.request_attribute == True):
      tenant_level_values.index_list.append("Request Attributes")

    license_df = pandas.DataFrame(tenant_level_values.tenant_license_dict, tenant_level_values.license_index_list)
    license_df.plot.barh(ax=ax2)
    ax1.table(cellText=license_df.values, rowLabels=tenant_level_values.license_index_list, colWidths = [0.40]*len(license_df.columns), colLabels=license_df.columns,loc='left')
    ax1.axis("off")

    plt.suptitle("License Consumption Details", fontsize=16,horizontalalignment='right', x = 0.6, fontweight='bold')
    plt.savefig("license.png",bbox_inches="tight",pad_inches=1, dpi=400)
    plt.subplots_adjust(top=0.85) 
    plt.show()

    ax1 = plt.subplot2grid((6,12),(0,0),rowspan=6, colspan=5)
    ax2 = plt.subplot2grid((6,12),(0,5),rowspan=6, colspan=7)

    print(tenant_level_values.tenant_dict)
    print(tenant_level_values.index_list)
    feature_df = pandas.DataFrame(tenant_level_values.tenant_dict, tenant_level_values.index_list)
    feature_df.plot.barh(ax=ax2)

    ax1.table(cellText=feature_df.values, rowLabels=tenant_level_values.index_list, colLabels=feature_df.columns,colWidths = [0.40]*len(feature_df.columns),loc="left")
    ax1.axis("off")

    plt.suptitle("Feature Adoption Status", fontsize=16, fontweight='bold', horizontalalignment='right', x = 0.6)
    plt.savefig("image1.png",bbox_inches="tight",pad_inches=1, dpi=400)
    plt.show()

  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"generate_bar_graph_html")
    logger.error("Received exception while running generate_bar_graph_html: ", exc_info=e)

  finally:
    return html, err_msg
#------------------------------------------------------------------------
# Author: Nikhil Goenka
# Function to call API and populate the excel file
#------------------------------------------------------------------------

def relay_generate_report(tenantObj, SMTPObj, EmailObj, featureObj):
  try:
    err_msg = ""
    email_body = ""
    final_string = ""
    totalHostUnits = 0

    logging.basicConfig(filename='log/log_file_dynatrace_health_report.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

    logger = logging.getLogger()
    smtp_server_details = email_details()
    err_msg, smtp_server_details = populate_smtp_variable(err_msg, logger, SMTPObj, EmailObj, smtp_server_details)
    if err_msg != "":
      return err_msg
    err_msg, smtp_server = initialize_email_server(err_msg, logger, smtp_server_details)
    if err_msg != "":
      return err_msg

    content = MIMEMultipart('related')
    content["Subject"] = "Dynatrace Health Report"

    html, err_msg = html_header(err_msg, logger)
    if err_msg != "":
      return err_msg
    
    dir_list = []
    absolute_list = []
    prb_dir_list = []
    app_dir_list = []
    tenant_level_values = tenant_data()

    print("About to enter")
    for tenant in tenantObj:
    	print (tenant)
    	table_list = []
    	mgmt_zone = {}
    	app_mgmt_zone = {}
    	mgmt_zone_struct = {} 
    	problem_mgmt_zone = {} 
    	alerting_profile_struct = {}

    	tenant_info = tenantInfo()
    	tenant_info, err_msg = populate_tenant_details(err_msg, logger, tenant, tenant_info)
    	if err_msg != "":
    	  return err_msg

    	problem_mgmt_zone, app_mgmt_zone, mgmt_zone, table_list, html, err_msg = func(err_msg, logger, totalHostUnits, smtp_server, smtp_server_details, html, tenant_info, table_list, email_body, mgmt_zone, app_mgmt_zone, problem_mgmt_zone, featureObj)
    	if err_msg != "":
    	  return err_msg

    	#logic to check if the feature flag is enabled
    	if(featureObj.process_group == True):
    	  print("Call PG")
    	  feature_name = "Process Group"
    	  mgmt_zone, err_msg = get_PG_data(err_msg, logger, tenant_info, feature_name, PROCESS_GROUP, mgmt_zone)

    	  if err_msg != "":
    	    print(err_msg)
    	    return err_msg
 
    	if(featureObj.tagging == True):
    	  feature_name = "tag"
    	  mgmt_zone, err_msg = get_tag_data(err_msg, logger, tenant_info, feature_name, TAGS, mgmt_zone)
    	  if err_msg != "":
    	    return err_msg

    	if(featureObj.naming_rules == True):
    	  feature_name = "service-naming"
    	  mgmt_zone, err_msg = get_naming_data(err_msg, logger, tenant_info, feature_name, NAMING_RULES, mgmt_zone)
    	  if err_msg != "":
    	    return err_msg

    	feature_name = "mgmt_zones"
    	mgmt_zone_struct, mgmt_zone, err_msg = get_mgmt_zone_details(err_msg, logger, tenant_info, feature_name, MGMT_ZONES_API, mgmt_zone_struct, mgmt_zone)
    	if err_msg != "":
    	  return err_msg

    	  #for alerting_profile
    	if(featureObj.alerting_profile == True):
    	  feature_name = "alerting profile" #or for problem notifications
    	  mgmt_zone, alerting_profile_struct, err_msg = get_alerting_profile_data(err_msg, logger, tenant_info, feature_name, ALERTING_PRF_API, ADD_PROP_ALERTING_PRF_API, mgmt_zone, mgmt_zone_struct, alerting_profile_struct)
    	  if err_msg != "":
    	    return err_msg

    	if(featureObj.problem_notifications == True):
    	  mgmt_zone, err_msg = get_problem_notifications_data(err_msg, logger, tenant_info, feature_name, PROBLEM_NOTIFICATIONS, SPECIFIC_PROBLEM_NOTIFICATION, mgmt_zone, mgmt_zone_struct, alerting_profile_struct)
    	  if err_msg != "":
    	    return err_msg

    	if(featureObj.api == True):
    	 pass 

    	 #Commented since the demo API token does not have permission to fetch token info
    	 #mgmt_zone, err_msg = get_api_tokens_data(err_msg, logger, tenant_info, feature_name, TOKENS, mgmt_zone)
    	 #if err_msg != "":
    	 #  return err_msg

    	if(featureObj.request_attribute == True):
    	  mgmt_zone, err_msg = get_request_attribute_data(err_msg, logger, tenant_info, feature_name, REQ_ATTRIBUTES, mgmt_zone)
    	  print ("request attributes: " + str(mgmt_zone["No management zone"].req_attr))
    	  if err_msg != "":
    	    return err_msg

    	app_dir_list, err_msg = push_app_data(err_msg, logger, app_mgmt_zone, app_dir_list, tenant_info.name)
    	if err_msg != "":
    	  return err_msg

    	prb_dir_list, err_msg = push_prb_data(err_msg, logger, problem_mgmt_zone, prb_dir_list, tenant_info.name)
    	if err_msg != "":
    	  return err_msg
    
    	dir_list, absolute_list, html, err_msg, column_list, absolute_column_list = html_body_health_rpt(err_msg, logger, html, mgmt_zone, dir_list, absolute_list, tenant_info.name, featureObj)
    	if err_msg != "":
    	  return err_msg

    	html, tenant_level_values, err_msg = generate_tenant_data(err_msg, logger, tenant_level_values, tenant, mgmt_zone, html, featureObj)
    	if err_msg != "":
    	  return err_msg

    html, err_msg = generate_bar_graph_html(err_msg, logger, html, tenant_level_values, featureObj)
    if err_msg != "":
      return err_msg

    df = pandas.DataFrame(dir_list)
    absolute_df = pandas.DataFrame(absolute_list)

    #html = absolute_df.to_html() 
    print (prb_dir_list)
    err_msg = populate_report_excel(err_msg, logger, df, absolute_df, app_dir_list, prb_dir_list, column_list, absolute_column_list)
    if err_msg != "":
      return err_msg

    content, err_msg = html_footer(err_msg, logger, html, content)
    if err_msg != "":
      return err_msg

    err_msg = send_email(err_msg, logger, smtp_server, content, smtp_server_details)
    if err_msg != "":
      return err_msg

  except Exception as e:
    err_msg = EXCEPTION_RCVD.format(e,"main")
    logger.error("Received exception while running main", exc_info=e)
  
  finally:
    return err_msg
