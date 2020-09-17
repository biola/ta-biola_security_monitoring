# Overview #

This simple Splunk technology add-on has been created for the purpose of pulling OS security update info into Splunk.

To deploy
* Create a tarball containing the TA-biola_security_monitoring directory itself (not just the contents of the directory)
* Deploy it to your splunk monitored server and install it:
** e.g. $SPLUNK_HOME/bin/splunk install app /opt/splunkforwarder/etc/apps/TA-biolasecuritymonitoring-v3.0.tar.gz -auth admin:password