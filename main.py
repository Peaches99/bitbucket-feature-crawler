import asyncio
import base64
import json
import os
import logging
import shutil
import sys
import datetime

import aiohttp
from aiohttp.client import ClientSession
from dotenv import load_dotenv
from numpy import empty, save

import util.objectBuilder as ob

try:
    os.remove("lastLog.log")
except:
    pass
logging.basicConfig(filename='lastLog.log', encoding='utf-8', level=logging.DEBUG)

# Important check as the script will not work without an environment file
if os.path.exists(".env") is False:
    logging.critical("Missing Env file.")
    sys.exit()
else:
    logging.info("Env file found.")

logging.info("Loading Env Data...")
load_dotenv()


token = os.getenv("BITBUCKET_CREDENTIAL_TOKEN")
bitbucket_projects = os.getenv("BITBUCKET_PROJECT_URL")
tcp_limit = int(os.getenv("TCP_REQUEST_LIMIT"))

logging.info("Env data loaded.")

if tcp_limit > 100:
    logging.warning("Tcp request limit over 100. This might impact your server performance.")
elif tcp_limit < 10:
    logging.warning("Tcp request limit under 10. This might slow down the script significantly.")
elif tcp_limit == 1:
    logging.warning("Tcp request limit is 1. This will run extremely low.")
elif tcp_limit == 0:
    logging.critical("Tcp request limit is 0. The script is not able to run.")

headers = {"Content-Type": "application/json", "Authorization": token}
projectUrl = bitbucket_projects.rstrip(bitbucket_projects[-1])+ "?limit=2000"
logging.info("Projects Url: "+projectUrl)
            

async def download_link(url:str,session:ClientSession):
    logging.info("downloading: "+url+" ...")
    headers = {"Content-Type": "application/json", "Authorization": token}
    async with session.get(url, headers=headers) as response:
        result = await response.text()
    if result is not empty:
        return(result)


async def download_all(urls:list):
    my_conn = aiohttp.TCPConnector(limit=tcp_limit)
    async with aiohttp.ClientSession(connector=my_conn) as session:
        tasks = []
        for url in urls:
            task = asyncio.ensure_future(download_link(url=url,session=session))
            tasks.append(task)
        out = await asyncio.gather(*tasks,return_exceptions=True)
        return(out)


def saveJson(name, inFile):
    logging.info("Saving Json: "+name+" ...")
    if os.path.exists(name+".json"):
        os.remove(name+".json")

    data = json.dumps(inFile, indent=4)
    
    file = open(name+".json", "x")
    file.write(data)
    file.close
    logging.info("Finished")


def cDir(name):
    try:
        os.makedirs(name)
    except:
        pass
        

def tokenize(s):
    arr = []
    stringTokenizer = s.split()
    for i in stringTokenizer:
        arr.append(i)
    return arr


def matchKey(target, matchList):
    for idx, keyList in enumerate(matchList):
        for i in range(len(matchList[idx])):
            if matchList[idx][i] == target:
                return(idx, i)
    return None


async def getAllFeatureUrls(repo_index, repo_feature_index, feature_repos, repo_key_index, keys):
    file_urls = []
        #Generate the urls before downloading all of them at the same time for efficiency
    for idx, repo in enumerate(repo_index):
        
        dir_url = []
        dir_names = []

        file_count = 0
        try:
            feature_index = feature_repos[repo]
            file_count = feature_index["size"]
            
            
        except:
            pass
        
        for i in range(file_count):
            if feature_index['values'][i]['type'] != "DIRECTORY":

                file_urls.append(bitbucket_projects+keys[matchKey(repo, repo_key_index)[0]]+"/repos/"+repo+"/browse/src/test/resources/features/"+feature_index["values"][i]["path"]["name"])

            elif feature_index['values'][i]['type'] == "DIRECTORY":
                dir_names.append(feature_index['values'][i]["path"]["name"])
                dir_url.append(bitbucket_projects+keys[matchKey(repo, repo_key_index)[0]]+"/repos/"+repo+"/browse/src/test/resources/features/"+feature_index["values"][i]["path"]["name"])

        dirs = await download_all(dir_url)
        subfiles = []

        for i, dir in enumerate(dirs):
            dir = json.loads(json.loads(json.dumps(dir, indent=4)))
            children = dir["children"]["values"]

            for child in children:
                child = json.loads(json.dumps(child, indent=4))
                if child["type"] != "DIRECTORY":
                    subfiles.append(child["path"]["name"])
        for file in subfiles:
            file_urls.append(bitbucket_projects+keys[matchKey(repo, repo_key_index)[0]]+"/repos/"+repo+"/browse/src/test/resources/features/"+dir_names[i]+"/"+file)
            repo_feature_index[idx] = str(int(repo_feature_index[idx]) + 1)

    return file_urls, repo_feature_index


async def getFeatureIndex(dir_features, repo_index):
    feature_repos = {}
    repo_feature_index = []

    for idx, dir in enumerate(dir_features):
        dir = json.loads(json.loads(json.dumps(dir, indent=4)))
        try:
            if dir["children"]["size"] > 0:
                feature_repos.update({repo_index[idx]: dir["children"]})

                temp = 0
                for feature in dir["children"]["values"]:
                    if feature['type'] != "DIRECTORY":
                        temp += 1
                        logging.info("Found feature at repo #"+idx)
                repo_feature_index.append(str(temp))
            else:
                repo_feature_index.append("0")
        except:
            repo_feature_index.append("0")
            

    return repo_feature_index, feature_repos


async def getRepoIndex(projects):

    repo_urls = []
    repo_key_index = []
    repo_index = []
    keys = []
    key_urls = []

    for p in projects:
        key = p["key"]
        key_urls.append(bitbucket_projects+key+"/repos?limit=1000")
        keys.append(p["key"])

    project_repos = await download_all(key_urls)
    project_count = len(keys)
    
    #Check how many repos have a feature dir which suggests they have feature files
    for i in range(project_count):
        repo_json = json.loads(json.loads(json.dumps(project_repos[i], indent=4)))
        repo_names = []
        repo_count = repo_json["size"]
        
        for x in range(repo_count):
            repo_name = repo_json["values"][x]["slug"]

            repo_index.append(str(repo_name))

            url = bitbucket_projects+keys[i]+"/repos/"+repo_name+"/browse/src/test/resources/features"
            repo_urls.append(url)
            repo_names.append(repo_name)
            
        repo_key_index.append(repo_names)

    return repo_index, repo_key_index, keys, repo_urls


async def buildOutput(repo_index, repo_key_index , repo_feature_index, keys, save_json):

    out = []

    for idx, repo in enumerate(repo_feature_index):
            
        if repo != "0":
            all_lines = []
            for elem in repo:
                elem = json.loads(json.loads(json.dumps(elem, indent=4)))
                lines = []
                for line in elem["lines"]:
                    lines.append(line["text"])
                
                all_lines.append(lines)

            # builds object using objectBuilder.py
            project = ob.buildProject(keys[matchKey(repo_index[idx], repo_key_index)[0]], repo_index[idx], all_lines)
            
            outJson = {}

            outJson.update({"projectID":project.getProjectID()})

            features = []

            for idx2, feature in enumerate(project.getFeatures()):

                features.append({"featureName": feature.getFeatureName(), "description": feature.getDescription(), "scenarios": []})

                for i, scenario in enumerate(feature.getScenarios()):
                        features[idx2]["scenarios"].append({"scenarioName": scenario.getScenarioName(), "syntax": {"given": "", "when": "", "then": "",}})
                        features[idx2]["scenarios"][i]["syntax"].update({"given": scenario.getGiven(), "when": scenario.getWhen(), "then": scenario.getThen()})
            
            outJson.update({"features": features})

            

            out.append(outJson)
    if save_json : saveJson("data/output", out)

    return out


async def assignFeatures(repo_feature_index, feature_files):

    files = feature_files

    for idx, elem in enumerate(repo_feature_index):
        if elem != "0":
            features = []
            for i in range(int(elem)):
                features.append(files[i])
                
            for i in range(int(elem)):
                files.pop(0)

            repo_feature_index[idx] = features

    return repo_feature_index


async def main():    

        
        logging.info("Downloading the project index")
        #Download all projects information for further processing
        projectsRaw = await download_all([projectUrl])
        projects = json.loads(json.loads(json.dumps(projectsRaw[0], indent=4)))["values"]
        
        #Uses the downloaded project data to figure out which repository belongs to each project and maps them out
        repo_index, repo_key_index, keys, repo_urls = await getRepoIndex(projects)
        logging.info("Finding all relevant repos...")
        

        logging.info("Starting download of "+str(len(repo_urls))+" elements.")

        #Downloads all root feature directories to map out how many feature files and subfolders exists before indexing them
        dir_features = await download_all(repo_urls)
        repo_feature_index, feature_repos = await getFeatureIndex(dir_features, repo_index)

        logging.info("Getting all feature files...")
        #Goes through all the names and generates the api call urls for every repository before downloading all of them asynchronously for a giant performance gain
        file_urls, repo_feature_index = await getAllFeatureUrls(repo_index, repo_feature_index, feature_repos, repo_key_index, keys)

        logging.info("Starting download of "+str(len(file_urls))+" elements.")
        feature_files = await download_all(file_urls)

        logging.info("Indexing Features...")

        #In order to know which features belong a repo this checks where feature files are expected
        repo_feature_index = await assignFeatures(repo_feature_index, feature_files)


        if os.path.isdir("data"):
                shutil.rmtree("data")
                logging.info("Clearing previous data...")
        cDir("data")

        logging.info("Building output...")
        #uses objectbuilder.py to format the gathered informatin into a single Json structure per repo
        out = await buildOutput(repo_index, repo_key_index, repo_feature_index, keys, save_json=True)

        #print out each project file in a seperate line for use in console interfaces
        #for project in out: print(project)

        return out
    
asyncio.run(main())
