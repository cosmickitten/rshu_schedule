#! /bin/bash
cd /opt/rshu_schedule
git fetch --all -f
git chechout main
source /opt/rshu_schedule/venv/bin/activate
python main.py 
deactivate

