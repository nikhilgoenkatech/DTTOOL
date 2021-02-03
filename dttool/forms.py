from django import forms
from django.contrib.auth.models import User

from .models import TenantDetail, EmailDetail
from advancedConfig.models import FeatureAdoption, SMTPServer

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class FeatureAdoption(forms.ModelForm):
   class Meta:
     model = FeatureAdoption 
     fields = ['request_attribute','alerting_profile','tagging','process_group','host_group','problem_notifications','key_usr_actions','naming_rules','cloud_platform','api']

class TenantDetailForm(forms.ModelForm):

  class Meta:
    model = TenantDetail
    widgets = {
      'tenant_API_token': forms.PasswordInput(attrs={'rows':3,'cols':70,'style':'height:1em;'})
    }
    fields = ['tenant_name', 'tenant_URL', 'tenant_API_token']

class EmailDetail(forms.ModelForm):
  class Meta:
    model = EmailDetail 
    fields = ['senders_email','receivers_email']


class SMTPServerForm(forms.ModelForm):

  class Meta:
    model = SMTPServer 
    widgets = {
      'smtp_password': forms.PasswordInput(attrs={'rows':3,'cols':70,'style':'height:1em;'})
    }
    fields = ['smtp_user', 'smtp_server', 'smtp_port','smtp_password']

