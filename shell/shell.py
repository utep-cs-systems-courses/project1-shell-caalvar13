#!/usr/bin/env python3

import os,sys,re

pid=os.getpid()
exit = False
if "PS1" in os.environ:
    ps1=os.environ["PS1"]
else:
    ps1="$ "
response = ""
while (1):
    tokens = None
    try:
        response = input(ps1)
    except EOFError:
        sys.exit()
        pass
    response = response.strip()
    if "|" in response:
        commands=response.split("|")#since we only need to test 1 pipe 
        commands[0],commands[1]=commands[0].strip(),commands[1].strip()
        rc = os.fork()
        if rc==0:
            pr,pw=os.pipe()
            for f in (pr,pw):
                os.set_inheritable(f,True)
            piping=os.fork()#forking twice 
            if piping==0:#child is sending output to second child
                os.close(1)#snippet modified from pipe demo
                os.dup2(pw,1)
                for fd in (pr,pw):
                    os.close(fd)
                tokens=commands[0].split(" ",1)#tokenizing args
                try:#in case the whole path is given
                    os.execve(tokens[0],tokens,os.environ)
                except FileNotFoundError:
                    pass
                for dir in re.split(":",os.environ["PATH"]):#searching for program in PATH
                    program= "%s/%s" % (dir,tokens[0])
                    try:
                        os.execve(program,tokens,os.environ)
                    except FileNotFoundError:
                        pass
                    print(tokens[0] + ": command not found.") 
            else:#second child receives the output of first child
                os.wait()
                os.close(0)#closed to allow piping
                os.dup2(pr,0)
                for fd in (pr,pw):
                    os.close(fd)
                tokens=commands[1].split(" ",1)#tokenizing the args
                try:#in case the whole path is given up front
                    os.execve(tokens[0],tokens,os.environ)
                except FileNotFoundError:
                    pass
                for dir in re.split(":",os.environ["PATH"]):#searching for the program in PATH.
                    program= "%s/%s" % (dir,tokens[0])
                    try:
                        os.execve(program,tokens,os.environ)
                    except FileNotFoundError:
                        pass
                print(tokens[0] + ": command not found.")
                sys.exit()
        else:
            os.wait()#waits for children to finish to accept more commands
    