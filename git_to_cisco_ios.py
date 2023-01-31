"Copy Cisco IOS configs from git repo."

import getopt
import subprocess
import sys
import tempfile
from netmiko import ConnectHandler
import serial

class MissingMandatoryOpt(Exception):
    "Raised when one or more mandatory options is missing."

def device_connect(device_name, git_repo, git_user, tty_name, serial_or_ssh, device):

    '''
    Clones the git repository.
    Copies configuration into a list.
    Writes the confgiuration to the device.
    '''

    # Create temporary directory and change into it
    temporary_folder = tempfile.TemporaryDirectory()
    subprocess.call(
        f'cd {temporary_folder.name}',
        shell=True
    )

    # Clone Git Repo
    subprocess.call(
        f'cd {temporary_folder.name} && git clone git@github.com:{git_user}/{git_repo}.git .',
        shell=True
    )

    if serial_or_ssh == 'serial':
        # Copy the config to a list containing each individual line
        with open(
            f'{temporary_folder.name}/{device_name}_config.txt', 'r', encoding='utf-8'
        ) as sw_config:
            conf_lines = sw_config.read()
        conf_list = conf_lines.split('\n')

        ser = serial.Serial(f'{tty_name}')
        ser.write(b'enable\r\nconfigure terminal\r\n')
        for line in conf_list:
            line_b = line.encode()
            ser.write(line_b + b'\r\n')
        ser.close()
    elif serial_or_ssh == 'ssh':
        # Connect to device
        net_connect = ConnectHandler(**device)
        net_connect.send_config_from_file(f'{temporary_folder.name}/{device_name}_config.txt')
        net_connect.disconnect()

    # Delete temporary directory
    temporary_folder.cleanup()


def help_menu():

    "Stores the help menu text"

    menu = '''
    Git repo to Cisco IOS tool.

    Usage: python3 git_to_cisco_ios.py [options]
    
    Options:
    
    -h  Print this menu and exit. 
    -n  Specify the name of the device to be used in <name>_config.txt
    -g  The username belonging to the owner of the repo you would like to copy the configuration from.
    -r  The repository you would like to copy the configuration from.
    -s  Declare whether you're using a serial or SSH connection (optional, default is serial).
        If using a serial connection:
            -t  The name of the device being used for the serial connection, e.g. ttyUSB0.
        If using an SSH connection:
            -d  The type of device being connected to. Default is 'cisco_ios' (Optional).
            -i  The IP address of the device you wish to connect to.
            -u  The username used to initiate the SSH connection.
            -p  The above user's password.
    '''

    return menu

def main(argv):

    '''
    Takes in command line options and passes the commands to the device connection function.
    '''

    # Device connection details
    device = {
        'device_type': 'cisco_ios',
        'host': '',
        'username': '',
        'password': ''
    }

    git_repo = ''
    git_user = ''
    tty_name = ''
    serial_or_ssh = 'serial'
    mandatory_options = ['-n', '-g', '-r']
    missing_options = []

    # Reads given command-line arguments
    # If a mandatory option is missing or none are given, exceptions are raised.
    try:
        opts, args = getopt.getopt(argv,'hn:g:r:s:t:d:i:u:p:')

        for opt, arg in opts:
            if opt in ('-h'):
                print(help_menu())
                sys.exit()
            if opt in ('-s'):
                if not arg.lower() in ('serial', 'ssh'):
                    print('When using the -s option, enter either "serial" or "ssh".')
                    sys.exit(2)
                else:
                    serial_or_ssh = arg.lower()
                    if serial_or_ssh == 'serial':
                        mandatory_options.append('-t')
                    elif serial_or_ssh == 'ssh':
                        new_opts = ['-i', '-u', '-p']
                        for i in new_opts:
                            mandatory_options.append(i)

        if not opts:
            print('No options were given. Please use -h to see a list of available options.')
            sys.exit(2)

        for option in mandatory_options:
            if (option not in [opt[0] for opt in opts]):
                missing_options.append(option)

        if missing_options:
            raise \
                MissingMandatoryOpt(f'Mandatory options are missing: {", ".join(missing_options)}')

    except getopt.GetoptError:
        print('That is not a recognized option. Please use -h to see a list of available options.')
        sys.exit(2)

    except MissingMandatoryOpt as err:
        print(f'{err}. Please use -h to see available options.')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-n'):
            device_name = arg
        elif opt in ('-t'):
            tty_name = arg
        elif opt in ('-g'):
            git_user = arg
        elif opt in ('-r'):
            git_repo = arg
        elif opt in ('-d'):
            device['device_type'] = arg
        elif opt in ('-i'):
            device['host'] = arg
        elif opt in ('-u'):
            device['username'] = arg
        elif opt in ('-p'):
            device['password'] = arg

    device_connect(device_name, git_repo, git_user, tty_name, serial_or_ssh, device)

if __name__ == '__main__':
    main(sys.argv[1:])
