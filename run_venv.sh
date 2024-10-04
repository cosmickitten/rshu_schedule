#! /bin/bash
cd /opt/rshu_schedule
git pull
git chechout main
source /opt/rshu_schedule/venv/bin/activate
python main.py 
deactivate

