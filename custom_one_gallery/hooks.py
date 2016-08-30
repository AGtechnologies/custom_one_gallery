# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "custom_one_gallery"
app_title = "Custom One Gallery"
app_publisher = "AG Technologies Pte Ltd"
app_description = "Customisation for One Gallery Pte Ltd"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@agtech.com.sg"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/custom_one_gallery/css/custom_one_gallery.css"
# app_include_js = "/assets/custom_one_gallery/js/custom_one_gallery.js"

# include js, css files in header of web template
# web_include_css = "/assets/custom_one_gallery/css/custom_one_gallery.css"
# web_include_js = "/assets/custom_one_gallery/js/custom_one_gallery.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "custom_one_gallery.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "custom_one_gallery.install.before_install"
# after_install = "custom_one_gallery.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "custom_one_gallery.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"custom_one_gallery.tasks.all"
# 	],
# 	"daily": [
# 		"custom_one_gallery.tasks.daily"
# 	],
# 	"hourly": [
# 		"custom_one_gallery.tasks.hourly"
# 	],
# 	"weekly": [
# 		"custom_one_gallery.tasks.weekly"
# 	]
# 	"monthly": [
# 		"custom_one_gallery.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "custom_one_gallery.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "custom_one_gallery.event.get_events"
# }

