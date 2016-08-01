# bb-data-viz

Britain Breathing data visualisation Wordpress plugin and data API.

Includes api.py which generates static KML files of the research data from the local database.

See import list in api.py for dependencies.

The file *api.py* requires a *config.ini* file in the same directory containing the remote and local database logins. In the following format:

<pre>
<code>localusername: username  
localpassword: password  
localhostname: localhost  
remoteusername: username  
remotepassword: password  
remotehostname: remotedb.com</code>
</pre>
