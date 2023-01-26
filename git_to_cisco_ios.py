'''
Copy Cisco IOS configs from git repo.
'''

import getopt
import subprocess
import sys
import tempfile
import serial

def device_connect(device_name, git_repo, git_user, tty_name):
    '''
    Clones the git repository, copies configuration to a list,
        and writes the confgiuration to the device.
    '''

    # Create temporary directory and change into it
    temporary_folder = tempfile.TemporaryDirectory()
    subprocess.call(
        f'cd {temporary_folder.name}',
        shell=True)

    # Clone Git Repo
    subprocess.call(
        f'git clone git@github.com:{git_user}/{git_repo}.git .',
        shell=True)

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

    '''
    Stores the help menu text
    '''

    menu = '''
    Git repo to Cisco IOS tool.

    Usage: python3 git_to_cisco_ios.py [options]
    
    Options:
    
    -h,--help=          Print this menu and exit.
    -n,--name=          Specify the name of the device to be used in <name>_config.txt
    -t,--tty=           The name of the device being used for the serial connection. (e.g. ttyUSB0)
    -g,--gituser=       The username belonging to the owner of the repo you would like to copy the configuration from.
    -r,--gitrepo=       The repository you would like to copy the configuration from.
    '''

    return menu

def main(argv):

    '''
    Takes in command line options and passes the commands to the device connection function.
    '''

    git_repo = ''
    git_user = ''
    tty_name = ''

    # Reads given command-line arguments
    try:
        opts, args = getopt.getopt(argv,'hn:t:g:r:',
                ['help',
                'name=',
                'tty=',
                'gituser=','gitrepo='])
    except getopt.GetoptError:
        print('That is not a recognized option. Please use -h or --help available options.')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help', ''):
            print(help_menu())
            sys.exit()
        elif opt in ('-n', '--name'):
            device_name = arg
        elif opt in ('-t', '--tty'):
            tty_name = arg
        elif opt in ('-g', '--gituser'):
            git_user = arg
        elif opt in ('-r', '--gitrepo'):
            git_repo = arg
    if not opts:
        print('No options were given. Please use -h or --help to see a list of available options.')
        sys.exit()

    device_connect(device_name, git_repo, git_user, tty_name)

if __name__ == '__main__':
    main(sys.argv[1:])
