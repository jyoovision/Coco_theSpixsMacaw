# ArtechCapstoneProject
[English](README.md) | [한국어](README-ko.md)  

## About
This project involves the use of Retrieval-based Voice Conversion (RVC) to transform and output recorded voices in Unreal Engine 5.  
The RVC project can be found [here](https://github.com/RVC-Project).

## Installation and Execution
To run the project on your local computer, follow these steps:

### 1. Clone the Repository
Clone the repository to your local files by executing the following command:

``` bash
git clone "https://github.com/jyoovision/ArtechCapstoneProject.git"
```

### 2. Set Up Conda Virtual Environment
Create a Conda virtual environment using the environment.yml file. This will install all the necessary dependencies.  
The environment is named capstone. Be cautious to avoid conflicts with any existing local environments.  
 
``` bash
conda env create -f environment.yml
```

### 3. Launch the Server
To start the server, navigate to the RVC_server directory and execute the following command:

``` python
python server.py
```

### 4. Build CapstoneProject_v01
This project is designed for Unreal Engine version 5.1.1.  
To build the UE project, open the CapstoneProject_v01.uproject file located in CapstoneProject_v01.  
You may encounter warnings during the initial launch, but these should resolve after a short wait.  

### 5. Run RVC in CapstoneProject_v01
To execute RVC in the Unreal Engine environment, follow these steps:

- Launch the in-game mode in CapstoneProject_v01.  
- Once the in-game mode is running, press the "R" key to start recording.  
- After recording, the voice transformed by RVC will be played back after a few seconds.  

This process allows you to utilize the RVC features within Unreal Engine 5.  

## References
- [Retrieval-based-Voice-Conversion-WebUI](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)