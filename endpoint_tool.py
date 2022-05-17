import os
import csv
import json
import time
import requests
import pandas as pd
from tqdm import tqdm
import PySimpleGUI as sg
from csv import DictReader
from datetime import datetime

'''
Farmers Insurance ThousandEyes Endpoint Agent Management Tool
Written by ThousandEyes Techical Account Management 2022
For help or feature requests, please contact collsull@cisco.com
'''

def get_epas():
    print("[*] Populating Endpoint Agents...")
    epa = []
    epas = requests.get(api_endpoint, auth=(username, api_key))
    epas = json.loads(epas.text)

    #COLLECT EPAS###################################################################
    epa.append(epas["endpointAgents"])
    while "next" in epas["pages"]:
        api_endpoint = epas["pages"]["next"]
        epas = requests.get(api_endpoint, auth=(username, api_key))
        epas = json.loads(epas.text)
        epa.append(epas["endpointAgents"])
    final_list_epas = []
    if len(epa) >= 1:
        for lst in epa:
            for agent in lst:
                final_list_epas.append(agent)
    #COLLECT EPAS###################################################################

    #ITERATE THROUGH JSON###########################################################
    count = 0
    new_agents_ids = []
    new_agents_names = []
    for x in tqdm(final_list_epas):
        agentId = x['agentId']
        agentName = x['agentName']
        computerName = x['computerName']
        createdTime = x['createdTime']
        status = x['status']

        if "2022-02-10" in createdTime:
            new_agents_ids.append(agentId)
            headers = {"content-type": "application/json"}
            payload = {
                    "status": "disabled"
            }

            result = requests.put(
                f"https://api.thousandeyes.com/v6/endpoint-agents/{agentId}/disable.json",
                json=payload,
                headers=headers,
                auth=(username, api_key),
            )
            print(f"\u001b[32m[*] {agentName} DISABLED: {agentId} !\u001b[0m")
            time.sleep(.5)
            count+=1
    #ITERATE THROUGH JSON###########################################################

    #PRINT TOTAL COUNT##############################################################
    print(f"\u001b[33m[*] Total agents discovered:\u001b[0m {count}")
    new_agent_count = 0
    for a in new_agents_ids:
        new_agent_count += 1
    print(f"\u001b[33m[*] Total new agents discovered and disabled\u001b[0m: {new_agent_count}")
    #PRINT TOTAL COUNT##############################################################


def rename_all_epas():
    '''
    Renames all endpoint agents using following naming convention: USER_NAME_PC_NAME
    '''
    api_endpoint = "https://api.thousandeyes.com/v6/endpoint-agents.json"

    print("[*] Populating Endpoint Agents...")
    epa = []
    epas = requests.get(api_endpoint, auth=(username, api_key))
    epas = json.loads(epas.text)
    epa.append(epas["endpointAgents"])
    while "next" in epas["pages"]:
        api_endpoint = epas["pages"]["next"]
        epas = requests.get(api_endpoint, auth=(username, api_key))
        epas = json.loads(epas.text)
        epa.append(epas["endpointAgents"])
    final_list_epas = []
    if len(epa) >= 1:
        for lst in epa:
            for agent in lst:
                final_list_epas.append(agent)
    count = 0
    new_agents_ids = []
    new_agents_names = []
    for x in tqdm(final_list_epas):
        agentId = x['agentId']
        agentName = x['agentName']
        computerName = x['computerName']
        createdTime = x['createdTime']
        status = x['status']
        if status == "enabled" or status == "disabled":
            if "2022" in createdTime:
                new_agents_ids.append(agentId)
            try:
                real_name = x['clients'][0]['userProfile']['userName']
                if "christian.robinson" in real_name or "orlando.s.rodriguez" in real_name:
                    try:
                        real_name = x['clients'][1]['userProfile']['userName']
                    except:
                        pass
            except:
                pass
            final_name = real_name.replace("GITDIR\\", "")
            print(final_name)

            headers = {"content-type": "application/json"}
            payload = {
                    "newAgentName":f"{final_name}"+"_"+ f"{computerName}"
            }
            result = requests.put(
                f"https://api.thousandeyes.com/v6/endpoint-agents/{agentId}.json",
                json=payload,
                headers=headers,
                auth=(username, api_key),
            )
            print(f"\u001b[32m[*] Updated agent: {agentId} from {agentName} to {final_name}\u001b[0m")
            time.sleep(.3)
            count+=1
    print(f"\u001b[33m[*] Total agents discovered:\u001b[0m {count}")
    new_agent_count = 0
    for a in new_agents_ids:
        new_agent_count += 1
    print(f"\u001b[33m[*] Total new agents discovered\u001b[0m: {new_agent_count}")


def save_agents_to_file():
    timestamp = int(time.time())
    api_endpoint = "https://api.thousandeyes.com/v6/endpoint-agents.json"
    print("\u001b[33m[*] Populating Endpoint Agents...\u001b[0m")
    epa = []
    epas = requests.get(api_endpoint, auth=(username, api_key))
    epas = json.loads(epas.text)
    epa.append(epas["endpointAgents"])
    while "next" in epas["pages"]:
        api_endpoint = epas["pages"]["next"]
        epas = requests.get(api_endpoint, auth=(username, api_key))
        epas = json.loads(epas.text)
        epa.append(epas["endpointAgents"])
    final_list_epas = []
    if len(epa) >= 1:
        for lst in epa:
            for agent in lst:
                final_list_epas.append(agent)
    count = 0
    row = 0
    new_agents_ids = []
    new_agents_names = []
    with open(f'epa_farmers_{timestamp}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Row" ,"Name","Status", "Agent ID", "Manufacturer", "Model"])
        for x in tqdm(final_list_epas):
            agentId = x['agentId']
            agentName = x['agentName']
            computerName = x['computerName']
            createdTime = x['createdTime']
            status = x['status']
            manufacturer = x['manufacturer']
            model = x['model']
            try:
                real_name = x['clients'][0]['userProfile']['userName']
            except:
                pass
            print(agentName + " " + real_name)
            if status == "enabled":
                writer.writerow([row + 1,f"{real_name}" + "_" + f"{computerName}",f"{status}", f"{agentId}", f"{manufacturer}", f"{model}"])
            elif status == "disabled":
                writer.writerow([row + 1,f"{real_name}" + "_" + f"{computerName}",f"{status}", f"{agentId}", f"{manufacturer}", f"{model}"])
            row += 1
    print("\u001b[31m[*] CSV population complete...\u001b[0m")
    print(f"\u001b[33m[*] Filename:\u001b[0m {file}")
    file_list.append(os.path.basename(file.name))


def update_from_file():
    input_menu_user = input("Please enter CSV filename: ")
    with open(input_menu_user, 'r') as read_obj:
        csv_dict_reader = DictReader(read_obj)
        for row in csv_dict_reader:
            name = row['Name']
            state = row['Status']
            agentId = row['Agent ID']
            print(row['Name'] + " " + row['Status'] + " " + row["Agent ID"])
            if row['Status'] == "enabled" or row["Status"] == "Enabled":
                print(f"[*] Enabling {name}...")

                headers = {"content-type": "application/json"}
                payload = {
                        "status":"enabled"
                }
                result = requests.put(
                    f"https://api.thousandeyes.com/v6/endpoint-agents/{agentId}.json",
                    json=payload,
                    headers=headers,
                    auth=(username, api_key),
                )
                time.sleep(.2)
            if row["Status"] == "disabled" or row["Status"] == "Disabled":
                print(f"[!] Disabling {name}...")
                headers = {"content-type": "application/json"}
                payload = {
                        "status":"disabled"
                }
                result = requests.put(
                    f"https://api.thousandeyes.com/v6/endpoint-agents/{agentId}.json",
                    json=payload,
                    headers=headers,
                    auth=(username, api_key),
                )
                time.sleep(.2)



if __name__ == "__main__":

    username = ""
    api_key = ""

    file_list = []
    sg.theme('dark grey 9')
    font = ("Arial, 15")
    col1=[[sg.Listbox(values=['Renames all endpoint agents to standard naming convention','Save all endpoint agents to CSV file for viewing', 'Update agent state from CSV file', 'Add disabled agents to disabled label'], select_mode='extended', key='fac', size=(70, 20), font=font)]]
    col2=[[sg.Image('eye2.png', size=(400,400))]]
    col4=[[sg.Text('TAM Endpoint Automation Tool', font=font)]]
    layout = [[sg.Column(col1, element_justification='c'), sg.Column(col2, element_justification='c')]]
    window = sg.Window('TAM Endpoint Automation Tool', layout+[[sg.OK("Enter")]])
    event, values = window.read()
    if values['fac'] == 1 or values['fac'] == ['Renames all endpoint agents to standard naming convention']:
        get_epas()
    elif values['fac'] == 2 or values['fac'] == ['Save all endpoint agents to CSV file for viewing']:
        rename_all_epas()
    elif values['fac'] == 3 or values['fac'] == ['Update agent state from CSV file']:
        save_agents_to_file()
        window.close()
        column_1=[[sg.Text(f'File generated: {file_list[0]}', key='-text-', font=font)]]
        column_2=[[sg.Image('eye2.png', size=(400,400))]]
        layout2 = [[sg.Column(column_1, element_justification='c'), sg.Column(column_2, element_justification='c')]]
        window2 = sg.Window('TAM Endpoint Automation Tool', layout2+[[sg.OK("Close")]])
        event, values = window2.read()
    elif values['fac'] == 4 or values['fac'] == ['Add disabled agents to disabled label']:
        update_from_file()
    else:
        print("Not a valid option...")
    window.close()
    #get_epas()
