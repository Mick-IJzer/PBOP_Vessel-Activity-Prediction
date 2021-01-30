# Information for how to run the Dashboard application

Navigate to: 

`cd .../Robin1/Dashboard/`

Build docker image:

`docker build -t dss_robin1 .`

Run docker container:

`docker run -p {available port*}:2021 --name dss_robin1 dss_robin1`

Open the application in your browser:

`localhost:{available port*}`

\* available port means a port on which you want the docker container to run on your machine. In our case this was 2021, but in the case you already have something running on this port, you can choose a different port. So in the case port 2021 is still available on your localhost, use the following commands to run the docker container:
`docker run -p 2021:2021 --name dss_robin1 dss_robin1`