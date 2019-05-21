#! /usr/bin/python3
import shutil
import subprocess
import time
from datetime import datetime
import configparser
import os
import platform

# This script will work in conjunction with Ansible to configure a Red Team/PenTesting SOE
# The python script will clone the base VM, start up the VM, obtain the IP, and kick off the Ansible Playbook
# Variables
startTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # helps give us information on how much time it took to run
ovftool_path = [r"c:\Program Files\VMware\VMware OVF Tool"]
vmrun_path = [r"c:\Program Files (x86)\VMware\VMware Workstation"]

def config():
    config = configparser.ConfigParser()
    config.read('config.txt')
    basePath = config['DEFAULT']['basePath']
    OVATemplate = config['DEFAULT']['OVATemplate']
    privKeyLoc = config['DEFAULT']['privKeyLoc']
    SOEuser = config['DEFAULT']['SOEuser']
    return basePath, OVATemplate, privKeyLoc, SOEuser

# Clone VM
def cloneBaseVM(customerName, basePath, OVATemplate, privKeyLoc, SOEuser, osArch):
    print("[+] Deploying Base VM from OVA")
    # Need OVFTool from here: https://my.vmware.com/web/vmware/details?productId=352&downloadGroup=OVFTOOL350
    # /Applications/VMware\ OVF\ Tool/ovftool --allowExtraConfig --lax <path_to_ovf_file> <path_to_target_folder>
    args = "--allowExtraConfig --lax --name==" + customerName + "-Ubuntu " + basePath + OVATemplate + " " + basePath + customerName + "/VM/"
    if osArch == 'win':
        subprocess.call([ovftool_path[0] + "\ovftool.exe", "--allowExtraConfig", "--lax", "--name=" + customerName + "-Ubuntu", basePath + OVATemplate, basePath + customerName + "\VM"])
    elif osArch == 'linux':
        subprocess.call("ovftool " + args, shell=True)
    elif osArch == 'mac':
        subprocess.call("/Applications/VMware\ OVF\ Tool/ovftool " + args, shell=True)
    print("[+] VM Cloned")

def cusFolderSetup(basePath):
    # Get Customer Name to setup folder
    templateName = "TEMPLATE"
    while True:
        customerName = input("[!] Enter Customer Name (Without spaces is best): ")
        if customerName.isalnum(): # Try to prevent those hacxorz from hackin'
            break
        else:
            print("[-] Special Characters not alowed.")
    # Copy Template to CustomerName Folder
    try:
        shutil.copytree(basePath + templateName, basePath + customerName)
    except FileExistsError:
        print("[-] Folder Exists.")
    return customerName

# Start VM
def startVM(customerName, basePath, OVATemplate, privKeyLoc, SOEuser, osArch):
    print("[+] Starting VM")
    # vmrun -T fusion start <path_to_file.vmx>
    if osArch == 'win':
        arg1 = vmrun_path[0] + "\\vmrun.exe"
        arg2 = "-T"
        arg3 = "ws" #change to fusion if Mac
        arg4 = "start"
        arg5 = basePath + customerName + "\\VM\\" + customerName + "-Ubuntu\\" + customerName + "-Ubuntu" + ".vmx"
        subprocess.call([arg1, arg2, arg3, arg4, arg5], shell=True)
    elif osArch == 'linux':
        subprocess.call("vmrun -T ws start " + basePath + customerName + "/VM/" + customerName + "-Ubuntu" + ".vmwarevm/" + customerName + "-Ubuntu" + ".vmx", shell=True)
    elif osArch == 'mac':
        subprocess.call("vmrun -T fusion start " + basePath + customerName + "/VM/" + customerName + "-Ubuntu" + ".vmwarevm/" + customerName + "-Ubuntu" + ".vmx", shell=True)
    print("[!] Waiting a minute to let the VM fully start...")
    time.sleep(60)
    print("[+] VM Should be Started")

# Determine VM IP
def vmIPlookup(customerName, basePath, OVATemplate, privKeyLoc, SOEuser, osArch):
    print("[+] Determining VM IP and updating hostlist")
    # vmrun getGuestIPAddress <path_to_file.vmx>
    if osArch == 'win':
        vm_ip = subprocess.check_output([vmrun_path[0] + "\\vmrun.exe", "getGuestIPAddress", basePath + customerName + "\\VM\\" + customerName + "-Ubuntu\\" + customerName + "-Ubuntu" + ".vmx"], shell=True)
    else:
        vm_ip = subprocess.check_output("vmrun getGuestIPAddress " + basePath + customerName + "/VM/" + customerName + "-Ubuntu" + ".vmwarevm/" + customerName + "-Ubuntu" + ".vmx", shell=True)
    vm_ip = str(vm_ip).split("'")[1]
    vm_ip = vm_ip.split("\\n")[0]
    if osArch == 'win':
        vm_ip = vm_ip.split("\\r")[0]
    return vm_ip

def discoverOsArch():
    # Figure out OS Architecture because Windows pathing is so much different...
    print("[+] Discovering OS Architecture")
    osType = platform.system()
    if osType == "Windows":
        osArch = 'win'
    elif osType == "Linux":
        osArch = 'linux'
    else:
        osArch = 'mac'
    print("[+] Running on " + osType)
    return osArch

def ansibleFun(vm_ip, basePath, OVATemplate, privKeyLoc, SOEuser, osArch):
    # Write IP to hosts file
    f = open("hosts.txt", "w")
    f.write(vm_ip)
    f.close()
    print("[+] Your VM appears to be at " + vm_ip)
    # Start Ansible Playbook
    print("[+] Running Ansible Playlist...This may take some time...Just need two bits of information, then go grab a coffee!")
    if osArch == 'win':
        subprocess.call('bash -c "ansible-playbook -i hosts.txt -become -u ' + SOEuser + ' --private-key=' + privKeyLoc + ' -K main.yml"', shell=True)
    else:
        subprocess.call("ansible-playbook -i hosts.txt -become -u " + SOEuser + " --private-key=" + privKeyLoc + " -K main.yml", shell=True)

def main():
    osArch = discoverOsArch()
    basePath, OVATemplate, privKeyLoc, SOEuser = config()
    customerName = cusFolderSetup(basePath)
    cloneBaseVM(customerName, basePath, OVATemplate, privKeyLoc, SOEuser, osArch)
    startVM(customerName, basePath, OVATemplate, privKeyLoc, SOEuser, osArch)
    vm_ip = vmIPlookup(customerName, basePath, OVATemplate, privKeyLoc, SOEuser, osArch)
    ansibleFun(vm_ip, basePath, OVATemplate, privKeyLoc, SOEuser, osArch)
    endTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("[+] Completed.")
    print("[+] The start time was: " + startTime)
    print("[+] The end time was: " + endTime)

if __name__ == '__main__':
    main()
