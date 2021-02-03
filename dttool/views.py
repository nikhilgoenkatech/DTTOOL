from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .forms import UserForm
from .models import EmailDetail, TenantDetail
from advancedConfig.models import FeatureAdoption, SMTPServer 
from backend.constant_host_unit import *
from backend.host_mgmt_zone import *
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect


def change_password(request):
    if request.method == 'POST':
        print(request.method)
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            print("IN HERE")
            user = form.save()
            update_session_auth_hash(request, user) 
            return redirect('../')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'dttool/change_password.html', {
        'form': form
    })
	
def index(request):

    if not hasattr(request, 'user'):
        return render(request, 'dttool/login.html')

    if not request.user.is_authenticated():
        return render(request, 'dttool/login.html')
    else:
        model = EmailDetail
        field_names = list(model._meta.get_fields())
        email_tbl = [f.verbose_name for f in field_names if (not("SMTP" in f.verbose_name) and f.verbose_name != "ID" and f.verbose_name != "user")]  

        field_names = [f.name for f in model._meta.get_fields() if f.name != "id" and not("smtp" in f.name) and not("user" in f.name)]
        email_data = [[getattr(ins, name) for name in field_names]
                for ins in model.objects.prefetch_related().all()]

        model = TenantDetail 
        field_names = list(model._meta.get_fields())
        tenant_tbl = [f.verbose_name for f in field_names if (not("Token" in f.verbose_name) and f.verbose_name != "ID" and f.verbose_name != "User")]

        field_names = [f.name for f in model._meta.get_fields() if f.name != "id" and not("token" in f.name) and not("user" in f.name)]
        tenant_data = [[getattr(ins, name) for name in field_names]
                for ins in model.objects.prefetch_related().all()]

        model = FeatureAdoption
        field_names = list(model._meta.get_fields())
        titles = [f.verbose_name for f in field_names if (not("Enabled" in f.verbose_name) and f.verbose_name != "ID")]  

        field_names = [f.name for f in model._meta.get_fields() if f.name != "id" and not("count" in f.name)]
        data = [[getattr(ins, name) for name in field_names]
                for ins in model.objects.prefetch_related().all()]

        model = SMTPServer 
        field_names = list(model._meta.get_fields())
        smtp_titles = [f.verbose_name for f in field_names if (not("Password" in f.verbose_name) and f.verbose_name != "ID" )]  

        field_names = [f.name for f in model._meta.get_fields() if f.name != "id" and not("Password" in f.verbose_name)]
        smtp_data = [[getattr(ins, name) for name in field_names]
                for ins in model.objects.prefetch_related().all()]

        return render(request, 'dttool/index.html', {'field_names': titles, 'data': data, 'email_tbl':email_tbl, 'email_data':email_data, 'tenant_tbl':tenant_tbl, 'tenant_data':tenant_data, 'smtp_titles': smtp_titles, 'smtp_data':smtp_data})

def generate_report(request):
    if not request.user.is_authenticated():
        return render(request, 'dttool/login.html')
    else:
        SMTPObj = SMTPServer.objects.filter()
        tenantObj = TenantDetail.objects.filter()
        EmailObj = EmailDetail.objects.all()
        featureObj = FeatureAdoption.objects.filter()
        err_msg = relay_generate_report(tenantObj, SMTPObj, EmailObj, featureObj[0])
        model = EmailDetail
        field_names = list(model._meta.get_fields())
        email_tbl = [f.verbose_name for f in field_names if (not("SMTP" in f.verbose_name) and f.verbose_name != "ID" and f.verbose_name != "user")]  

        field_names = [f.name for f in model._meta.get_fields() if f.name != "id" and not("smtp" in f.name) and not("user" in f.name)]
        email_data = [[getattr(ins, name) for name in field_names]
                for ins in model.objects.prefetch_related().all()]

        model = TenantDetail 
        field_names = list(model._meta.get_fields())
        tenant_tbl = [f.verbose_name for f in field_names if (not("Token" in f.verbose_name) and f.verbose_name != "ID" and f.verbose_name != "User")]

        field_names = [f.name for f in model._meta.get_fields() if f.name != "id" and not("token" in f.name) and not("user" in f.name)]
        tenant_data = [[getattr(ins, name) for name in field_names]
                for ins in model.objects.prefetch_related().all()]

        model = FeatureAdoption
        field_names = list(model._meta.get_fields())
        titles = [f.verbose_name for f in field_names if (not("Enabled" in f.verbose_name) and f.verbose_name != "ID")]  

        field_names = [f.name for f in model._meta.get_fields() if f.name != "id" and not("count" in f.name)]
        data = [[getattr(ins, name) for name in field_names]
                for ins in model.objects.prefetch_related().all()]

        model = SMTPServer 
        field_names = list(model._meta.get_fields())
        smtp_titles = [f.verbose_name for f in field_names if (not("Password" in f.verbose_name) and f.verbose_name != "ID" )]  

        field_names = [f.name for f in model._meta.get_fields() if f.name != "id" and not("Password" in f.verbose_name)]
        smtp_data = [[getattr(ins, name) for name in field_names]
                for ins in model.objects.prefetch_related().all()]
        
        context_dict={}
        context_dict["field_names"] = titles
        context_dict["data"] = data
        context_dict["email_tbl"]=email_tbl
        context_dict["email_data"]=email_data
        context_dict["tenant_tbl"]=tenant_tbl
        context_dict["tenant_data"]=tenant_data
        context_dict["smtp_titles"]=smtp_titles
        context_dict["smtp_data"]=smtp_data
        context_dict["error_message"] = "The Report has been generated and e-mailed"
        if err_msg == "":
          err_msg = "Thank-you for using the tool. The report has been generated succesfully and emailed to the configured e-mail addresses."

        #return render(request, 'dttool/index.html', context_dict)
        return render(request, 'dttool/index.html', {'field_names': titles, 'data': data, 'email_tbl':email_tbl, 'email_data':email_data, 'tenant_tbl':tenant_tbl, 'tenant_data':tenant_data, 'smtp_titles': smtp_titles, 'smtp_data':smtp_data, 'flag':True, 'message': err_msg})


def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'dttool/login.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                model = EmailDetail
                field_names = list(model._meta.get_fields())
                email_tbl = [f.verbose_name for f in field_names if (not("SMTP" in f.verbose_name) and f.verbose_name != "ID" and f.verbose_name != "user")]

                field_names = [f.name for f in model._meta.get_fields() if f.name != "id" and not("smtp" in f.name) and not("user" in f.name)]
                email_data = [[getattr(ins, name) for name in field_names]
                        for ins in model.objects.prefetch_related().all()]

                model = TenantDetail
                field_names = list(model._meta.get_fields())
                tenant_tbl = [f.verbose_name for f in field_names if (not("Token" in f.verbose_name) and f.verbose_name != "ID" and f.verbose_name != "User")]

                field_names = [f.name for f in model._meta.get_fields() if f.name != "id" and not("token" in f.name) and not("user" in f.name)]
                tenant_data = [[getattr(ins, name) for name in field_names]
                        for ins in model.objects.prefetch_related().all()]

                model = FeatureAdoption
                field_names = list(model._meta.get_fields())
                titles = [f.verbose_name for f in field_names if (not("Enabled" in f.verbose_name) and f.verbose_name != "ID")]

                field_names = [f.name for f in model._meta.get_fields() if f.name != "id" and not("count" in f.name)]
                data = [[getattr(ins, name) for name in field_names]
                        for ins in model.objects.prefetch_related().all()]

                model = SMTPServer
                field_names = list(model._meta.get_fields())
                smtp_titles = [f.verbose_name for f in field_names if (not("Password" in f.verbose_name) and f.verbose_name != "ID" )]
        
                field_names = [f.name for f in model._meta.get_fields() if f.name != "id" and not("Password" in f.verbose_name)]
                smtp_data = [[getattr(ins, name) for name in field_names]
                        for ins in model.objects.prefetch_related().all()]
        
                return render(request, 'dttool/index.html', {'field_names': titles, 'data': data, 'email_tbl':email_tbl, 'email_data':email_data, 'tenant_tbl':tenant_tbl, 'tenant_data':tenant_data, 'smtp_titles': smtp_titles, 'smtp_data':smtp_data})


            else:
                return render(request, 'dttool/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'dttool/login.html', {'error_message': 'Invalid login'})
    return render(request, 'dttool/login.html')


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                feature_count = FeatureAdoption.objects.all().count()
                if feature_count == 0:
                  #make sure there is atleast one object in model available
                  FeatureAdoption.objects.create()

                smtp_count = SMTPServer.objects.all().count()
                if smtp_count == 0:
                  #make sure there is atleast one object in model available
                  SMTPServer.objects.create()

                model = EmailDetail
                field_names = list(model._meta.get_fields())
                email_tbl = [f.verbose_name for f in field_names if (not("SMTP" in f.verbose_name) and f.verbose_name != "ID" and f.verbose_name != "user")]  

                field_names = [f.name for f in model._meta.get_fields() if f.name != "id" and not("smtp" in f.name) and not("user" in f.name)]
                email_data = [[getattr(ins, name) for name in field_names]
                        for ins in model.objects.prefetch_related().all()]

                model = TenantDetail 
                field_names = list(model._meta.get_fields())
                tenant_tbl = [f.verbose_name for f in field_names if (not("Token" in f.verbose_name) and f.verbose_name != "ID" and f.verbose_name != "User")]

                field_names = [f.name for f in model._meta.get_fields() if f.name != "id" and not("token" in f.name) and not("user" in f.name)]
                tenant_data = [[getattr(ins, name) for name in field_names]
                        for ins in model.objects.prefetch_related().all()]

                model = FeatureAdoption
                field_names = list(model._meta.get_fields())
                titles = [f.verbose_name for f in field_names if (not("Enabled" in f.verbose_name) and f.verbose_name != "ID")]  

                field_names = [f.name for f in model._meta.get_fields() if f.name != "id" and not("count" in f.name)]
                data = [[getattr(ins, name) for name in field_names]
                        for ins in model.objects.prefetch_related().all()]

                model = SMTPServer 
                field_names = list(model._meta.get_fields())
                smtp_titles = [f.verbose_name for f in field_names if (not("Password" in f.verbose_name) and f.verbose_name != "ID" )]  

                field_names = [f.name for f in model._meta.get_fields() if f.name != "id" and not("Password" in f.verbose_name)]
                smtp_data = [[getattr(ins, name) for name in field_names]
                        for ins in model.objects.prefetch_related().all()]
                
                context_dict={}
                context_dict["field_names"] = titles
                context_dict["data"] = data
                context_dict["email_tbl"]=email_tbl
                context_dict["email_data"]=email_data
                context_dict["tenant_tbl"]=tenant_tbl
                context_dict["tenant_data"]=tenant_data
                context_dict["smtp_titles"]=smtp_titles
                context_dict["smtp_data"]=smtp_data
                context_dict["error_message"] = "The Report has been generated and e-mailed"

                #return render(request, 'dttool/index.html', context_dict)
                return render(request, 'dttool/index.html', {'field_names': titles, 'data': data, 'email_tbl':email_tbl, 'email_data':email_data, 'tenant_tbl':tenant_tbl, 'tenant_data':tenant_data, 'smtp_titles': smtp_titles, 'smtp_data':smtp_data, 'flag':False})
    context = {
        "form": form,
    }
    return render(request, 'dttool/register.html', context)

