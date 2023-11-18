# ArtechCapstoneProject

## About
This project uses Retrieval-based-Voice-Conversion to convert and export recorded vocals from Unreal Engine 5.  
The RVC-project can be found [here](https://github.com/RVC-Project).

## Installation and Running
Follow these steps to set up the project on your local machine:

### 1. Clone the Repository
Begin by cloning the repository and local files to your system.

``` bash
git clone "https://github.com/jyoovision/ArtechCapstoneProject.git"
```

### 2. Set Up Conda Environment
Use the environment.yml file to create a Conda virtual environment. This will ensure that all necessary dependencies are installed. The environment will be named capstone. Be cautious to avoid conflicts with any existing local environments.

```bash
conda env create -f environment.yml
```

### 3. Launch the Server
To start the server, navigate to the RVC_server directory and run the following command:

``` python
python server.py
```

This command initiates the server.

### 4. Build the UE5 Project
This repository is designed for Unreal Engine version 5.1.1. To build the UE project, open the .uproject file located in CapstoneProject_v01. Be aware that initial execution might prompt warnings, but these should resolve after a short wait.

### 5. Running RVC in Unreal Engine 5
To interact with RVC in the Unreal Engine environment, follow these steps:
- Launch the CapstoneProject_v01.
- Once the project is running, press the "R" key to start recording.
- After recording, RVC will respond accordingly.

This process enables you to engage with RVC features within the Unreal Engine 5 platform.

## References
- [Retrieval-based-Voice-Conversion-WebUI](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)
