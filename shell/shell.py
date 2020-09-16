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
    elif "<" in response:#Input redirection
        commands=response.split("<")
        commands[0],commands[1]=commands[0].strip(),commands[1].strip()
        rc = os.fork()
        if rc==0:
            pr,pw=os.pipe()
            for f in (pr,pw):
                os.set_inheritable(f,True)
            piping=os.fork()
            if piping==0:
                os.close(1)
                os.dup2(pw,1)
                for fd in (pr,pw):
                    os.close(fd)
                tokens=commands[1].split(" ",1)#just changed which command sent output to the other
                try:
                    os.execve(tokens[0],tokens,os.environ)
                except FileNotFoundError:
                    pass
                for dir in re.split(":",os.environ["PATH"]):
                    program= "%s/%s" % (dir,tokens[0])
                    try:
                        os.execve(program,tokens,os.environ)
                    except FileNotFoundError:
                        pass
                    print(tokens[0] + ": command not found.") 
            else:#now command 0 receives output from command 1
                os.wait()
                os.close(0)
                os.dup2(pr,0)
                for fd in (pr,pw):
                    os.close(fd)
                commands[0].replace('\n','')
                tokens=commands[0].split(" ",1)
                try:
                    os.execve(tokens[0],tokens,os.environ)
                except FileNotFoundError:
                    pass
                for dir in re.split(":",os.environ["PATH"]):
                    program= "%s/%s" % (dir,tokens[0])
                    try:
                        os.execve(program,tokens,os.environ)
                    except FileNotFoundError:
                        pass
                print(tokens[0] + ": command not found.")
                sys.exit()
        else:
            os.wait()

    elif ">" in response:#redirect to file
        io=response.split(">")
        io[0]=io[0].strip()
        io[1]=io[1].strip()
        tokens=io[0].split(" ",1)#the command is only the first half
        if tokens[0] == "exit":
            print("Now exiting shell")
            sys.exit()
        elif tokens[0] == "cd":
            if len(tokens)>1: 
                try:
                    os.chdir(tokens[1])
                    os.write(1, os.getcwd().encode())
                except FileNotFoundError:
                    print ("No such file or folder")
                    pass
            else:
                if "HOME" in os.environ:#couldn't remember if you have to export HOME
                    os.chdir(os.environ["HOME"])
                else:
                    pass
        else:
            rc = os.fork()
            if rc==0:
                if response!="":
                    os.close(1)#closing to allow redirection
                    sys.stdout=open(io[1],"w")#redirects output to the file
                    os.set_inheritable(1,True)#passes on file descriptor to the executed program
                    try:#in case the whole path is given
                        os.execve(tokens[0],tokens,os.environ)
                    except FileNotFoundError:
                        pass
                    for dir in re.split(":",os.environ["PATH"]):#searches for program in PATH
                        program= "%s/%s" % (dir,tokens[0])
                        try:
                            os.execve(program,tokens,os.environ)
                        except FileNotFoundError:
                            pass
                    print(tokens[0] + ": command not found.")
                    sys.exit()#exits in case not found
                else:
                    sys.exit()#if empty string
            else:
                os.wait()#waits for child to finish to accept more input
    else:# if there are no pipes or redirections
        tokens=response.split(" ",1)
        if tokens[0] == "exit":
            print("Now exiting shell")
            sys.exit()
        elif tokens[0] == "cd":
            if len(tokens)>1: 
                try:
                    os.chdir(tokens[1])
                    os.write(1, os.getcwd().encode())
                except FileNotFoundError:
                    print ("No such file or folder")
                    pass
            else:
                if "HOME" in os.environ:#couldn't remember if you have to export HOME or not
                    os.chdir(os.environ["HOME"])
                else:
                    pass
        else:
            rc = os.fork()
            if rc==0:
                if response!="":#this handles \n characters by themselves
                    try:#in case the whole path is given
                        os.execve(tokens[0],tokens,os.environ)
                    except FileNotFoundError:
                        pass
                    for dir in re.split(":",os.environ["PATH"]):#searches for the program in PATH
                        program= "%s/%s" % (dir,tokens[0])
                        try:
                            os.execve(program,tokens,os.environ)
                        except FileNotFoundError:
                            pass
                    print(tokens[0] + ": command not found.")  
                    sys.exit()#exits in case it's not found
                else:
                    sys.exit()#exits if empty string
            else:
                os.wait()#waits for child to finish to accept more input