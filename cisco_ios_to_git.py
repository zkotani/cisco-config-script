'''
Copy Cisco IOS configs to git repo.
'''

import getopt
import tempfile
import subprocess
import sys
from netmiko import ConnectHandler

# Define global variables

def device_connect(commit_message,
                    device, device_name,
                    git_repo, git_user):

    '''
    Connect to device and get device config.
    Clone git repo in temporary directory,
        replace files with new config file and push changes back to git repo
    '''

    # Connect to device
    net_connect = ConnectHandler(**device)

    # Run show command on device
    device_config = net_connect.send_command('show run')

    # Disconnect from Device
    net_connect.disconnect()

    # Create temporary directory and change into it
    temporary_folder = tempfile.TemporaryDirectory()
    subprocess.call(
        f'cd {temporary_folder.name}',
        shell=True
    )

    # Clone Git Repo
    subprocess.call(
        f'cd {temporary_folder.name} && git clone {git_repo_url} . && rm {device_name}_config.*', shell=True
    )

    # Write all config to file
    with open(f"{temporary_folder.name}/{device_name}_config.txt", 'w', encoding='utf-8') \
        as outfile:
        outfile.write(device_config)

    # Git commit all changes
    subprocess.call(
        f"cd {temporary_folder.name} && git add -A",
        shell=True
    )
    subprocess.call(
        f"git commit -a -m '{commit_message}' && git push",
        shell=True
    )

    # Delete temporary directory
    temporary_folder.cleanup()

def help_menu():

    '''
    Stores the help menu text
    '''

    menu = '''Cisco IOS to git repo tool.
    Usage: python3 cisco_ios_to_git.py [options]
    
    Options:'''

    return menu

def main(argv):

    '''
    Takes in command line options and connects to given Cisco IOS device.
    Copies the running configuration to a variable.
    Creates a temporary directory and clones the given git repo.
    Writes the configuration to the given device name's file.
    Pushes the git repo with the given commit message.
    '''

    # Device connection details
    device = {
        'device_type': 'cisco_ios',
        'host': '0.0.0.0',
        'username': 'username',
        'password': 'password'
    }

    commit_message = ''
    git_repo = ''
    git_user = ''
    device_name = ''

    # Reads given command-line arguments
    opts, args = getopt.getopt(argv,'hn:d:i:u:p:g:r:c:',
            ['help',
            'name=',
            'device=',
            'ip=',
            'user=','pass=',
            'gituser=','gitrepo=',
            'commit='])
    for opt, arg in opts:
        if opt in ('-h', '--help', ''):
            print(help_menu())
            sys.exit()
        elif opt in ('-n', '--name'):
            device_name = arg
        elif opt in ('-d', '--device'):
            device['device_type'] = arg
        elif opt in ('-i', '--ip'):
            device['ip_address'] = arg
        elif opt in ('-u', '--user'):
            device['username'] = arg
        elif opt in ('-p', '--pass'):
            device['password'] = arg
        elif opt in ('-g', '--gituser'):
            git_user = arg
        elif opt in ('-r', '--gitrepo'):
            git_repo = arg
        elif opt in ('-c', '--commit'):
            commit_message = arg
        else:
            sys.exit()

    device_connect(commit_message,
                    device, device_name,
                    git_repo, git_user)

if __name__ == '__main__':
    main(sys.argv[1:])
