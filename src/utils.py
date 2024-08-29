# -*- coding: utf-8 -*-

import os
import subprocess
import sys

from pathlib import Path

def get_run_dir():
    return "/run/user/{0}".format(os.getuid())
    
def is_pid_alive(pid):
    try:
        os.kill(pid,0)
        return True
    except:
        return False

def get_pid_from_file(name):
    run = get_run_dir()
    filename = Path(run + "/" + name)
    
    if (filename.exists()):
        f=open(str(filename),"r")
        data=f.readlines()
        f.close()
        if (len(data)>0):
            return int(data[0])
        else:
            return 0
    else:
        return 0
    
def create_pid_file(name):
    
    filename = get_run_dir() + "/" + name
    f=open(filename,"w")
    f.write("{0}".format(os.getpid()))
    f.close()
    
    return True

def destroy_pid_file(name):
    filename = get_run_dir() + "/" + name
    
    if (Path(filename).exists()):
        os.remove(filename)

def application_lock(name):
    pid = get_pid_from_file(name)

    if (pid>0):
        if (is_pid_alive(pid)):
            print("process is already running",file=sys.stderr)
            sys.exit(1)
        
    create_pid_file(name)
    
def application_release(name):
    destroy_pid_file(name)

