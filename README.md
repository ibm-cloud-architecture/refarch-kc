# Reefer Container Shipment solution - EDA reference implementation

The IBM Event Driven architecture reference implementation solution illustrates the deployment of real time analytics on event streams in the context of container shipment in an [event driven architecture](https://ibm-cloud-architecture.github.io/refarch-eda) with event backbone, functions as service and event-driven microservices, and aims to illustrate the different event driven patterns like event sourcing, CQRS and Saga. There is a lot of content, so consider this to be a living book, for better reading experience go to [the BOOK view.](http://ibm-cloud-architecture.github.io/refarch-kc)

## TL;DR

If you want to just get the code, build and run we propose running locally with docker-compose.

To build and run the solution locally we are delivering some scripts which should help you to quickly get the solution cloned, built and deployed. Those bash scripts are under the `scripts` folder of this project.

```
git clone https://github.com/ibm-cloud-architecture/refarch-kc.git
```

```
cd refarch
./scripts/clone.sh
```

### Running locally with docker-compose

* Start Kafka, zookeeper and postgresql using: `./docker/startbackend.sh`
* Start the solution using the development settings: `docker-compose -f  

### Running in a local Kubernetes environment

The scripts provided in [`scripts/localk8s/`](./scripts/localk8s/) can be used to deploy to a local (vanilla) Kubernetes environment, such as a cluster provided by Docker Desktop.

Prereqs:
- Helm (Helm v3 is recommended),
- A Kubernetes cluster, and sufficient permissions to create namespaces, service accounts etc.

For more information, see the [README for the scripts](./scripts/localk8s/README.md).

### Building this booklet locally

The content of this repository is written with markdown files, built with Gatsby.  For more information, see the [README for the docs](./docs/README.md).

1. Install NodeJS (https://nodejs.org/)
2. `git clone https://github.com/ibm-cloud-architecture/refarch-kc.git` _(or your forked repository if you plan to edit)_
3. `cd refarch-kc/docs`
4. `npm install`
5. `npm run dev`
6. Go to `http://127.0.0.1:8000/` in your browser.

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

As this implementation solution is part of the Event Driven architecture reference architecture, the [contribution policies](./CONTRIBUTING.md) apply the same way here.

