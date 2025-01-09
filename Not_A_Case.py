###################################################################################################
#
# Purpose: Reviews every EDHR record in the IBM cloud production database
# and only retrieve case id and case log data for non-surgical cases.
# Criterion for a record to be considered a true surgical case is seeing foot pedeal action.
# I want to know which cases NO NOT contain "FIRST_FP_ACTIVE" (this is what begins a surgery).
# Output is converted into a flat .csv file for export into Excel.
# It will be reviewed and used to determine how much junk is in the database.
# I will review each case log to determine if it was a demo/test, manufacturing error, or false start/user error.
#
# Version: 1.0
#
###################################################################################################
#
import os
import json
import requests
import time
from cloudant import cloudant
from datetime import datetime
from time import sleep

global g_In_Process_List
g_In_Process_List = [];

global g_iSkip
g_iSkip = 0;

global g_cserviceURL
g_cserviceURL = "";

def Get_Credential(strCredential):

    strNew1 = strCredential.replace('=', "");
    strNew1 = strNew1.replace("'", "");
    strNew1 = strNew1.replace(";", "");
    strNew1 = strNew1.replace(" ", "");
    strNew1 = strNew1.replace("\n", "");
    strNew1 = strNew1.replace("\r", "");
    strNew1 = strNew1.replace("\t", "");
    strNew1 = strNew1.strip();

    return strNew1;

def Read_Credentials(filename):

    global g_cserviceURL
    
    if os.path.exists(filename) == False:
        print('Error!   Can Not Find Process List File: ' + filename);
        return;

    fh = open(filename, "r");

    while True:
        strData = fh.readline();

        if (strData.find('#', 0, 1) == -1):
            if (len(strData) > 11):
                if (strData.find("cserviceURL", 0, 11) != -1):
                    strTempArray = strData.split("=");
                    g_cserviceURL = Get_Credential(strTempArray[1]);

        if (strData == ""):
            break;

    fh.close;

    print(g_cserviceURL);

    if (g_cserviceURL == ""):
        print("Error: Reading in Credentials!");
        
    return;


def _api_get(url):
    requisite_headers = { 'Accept' : 'application/json',
                          'Content-Type' : 'application/json'}
    
    response =  requests.get(url, headers=requisite_headers);
    
    return response.status_code, response.text;


def Open_File_For_Output(filename):

    i = 0;
    
    print('Preparing Filename: ' + filename);
    try:
        os.remove(filename);
    except:
        i = 0;

#   fh = open(filename, "a+", encoding="utf-8");
    fh = open(filename, "a+");

    return fh;


def CheckJSONField(json_dict, strFieldName):

    str_data = "OK";

    try:
        str_data = str(json_dict['doc'][strFieldName]);
    except:
        str_data = 'Error';

    return str_data;



def GetRecords():

    global g_iSkip
    global g_cserviceURL

    strCloudantDB = '/stellaris_logs/_all_docs?include_docs=true&limit=200&skip=' + str(g_iSkip) + ';';

    resp = _api_get(g_cserviceURL + strCloudantDB);
    if resp[0] != 200:
        print("Could not retrieve requested records for the following request: " + strCloudantDB);
        fh_excel.close;
        quit();

    g_iSkip = g_iSkip + 200;

    return resp;
  
#
#
#
# Main - Starts here!
#

strDocType = 'case';

print("Program - Started\n");


strFileName = 'c:\\stellaris\\python\\Foot_Pedal\\No_Foot_Pedal_Data.txt';
fh_excel = Open_File_For_Output(strFileName);


strCredentialsFileName = 'c:\\stellaris\\python\\cleanup\\ProdDatabaseCredentials.txt'; #file key to the database, double check to ensure you're querying the intended enviornment (e.g. Dev, Test, or Prod)
Read_Credentials(strCredentialsFileName);
print("");
print(g_cserviceURL);
print("");
if (g_cserviceURL == ""):
    print("Error: Unable to open the Process List File: " + strCredentialsFileName);
    fh_excel.close;
    exit();


print("Program - Begin processing!\n");


iRecordCount = 0;

resp = GetRecords();

design_doc = json.loads(resp[1]);

strTemp = design_doc.get('total_rows');
iTotalRows = int(strTemp);



print("Processing Total Rows: " + str(iTotalRows));

while (iRecordCount < iTotalRows):
    
    for json_dict in design_doc['rows']:

        iRecordCount = iRecordCount + 1;

        str_doc_type = CheckJSONField(json_dict, "doc_type");
        str_doc_type = str_doc_type.strip();

        if (str_doc_type == strDocType):      

            strCase = CheckJSONField(json_dict, "case_log");

            if (",FIRST_FP_ACTIVE," not in strCase):
                strID = CheckJSONField(json_dict, "_id");

                strOutput = "_id: " + str(strID) + "  Case Log: " + str(strCase) + "\n";
                print(strOutput);
                fh_excel.write (strOutput);

        print("Processing Record: " + str(iRecordCount) + ' of ' + str(iTotalRows));

    resp = GetRecords();
    design_doc = json.loads(resp[1]);
    


print("Program - Ended\n");

fh_excel.flush();
fh_excel.close;

quit();