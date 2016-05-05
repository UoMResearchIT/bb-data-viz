# bb-data-viz
Britain Breathing data visualisation Wordpress plugin.

Includes api.py which generates a static JSON file of the research data from the remote database.

api.py dependencies:

* Python 3
* PyMySQL: [https://github.com/PyMySQL/PyMySQL] (https://github.com/PyMySQL/PyMySQL)

The file *api.py* requires a *config.ini* file in the same directory containing the remote and local database logins. In the following format:

<pre>
<code>localusername: username  
localpassword: password  
localhostname: localhost  
remoteusername: username  
remotepassword: password  
remotehostname: remotedb.com</code>
</pre>