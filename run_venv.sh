#! /bin/bash
cd /opt/rshu_schedule
source /opt/rshu_schedule/venv/bin/activate
git chechout dev
python main.py 
deactivate

