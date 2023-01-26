# Cisco Config Script

## Introduction

This takes the existing script from GShuttleworth (https://github.com/GShuttleworth/Cisco-IOS-XE-config-to-Git) and expands on it to take command line arguments. This allows for backing up multiple switches simply and without rewriting the script between running the program.

This modified script also requires using SSH with git.

## Arguments

```
-h Print this help menu
    --help
-n '<devicename>'
    --devicename='<devicename>'
-d '<devicetype>'
    --devicetype='<devicetype>'
-i '<ipaddress>'
    --ipaddress='<ipaddres>'
-u '<username>'
    --username='<username>'
-p  '<password>'
    --password='<password>'
-g '<gituser>'
    --gituser='<gituser>'
-r '<gitrepo>'
    --gitrepo='<gitrepo>'
-c '<commit>'
    --commit='<commit>'
```

## In Progress

Currently developing a script to write configurations to a Cisco IOS device. First will utilize a serial connection but planning on expanding to allow for using SSH for devices which have SSH enabled.