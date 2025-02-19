# Generated by Django 2.2 on 2020-07-22 15:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='applicationDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entityId', models.CharField(max_length=255, verbose_name='Entity ID')),
                ('application_displayName', models.CharField(max_length=255, verbose_name='Application Name')),
                ('overall_apdex', models.PositiveSmallIntegerField(default=0, verbose_name='Application Apdex')),
                ('satisfied_apdex_actions', models.PositiveSmallIntegerField(default=0, verbose_name='Apdex - Satisfied Actions')),
                ('tolerated_apdex_actions', models.PositiveSmallIntegerField(default=0, verbose_name='Apdex - Tolerated Actions')),
                ('frustrated_apdex_actions', models.PositiveSmallIntegerField(default=0, verbose_name='Apdex - Frustrated Actions')),
                ('conversion_goals', models.PositiveSmallIntegerField(default=0, verbose_name='Conversion Goals')),
                ('key_user_action', models.PositiveSmallIntegerField(default=0, verbose_name='Key User Actions')),
            ],
            options={
                'verbose_name': 'Application Details',
            },
        ),
        migrations.CreateModel(
            name='FeatureAdoption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_attribute', models.BooleanField(default=True, verbose_name='Request Attributes')),
                ('alerting_profile', models.BooleanField(default=True, verbose_name='Alerting Profile')),
                ('tagging', models.BooleanField(default=True, verbose_name='Automatic Tag')),
                ('host_group', models.BooleanField(default=True, verbose_name='Host Groups')),
                ('problem_notifications', models.BooleanField(default=True, verbose_name='Problem Notifications')),
                ('key_usr_actions', models.BooleanField(default=True, verbose_name='Key User Actions')),
                ('naming_rules', models.BooleanField(default=True, verbose_name='Naming Rules')),
                ('cloud_platform', models.BooleanField(default=True, verbose_name='Cloud Platforms')),
            ],
            options={
                'verbose_name': 'Feature Adoption Collection',
            },
        ),
        migrations.CreateModel(
            name='problemDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tenant', models.CharField(max_length=255, verbose_name='Tenant Name')),
                ('total_prb', models.PositiveSmallIntegerField(default=0, verbose_name='Total Problems')),
                ('total_prb_resolved', models.PositiveSmallIntegerField(default=0, verbose_name='Resolved Problems')),
                ('availability_severity', models.PositiveSmallIntegerField(default=0, verbose_name='Severity - Availability')),
                ('performance_severity', models.PositiveSmallIntegerField(default=0, verbose_name='Severity - Performance')),
                ('error_severity', models.PositiveSmallIntegerField(default=0, verbose_name='Severity - Error')),
                ('resource_severity', models.PositiveSmallIntegerField(default=0, verbose_name='Severity - Resource')),
                ('impact_service', models.PositiveSmallIntegerField(default=0, verbose_name='Impact - Service')),
                ('impact_app', models.PositiveSmallIntegerField(default=0, verbose_name='Impact - Application')),
                ('impact_environment', models.PositiveSmallIntegerField(default=0, verbose_name='Impact - Environment')),
                ('impact_infra', models.PositiveSmallIntegerField(default=0, verbose_name='Impact - Infrastructure')),
                ('mean_rsp_time', models.PositiveSmallIntegerField(default=0, verbose_name='Mean Response Time')),
            ],
            options={
                'verbose_name': 'Problem Details',
            },
        ),
        migrations.CreateModel(
            name='SMTPServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('smtp_user', models.CharField(max_length=250, verbose_name='SMTP User')),
                ('smtp_server', models.CharField(max_length=250, verbose_name='SMTP Server')),
                ('smtp_password', models.CharField(max_length=250, verbose_name='SMTP Password')),
                ('smtp_port', models.CharField(max_length=10, verbose_name='SMTP PORT')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'SMTP Server Configuration',
            },
        ),
        migrations.CreateModel(
            name='featureAdoptionCount',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('tenant', models.CharField(max_length=255, verbose_name='Tenant name')),
                ('mgmt_zone', models.CharField(max_length=255, verbose_name='Management Zone')),
                ('host_units_consumption', models.FloatField(default=0, null=True, verbose_name='Host Unit Consumption')),
                ('dem_units_consumption', models.FloatField(default=0, null=True, verbose_name='DEM Unit Consumption')),
                ('application_count', models.PositiveSmallIntegerField(default=0, verbose_name='Applications Count')),
                ('syn_browser_count', models.PositiveSmallIntegerField(default=0, verbose_name='Synthetic Browser Count')),
                ('http_browser_count', models.PositiveSmallIntegerField(default=0, verbose_name='HTTP Count')),
                ('host_group_count', models.PositiveSmallIntegerField(default=0, verbose_name='Host Groups Count')),
                ('process_group_count', models.PositiveSmallIntegerField(default=0, verbose_name='Process Group Count')),
                ('tag_count', models.PositiveSmallIntegerField(default=0, verbose_name='Tag Count')),
                ('alerting_profile_count', models.PositiveSmallIntegerField(default=0, verbose_name='Alerting Profile Count')),
                ('mgmt_zone_count', models.PositiveSmallIntegerField(default=0, verbose_name='Management Zone Count')),
                ('naming_rule_count', models.PositiveSmallIntegerField(default=0, verbose_name='Naming Rule Count')),
                ('problem_notifications_count', models.PositiveSmallIntegerField(default=0, verbose_name='Problem Integration Count')),
                ('cloud_platform_count', models.PositiveSmallIntegerField(default=0, verbose_name='Cloud Platform Count')),
                ('key_usr_req_count', models.PositiveSmallIntegerField(default=0, verbose_name='Key User Actions')),
                ('api_token_count', models.PositiveSmallIntegerField(default=0, verbose_name='API Tokens')),
                ('request_attr_count', models.PositiveSmallIntegerField(default=0, verbose_name='Request Attribute')),
            ],
            options={
                'verbose_name': 'Feature Adoption Data',
                'unique_together': {('id', 'tenant', 'mgmt_zone')},
            },
        ),
    ]
