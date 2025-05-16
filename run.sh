#!/bin/bash
cd /root/work/dev/vanna
source /root/miniconda3/etc/profile.d/conda.sh
conda activate vanna
nohup python vanna_server.py >> /root/work/dev/vanna/logs/run_server-`date +%Y%m%d`.log 2>&1 &