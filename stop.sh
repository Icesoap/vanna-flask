#!/bin/bash
ps -ef |grep -v grep|grep 'python vanna_server.py'|awk '{print $2}'|xargs kill -9