# Container Shipment Analysis
From the design thinking workshop we extracted the following artifacts:
* a persona list: We develop personas for each of the business stakeholders to better understand their work environment, motivations and challenges.  Personas helps to capture the decisions and questions that these stakeholders must address with respect to the targeted key business initiative.

Persona name | Objectives | Challenges
--- | --- | ---
Retailer |Receive shipped goods on time, on date contracted with manufacturer |
Manufacturer |Good enough estimates of shipment times from Shipment Company to close sale and delivery with Retailer<br>Pickup of containers by land transporter <br>Timely delivery of container to Retailer as contracted with Shipment company<br>able to get information on current locatbr>ion and state of container in transit|   
Shipment Company |Provide good enough estimates of shipment time to close shipment contract with Manufacturer<br>Execute shipment contracts on time profitably ( with minimal cost)|Limited itinerary schedule<br>variability in ship leg travel times and costs<br>variability in port congestion and load / unload times at dock <br> variability in Land transport timings 
Land Transporter | |
Port Docker | |
Customs Office| |

* the MVP hills
* At the high level the shipment process flow can be presented in the diagram below:

![](shipment-bp.png)



### Step 1: Domain Events
From the business context description above, we started the [Event Storming](https://github.com/ibm-cloud-architecture/refarch-eda/blob/master/docs/methodology/readme.md) Analysis to build the following events timeline. The process start with a request for quote so a `delivery estimate time and cost requested` event occurs.

<img src="ship-dom-evt1.png" width="700">

Three swim lanes were quickly added to the model, after the event storming activity so we can organize event sequencing and parallelism.

<img src="ship-dom-evt2.png" width="700">

<img src="ship-dom-evt3.png" width="700">

<img src="ship-dom-evt4.png" width="700">

<img src="ship-dom-evt5.png" width="700">

<img src="ship-dom-evt6.png" width="700">

<img src="ship-dom-evt7.png" width="700">


### Step 2: Commands

<img src="ship-dom-cmd1.png" width="700">

The above figure can be alterred using event flow:

<img src="ship-dom-cmd1.2.png" width="700">

<img src="ship-dom-cmd2.png" width="700">

<img src="ship-dom-cmd3.png" width="700">

<img src="ship-dom-cmd4.png" width="700">

### Step 3: Aggregates

<img src="ship-aggr-transport-quote.png" width="700">

<img src="ship-aggr-shipment.png" width="700">

<img src="ship-aggr-transp.png" width="700">

### Step 4: Business context

### Step 5: Data
