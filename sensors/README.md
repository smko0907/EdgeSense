## Datasets
Background Noise Dataset from AI Hub
https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=568
https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=71376


## Dependencies
```sh
pip install openai-whisper pyaudio mediapipe opencv-python msvc-runtime numpy tensorflow pandas scikit-learn

sudo apt install ffmpeg  # Debian/Ubuntu
choco install ffmpeg # Windows
                    # or download from https://www.gyan.dev/ffmpeg/builds/
```

## Broken DDL Error
#1. Create a new virtual environment with the following command:
```sh
python -m venv mediapipe_env

# Activate the environment (for Windows PowerShell)
mediapipe_env\Scripts\activate  
# OR Activate (for Windows Command Prompt)
# source mediapipe_env/Scripts/activate

pip install --upgrade pip
pip install mediapipe opencv-python msvc-runtime

```

#2. Find the path for the site-packages folder by running:
```sh
python -c "import sys; print(sys.path)"
```

#3. Manually add the Windows PATH by:
- Press Win + R, type sysdm.cpl, and hit Enter.
- Go to Advanced → Environment Variables.
- Under System Variables, find Path, then click Edit.
- Click New and paste the path you found.
- Click OK, restart your PC, and try running the script again.
