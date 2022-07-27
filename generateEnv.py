import asyncio
import base64
import json
import os
from logging import log
import shutil
import ansi
import getpass

import aiohttp
from aiohttp.client import ClientSession
from dotenv import load_dotenv
from numpy import empty, save

import objectBuilder as ob

os.system('color')

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def encodeB64(toEncode):
    encoded = str(base64.b64encode(bytes(toEncode, "utf-8")))
    return encoded

def formatKey(usernamae, password):
    before = usernamae+":"+password
    after = "BITBUCKET_CREDENTIAL_TOKEN='Basic "+(encodeB64(before)[2:-1])+"'"
    return after

def formatUrl(bitbucket_url):
    out = "BITBUCKET_PROJECT_URL='"+bitbucket_url+"'"
    return out


def formatTcp(tcp_limit):
    out = str("TCP_REQUEST_LIMIT="+tcp_limit)
    return out

def writeFile(inString):
    file = open(".env", "x")
    file.write(inString)
    file.close

def setup():
    print(f"{bcolors.HEADER}Beggining Setup . . .{bcolors.ENDC}\n")

    if os.path.exists(".env"):
        print(f"{bcolors.WARNING}Found existing Env file!\nDo you want to replace it? \n  {bcolors.ENDC}",f"{bcolors.OKBLUE}       (y/n){bcolors.ENDC}\n")
        usrIn = input()

        if usrIn == "Y" or usrIn == "y":
            os.remove(".env")
            print(f"{bcolors.OKGREEN}Restarting...{bcolors.ENDC}")
            setup()
        else:
            print(f"\n{bcolors.WARNING}Cancelling Setup . . .{bcolors.ENDC}")
    else:
        print(f"\n{bcolors.OKBLUE}Enter your bitbucket Username:{bcolors.ENDC}")

        usrIn = input()
        


        pwdIn = getpass.getpass(f"{bcolors.OKBLUE}Enter your bitbucket Password:{bcolors.ENDC}\n")
        
 

        
        print(f"{bcolors.OKBLUE}Enter your Bitbucket server API project path:{bcolors.ENDC}    "+"Example: http://some.company.com/rest/api/1.0/projects/")
       


        url = input()
        

        print(f"\n{bcolors.WARNING}Enter the tcp request limit:{bcolors.ENDC}    "+"Keep below 100 to avoid nuking your server (Recommended 50)")
        


    
        tcpString = formatTcp(input())
        

        authString = formatKey(usrIn, pwdIn)
        urlString = formatUrl(url)

        out = authString+"\n"+urlString+"\n"+tcpString
        writeFile(out)

        if os.path.exists(".env"):
            print(f"{bcolors.OKGREEN}Setup complete...{bcolors.ENDC}\n\n")
        else:
            print(f"{bcolors.FAIL}Something failed! Cannot find generated Env!.{bcolors.ENDC}\n\n")


            
setup()
