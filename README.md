### Nightly Build Status (develop branch)

| Workflow | Clean | Build/Deploy | Unit Tests | Flake8
| :----- | :--- | :--- | :-------- | :------------ | :----------- |
| [![Build Status](http://ci.myhpom.renci.org:8080/job/nightly-build-workflow/badge/icon?style=plastic)](http://ci.myhpom.renci.org:8080/job/nightly-build-workflow/) | [![Build Status](http://ci.myhpom.renci.org:8080/job/nightly-build-clean/badge/icon?style=plastic)](http://ci.myhpom.renci.org:8080/job/nightly-build-clean/) | [![Build Status](http://ci.myhpom.renci.org:8080/job/nightly-build-deploy/badge/icon?style=plastic)](http://ci.myhpom.renci.org:8080/job/nightly-build-deploy/) | [![Build Status](http://ci.myhpom.renci.org:8080/job/nightly-build-test/badge/icon?style=plastic)](http://ci.myhpom.renci.org:8080/job/nightly-build-test/) | [![Build Status](http://ci.myhpom.renci.org:8080/job/nightly-build-flake8/badge/icon?style=plastic)](http://ci.myhpom.renci.org:8080/job/nightly-build-flake8/) |

Build generate by [Jenkins CI](http://ci.myhpom.renci.org:8080)

### requires.io
[![Requirements Status](https://requires.io/github/SoftwareResearchInstitute/MyHPOM/hs_docker_base/requirements.svg?branch=develop)](https://requires.io/github/SoftwareResearchInstitute/MyHPOM/hs_docker_base/requirements/?branch=master)

MyHPOM
============

MyHPOM is a collaborative website being developed for better management of personal health and healthcare information. MyHPOM is derived directly from the NSF-funded 3-clause BSD [HydroShare open source codebase](https://github.com/hydroshare/hydroshare), NSF awards [1148453](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1148453) and [1148090](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1148090). MyHPOM provides the sustainable technology infrastructure needed to address planning and communicating important information about your future healthcare wishes to those closest to you and those who provide medical care to you.

If you want to contribute to MyHPOM, please see the [MyHPOM Wiki](https://github.com/SoftwareResearchInstitute/MyHPOM/wiki/).

More information can be found in the [MyHPOM Wiki](https://github.com/SoftwareResearchInstitute/MyHPOM/wiki/).

Development
===========

There are very good instructions on the [hydroshare
wiki](https://github.com/hydroshare/hydroshare/wiki/getting_started) to set up a
local dev environment that matches production.

If you have docker installed locally, you can use `hsctl` commands to setup a
local development environment without VirtualBox.

*OS X Users* note that `hsctl` requires gnu sed. You can use
[homebrew](https://brew.sh) to install it as the default using the following
command: `brew install gnu-sed --with-default-names`.

Environments
------------

This project extends the hydroshare configuration by allowing one to override
settings from a .env file. Most common configurable settings will be picked up
from this file.

In local development one can override local settings by copying a local .env
template and customizing it:

```shell

cp ./.env.example .env
cp ./hydroshare/dev_settings.example.py ./hydroshare/dev_settings.py
```

Deployments settings can also take advantage of dotenv based settings by
specifying any variables directly in a .env file.

The .env file can also specify a different hydroshare-config.yaml
derived file (i.e., a production version).
