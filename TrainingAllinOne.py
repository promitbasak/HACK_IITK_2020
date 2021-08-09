#!/usr/bin/env python
# coding: utf-8



import os
from os.path import join
from pathlib import PurePath
import sys
import re
import json
import numpy as np
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.svm import SVC



path = input("Enter Path to the data folder:")




with open('resources/priv.pkl', 'rb') as handle:
    priv = pickle.load(handle)
with open('resources/regkeys.pkl', 'rb') as handle:
    regkeys = pickle.load(handle)
with open('resources/docstub.pkl', 'rb') as handle:
    docstub = pickle.load(handle)
with open('resources/bl_str.pkl', 'rb') as handle:
    bl_str = pickle.load(handle)
with open('resources/wl_str.pkl', 'rb') as handle:
    wl_str = pickle.load(handle)
with open('resources/bl_dll.pkl', 'rb') as handle:
    bl_dll = pickle.load(handle)
with open('resources/bl_func.pkl', 'rb') as handle:
    bl_func = pickle.load(handle)
with open('resources/dynamic_dll.pkl', 'rb') as handle:
    dynamic_dll = pickle.load(handle)
with open('resources/pe_dll.pkl', 'rb') as handle:
    pe_dll = pickle.load(handle)



# print(len(priv))
# print(len(regkeys))
# print(len(bl_str))
# print(len(bl_dll))
# print(len(bl_func))
# print(len(dynamic_dll))
# print(len(pe_dll))




classes = ["Benign","Malware"]
malware = ["Backdoor", "Trojan", "TrojanDownloader", "TrojanDropper", "Virus", "Worm"]




def stringextract(path, inpt,output):
    ft = [inpt, output]
    try:
        f = open(path)
        line = f.readline().strip()
        x1 = 0
        for s in docstub:
            if s in line:
                x1 = 1
                break
        ft.append(x1)
        text = f.read()
        tosearch = priv + regkeys + bl_str
        for i in tosearch:
            if i in text:
                ft.append(1)
            else:
                ft.append(0)
        count = 0
        for i in wl_str:
            if i in text:
                count += 1
        ft.append(count)
        ft.append(text.count("http://"))
        ft.append(text.count("https://"))
        f.close()
    except:
        try:
            f = open(path, encoding="cp1252")
            line = f.readline().strip()
            x1 = 0
            for s in docstub:
                if s in line:
                    x1 = 1
                    break
            ft.append(x1)
            text = f.read()
            tosearch = priv + regkeys + bl_str
            for i in tosearch:
                if i in text:
                    ft.append(1)
                else:
                    ft.append(0)
            count = 0
            for i in wl_str:
                if i in text:
                    count += 1
            ft.append(count)
            ft.append(text.count("http://"))
            ft.append(text.count("https://"))
            f.close()
        except:
            print("Passed")
    return ft




def peextract(path, inpt,output):
    ft2 = [inpt, output]
    
    parsing_warning_key = 0
    file_header_key = 0
    optional_header_key = 0
    imported_symbols_key = 0

    parsing_warning = 0

    NumberOfSections = 0
    TimeDateStamp = 0

    SizeOfCode = 0
    SizeOfImage = 0
    code_by_image = 0

    LoadLibraryW = 0
    LoadLibraryA = 0
    dlls = dict(zip(bl_dll,[0 for i in range(len(pe_dll))]))
    nfunc = 0
    
    try:
        f = open(path)
        for line in f:
            line = line.strip()
            if len(line)==0:
                continue

            ############# Reset ##############
            if line.startswith("--------"):
                if parsing_warning_key == 1:
                    parsing_warning_key = 2
                if file_header_key == 1:
                    file_header_key = 2
                if optional_header_key == 1:
                    if SizeOfImage:
                        code_by_image = SizeOfCode/SizeOfImage
                    optional_header_key = 2
                if imported_symbols_key == 1:
                    imported_symbols_key = 2
            ###################################



            #######----------Parsing Warnings----------########
            if parsing_warning_key == 1:
                parsing_warning += 1
            ###################################################



            #######----------FILE_HEADER----------########
            if file_header_key == 1:
                if not TimeDateStamp and "TimeDateStamp" in line:
                    TimeDateStamp = int(re.findall("TimeDateStamp:\s*0x(\S+)",line)[0], 16)
                if not NumberOfSections and "NumberOfSections" in line:
                    NumberOfSections = int(re.findall("NumberOfSections:\s*0x(\S+)",line)[0], 16)
            ###################################################



            #######----------OPTIONAL_HEADER----------#########
            if optional_header_key == 1:
                if not SizeOfCode and "SizeOfCode" in line:
                    SizeOfCode = int(re.findall("SizeOfCode:\s*0x(\S+)",line)[0], 16)
                if not SizeOfImage and "SizeOfImage" in line:
                    SizeOfImage = int(re.findall("SizeOfImage:\s*0x(\S+)",line)[0], 16)
            ###################################################



            #######----------Imported symbols----------########
            if imported_symbols_key==1:
                if not LoadLibraryW:
                    if "LoadLibraryW" in line:
                        LoadLibraryW = 1
                if not LoadLibraryA:
                    if "LoadLibraryA" in  line:
                        LoadLibraryA = 1
                if ".dll" in line:
                    dll = re.findall("^.*.dll",line)[0]
                    function = re.findall(".dll.(\S+)",line)[0]
                    if dll in dlls:
                        dlls[dll] = 1
                    elif dll.lower() in dlls:
                        dlls[dll.lower()] = 1
                    if dll in bl_func and function in bl_func[dll]:
                        nfunc += 1
                    elif dll.lower() in bl_func and function in bl_func[dll.lower()]:
                        nfunc += 1
            ###################################################



            ##################### START #####################
            if line=="----------Parsing Warnings----------":
                if not parsing_warning_key:
                    parsing_warning_key = 1
            if line=="----------FILE_HEADER----------":
                if not file_header_key:
                    file_header_key = 1
            if line=="----------OPTIONAL_HEADER----------":
                if not optional_header_key:
                    optional_header_key = 1
            if line=="----------Imported symbols----------":
                if not imported_symbols_key:
                    imported_symbols_key = 1
            #####################################################
        f.close()
    except:
        try:
            f = open(path, encoding="cp1252")
            for line in f:
                line = line.strip()
                if len(line)==0:
                    continue

                ############# Reset ##############
                if line.startswith("--------"):
                    if parsing_warning_key == 1:
                        parsing_warning_key = 2
                    if file_header_key == 1:
                        file_header_key = 2
                    if optional_header_key == 1:
                        if SizeOfImage:
                            code_by_image = SizeOfCode/SizeOfImage
                        optional_header_key = 2
                    if imported_symbols_key == 1:
                        imported_symbols_key = 2
                ###################################



                #######----------Parsing Warnings----------########
                if parsing_warning_key == 1:
                    parsing_warning += 1
                ###################################################



                #######----------FILE_HEADER----------########
                if file_header_key == 1:
                    if not TimeDateStamp and "TimeDateStamp" in line:
                        TimeDateStamp = int(re.findall("TimeDateStamp:\s*0x(\S+)",line)[0], 16)
                    if not NumberOfSections and "NumberOfSections" in line:
                        NumberOfSections = int(re.findall("NumberOfSections:\s*0x(\S+)",line)[0], 16)
                ###################################################



                #######----------OPTIONAL_HEADER----------#########
                if optional_header_key == 1:
                    if not SizeOfCode and "SizeOfCode" in line:
                        SizeOfCode = int(re.findall("SizeOfCode:\s*0x(\S+)",line)[0], 16)
                    if not SizeOfImage and "SizeOfImage" in line:
                        SizeOfImage = int(re.findall("SizeOfImage:\s*0x(\S+)",line)[0], 16)
                ###################################################



                #######----------Imported symbols----------########
                if imported_symbols_key==1:
                    if not LoadLibraryW:
                        if "LoadLibraryW" in line:
                            LoadLibraryW = 1
                    if not LoadLibraryA:
                        if "LoadLibraryA" in  line:
                            LoadLibraryA = 1
                    if ".dll" in line:
                        dll = re.findall("^.*.dll",line)[0]
                        function = re.findall(".dll.(\S+)",line)[0]
                        if dll in dlls:
                            dlls[dll] = 1
                        elif dll.lower() in dlls:
                            dlls[dll.lower()] = 1
                        if dll in bl_func and function in bl_func[dll]:
                            nfunc += 1
                        elif dll.lower() in bl_func and function in bl_func[dll.lower()]:
                            nfunc += 1
                ###################################################



                ##################### START #####################
                if line=="----------Parsing Warnings----------":
                    if not parsing_warning_key:
                        parsing_warning_key = 1
                if line=="----------FILE_HEADER----------":
                    if not file_header_key:
                        file_header_key = 1
                if line=="----------OPTIONAL_HEADER----------":
                    if not optional_header_key:
                        optional_header_key = 1
                if line=="----------Imported symbols----------":
                    if not imported_symbols_key:
                        imported_symbols_key = 1
                #####################################################
            f.close()
        except:
            print("Passed")
    dll_ft = [dlls[i] for i in sorted(dlls.keys())]
    ft2.extend([parsing_warning, NumberOfSections, TimeDateStamp, SizeOfCode, SizeOfImage, code_by_image , LoadLibraryW, LoadLibraryA, nfunc])
    ft2.extend(dll_ft)
    return ft2




def dynamicextract(path, inpt, output):
    ft3 = [inpt, output]
    
    
    duration = 0
    score = 0
    signatures_count = 0
    severity = 0

    tls_count = 0
    udp_count = 0
    dns_servers_count = 0
    http_count = 0
    icmp_count = 0
    tcp_count = 0
    hosts_count = 0
    dns_count = 0
    domains_count = 0
    dead_hosts_count = 0

    file_recreated_count = 0
    regkey_written_count = 0
    file_created_count = 0
    directory_created_count = 0
    dll_loaded_count = 0
    file_opened_count = 0
    regkey_opened_count = 0
    file_written_count = 0
    file_deleted_count = 0
    file_read_count = 0
    regkey_read_count = 0
    directory_enumerated_count = 0

    dlls = dict(zip(bl_dll,[0 for i in range(len(dynamic_dll))]))
    
    
    try:
        f = open(path)
        ############### Extraction ####################
        js = json.load(f)
        ###############################################


        ############## Info ###################
        try:
            duration = js["info"]["duration"]
        except:
            pass

        try:
            score = js["info"]["score"]
        except:
            pass

        try:
            signatures_count = len(js["signatures"])
        except:
            pass

        try:
            sev = 0
            for i in js["signatures"]:
                sev += i["severity"]
            severity = signatures_count*10 - sev
        except:
            pass
        ################################################################


        ##################### Network ##################
        try:
            tls_count = len(js["network"]["tls"])
        except:
            pass

        try:
            udp_count = len(js["network"]["udp"])
        except:
            pass

        try:
            dns_servers_count = len(js["network"]["dns_servers"])
        except:
            pass

        try:
            http_count = len(js["network"]["http"])
        except:
            pass

        try:
            icmp_count = len(js["network"]["icmp"])
        except:
            pass


        try:
            tcp_count = len(js["network"]["tcp"])
        except:
            pass


        try:
            hosts_count = len(js["network"]["hosts"])
        except:
            pass

        try:
            dns_count = len(js["network"]["dns"])
        except:
            pass


        try:
            domains_count = len(js["network"]["domains"])
        except:
            pass

        try:
            dead_hosts_count = len(js["network"]["dead_hosts"])
        except:
            pass
        ################################################################



        ######################## Summary #########################
        try:
            file_recreated_count = len(js["behavior"]["summary"]["file_recreated"])
        except:
            pass

        try:
            regkey_written_count = len(js["behavior"]["summary"]["regkey_written"])
        except:
            pass

        try:
            file_created_count = len(js["behavior"]["summary"]["file_created"])
        except:
            pass

        try:
            directory_created_count = len(js["behavior"]["summary"]["directory_created"])
        except:
            pass

        try:
            dll_loaded_count = len(js["behavior"]["summary"]["dll_loaded"])
        except:
            pass

        try:
            file_opened_count = len(js["behavior"]["summary"]["file_opened"])
        except:
            pass

        try:
            regkey_opened_count = len(js["behavior"]["summary"]["regkey_opened"])
        except:
            pass

        try:
            file_written_count = len(js["behavior"]["summary"]["file_written"])
        except:
            pass

        try:
            file_deleted_count = len(js["behavior"]["summary"]["file_deleted"])
        except:
            pass

        try:
            file_read_count = len(js["behavior"]["summary"]["file_read"])
        except:
            pass

        try:
            regkey_read_count = len(js["behavior"]["summary"]["regkey_read"])
        except:
            pass

        try:
            directory_enumerated_count = len(js["behavior"]["summary"]["directory_enumerated"])
        except:
            pass
        ################################################################


        ################################ DLL ############################
        try:
            lst = js["behavior"]["summary"]["dll_loaded"]
            dlllist = [i.split("\\")[-1] for i in lst]
            for dll in dlllist:
                if dll in dlls:
                    dlls[dll] = 1
        except:
            pass
        ################################################################
        f.close()
    except:
        try:
            f = open(path, encoding="cp1252")
            ############### Extraction ####################
            js = json.load(f)
            ###############################################


            ############## Info ###################
            try:
                duration = js["info"]["duration"]
            except:
                pass

            try:
                score = js["info"]["score"]
            except:
                pass

            try:
                signatures_count = len(js["signatures"])
            except:
                pass

            try:
                sev = 0
                for i in js["signatures"]:
                    sev += i["severity"]
                severity = signatures_count*10 - sev
            except:
                pass
            ################################################################


            ##################### Network ##################
            try:
                tls_count = len(js["network"]["tls"])
            except:
                pass

            try:
                udp_count = len(js["network"]["udp"])
            except:
                pass

            try:
                dns_servers_count = len(js["network"]["dns_servers"])
            except:
                pass

            try:
                http_count = len(js["network"]["http"])
            except:
                pass

            try:
                icmp_count = len(js["network"]["icmp"])
            except:
                pass


            try:
                tcp_count = len(js["network"]["tcp"])
            except:
                pass

            try:
                hosts_count = len(js["network"]["hosts"])
            except:
                pass

            try:
                dns_count = len(js["network"]["dns"])
            except:
                pass

            try:
                domains_count = len(js["network"]["domains"])
            except:
                pass

            try:
                dead_hosts_count = len(js["network"]["dead_hosts"])
            except:
                pass

            ################################################################



            ######################## Summary #########################
            try:
                file_recreated_count = len(js["behavior"]["summary"]["file_recreated"])
            except:
                pass

            try:
                regkey_written_count = len(js["behavior"]["summary"]["regkey_written"])
            except:
                pass

            try:
                file_created_count = len(js["behavior"]["summary"]["file_created"])
            except:
                pass

            try:
                directory_created_count = len(js["behavior"]["summary"]["directory_created"])
            except:
                pass

            try:
                dll_loaded_count = len(js["behavior"]["summary"]["dll_loaded"])
            except:
                pass

            try:
                file_opened_count = len(js["behavior"]["summary"]["file_opened"])
            except:
                pass

            try:
                regkey_opened_count = len(js["behavior"]["summary"]["regkey_opened"])
            except:
                pass

            try:
                file_written_count = len(js["behavior"]["summary"]["file_written"])
            except:
                pass

            try:
                file_deleted_count = len(js["behavior"]["summary"]["file_deleted"])
            except:
                pass

            try:
                file_read_count = len(js["behavior"]["summary"]["file_read"])
            except:
                pass

            try:
                regkey_read_count = len(js["behavior"]["summary"]["regkey_read"])
            except:
                pass

            try:
                directory_enumerated_count = len(js["behavior"]["summary"]["directory_enumerated"])
            except:
                pass
            ################################################################


            ################################ DLL ############################
            try:
                lst = js["behavior"]["summary"]["dll_loaded"]
                dlllist = [i.split("\\")[-1] for i in lst]
                for dll in dlllist:
                    if dll in dlls:
                        dlls[dll] = 1
            except:
                pass
            ################################################################
            f.close()
        except:
            print("Passed")
    
    dll_ft = [dlls[i] for i in sorted(dlls.keys())]
    ft3.extend([duration, score, signatures_count, severity])
    ft3.extend([tls_count, udp_count, dns_servers_count, http_count, icmp_count, tcp_count ,hosts_count , dns_count,\
                domains_count , dead_hosts_count ])
    ft3.extend([file_recreated_count , regkey_written_count , file_created_count , directory_created_count,\ dll_loaded_count,\
                file_opened_count , regkey_opened_count , file_written_count , file_deleted_count , file_read_count , \
                regkey_read_count, directory_enumerated_count])
    ft3.extend(dll_ft)
    return ft3




total_files = 0
benigns = []
malwares = []
samples = []
features = []
features2 = []
features3 = []
i = 0
count = 0
for root, dirs, files in os.walk(path):
    i += 1
    if not len(files):
        continue
    total_files += len(files)
    rootpath = PurePath(root)
    directories = rootpath.parts
    for file in files:
        ft = []
        ft2 = []
        ft3 = []
        if file=="String.txt":
            if directories[-2]=="Benign":
                benigns.append(directories[-1])
            else:
                malwares.append(directories[-1])
            ft = stringextract(join(root,file),directories[-1],directories[-2])
        elif file=="Structure_Info.txt":
            if directories[-2]=="Benign":
                benigns.append(directories[-1])
            else:
                malwares.append(directories[-1])
            ft2 = peextract(join(root,file),directories[-1],directories[-2])
        elif file.endswith(".json"):
            count += 1
            fname = file[:-5]
            if directories[-1]=="Benign":
                benigns.append(fname)
            else:
                malwares.append(fname)
            ft3 = dynamicextract(join(root,file),fname,directories[-1])
        if ft:
            features.append(ft)
        if ft2:
            features2.append(ft2)
        if ft3:
            features3.append(ft3)
print(total_files)
print(len(benigns))
print(len(malwares))






string_cols = ["name", "output", "docstub"]
string_cols.extend([f"priv{i}" for i in range(len(priv))])
string_cols.extend([f"regkeys{i}" for i in range(len(regkeys))])
string_cols.extend([f"bl_str{i}" for i in range(len(bl_str))])
string_cols.extend(["wl_str","http","https"])




pe_cols = ["name", "output","parsing_warning", "NumberOfSections", "TimeDateStamp", "SizeOfCode", \
           "SizeOfImage", "code_by_image" , "LoadLibraryW", "LoadLibraryA", "nfunc"]
pe_cols.extend([f"dll{i}" for i in range(len(pe_dll))])




dynamic_cols = ["name", "output", "duration", "score", "signatures_count", "severity"]
dynamic_cols.extend(["tls_count", "udp_count", "dns_servers_count", "http_count", "icmp_count","tcp_count" , \
                     "hosts_count" , "dns_count" , "domains_count" ,"dead_hosts_count"])
dynamic_cols.extend(["file_recreated_count" , "regkey_written_count" , "file_created_count" , "directory_created_count" ,\
                     "dll_loaded_count" ,"file_opened_count" , "regkey_opened_count" ,"file_written_count" , \
                     "file_deleted_count" , "file_read_count" ,"regkey_read_count","directory_enumerated_count"])
dynamic_cols.extend([f"d_dll{i}" for i in range(len(dynamic_dll))])



# str_df
str_df = pd.DataFrame(features, columns=string_cols)


# pe_df
pe_df = pd.DataFrame(features2, columns=pe_cols)


# dynamic_df
dynamic_df = pd.DataFrame(features3, columns=dynamic_cols)


# staticdf
pe_df.drop(columns=["output"], inplace=True)
dynamic_df.drop(columns=["output"], inplace=True)
staticdf = pd.merge(str_df,pe_df, on="name", how="outer")
staticdf = pd.merge(staticdf,dynamic_df, on="name", how="outer")
staticdf["output"] = staticdf["output"] != "Benign"
staticdf["output"] = staticdf["output"].astype(np.int8)

staticdf = staticdf.dropna().reset_index(drop=True)


# # Model Train

names = staticdf["name"]
y = staticdf["output"]
X = staticdf.drop(columns = ["name", "output"])



scaler = MinMaxScaler(feature_range=(-1,1))
X = scaler.fit_transform(X)
model = SVC(C=10)
scores = cross_val_score(model, X, y, cv=10, scoring='f1_macro')
print(scores)
print(sum(scores) / 10)




scaler = MinMaxScaler(feature_range=(-1,1))
X = scaler.fit_transform(X)

X_train , X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25, random_state = 100, stratify=y)
print('Splitting done')
model = SVC(C=10)
model.fit(X_train, y_train)
print('Training done')
y_pred = model.predict(X_test)
print('Prediction generated, creating classification report and confusion matrix........\n')

print(accuracy_score(y_test,y_pred), '\n')
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))


