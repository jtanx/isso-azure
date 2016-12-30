Installing Isso on an Azure Web App
===================================
1. Create a new web app (click [here](https://portal.azure.com/#create/Microsoft.WebSite) for shortcut to location in portal)
2. Once created, go to `your-app-name.scm.azurewebsites.net` (the Kudu interface)
3. Install the `Python 2.7.12 x64` and `IIS Manager` extensions. Click on `Restart site` when both are installed.
4. Under the installed site extensions, click on the play (▶) button for `IIS Manager`.
5. Go to the `applicationHost.xdt` tab
6. Enter the following contents:

   ```xml
   <?xml version="1.0"?>
   <configuration xmlns:xdt="http://schemas.microsoft.com/XML-Document-Transform">
     <system.webServer>
       <rewrite>
         <allowedServerVariables>
           <add name="HTTP_X_FORWARDED_FOR" xdt:Transform="InsertIfMissing"/>
         </allowedServerVariables>
       </rewrite>
       <fastCgi>
         <application
           fullPath="D:\home\Python27\python.exe"
           arguments="D:\home\Python27\wfastcgi.py"
           maxInstances="16"
           idleTimeout="21600"
           instanceMaxRequests="10000000"
           signalBeforeTerminateSeconds="60"
           xdt:Transform="InsertIfMissing"
           xdt:Locator="Match(fullPath)">
           <environmentVariables>
             <environmentVariable name="PYTHONHOME" value="D:\home\Python27" />
           </environmentVariables>
         </application>
       </fastCgi>
     </system.webServer>
     <location path="%XDT_SITENAME%" xdt:Transform="InsertIfMissing" xdt:Locator="Match(path)">
       <system.webServer xdt:Transform="InsertIfMissing">
         <applicationInitialization xdt:Transform="InsertIfMissing">
           <add initializationPage="/"  xdt:Transform="InsertIfMissing"/>
         </applicationInitialization>

         <rewrite xdt:Transform="InsertIfMissing">
           <rules xdt:Transform="InsertIfMissing">
             <rule name="Force HTTPS" enabled="true" stopProcessing="true">
               <match url="(.*)" ignoreCase="false" />
               <conditions>
                 <add input="{HTTPS}" pattern="off" />
                 <add input="{WARMUP_REQUEST}" pattern="1" negate="true" />
               </conditions>
               <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" appendQueryString="true" redirectType="Permanent" />
             </rule>
           </rules>
         </rewrite>    
       </system.webServer>
     </location>
   </configuration>
   ```
   
   You may omit the `<location>` block if you wish, but this forces HTTPS.
7. Click on `Save XDT`, then on `Restart site`.
8. Go back to Kudu and go to `Debug console->CMD`
9. Upgrade pip and install virtualenv:

   ```bat
   D:\home\Python27\python -m pip install --upgrade pip
   D:\home\Python27\python -m pip install virtualenv
   ```
11. Back in the Azure portal, go to `Deployment options`->`Configure required settings` and select `Local Git Repository`. Click Ok.
12. Modify `production.cfg` to configure Isso to suit your needs.
12. Push this repository using the provided git details from the portal.

## Notes

* As is, Isso does not require any of its dependencies to be compiled, as they all provide the necessary wheels. If any Python packages require compilation, you must compile it yourself and make the wheels. Install [Microsoft Visual C++ Compiler for Python 2.7](https://www.microsoft.com/en-au/download/details.aspx?id=44266) and use the provided console to compile the required packages with `pip wheel your-package`. Dump the wheels in a folder called `wheelhouse` and add `--find-links=wheelhouse` to `requirements.txt`.
* We use the Python provided by the extension as the pre-installed version runs a 32-bit version of Python 2.7.8. If you really want to, you can make use of this instead of the extension. However, to do so, you will have to build the `misaka` wheel yourself using a version of `pip wheel` that is compatible with the server. From past experience, version 0.24.0 of `pip wheel` should work. You may also need to downgrade `pip` to match that on the server.
* A custom Python deployment script is also used. This is necessary as the original deployment script assumes the use of the system/preinstalled Python. This was made by running:

   ```
   npm install -g azure-cli
   azure config mode asm
   azure site deploymentscript --python
   ```

   This generates the `.deployment` and `deploy.cmd` files. In `deploy.cmd`, replace everything in the `SelectPythonVersion` with:

   ```bat
   :SelectPythonVersion
   SET PYTHON_RUNTIME=python-2.7
   SET PYTHON_VER=2.7
   SET PYTHON_EXE=%SYSTEMDRIVE%\home\python27\python.exe
   SET PYTHON_ENV_MODULE=virtualenv
   ```
  
   The goal is to replace `D:\Python27` with `D:\home\Python27`
   
* The modification to `applicationHost.xdt` (which should reside in `D:\home\site`) is necessary so that IIS knows how to handle Python requests using the extension version that we installed. See [here](https://github.com/Azure/azure-python-siteextensions/issues/2) for more information.
* The (half-baked) [blog post](https://blogs.msdn.microsoft.com/pythonengineering/2016/08/04/upgrading-python-on-azure-app-service/) by MS on upgrading Python suggests to install Python modules directly and without the use of a virtualenv. I strongly disagree with this. If any of the packages break for whatever reason, it's much easier to just wipe the `env` folder and rebuild the virtualenv than it is to remove the packages from the installed Python.
* `HTTP_X_FORWARDED_FOR` needs to be set, otherwise the `remote_addr` that Isso gets will be `0.0.0.0`.

