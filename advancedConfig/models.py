from __future__ import unicode_literals
from django.contrib.auth.models import Permission, User
from dttool.models import TenantDetail
from django.db import models

# Create your models here.
class FeatureAdoption(models.Model):
    process_group = models.BooleanField(default=True, verbose_name="Process Group")
    request_attribute = models.BooleanField(default=True,verbose_name="Request Attributes")
    alerting_profile = models.BooleanField(default=True,verbose_name="Alerting Profile")
    tagging = models.BooleanField(default=True,verbose_name = "Automatic Tag")
    host_group = models.BooleanField(default=True, verbose_name="Host Groups")
    problem_notifications =  models.BooleanField(default=True, verbose_name="Problem Notifications")
    key_usr_actions = models.BooleanField(default=True, verbose_name="Key User Actions")
    naming_rules = models.BooleanField(default=True, verbose_name="Naming Rules")
    cloud_platform = models.BooleanField(default=True, verbose_name="Cloud Platforms")
    api = models.BooleanField(default=True, verbose_name="API")
    application = models.BooleanField(default=True, verbose_name="Applications")
    conversion_goal = models.BooleanField(default=True, verbose_name="Conversion Goal")
    synthetic = models.BooleanField(default=True, verbose_name="Synthetic Browsers")
    http_monitors = models.BooleanField(default=True, verbose_name="HTTP Monitors")

    class Meta:
        verbose_name = "Feature Adoption Collection"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request):
        return False 
 

class SMTPServer(models.Model):
   smtp_user = models.CharField(max_length=250,verbose_name="SMTP User")
   smtp_server = models.CharField(max_length=250,verbose_name="SMTP Server")
   smtp_password = models.CharField(max_length=250, verbose_name="SMTP Password")
   smtp_port = models.CharField(max_length=10, verbose_name="SMTP PORT")
  
   class Meta:
     verbose_name = "SMTP Server Configuration"
     
   def has_add_permission(self, request):
     return False

class featureAdoptionCount(models.Model):
    id = models.AutoField(primary_key=True)
    tenant = models.CharField(max_length=255, verbose_name="Tenant name")
    mgmt_zone = models.CharField(max_length=255, verbose_name="Management Zone")

    host_units_consumption = models.FloatField(null=True, default=0, verbose_name="Host Unit Consumption")
    dem_units_consumption = models.FloatField(null=True, default=0,verbose_name="DEM Unit Consumption")
    application_count = models.PositiveSmallIntegerField(default=0,verbose_name="Applications Count")
    syn_browser_count = models.PositiveSmallIntegerField(default=0,verbose_name="Synthetic Browser Count")
    http_browser_count = models.PositiveSmallIntegerField(default=0,verbose_name="HTTP Count")
    host_group_count = models.PositiveSmallIntegerField(default=0,verbose_name="Host Groups Count")
    process_group_count = models.PositiveSmallIntegerField(default=0,verbose_name="Process Group Count")
    tag_count = models.PositiveSmallIntegerField(default=0,verbose_name="Tag Count")
    alerting_profile_count = models.PositiveSmallIntegerField(default=0,verbose_name="Alerting Profile Count")
    mgmt_zone_count = models.PositiveSmallIntegerField(default=0,verbose_name="Management Zone Count")
    naming_rule_count = models.PositiveSmallIntegerField(default=0,verbose_name="Naming Rule Count")
    problem_notifications_count = models.PositiveSmallIntegerField(default=0,verbose_name="Problem Integration Count")
    cloud_platform_count = models.PositiveSmallIntegerField(default=0,verbose_name="Cloud Platform Count")
    key_usr_req_count = models.PositiveSmallIntegerField(default=0,verbose_name="Key User Actions")
    api_token_count = models.PositiveSmallIntegerField(default=0,verbose_name="API Tokens")
    request_attr_count = models.PositiveSmallIntegerField(default=0,verbose_name="Request Attribute")

    class Meta:
        unique_together = (("id", "tenant", "mgmt_zone"),)
        verbose_name = "Feature Adoption Data"

class applicationDetails(models.Model):
    entityId = models.CharField(max_length=255, verbose_name="Entity ID")
    application_displayName = models.CharField(max_length=255, verbose_name="Application Name")
    
    overall_apdex = models.PositiveSmallIntegerField(default=0,verbose_name="Application Apdex")
    satisfied_apdex_actions = models.PositiveSmallIntegerField(default=0,verbose_name="Apdex - Satisfied Actions")
    tolerated_apdex_actions = models.PositiveSmallIntegerField(default=0,verbose_name="Apdex - Tolerated Actions")
    frustrated_apdex_actions = models.PositiveSmallIntegerField(default=0,verbose_name="Apdex - Frustrated Actions")

    conversion_goals = models.PositiveSmallIntegerField(default=0,verbose_name="Conversion Goals")
    key_user_action = models.PositiveSmallIntegerField(default=0,verbose_name="Key User Actions")

    class Meta:
        verbose_name = "Application Details"

class problemDetails(models.Model):
    tenant = models.CharField(max_length=255, verbose_name="Tenant Name")

    total_prb = models.PositiveSmallIntegerField(default=0,verbose_name="Total Problems")
    total_prb_resolved = models.PositiveSmallIntegerField(default=0,verbose_name="Resolved Problems")

    availability_severity = models.PositiveSmallIntegerField(default=0,verbose_name="Severity - Availability")
    performance_severity = models.PositiveSmallIntegerField(default=0,verbose_name="Severity - Performance")
    error_severity = models.PositiveSmallIntegerField(default=0,verbose_name="Severity - Error")
    resource_severity = models.PositiveSmallIntegerField(default=0,verbose_name="Severity - Resource")

    impact_service = models.PositiveSmallIntegerField(default=0,verbose_name="Impact - Service")
    impact_app = models.PositiveSmallIntegerField(default=0,verbose_name="Impact - Application")
    impact_environment = models.PositiveSmallIntegerField(default=0,verbose_name="Impact - Environment")
    impact_infra = models.PositiveSmallIntegerField(default=0,verbose_name="Impact - Infrastructure")
    mean_rsp_time = models.PositiveSmallIntegerField(default=0,verbose_name="Mean Response Time")

    class Meta:
        verbose_name = "Problem Details"

