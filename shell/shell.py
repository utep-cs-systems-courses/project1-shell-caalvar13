import os, sys, re

def ExecuteProcess(command):
    pid = os.getpid()

    os.write(1, ("About to fork (pid:%d)\n" % pid).encode())

    rc = os.fork()
    
    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:                   # child
        os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
                (os.getpid(), pid)).encode())
        command = command.split()
        args = command
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly

        os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
        sys.exit(1)                 # terminate with error

    else:                           # parent (forked ok)
        os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
                 (pid, rc)).encode())
        childPidCode = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                childPidCode).encode())

while True:
    command = input()
    
    if "cd" in command:
        command = command.split("cd")[1].strip()
        try:
            os.chdir(command)
            os.write(1, (os.getcwd() + " ").encode())
        except FileNotFoundError:
            os.write(1, ("file not found\n").encode())
        continue
        
    if "ls" in command:
        print(os.listdir())
        continue
 
    if "exit" in command:
        sys.exit(1)
    
    if "<" in command:
        
    ExecuteProcess(command)