import sys, getopt
import tempfile
import subprocess
from netmiko import ConnectHandler

def main(argv):
    device_type = ''
    ip_address = ''
    username = ''
    password = ''
    git_user = ''
    git_repo = ''
    commit = ''

    opts, args = \
        getopt.getopt(argv,'hd:i:u:p:g:r:c:', \
            ['help','devicetype=','ipaddress=','username=','password=',
            'gituser=','gitrepo=','commit='])
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('Cisco IOS Config Script')
            print('-h Print this help menu')
            print('-d <devicetype>')
            print('-i <ipaddress>')
            print('-u <username>')
            print('-p <password>')
            print('-g <gituser>')
            print('-r <gitrepo>')
            print('-c <commit>')
            sys.exit()
        elif opt in ('-d', '--devicetype'):
            device_type = arg
        elif opt in ('-i', '--ipaddress'):
            ip_address = arg
        elif opt in ('-u', '--username'):
            username = arg
        elif opt in ('-p', '--password'):
            password = arg
        elif opt in ('-g', '--gituser'):
            git_user = arg
        elif opt in ('-r', '--gitrepo'):
            git_repo = arg
        elif opt in ('-c', '--commit'):
            commit = arg

    # Cisco IOS-XE connection details
    device = {
        'device_type': f'{device_type}',
        'host': f'{ip_address}',
        'username': f'{username}',
        'password': f'{password}',
    }
    # Git repository details
    git_repo_url = f'git@github.com:{git_user}/{git_repo}'
    commit_message = f'{commit}'


    # ------ Connect to device and get device config ------

    # Connect to IOS-XE device
    net_connect = ConnectHandler(**device)

    # Run show command on device
    device_config = net_connect.send_command('show run')

    # Disconnect from Device
    net_connect.disconnect()


    # ------ Clone git repo in temporary directory,
    # replace files with new config file and push changes back to git repo  ------

    # Create temporary directory
    temporary_folder = tempfile.TemporaryDirectory()

    # Clone Git Repo
    subprocess.call(
        f'cd {temporary_folder.name} && git clone {git_repo_url} . && rm *.*', shell=True
    )

    # Write all config to file
    with open(f"{temporary_folder.name}/{device['host']}_config.txt", 'w', encoding='utf-8') \
        as outfile:
        outfile.write(device_config)

    # Git commit all changes
    subprocess.call(
        f"cd {temporary_folder.name} && git add -A && git commit -a -m '{commit_message}' && git push",
        shell=True,
    )

    # Delete temporary directory
    temporary_folder.cleanup()

if __name__ == '__main__':
    main(sys.argv[1:])
