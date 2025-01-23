**Home Temperature Monitoring and Display

This repository has code for 2 system services:

1. Periodically (every 5 minutes) read temperatures from a Hubitat device at a fixed IP.
2. Provide a web server that allows a browser (on the local network only) to list the available data files, choose a file, and plot it.

The 'get_hub.py file is used by 'monitoring.service' to read the hub data and append to a csv file.

The 'plot.py' file is used by 'web_server.service' to list the files and plot the data.

