# Pre-requisites

To be able to build and execute the solution, you need to do the following tasks:

## Get a Git client

If not already done, get a git client. See the following [installation instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git). 

On a Centos box we did:

```
yum install git
```

## Clone all the repositories


```
git clone https://github.com/ibm-cloud-architecture/refarch-kc/
```

Open a terminal window and go to the `refarch-kc` folder.

Use the command:
```
./script/clone.sh
``` 

to get all the solution repositories. You should have at least the following repositories:

```
refarch-kc-container-ms
refarch-kc-order-ms
refarch-kc-ui
refarch-kc
refarch-kc-ms
refarch-kc-streams
```


## Get docker

Get [docker engine and install](https://docs.docker.com/install/) it (if not done yet.) To verify docker runs fine use the command `docker version`. We run on v19.03 community edition.

or use one of the packaged solution like on Centos

```
yum install docker
```

## Verifying current environment

To assess the tools installed on your computer, run the following command under the `refarch-kc` project:

```
./scripts/prepareEnv
```

The script will create the docker images for maven, nodejs, and python if those tools are not found on your computer. 

```
docker images
```

```
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
ibmcase/python      latest              8d38aefd0346        2 minutes ago       1.14 GB
ibmcase/nodetools   latest              7a736a07ba09        2 minutes ago       959 MB
ibmcase/javatools   latest              bdf79f64d721        23 minutes ago      715 MB

```

You to have two choices to build the solution: 

1. installing node, python and maven on your computer
1. use our own docker images for running those tools. 

You can mix too, if for example you already developed in the past with Nodejs or Java you may want to leverage your own configurations. If you do not want to impact your python environment, you can user our docker images. 

To be able to build without our docker images do the following:

## Get Java

Do something like this:

```
yum install java-1.8.0-openjdk-devel
```

## Get Maven

get [maven](https://maven.apache.org/install.html) and add it to your PATH.

or for a Centos linux:

```
yum install maven
```

## Get nodejs

Get [node and npm](https://nodejs.org/en/)

or for a Centos linux:

```
yum install node
```


## Get Python 3.7

Most of our integration tests are done in python. To avoid impacting your own python environment, we defined a docker file to build an image with the necessary python library. The image may have been already built with the `preparenv` script.

If you want to rebuild it, go to the `docker` folder and run the following command: 
```
docker build -f docker-python-tools -t ibmcase/python .
```

## Global environment settings

In the `refarch-kc` rename `./script/setenv.sh.tmpl` to `./script/setenv.sh`:

```
mv setenv.sh.tmpl setenv.sh
```

Then modify the environment variables according to your settings. This file is used by a lot of scripts in the solution to set the target deployment environment: LOCAL, IBMCLOUD, ICP, MINIKUBE.
