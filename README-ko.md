# ArtechCapstoneProject
[English](README.md) | [한국어](README-ko.md)  

## 소개
이 프로젝트는 Retrieval-based-Voice-Conversion을 사용하여 Unreal Engine 5에서 녹음된 음성을 변환하고 내보냅니다.  
RVC-project는 [여기](https://github.com/RVC-Project)에서 찾을 수 있습니다.  

## 설치 및 실행
로컬 컴퓨터에서 프로젝트를 실행하려면 다음 단계를 따르세요:

### 1. 레포지토리 클론하기
다음 명령어를 실행하여 로컬 파일에 레포지토리를 클론하세요.
``` bash
git clone "https://github.com/jyoovision/ArtechCapstoneProject.git"
```

### 2. Conda 가상 환경 구성하기
environment.yml 파일을 통해 Conda 가상 환경을 만듭니다. 이렇게 하면 필요한 모든 종속성이 설치됩니다.  
환경 이름은 capstone으로 지정됩니다. 기존 로컬 환경과 충돌하지 않도록 주의하세요.

```bash
conda env create -f environment.yml
```

### 3. 서버 실행하기
서버를 시작하려면 RVC_server 디렉터리로 이동하여 다음 명령을 실행하세요.

``` python
python server.py
```

### 4. CapstoneProject_v01 빌드하기
이 프로젝트는 Unreal Engine 버전 5.1.1을 사용합니다.  
UE 프로젝트를 빌드하려면 CapstoneProject_v01에 있는 CapstoneProject_v01.uproject 파일을 엽니다.  
초기 실행 시 경고가 표시될 수 있지만 잠시 기다리면 해결됩니다.

### 5. CapstoneProject_v01에서 RVC 실행하기
Unreal Engine 환경에서 RVC를 실행하려면 다음 단계를 따르세요.
- CapstoneProject_v01에서 인게임모드를 실행합니다.
- 인게임모드가 실행되면 "R" 키를 눌러 녹음합니다.
- 녹음이 끝나면 몇 초뒤 RVC를 통해 변환된 목소리가 실행됩니다.

이 과정을 통해 Unreal Engine 5 내에서 RVC 기능을 활용할 수 있습니다.

## 참조
- [Retrieval-based-Voice-Conversion-WebUI](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)