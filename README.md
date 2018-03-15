# sixnet-tools
Tool for exploiting sixnet RTUs

1 Abstract
Supervisory Control and Data Acquisition (SCADA) networks and devices are the
computational brains behind the nation’s infrastructure. They monitor and control
industrial machinery in power plants, oil and gas lines, assembly lines, and etcetera.
There exist programmable logic controllers and remote terminal units sitting on these
SCADA networks that are critically lacking in some of the most basic security processes
and controls. This paper and the corresponding project are meant to highlight such a
weakness at the application level of Sixnet SCADA devices. The tool detailed in this
project is written in Python and allows an attacker to gain root level access to these
Sixnet devices with very little effort.
2 The Project
There are three aspects to a basic SCADA network. The network itself is the medium
through which the endpoints communicate with each other. These networks are very
similar to corporate local area or wide area networks and may consist of various routing
and switching components. Ideally a SCADA network is a completely isolated subnet
of a greater corporate network and out of reach of the internet. Another aspect of
a SCADA network is the human-machine interface (HMI). This is the vendor-specific
monitoring and control software that presents easily readable data from the endpoints
of the network to the engineer in charge. For this particular project the HMI used is
Sixnet’s I/O toolkit, available free from their website. The final aspect is the endpoints
of the network. These are the Programmable Logic Controllers (PLCs) and Remote
Terminal Units (RTUs) that interface directly with the industrial machinery. This final
aspect is the focus of this paper. There is a very serious lack of system and application
security with Sixnet’s PLC and RTU families and this projects sets out to show why.
The device used for this project was Sixnet’s VersaTRAK Mini iPm Open RTU/Controller
2 Series. It was running the latest firmware version, 4.3.144, and Linux 2.4 as the
base operating system. It had 12 discreet inputs, 4 discreet outputs, 8 analog inputs,
2 analog outputs, an RS232 port, and RS485 port, and two Ethernet ports. For the
experiments the device was connected to a small lab network consisting of a switch, a
lab computer acting as an Engineer’s computer, a router for DHCP, and a laptop acting
as an attacker. All three endpoints were connected to the switch and resided on the
same subnet.
Sixnet Tools was created by reverse engineering the Sixnet Universal Protocol. This
protocol is a proprietary communication standard supported by most, if not all, of
Sixnet’s PLCs and RTUs, including VersaTRAK RTUs, SIXTRAK, RemoteTRAK and
2
EtherTRAK, IOMUX, VERSAMUX RTUs [1]. Depending on the device it can be used
over Ethernet, serial, or Modbus communication. The protocol has built-in commands
for data acquisition related tasks such as reading and setting I/O and was created as a
way to make managing a distributed Sixnet SCADA network easier.
3 Reversing
The reversing process entailed generating traffic from the HMI to simulate a live environment
and snooping the traffic going across the network using Wireshark. Common
tasks like verifying the I/O and configuring network protocols were kicked off using the
HMI while monitoring the traffic. Certain patterns arose from this. For instance, all of
the traffic between the two points was sent over UDP. Also, even though the port was
not detected as open from an Nmap scan all traffic was sent on port 1594. After dissecting
and analyzing innumerable packets a specialized driver for the Sixnet Universal
Protocol was created. The fields of the protocol are described below as seen for a basic
Set Discreet command. A couple notes on the fields: all alphanumeric characters are
encoded in ASCII hex values and the destination, source, session, sequence, and CRC
fields are left as seen below for every packet sent by Sixnet Tools regardless of command.
Table 1:
3.1 SETD
This command is used to set the discreet output ports on the device. The command
field is set to 0e and the data field is set as follows:
Table 2: SETD
F ield Length
00(input) or 01(output) 1 byte
Start pin 2 bytes
Pins to set/clear 2 bytes
ACK:
Other than confirming a 01 in the command field no useful data is returned in the
ACK.
3.2 NOP
A simple no-operation command with command byte 00 that causes the Sixnet device
receiving it to reply to the sender with an ACK. The data field is left empty.
ACK:
The ACK replying to a NOP contains an empty data field.
3.3 File Manipulation
This command and its various sub-commands are used to directly interact with the
underlying file system of the device. The command field is set to 1a and the data field
is set as follows
3.3.1 Sub-command – Read file (01)
Returns x characters from the file at the given file path from the given start
4
Table 3: Read File
F ield Length
file descriptor 4 bytes
Start index 4 bytes
00 1 bytes
midrule x 1 byte
ACK:
Index 22 of the data field onward contain the next x contents of the file. Returns 02
if the file is not found.
3.3.2 Sub-command – write file (02)
Writes contents to the given file path starting at the given index
Table 4: Write File
F ield Length
file descriptor 4 bytes
Length 2 bytes
Contents variable
ACK:
00 in the data field if successful
3.3.3 Sub-command – find file (00:03)
Returns the file descriptor of the file located at the given path. [File path] variable
Null terminator (00) 1 byte
5
Table 5: Find File
F ield Length
file path 4 variable
Null terminator 1 byte
ACK:
The last 5 bytes of the data field contain the file descriptor. Returns 02 if the file is
not found.
3.3.4 Sub-command – create file (03:03)
Returns the file descriptor of a newly created file located at the given file path.
Table 6: Create File
F ield Length
file size 4 bytes
file path variable
Null terminator 1 byte
ACK:
The last 4 bytes of the data field contain the file descriptor
3.3.5 Sub-Command – get file size (06)
Returns a 4 byte file size for the given file descriptor
Table 7: Get File Size
F ield Length
file descriptor 5 bytes
6
ACK:
The first half of the last 10 bytes of the data field contains the file size. Returns 02
if the file is not found.
3.3.6 Sub-command – Rename/move (09:00)
Moves or renames the file from source to destination
Table 8: Move/Rename
F ield Length
Source variable
Null terminator 1 byte
destination variable
Null terminator 1 byte
ACK:
Unknown, unnecessary to keep track of.
3.4 System Command
This command runs the contents of the data field much like fork() or exec() would
in a C program. A d0 in the command field designates a shell command
Table 9: System Command
F ield Length
1e:01:00 3 bytes
Command string variable
Null terminator 1 byte
ACK:
7
Starting from index 4 of the data field, the first 245 characters of the output of the
command are returned
4 Attactions
Sixnet Tools is an organization of these commands into a ready-made reconnaissance
and attack program. The arguments for Sixnet_Tools.py are as follows:
4.1 -s {host | network} NOP Scan
Sends a single NOP packet to either the give IP address or to each host on the given
network. The network is expressed in CIDR notation. If a properly formatted ACK is
returned a Sixnet device has been detected on the network
4.2 -T {host} Enable Telnet
On the specific device tested the Sixnet rootkit checks the flags in the file /etc/stacfg/general.config
to determine if certain services such as FTP, Telnet, and HTTP are
enabled or disabled. This option uses the file manipulation commands to read /etc/stacfg/general.config,
convert the line enable telnet=0 to enable telnet=1, and writes the
result back to /etc/stacfg/general.config. This removes the block the Sixnet software
imposes on telnet.
4.3 -F {host} Enable FTP
On the specific device tested the Sixnet rootkit checks the flags in the file /etc/stacfg/general.config
to determine if certain services such as FTP, Telnet, and HTTP are
enabled or disabled. This option uses the file manipulation commands to read /etc/stacfg/general.config,
convert the line enable FTP=0 to enable FTP=1, and writes the
result back to /etc/stacfg/general.config. This removes the block the Sixnet software
imposes on FTP.
8
4.4 -f {host} Fingerprint
Gathers information about the Sixnet device at the given IP address. The firmware
version is determined by reading the file located at /etc/sxbuildinfo.txt. The OS version
is determined by sending a uname -sr shell command and formatting the result.
The hostname is determined by sending the hostname command. The station number
is determined by reading /etc/stacfg/general.config and picking out the line “station
number=”.
4.5 -S {host} Very Dumb Shell
Starts a very dumb pseudo-shell aimed at the given IP address. This is simply a whileloop
that encapsulates the user’s input into a Sixnet Universal Protocol shell command
packet and prints the contents of the ACK packet (the output of the command) to the
console.
4.6 -r {host} {source} {destination} Read file
Reads a file from a Sixnet device at the given IP and writes it to a local file designated
by destination. This uses the file manipulation commands.
4.7 -w {host} {source} {destination} Write file
Source is a file located on the local machine. This option writes the source to the
destination on the remote Sixnet device at the given IP.
4.8 -p {host} Clear password
Clears the password of the account that the Sixnet software suite is running under
on the Sixnet devices at the given IP. This is most likely the root account. This works
by sending a passwd command. For some reason just sending passwd runs through the
entire password change program setting the password to blank.
9
4.9 -l {host} Blinkenlights
Blinks the lights attached to the discreet IO of the specific lab setup used to create
this program. This was for proof of concept only and is not intended for use outside of
that context.
4.10 -b {host} Fork bomb
Sends a command containing the string p(){ p|p& }; p. This fork bombs the remote
Sixnet device at the given IP
5 Conclusion
The goal of this project was to demonstrate the critical lack of security inherent in
certain applications on a SCADA network. This goal was soundly reached and the result
is an easy to use tool that can gain root-level permissions on a SIXNET PLC or RTU.
With the exception of the Blinkenlights option, this tool set was designed to be very
general and accommodate just about every device running the Sixnet software suite.
6 Recommendations for Future Work
The next logical step for furthering this research would be to develop a method for
defending against the attacks used in this tool kit. Perhaps a middle-man device could
be created that can perform a deep-packet analysis on incoming packets to determine
if they are malicious. It may be possible to reject certain Sixnet Universal Protocol
commands based on the content of the data, whether the session and sequence numbers
align, or based on some outside criteria like time of day. These are all possibilities for
defending a Sixnet Tools type of attack.
