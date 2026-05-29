**Home Temperature Monitoring and Display

This repository has code for 2 system services:

1. monitoring: Periodically (every 5 minutes) read temperatures from a Hubitat device at hubitat.local (discovered via mDNS).
2. web-server: Provide a web server that allows a browser (on the local network only) to list the available data files, choose a file, and plot it.

The 'get_hub.py file is used by 'monitoring.service' to read the hub data and append to a csv file.

The 'plot.py' file is used by 'web-server.service' to provide a www page (at localhost:5000) to list the files and plot the data.

Note that the service files assume the python scripts are located at ~/Documents/Projects/gethub.
To install:

1. Copy service files to ~/.config/systemd/user.
2. Enable services using 
		systemctl --user enable monitoring web-server

Data (.csv) and error (.err) files will be located at ~/.logs/monitoring.
