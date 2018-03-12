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

Environments
============

This project is set up to read environmental settings from your .env file.
Common configurable settings will be picked up from this file.

Development
-----------

To get started with your own configurable developer setup perform the following
commands:

```shell

cp ./.env.example .env
cp ./hydroshare/dev_settings.example.py ./hydroshare/dev_settings.py
```

Once these changes are made you can customize your development environment
within your dev_settings.py (which will not be added to git).

Deployment
----------

Deployments settings can also take advantage of dotenv based settings by
specifying any variables directly in a .env file.

You can also use the .env file to specify a different hydroshare-config.yaml
derived file (i.e., a production version).

The staging deployment configuration is configured this way and requires the
following steps to do a formal deploy:

 1. Any custom configuration is stored within `.env.staging.template.gpg`, a
    [gpg](https://www.gnupg.org/) encrypted file. Ask another developer or
    sysadmin for the password to edit this file.

 2. When Jenkins checks out a version of this project it will decrypt this file
    to `.env.staging.template`, and run it through the `envsubst` built-in linux
    command. This allows template files to pick up any environmental variables
    configured by the Jenkins system. The result is stored in `.env` in the
    deployed system, which is read by the Django app and hsctl script on startup.
