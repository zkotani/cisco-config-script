# Cisco Config Script

This takes the existing script from GShuttleworth (https://github.com/GShuttleworth/Cisco-IOS-XE-config-to-Git) and expands on it to take command line arguments. This allows for backing up multiple switches simply and without rewriting the script between running the program.

This modified script also requires using SSH with git.

## Copying Configuration to Git Repo

```
Cisco IOS to git repo tool.

    Usage: python3 cisco_ios_to_git.py [options]
    
    Options:
    
    -h,--help=          Print this menu and exit.
    -n,--name=          Specify the name of the device to be used in <name>_config.txt
    -d,--devicetype     The type of device being connected to. Default is 'cisco_ios'.
    -i,--ip=            The IP address of the device you wish to connect to.
    -u,--user=          The username used to initiate the SSH connection.
    -p,--pass=          The above user's password.
    -g,--gituser=       The username belonging to the owner of the repo you would like to save the configuration to.
    -r,--gitrepo=       The repository you would like to save the configuration to.
    -c,--commit=        The commit message you would like to use. Wrap multi-word commit messages in single or double quotes.
```

## Copying Configuration from Git Repo

```
Git repo to Cisco IOS tool.

    Usage: python3 git_to_cisco_ios.py [options]
    
    Options:
    
    -h,--help=          Print this menu and exit.
    -n,--name=          Specify the name of the device to be used in <name>_config.txt
    -t,--tty=           The name of the device being used for the serial connection. (e.g. ttyUSB0)
    -g,--gituser=       The username belonging to the owner of the repo you would like to copy the configuration from.
    -r,--gitrepo=       The repository you would like to copy the configuration from.
```