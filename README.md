# SyWorld
## Introduction
* SyWorld is (will be) a multi-platforms Synergy Software (Script). for now, just between windows
* Currently use UDP to transport data, it has an advantage of free from connection, but may lose some operation sequences under poor net conditions. File transport could be worse in such case.
* But it is very likely to be worked nicely under good net conditions.

## Installation
* ` $ git clone git@github.com:xhyumiracle/SyWorld.git`
* Need to install some packets which I haven't list them.

## Configuration
* Always modify ***conf.conf*** laying in the same dir with main module.
* left, right, down, up: ip addresses of for neighbours of your screen. '0' for disable (offline)

## Run
* cd into the dir of main entry file showed below (under Current Version), ***SyWorld New*** are recommended.
* make sure you correctly configured ***conf.conf*** in this dir.
* `$ python SyWorldNew_Windows.py` (or other version)
* launch SyWorld on another windows host.

## Current Version
### SyWorld New
* /SyWorld/SyWorldNew/SyWorldNew_Windows.py
* First multi files version, fixed some bugs when switching mouse between hosts

### SyWorld v5.0
* /SyWorld/stable_version/SyWorld_Windows_v5.0
* The last worked single file version.

***powered by python***
