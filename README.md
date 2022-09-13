# QGS Parse Layer Plugin

Parse QGIS 3 project and write a JSON config file with layer information.

As the plugin offers the possiblity to upload the generated configuration files to a SFTP server, it uses pysftp. This Python library has some dependencies which can't be resolved easily on different operating systems. So for now you have to manually install pysftp:

1. Open console and go to `qgis_installation_directory\apps\Python39\Scripts\` (or just `OSGeo4W_installation_directoy` on Windows)
2. Type: `pip install pysftp`
3. Install the plugin from QGIS

More information coming soon...