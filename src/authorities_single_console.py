import os
import subprocess
import signal
import atexit
from authorities_info import authorities_count


#Retrieve the number of authorities from the ".env" file
numberOfAuthorities  = authorities_count()


# Store the subprocesses globally to access them in the signal handler
processes = []


# To close automatically subprocesses (attribute_certification())
def handle_exit():
    for process in processes:
        # Send SIGTERM to the process group
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        

# Ensure subprocesses are killed on exit
atexit.register(handle_exit)


# Initialization of the authorities through a subprocess in the same console
commands = []
for i in range(1, numberOfAuthorities + 1):
    commands.append(f"python3 ../src/authority.py -a {i}")
command_string = " & ".join(commands)
process = subprocess.Popen(
    ["bash", "-c", command_string],
    # Create a new process group
    preexec_fn=os.setsid  
)
# Wait until the authorities' initialization is complete (subprocess finishes)
process.wait()
# Start another subprocess to put on hold the authorities to answer for decryption keys
commands = []
for i in range(1, numberOfAuthorities + 1):
    commands.append(f"python3 ../src/server_authority.py -a {i}")
# Join the commands with ' & ' to run them in parallel
command_string = " & ".join(commands)
process = subprocess.Popen(
    ["bash", "-c", command_string],
    #Creates a new process group
    preexec_fn=os.setsid
)
processes.append(process)
process.wait()