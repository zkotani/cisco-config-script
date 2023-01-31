"Copy Cisco IOS configs to git repo."

# https://stackoverflow.com/questions/16077912/
    #  python-serial-how-to-use-the-read-or-readline-function-to-read-more-than-1-char

import getopt
import io
import tempfile
import subprocess
import sys
from netmiko import ConnectHandler
import serial

class MissingMandatoryOpt(Exception):
    "Raised when one or more mandatory options is missing"

def device_connect(commit_message, device, device_name, git_repo, git_user, serial_or_ssh, tty_name):

    '''
    Connect to device and get device config.
    Clone git repo in temporary directory.
    Replace files with new config file and push changes back to git repo.
    '''

    if serial_or_ssh in 'ssh':
        # Connect to device
        net_connect = ConnectHandler(**device)

        # Run show command on device
        device_config = net_connect.send_command('show run')

        # Disconnect from Device
        net_connect.disconnect()
    elif serial_or_ssh == 'serial':
        ser = serial.Serial(f'{tty_name}')
        sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
        sio.write(str('echo "hello"\n'))
        # sio.flush()
        x = sio.readline()
        print(x)
        print(x == str("hello"))
        sys.exit()

    # Create temporary directory and change into it
    temporary_folder = tempfile.TemporaryDirectory()
    subprocess.call(f'cd {temporary_folder.name}', shell=True)

    # Clone Git Repo
    subprocess.call(
        f'cd {temporary_folder.name} && git clone git@github.com:{git_user}/{git_repo}.git .',
        shell=True
    )
    subprocess.call(f'rm {temporary_folder.name}/{device_name}_config.txt', shell=True)

    # Write all config to file
    with open(
        f"{temporary_folder.name}/{device_name}_config.txt", 'w', encoding='utf-8'
    ) as outfile:
        outfile.write(device_config)

    # Git commit all changes
    subprocess.call(
        f"cd {temporary_folder.name} && git add -A",
        shell=True
    )
    subprocess.call(
        f"cd {temporary_folder.name} && git commit -a -m '{commit_message}' && git push",
        shell=True
    )

    # Delete temporary directory
    temporary_folder.cleanup()

def help_menu():

    "Stores the help menu text"

    menu = '''
    Cisco IOS to git repo tool.

    Usage: python3 cisco_ios_to_git.py [options]
    
    Options:
    
    -h  Print this menu and exit.
    -n  Specify the name of the device to be used in <name>_config.txt
    -g  The username belonging to the owner of the repo you would like to save the configuration to.
    -r  The repository you would like to save the configuration to.
    -c  The commit message you would like to use. Wrap multi-word commit messages in single or double quotes.
    -s  Declare whether you're using a serial or SSH connection (optional, default is ssh).
        If using an SSH connection:
            -d  The type of device being connected to. Default is 'cisco_ios' (Optional)
            -i  The IP address of the device you wish to connect to.
            -u  The username used to initiate the SSH connection.
            -p  The above user's password.
        If using a serial connection:
            -t  The name of the device being used for the serial connection, e.g. ttyUSB0.
    '''

    return menu

def main(argv):

    "Takes in command line options and passes the commands to the device connection function."

    # Device connection details
    device = {
        'device_type': 'cisco_ios',
        'host': '',
        'username': '',
        'password': ''
    }

    commit_message = ''
    git_repo = ''
    git_user = ''
    device_name = ''
    tty_name = ''
    serial_or_ssh = 'ssh'
    mandatory_options = ['-n', '-g', '-r', '-c']
    missing_options = []

    # Reads given command-line arguments
    # If mandatory options are missing or no options are given, exceptions are raised
    try:
        opts, args = getopt.getopt(argv,'hn:g:r:c:s:d:i:u:p:t:',)

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
            sys.exit()

        for option in mandatory_options:
            if (option not in [opt[0] for opt in opts]):
                missing_options.append(option)

        if missing_options:
            raise \
                MissingMandatoryOpt(f'Mandatory options are missing: {", ".join(missing_options)}')

    except getopt.GetoptError:
        print('That is not a recognized option. Please use -h to see available options.')
        sys.exit(2)

    except MissingMandatoryOpt as err:
        print(f'{err}. Please use -h to see available options.')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-n'):
            device_name = arg
        elif opt in ('-d'):
            device['device_type'] = arg
        elif opt in ('-i'):
            device['host'] = arg
        elif opt in ('-u'):
            device['username'] = arg
        elif opt in ('-p'):
            device['password'] = arg
        elif opt in ('-g'):
            git_user = arg
        elif opt in ('-r'):
            git_repo = arg
        elif opt in ('-c'):
            commit_message = arg
        elif opt in ('-t'):
            tty_name = arg

    device_connect(commit_message, device, device_name, git_repo, git_user, serial_or_ssh, tty_name)

if __name__ == '__main__':
    main(sys.argv[1:])
