#!$SPLUNK_HOME/bin/python

# Copyright 2012, Biola University 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import os
import time
import datetime
import sys
import subprocess

now = datetime.datetime.now()
daysSinceLastUpdateCheck = 0
daysSinceLastUpgrade = 0
numberOfUpdatesPendingReboot = 0
numberOfPendingSecurityUpdates = 0

if sys.platform == "darwin":
	distro = sys.platform
else:
	# Check for distribution using proper method for present python version
	import platform
	if str(sys.version_info[0]) + "." +  str(sys.version_info[1]) + "." + str(sys.version_info[2]) >= "2.6":
		distro = platform.linux_distribution()[0]
	else:
		distro = platform.dist()[0]

if distro == "Ubuntu":

	# Check for most recent apt update
	if os.path.isfile("/var/lib/apt/periodic/update-stamp"):
		daysSinceLastUpdateCheck = round((time.time() - os.path.getmtime("/var/lib/apt/periodic/update-stamp"))/60/60/24, 2)
	else:
		daysSinceLastUpdateCheck = "ERROR -  No recorded apt updates found according to /var/lib/apt/periodic/update-stamp "

	# Check for most recent apt upgrade
	if os.path.isfile("/var/lib/apt/periodic/upgrade-stamp"):
		daysSinceLastUpgrade = round((time.time() - os.path.getmtime("/var/lib/apt/periodic/upgrade-stamp"))/60/60/24, 2)
	else:
		daysSinceLastUpgrade = "ERROR -  No recorded apt upgrades found according to /var/lib/apt/periodic/upgrade-stamp "

	# Check for number of pending security updates
	if os.path.isfile("/usr/lib/update-notifier/apt-check"):
		import re
		p = subprocess.Popen(["/usr/lib/update-notifier/apt-check"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		output, errors = p.communicate()
		numberOfPackagesSearch = re.search('[0-9]+;([0-9]+)', errors)
		numberOfPendingSecurityUpdates = numberOfPackagesSearch.group(1)
	else:
		numberOfPendingSecurityUpdates = "ERROR - update-notifier-common package does not appear to be installed"

	# Check for packages that require a reboot
	if os.path.isfile("/var/run/reboot-required.pkgs"):
		file = open("/var/run/reboot-required.pkgs")
		for line in file:
			numberOfUpdatesPendingReboot += 1

# Future python 2.7+ version notes:
# elif distro == "redhat":
# 	securityCheckOutput = subprocess.check_output(["yum", "list", "updates", "--security"])
elif distro == "redhat":
	if os.path.isfile("/usr/lib/yum-plugins/security.py"):
		p = subprocess.Popen(["yum", "list", "updates", "--security"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		output, errors = p.communicate()
		if "No packages needed, for security" in output:
			numberOfPendingSecurityUpdates = 0
		elif "Needed" in output:
			import re
			numberOfPackagesSearch = re.search('Needed\s(.*)\sof\s[0-9]+\spackages', output)
			numberOfPendingSecurityUpdates = numberOfPackagesSearch.group(1)
		else:
			numberOfPendingSecurityUpdates = "ERROR - Number of missing updates not properly detected"
	else:
		numberOfPendingSecurityUpdates = "ERROR - yum-security plugin does not appear to be installed"



elif distro == "darwin":
		p = subprocess.Popen(["softwareupdate", "-l"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		output, errors = p.communicate()
		if "No new software available" in output:
			numberOfPendingSecurityUpdates = 0
		elif "Software Update found the following" in output:
			import re
			for line in output.splitlines():
				if "recommended" in line:
					if "[restart]" in line:
						numberOfUpdatesPendingReboot += 1
					numberOfPendingSecurityUpdates += 1
					lineRegexObj = re.search('\\t([-._a-zA-Z0-9\s]+\([.0-9]+\)),\s', line)
					try:
						print(now.strftime("%Y-%m-%d %H:%M") +  " AvailableSecurityUpdate=\"" + lineRegexObj.group(1) + "\" Severity=recommended")
					except:
						print(now.strftime("%Y-%m-%d %H:%M") +  " ERROR - exception caught while checking for Apple Software Updates (likely a regular expression miss")
		else:
			numberOfPendingSecurityUpdates = "ERROR - Number of missing updates not properly detected"


#Output the results
if distro == "Ubuntu":
	print(now.strftime("%Y-%m-%d %H:%M") + " DaysSinceLastUpdateCheck=" + str(daysSinceLastUpdateCheck) + " DaysSinceLastUpgrade=" + str(daysSinceLastUpgrade) + " NumberOfPendingSecurityUpdates=" + str(numberOfPendingSecurityUpdates) + " NumberOfUpdatesPendingReboot=" + str(numberOfUpdatesPendingReboot))
elif distro == "redhat":
	print(now.strftime("%Y-%m-%d %H:%M") + " NumberOfPendingSecurityUpdates=" + str(numberOfPendingSecurityUpdates))
elif distro == "darwin":
	print(now.strftime("%Y-%m-%d %H:%M") + " NumberOfPendingSecurityUpdates=" + str(numberOfPendingSecurityUpdates) + " NumberOfUpdatesPendingReboot=" + str(numberOfUpdatesPendingReboot))
else:
	print(now.strftime("%Y-%m-%d %H:%M") + "ERROR - security update information not currently available on this platform")
