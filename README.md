# Magic-Crawler

Using Bitbucket's Rest Api (1.0) this script will search through all repositories in search of **gherkin feature files**.\
\
\
In it's default configuration it saves each repositories gathered data as Json files in the **/data/** directory as well as printing out the Json string to console
(each line being a seperate repository).\
The main function also returns a list of all Json strings sorted by the repository index\
\
It will only create a Project file if a repository has at least one feature file and if it has more than one they will all be added into a single project file.
<br/><br/>

## **Setup:**

You can use **generateEnv.py** to interactively generate the required config file interactively but if you want to do that manually follow the guide below
<br/><br/><br/><br/>
There needs to be a **.env** file in the root script directory with the bitbucket credentials and url in the following format:

You will find all these variables in an example file called **setup_example**
but don't forget to rename it **.env** when you are done.
<br/><br/>

### **User credentials**

>**BITBUCKET_CREDENTIAL_TOKEN="Basic <-encoded_credentials->"**

To get the encoded credentials you need to **base64** encode your credential string "**username:password**" and place it in the location above.
<br/><br/>

### **Api Url**

>**BITBUCKET_PROJECT_URL="http://<bitbucket_url>/rest/api/1.0/projects/"**

Replace the **bitbucket_url** tag with your bitbucket url.
<br/><br/>

### **Tcp limit**

>**TCP_REQUEST_LIMIT=30**

Here you can set how many maximum requests the script will send to the server.\
\
Avoid going over 50 if you don't want to nuke your internal bitbucket server.\
\
\
\
These variables need to be present and properly setup for the script to work its magic ;)
