"Copy Cisco IOS configs from git repo."

import getopt
import subprocess
import sys
import tempfile
import serial

class MissingMandatoryOpt(Exception):
    "Raised when one or more mandatory options is missing."

def device_connect(device_name, git_repo, git_user, tty_name):

    '''
    Clones the git repository.
    Copies configuration into a list.
    Writes the confgiuration to the device.
    '''

    # Create temporary directory and change into it
    temporary_folder = tempfile.TemporaryDirectory()
    subprocess.call(f'cd {temporary_folder.name}', shell=True)

    # Clone Git Repo
    subprocess.call(f'git clone git@github.com:{git_user}/{git_repo}.git .', shell=True)

    # Copy the config to a list containing each individual line
    with open(f'{device_name}', 'r', encoding='utf-8') as sw_config:
        conf_lines = sw_config.read()
    conf_list = conf_lines.split('\n')

    # Delete temporary directory
    temporary_folder.cleanup()

    ser = serial.Serial(f'/dev/{tty_name}')
    ser.write(b'enable\r\nconfigure terminal\r\n')

    for line in conf_list:
        line_b = line.encode()
        ser.write(line_b + b'\r\n')

    ser.close()


def help_menu():

    "Stores the help menu text"

    menu = '''
    Git repo to Cisco IOS tool.

    Usage: python3 git_to_cisco_ios.py [options]
    
    Options:
    
    -h  Print this menu and exit.
    -n  Specify the name of the device to be used in <name>_config.txt
    -t  The name of the device being used for the serial connection. (e.g. ttyUSB0)
    -g  The username belonging to the owner of the repo you would like to copy the configuration from.
    -r  The repository you would like to copy the configuration from.
    '''

    return menu

def main(argv):

    '''
    Takes in command line options and passes the commands to the device connection function.
    '''

    git_repo = ''
    git_user = ''
    tty_name = ''
    mandatory_options = ['-n', '-t', '-g', '-r']
    missing_options = []

    # Reads given command-line arguments
    # If a mandatory option is missing or none are given, exceptions are raised.
    try:
        opts, args = getopt.getopt(argv,'hn:t:g:r:')

        for opt, arg in opts:
            if opt in ('-h'):
                print(help_menu())
                sys.exit()

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

    device_connect(device_name, git_repo, git_user, tty_name)

if __name__ == '__main__':
    main(sys.argv[1:])
