import requests
from django.contrib.auth.models import Permission, User
from django.db import models
from django.core import validators
from django import forms

class TenantDetail(models.Model):
   user = models.ForeignKey(User, default=1, verbose_name="User",on_delete=models.CASCADE)
   tenant_name = models.CharField(max_length=250,verbose_name="Tenant Name")
   tenant_URL = models.CharField(max_length=1000, verbose_name="Tenant URL")
   tenant_API_token = models.CharField(max_length=250, verbose_name="Tenant Token")

   def __str__(self):
     return self.tenant_name

   def clean(self):
     validated_url = True
     try:
       super().clean()
       response = requests.get(str(self.tenant_URL))
       validated_url = True
     except Exception as e:
       raise forms.ValidationError("Incorrect Tenant URL... For SaaS, a valid URL would be similar to \"https://<tenant-id>.live.dynatrace.com/api/v1/\" while for Managed, it would be similar \"https://<cluster-server>/e/<environment-id>/api/v1/\"" )

     if validated_url == True:
       query = str(self.tenant_URL) + "entity/infrastructure/hosts?includeDetails=true" 
       get_param = {'Accept':'application/json', 'Authorization':'Api-Token {}'.format(self.tenant_API_token)}
       populate_data = requests.get(query, headers = get_param)
       rsp_code = populate_data.status_code
 
       if rsp_code >= 400:
         raise forms.ValidationError("HTTP:401 - Authentication error.. Please verify the token")

class EmailDetail(models.Model):
   user = models.ForeignKey(User, default=1,on_delete=models.CASCADE)
   senders_email = models.CharField(max_length=1000,verbose_name="Sender's email")
   receivers_email = models.CharField(max_length=1000, verbose_name="Receiver's email")
   def has_delete_permission(self, request, obj = None):
     return False 

