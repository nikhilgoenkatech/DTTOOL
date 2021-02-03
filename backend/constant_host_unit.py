#all the constants
INFRA_API = 'entity/infrastructure/hosts?includeDetails=true'
TIMESERIES_API="timeseries/com.dynatrace.builtin:host.availability?includeData=true&&relativeTime=10mins"
FETCH_APPLICATIONS = "entity/applications/"
FETCH_SYN_APPLICATIONS = "synthetic/monitors"
APP_BILLING_API = "metrics/query?metricSelector=builtin%3Abilling.apps.web.sessionsWithoutReplayByApplication%3Afold&resolution=1w"
SYN_BILLING_API = "metrics/query?metricSelector=builtin%3Abilling.synthetic.actions%3Afold&resolution=1w"
HTTP_BILLING_API = "metrics/query?metricSelector=builtin%3Abilling.synthetic.requests%3Afold&resolution=1w"
ALERTING_PRF_API = "alertingProfiles"
ADD_PROP_ALERTING_PRF_API="alertingProfiles/ID"
PROCESS_GROUP="entity/infrastructure/process-groups?includeDetails=true"
TAGS="autoTags"
NAMING_RULES="service/requestNaming"
MGMT_ZONES_API="managementZones"
PROBLEM_NOTIFICATIONS="notifications"
SPECIFIC_PROBLEM_NOTIFICATION="notifications/ID"
TOKENS="tokens"
REQ_ATTRIBUTES="service/requestAttributes"
KEY_REQUESTS="userSessionQueryLanguage/table?query=SELECT count(DISTINCT(useraction.name)) FROM useraction where useraction.internalKeyUserActionId IS NOT NULL and useraction.application=\"APP_NAME\""
APDEX_API="userSessionQueryLanguage/table?query=select userExperienceScore,count(*) as count FROM usersession WHERE useraction.application IS \"APP_NAME\" group by userExperienceScore ORDER BY count DESC&startTimestamp=STARTTIME&endTimestamp=ENDTIME&addDeepLinkFields=false&explain=false"
CONVERSION_GOAL="applications/web/ENTITY_ID"
APP_ERR_COUNT="select avg(userActionCount) FROM usersession WHERE useraction.errorCount > 1 and useraction.application=\"APP_NAME\""
PROBLEMS="problem/feed?relativeTime=week"
LINK_REQ_ATTR="https://www.dynatrace.com/support/help/shortlink/request-attributes"

