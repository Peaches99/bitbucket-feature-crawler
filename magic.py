import asyncio
import base64
import json
import os
from logging import log
import shutil

import aiohttp
from aiohttp.client import ClientSession
from dotenv import load_dotenv
from numpy import empty, save

import objectBuilder as ob

if os.path.exists(".env") is False:
        print("\n\n\nMissing .env file!!!\n\n\n")
        
load_dotenv()
token = os.getenv("BITBUCKET_CREDENTIAL_TOKEN")
headers = {"Content-Type": "application/json", "Authorization": token}
bitbucket_projects = os.getenv("BITBUCKET_PROJECT_URL")

projectUrl = bitbucket_projects.rstrip(bitbucket_projects[-1])+ "?limit=2000"

request_limit = int(os.getenv("TCP_REQUEST_LIMIT"))


def encodeB64(toEncode):
    encoded = base64.b64encode(bytes(toEncode, "utf-8"))
    return encoded
            

async def download_link(url:str,session:ClientSession):
    headers = {"Content-Type": "application/json", "Authorization": token}
    async with session.get(url, headers=headers) as response:
        result = await response.text()
    if result is not empty:
        return(result)


async def download_all(urls:list, tcp_limit):
    my_conn = aiohttp.TCPConnector(limit=tcp_limit)
    async with aiohttp.ClientSession(connector=my_conn) as session:
        tasks = []
        for url in urls:
            task = asyncio.ensure_future(download_link(url=url,session=session))
            tasks.append(task)
        out = await asyncio.gather(*tasks,return_exceptions=True)
        return(out)


def saveJson(name, inFile):
    if os.path.exists(name+".json"):
        os.remove(name+".json")

    data = json.dumps(inFile, indent=4)
    
    file = open(name+".json", "x")
    file.write(data)
    file.close


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
    return(None)

def getAllVariables(project):
    print(project.getProjectID())
    for feature in project.getFeatures():
        print(feature.getFeatureName())
        print(feature.getDescription())
        for scenario in feature.getScenarios():
            print(scenario.getScenarioName())
            print(scenario.getGiven())
            print(scenario.getWhen())
            print(scenario.getThen())



async def main():

        tcp_limit = request_limit

    
        repo_urls = []
        repo_key_index = []
        repo_index = []
        keys = []
        key_urls = []
        feature_repos = {}

        projectsRaw = await download_all([projectUrl], tcp_limit)
        projects = json.loads(json.loads(json.dumps(projectsRaw[0], indent=4)))["values"]


        #Index all Project keys
        for p in projects:
            key = p["key"]
            key_urls.append(bitbucket_projects+key+"/repos?limit=1000")
            keys.append(p["key"])

        project_repos = await download_all(key_urls, tcp_limit)
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
        
        dir_features = await download_all(repo_urls, tcp_limit)

        repo_feature_index = []

        #Index all feature files from their parent"s Json information
        for idx, dir in enumerate(dir_features):
            dir = json.loads(json.loads(json.dumps(dir, indent=4)))
            try:
                if dir["children"]["size"] > 0:
                    feature_repos.update({repo_index[idx]: dir["children"]})
                    repo_feature_index.append(str(dir["children"]["size"]))
            except:
                repo_feature_index.append("0")

        file_urls = []

        #Generate the urls before downloading all of them at the same time for efficiency
        for repo in repo_index:
            file_count = 0
            try:
                feature_index = feature_repos[repo]
                file_count = feature_index["size"]
            except:
                pass
            
            for i in range(file_count):
                file_urls.append(bitbucket_projects+keys[matchKey(repo, repo_key_index)[0]]+"/repos/"+repo+"/browse/src/test/resources/features/"+feature_index["values"][i]["path"]["name"])
        
        feature_files = await download_all(file_urls, tcp_limit)
        

        #Load all feature files found into their respective repository index
        for idx, elem in enumerate(repo_feature_index):
            if elem != "0":
                features = []
                for i in range(int(elem)):
                    features.append(feature_files[i])
                for i in range(int(elem)):
                    feature_files.pop(0)

                repo_feature_index[idx] = features


        out = []
        # Go through all repos, check if they have at least one feature file and build a project from the files
        for idx, repo in enumerate(repo_feature_index):
            if repo != "0":
                all_lines = []
                for elem in repo:
                    elem = json.loads(json.loads(json.dumps(elem, indent=4)))
                    lines = []
                    for line in elem["lines"]:
                        lines.append(line["text"])
                    
                    all_lines.append(lines)

                

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

                if os.path.isdir("data"):
                    shutil.rmtree("data")

                cDir("data")
                
                jsonName = repo_index[idx]
                print(outJson)

                saveJson("data/"+jsonName, outJson)

                out.append(outJson)

        return out
    
asyncio.run(main())
