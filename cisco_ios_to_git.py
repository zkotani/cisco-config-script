"Copy Cisco IOS configs to git repo."

import getopt
import tempfile
import subprocess
import sys
from netmiko import ConnectHandler

class MissingMandatoryOpt(Exception):
    "Raised when one or more mandatory options is missing"

def device_connect(commit_message, device, device_name, git_repo, git_user):

    '''
    Connect to device and get device config.
    Clone git repo in temporary directory.
    Replace files with new config file and push changes back to git repo.
    '''

    # Connect to device
    net_connect = ConnectHandler(**device)

    # Run show command on device
    device_config = net_connect.send_command('show run')

    # Disconnect from Device
    net_connect.disconnect()

    # Create temporary directory and change into it
    temporary_folder = tempfile.TemporaryDirectory()
    subprocess.call(f'cd {temporary_folder.name}', shell=True)

    # Clone Git Repo
    subprocess.call(
        f'cd {temporary_folder.name} && git clone git@github.com:{git_user}/{git_repo}.git .',
        shell=True)
    subprocess.call(f'rm {device_name}_config.txt', shell=True)

    # Write all config to file
    with open(\
    f"{temporary_folder.name}/{device_name}_config.txt", 'w', encoding='utf-8') as outfile:
        outfile.write(device_config)

    # Git commit all changes
    subprocess.call(f"cd {temporary_folder.name} && git add -A", shell=True)
    subprocess.call(f"git commit -a -m '{commit_message}' && git push", shell=True)

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
    -d  The type of device being connected to. Default is 'cisco_ios'.
    -i  The IP address of the device you wish to connect to.
    -u  The username used to initiate the SSH connection.
    -p  The above user's password.
    -g  The username belonging to the owner of the repo you would like to save the configuration to.
    -r  The repository you would like to save the configuration to.
    -c  The commit message you would like to use. Wrap multi-word commit messages in single or double quotes.
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
    mandatory_options = ['-n', '-d', '-i', '-u', '-p', '-g', '-r', '-c']
    missing_options = []

    # Reads given command-line arguments
    # If mandatory options are missing or no options are given, exceptions are raised
    try:
        opts, args = getopt.getopt(argv,'hn:d:i:u:p:g:r:c:',)

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

    device_connect(commit_message, device, device_name, git_repo, git_user)

if __name__ == '__main__':
    main(sys.argv[1:])
