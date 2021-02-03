from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import EmailDetail, TenantDetail
from advancedConfig.models import SMTPServer, FeatureAdoption
from django.db import models
import django.contrib.auth.admin
from django.contrib.auth.models import User, Group
from django.contrib import auth
from django.forms import ModelForm,PasswordInput
from dttool.forms import TenantDetailForm, SMTPServerForm
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _


admin.site.site_header = "Settings"
admin.site.site_title = "Settings"
admin.site.index_title = "Dynatrace Report Generation Tool"
admin.site.site_url = None

admin.site.unregister(User)
admin.site.unregister(Group)

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (_('User information'), {'fields': ('username', 'password','first_name','last_name','email','is_staff')}),
    )
    def has_add_permission(self, request):
      return True 
 
admin.site.register(User, CustomUserAdmin)


class SMTPServerAdmin(admin.ModelAdmin):
    form = SMTPServerForm

    class Meta:
      verbose_name = "SMTP Server Configuration"

    def has_add_permission(self, request):
      return False 

    def has_delete_permission(self, request, obj = None):
      return False 

admin.site.register(SMTPServer, SMTPServerAdmin)

class EmailDetailAdmin(admin.ModelAdmin):
    exclude = ["user"]
    senders_email = models.CharField(max_length=1000,verbose_name="Sender's email")
    receivers_email = models.CharField(max_length=1000, verbose_name="Receiver's email")

    list_display = ('receivers_email',)

    def __str__(self):
      return self.senders_email

    def has_add_permission(self, request):
      return True 

    def has_delete_permission(self, request, obj = None):
      return False 

admin.site.register(EmailDetail, EmailDetailAdmin)


class TenantDetailAdmin(admin.ModelAdmin):
    exclude = ["user"]
    form = TenantDetailForm
   
    def __str__(self):
      return self.tenant_name

    class Meta:
      verbose_name = "Tenant Details"

admin.site.register(TenantDetail, TenantDetailAdmin)
    
class FeatureAdoptionAdmin(admin.ModelAdmin):
    process_group = models.BooleanField(default=True, verbose_name="Process Group")
    request_attribute = models.BooleanField(default=True)
    alerting_profile = models.BooleanField(default=True)
    tagging = models.BooleanField(default=True)
    host_group = models.BooleanField(default=True)
    problem_notifications =  models.BooleanField(default=True, verbose_name="Problem Notifications")
    key_usr_actions = models.BooleanField(default=True, verbose_name="Key User Actions")
    naming_rules = models.BooleanField(default=True, verbose_name="Naming Rules")
    cloud_platform = models.BooleanField(default=True, verbose_name="Cloud Platforms")
    api = models.BooleanField(default=True, verbose_name="API")
    application = models.BooleanField(default=True, verbose_name="Applications")
    conversion_goal = models.BooleanField(default=True, verbose_name="Conversion Goal")
    synthetic = models.BooleanField(default=True, verbose_name="Synthetic Browsers")
    http_monitors = models.BooleanField(default=True, verbose_name="HTTP Monitors")

    def has_add_permission(self, request):
      return False 

    def has_delete_permission(self, request, obj = None):
      return False

admin.site.register(FeatureAdoption, FeatureAdoptionAdmin)
