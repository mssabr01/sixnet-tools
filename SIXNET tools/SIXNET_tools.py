#import antigravity
#antigravity.webbrowser.Mozilla
import sys, getopt
from attactions import sup_shell
import STX_Networking
import telnet
import file_manip, attactions
from SUP_message import sup_msg

welcome  = "rev 30ish Mehdi Sabraoui 2013\n"
welcome += "   _   _   _   _   _   _  \n"
welcome += "  / \ / \ / \ / \ / \ / \ \n"
welcome += " ( S | I | X | N | E | T )\n"
welcome += "  \_/ \_/ \_/ \_/ \_/ \_/ \n"
welcome += "   _   _   _   _   _      \n"
welcome += "  / \ / \ / \ / \ / \     \n"
welcome += " ( T | o | o | l | s )    \n"
welcome += "  \_/ \_/ \_/ \_/ \_/     \n"

usage   = "Usage: SIXNET_tools [Options] {target specifications}"

help     = "Sixnet Tools. Tools for poking at Sixnet things.\n"
help    += "TARGET SPECIFICATION:\n"
help    += "Can pass IP addresses or networks\n"
help    += " Ex: 192.168.1.1, 10.1.1.0/24\n"
help    += "Options:\n"
help    += " -h                      Displays this help dialog\n"
help    += " -s {host | network}     NOP scans a host or network for sixnet devices.\n"
help    += " -T {host}               Enables telnet for the given ip address\n"
help    += " -F {host}               Enables FTP for the given ip address\n"
help    += " -f {host}               Gets OS and Firmware information for the given ip address\n"
help    += " -S {host}               Opens a very dumb shell to the given ip address\n"
help    += " -r {host} {src} {dst}   Copies a file from the remote sixnet host to the local host\n"
help    += " -w {host} {src} {dst}   Copies a file from the local host to the remote sixnet host\n"
help    += " -p {host}               Clears the password for the owner account (likely root)\n"
help    += " -l {host}               Plays with the discreet outputs. For funsies only\n"
help    += " -b {host}               furk bamp\n"

def main(argv):
        try:
            opts, args = getopt.getopt(argv,"hs:T:F:f:S:b:r:w:p:l:",["help","scan=","enableTelnet=","enableFTP=","fingerprint=","shell=","forkbomb=","read=","write=","clrPass=","blink="])
        except getopt.GetoptError:
            print (welcome)
            print (usage)
            sys.exit()
        if(len(args) == 0):
            print (welcome)
            print (help)
            sys.exit()
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print (welcome)
                print (help)
                sys.exit()
            elif opt in ("-s", "--scan"):           #scan
                STX_Networking.NOP_scan(arg)
            elif opt in ("-T", "--enableTelnet"):       #enable telnet
                attactions.enable_telnet(arg)
            elif opt in ("-F", "--enableFTP"):          #enable ftp
                attactions.enable_ftp(arg)
            elif opt in ("-f", "--fingerprint"):    #fingerprint
                attactions.fingerprint(arg)
            elif opt in ("-S", "--shell"):         #shell
                attactions.sup_shell(arg)
            elif opt in ("-r", "--read"):
                if(len(args) == 2):
                    attactions.get_file(arg, args[0], args[1])
                else:
                    attactions.get_file(arg, args[0])
            elif opt in ("-w", "--write"):
                attactions.write_file(arg, args[0], args[1])
            elif opt in ("-p", "--clrPass"):
                attactions.clear_pass(arg)
            elif opt in ("-l", "--blink"):
                attactions.blinkenlights(arg)
            elif opt in ("-b", "--forkbomb"):
                attactions.forkbomb(arg)

if __name__ == "__main__":
        main(sys.argv[1:])




