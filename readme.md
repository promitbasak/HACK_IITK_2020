# Malware Detection with Machine Learning

## Summary
We used machine learning to detect different types of windows malwares. The dataset used to train the model 
has static and dynamic analysis of different progrmas. According to the data each program was labeled as `benign` or `malware`.
There are 6 types of malwares in total:
- Backdoor
- Trojan
- Trojan Downloader
- TrojanDropper
- Virus
- Worm
  
This project is made as a solution to the competition [HCL HACK IITK 2020](https://hackathon.iitk.ac.in/).
This goal of this hackathon is to apply the machine learning alogorithms to cyber security technologies.    
  
The data for this competition can be found at [Google Drive](https://drive.google.com/drive/folders/1-17jfRbJlrmtA4GuORd8dusOyMiYvaOg?usp=sharing)  

## Team Info
Team Name: **DU_Apophis**  
Members:
- Shahamat Tasin
- A.H.M. Nazmus Sakib 
- Promit Basak
  
## Codes
There are two .py files: `TrainingAllinOne.py` and `MalwareDetection.py`.  

`MalwareDetection.py` uses the pretrained model to predict and exports the result in a csv file in its path.  
`TrainingAllinOne.py` includes all the codes from feature extraction from Static and Dynamic analysis, feature selection and model training. The model is already trained,
 and there is no need to run this file unless you want to chenge or tune the model.  


## How to Use
Run `MalwareDetection.py` when it asks for path, enter the relative or absolute path 
that includes the test set. It will generate prediction as a csv file named `Prediction.csv`. The csv file
will have two columns, `hash` and `binary`.  

## Language and Libraries
`python` 3.7
`sklearn` 	- 0.23.1
`numpy` 	- 1.19.0
`pandas` 	- 1.0.5
`pathlib`
  

## Resources 
The code uses some resources to extract features, which are actually python lists in pkl (pickle) format.
csv and json files are given for visual representation.
bl_dll.pkl		- a list of suspicious dlls
bl_func.pkl		- a list of suspicious functions
bl_str.pkl		- a list of suspicious strings
docstub.pkl		- a list of suspicious docstubs
dynamic_dll.pkl	- a list of dynamic dlls
pe_dll.pkl		- a list of PE dlls
priv.pkl		- list of privilages
regkeys.pkl		- a list of suspicious regestry keys
wl_str.pkl		- a list of whitelisted strings  
  
## Trained Model  
The training code `TrainingAllinOne.py` exports the trained dataframes that is used to train the model
in test code. The `MalwareDetection.py` code uses two files to train the model: `X.pkl` and `y.pkl`.
I have already trained the whole model and added the preprocessed `X.pkl` and `y.pkl` in the repository.
For safety purpose, exporting these two files are commented out in the code `TrainingAllinOne.py` to protect the trained models.
If you want to modify the feature extraction process, please uncomment those lines.  
  
## Features  
The features we extracted are listed in features.txt file
