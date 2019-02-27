# K Container Shipment EDA reference implementation

The IBM Event Driven architecture reference implementation illustrates the deployment of real time analytics on event streams in the context of container shipment in an [event driven architecture](https://github.com/ibm-cloud-architecture/refarch-eda) with event backbone, functions as service and microservices, and aims to illustrate the different event driven patterns like event sourcing, CQRS and Saga.

To read the detail of this implementation go to [the book view](http://ibm-cloud-architecture.github.io/refarch-kc)

### Using the scripts for this root project

We are delivering some scripts that could help to quickly get the solution cloned, built and deploy locally. Those bash tools are under the 'scripts` folder.

* To clone all the related projects: `./scripts/clone.sh`
* To assess your environment and build the docker images needed for build: `./scripts/prepareEnv`.
* If you want to build a docker image so you do not need to install Java and Maven (This image will be used in the build of all the java based projects). Use the following commands under the `scripts` folder (prepareEnv shell script does it too):

```
$ docker build -t ibmcase/javatools -f docker-java-tools .
$ ./imageStatus 
> ibmcase/javatools    latest       6c85964f2385     4 seconds ago  563MB
```
* If you want to build a docker image so you do not need to install angular CLI, nodejs and npm last version, (prepareEnv shell script does it too) you can do:
```
$ docker build -t ibmcase/nodetools -f docker-node-tools .
$ ./imageStatus
> ibmcase/nodetools     latest     5bfbc87c143d     30 seconds  ago     1GB
```
* To build all the related projects: `buildAll`
* To validate all services run correctly, execute the `smokeLocalTests` scripts.


### Building this booklet locally

The content of this repository is written with markdown files, packaged with [MkDocs](https://www.mkdocs.org/) and can be built into a book-readable format by MkDocs build processes.

1. Install MkDocs locally following the [official documentation instructions](https://www.mkdocs.org/#installation).
2. `git clone https://github.com/ibm-cloud-architecture/refarch-kc.git` _(or your forked repository if you plan to edit)_
3. `cd refarch-kc`
4. `mkdocs serve`
5. Go to `http://127.0.0.1:8000/` in your browser.

### Pushing the book to GitHub Pages

1. Ensure that all your local changes to the `master` branch have been committed and pushed to the remote repository.
   1. `git push origin master`
2. Ensure that you have the latest commits to the `gh-pages` branch, so you can get others' updates.
	```bash
	git checkout gh-pages
	git pull origin gh-pages
	
	git checkout master
	```
3. Run `mkdocs gh-deploy` from the root refarch-kc directory.

--- 

## Contribute

As this implementation solution is part of the Event Driven architeture reference architecture, the [contribution policies](./CONTRIBUTING.md) apply the same way here.

**Contributors:**
* [Jerome Boyer](https://www.linkedin.com/in/jeromeboyer/)
* [Martin Siegenthaler](https://www.linkedin.com/in/martin-siegenthaler-7654184/)
* [David Engebretsen](https://www.linkedin.com/in/david-engebretsen/)
* [Francis Parr](https://www.linkedin.com/in/francis-parr-26041924)
* [Hemankita Perabathini](https://www.linkedin.com/in/hemankita-perabathini/)

Please [contact me](mailto:boyerje@us.ibm.com) for any questions.
