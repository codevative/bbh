app_name = "bbh"
app_title = "BBH Property Management"
app_publisher = "Codevative"
app_description = "Frappe App for Management of requirements of BBH Group"
app_email = "mavee.shah@hotmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/bbh/css/bbh.css"
# app_include_js = "/assets/bbh/js/bbh.js"

# include js, css files in header of web template
# web_include_css = "/assets/bbh/css/bbh.css"
# web_include_js = "/assets/bbh/js/bbh.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "bbh/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {
    "Sales Invoice" : "public/js/custom_sales_invoice.js",
    "Subscription Plan" : "public/js/custom_subscription_plan.js"
    }
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "bbh.utils.jinja_methods",
# 	"filters": "bbh.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "bbh.install.before_install"
# after_install = "bbh.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "bbh.uninstall.before_uninstall"
# after_uninstall = "bbh.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "bbh.utils.before_app_install"
# after_app_install = "bbh.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "bbh.utils.before_app_uninstall"
# after_app_uninstall = "bbh.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "bbh.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }
override_doctype_class = {
	"Subscription": "bbh.bbh_property_management.overrides.custom_subscription.CustomSubscription"
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

doc_events = {
	"Sales Invoice": {
		"on_cancel": "bbh.utils.update_unit",
		"on_submit": "bbh.utils.update_unit"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"bbh.tasks.all"
# 	],
# 	"daily": [
# 		"bbh.tasks.daily"
# 	],
# 	"hourly": [
# 		"bbh.tasks.hourly"
# 	],
# 	"weekly": [
# 		"bbh.tasks.weekly"
# 	],
# 	"monthly": [
# 		"bbh.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "bbh.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "bbh.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "bbh.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["bbh.utils.before_request"]
# after_request = ["bbh.utils.after_request"]

# Job Events
# ----------
# before_job = ["bbh.utils.before_job"]
# after_job = ["bbh.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"bbh.auth.validate"
# ]
