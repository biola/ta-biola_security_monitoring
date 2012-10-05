#!$SPLUNK_HOME/bin/python

import os
import time
import platform
import datetime
import sys

now = datetime.datetime.now()
daysSinceLastUpdateCheck = 0
daysSinceLastUpgrade = 0
numberOfUpdatesPendingReboot = 0

# Check for distribution using proper method for present python version
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
		import subprocess
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

#Output the results
if distro == "Ubuntu":
	print(now.strftime("%Y-%m-%d %H:%M") + " DaysSinceLastUpdateCheck=" + str(daysSinceLastUpdateCheck) + " DaysSinceLastUpgrade=" + str(daysSinceLastUpgrade) + " NumberOfUpdatesPendingReboot=" + str(numberOfUpdatesPendingReboot))
elif distro == "redhat":
	print(now.strftime("%Y-%m-%d %H:%M") + " NumberOfPendingSecurityUpdates=" + str(numberOfPendingSecurityUpdates))
else:
	print(now.strftime("%Y-%m-%d %H:%M") + "FIXME - security update information not currently available on this platform")
