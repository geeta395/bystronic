# debian package icpdataprocessor
Generates .deb package with a venv for Python 3.9.2.
Purpose: Edge application on ByBrain to process Python files in the contect of ICP (intelligent cutting process).
See documentation inside `src/topics/*/doc`.



## Description

Package contains

* `setup` to create the `.deb` package for the deployment to the target system (ByBrain)
* `src` that is used
  * To train NN-modles (that are also contained in `resources`fodlers)
  * To be run to inference on target system

| What                                  | Description | Depoly |
| ------------------------------------- | ------------ | ------------ |
| `setup`                               | Deployment infrastructure |              |
| `setup/requirements.txt`              | Defines packages for pip / virtual environment on target system. |   |
| `setup/deb`                           | Defines .deb package using debhelper. |              |
| `src/log`                             | Soft-link for logger | x |
| `src/work`                            | Soft-link for temporal files | x |
| `src/resource/config.json`     | Configuration (e. g. mqtt-client) |              |
| `src/main.py`                         | Entry point for systemd | x |
| `src/test.py`                         | Entry point for test routines. Executed in docker before creating .deb | ? |
| `src/modules`                         | mqtt-client, azure-uploader, ... | x |
| `src/tools` | Methods to work on data like uploader of a folder... |  |
| `src/topics`                          | Different use cases are represented as topics with similar a structure | x |
| `src/topics/newTopic`                   | Structure/template for a new topic |              |
| `src/topics/newTopic/doc`                      | Describe topic |              |
| `src/topics/newTopic/machine`                  | Main routines on target system | x |
| `src/topics/newTopic/common`                   | Shared files, used on `machine` and during `training` | x |
| `src/topics/newTopic/common/resources`       | Models, config files, ... | x |
| `src/topics/newTopic/training`                 | MLOps is a set of practices that aims to deploy and maintain machine learning models in production reliably and efficiently.<br />Please use different place for training data. |              |
| `src/topics/newTopic/test`                     | Do a representative test for that topic |  |
| `src/topics/loc`                      | First topic `loc` is used to process the dumpLossOfCutDetected | x |
| `src/topics/nozzleControl` |  |  |



### Description of debhelper package

| What                                         | Location                                                     |
| -------------------------------------------- | ------------------------------------------------------------ |
| Python venv                                  | `/opt/bystronic/venvs/icpdataprocessor`                      |
| Working folder                               | `/opt/bystronic/icpdataprocessor/work` points to persistent folder `/opt/data/bystronic/icpdataprocessor/work` |
| Logging folder, link                         | `/opt/bystronic/icpdataprocessor/log` points to persistent folder `/opt/data/bystronic/icpdataprocessor/log` |
| Python source code                           | `/opt/bystronic/icpdataprocessor/src`                        |
| Service `icpdataprocessor`                   | `(/usr)/lib/systemd/system/icpdataprocessor.service`         |
| Config for service to configure **Proxy**... | `/opt/bystronic/icpdataprocessor/icpdataprocessor.conf`      |



## Docker container

### Setup container

``` bash
# replace lcfa by different user :-)
sudo usermod -aG docker lcfa
# go to folder with Dockerfile 
sudo docker build -t debian-python-create-deb .
# mount folder icpdataprocessor
sudo docker run --name icpDataProcessorCnt_lcfa -it --rm -v /home/lcfa/:/mnt debian-python-create-deb
```



### Test a package from docker

`python3 src/tests.py`




### Build a package from docker

``` bash
# after docker has started, navigate to the setup/deb folder:
cd mnt/.../setup/deb
dpkg-buildpackage -us -uc
# when finished (~10min) the generated files can be found in the setup folder
```
