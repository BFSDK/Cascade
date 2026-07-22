### CascadeLang ###
# Go compiler module
#
# Compiles Go code into an EXE binary using the local Go environment
###################
import os
import sys
import subprocess

import sub.errorlib as erl

def get_sub_dir():
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        return os.path.join(exe_dir, "sub")
    return os.path.abspath("sub")

def get_go_dir():
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        return os.path.join(exe_dir, "go")
    return os.path.abspath("go")

SUB_DIR = get_sub_dir()
GO_DIR = get_go_dir()

def kill_old_processes():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "output.exe"], 
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL)
    except Exception:
        pass

def buildExe(code):
    kill_old_processes()
    
    exe_path = os.path.join(SUB_DIR, "output.exe")
    temp_go = os.path.join(SUB_DIR, "temp.go")

    if os.path.exists(exe_path):
        try:
            os.remove(exe_path)
        except PermissionError:
            erl.showFastError("Compilation", "The recompile file is already running, and its process could not be completed", "Complete the process through the Task Manager")
            return

    with open(temp_go, 'w', encoding='utf-8') as f:
        f.write(code)

    cmd = f'go build -o "{exe_path}" "{temp_go}"'
    subprocess.run(cmd, shell=True, cwd=GO_DIR)

    if os.path.exists(temp_go):
        try:
            os.remove(temp_go)
        except OSError:
            pass