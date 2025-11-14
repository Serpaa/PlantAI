# PlantAI
Plant soil moisture prediction using machine learning with Scikit-learn.

## Installation
* Install Python dependencies:
```
sudo apt install python3-pip
sudo apt install python3-venv
```
* Install session manager (tmux):
```
sudo apt install tmux
```
* Create and activate the virtual environment:
```
python3 -m venv ~/plantai
source ~/plantai/bin/activate
```
* Clone repository and install all dependencies:
```
git clone -b dev https://github.com/Serpaa/PlantAI
cd PlantAI
pip install -r requirements.txt
```
* Create a new tmux session and start PlantAI:
```
tmux new -s plantai
python3 PlantAI/main.py
```
* Exit the session with Ctrl + B, then D then reconnect later with:
```
tmux attach -t plantai
```