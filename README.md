# Recruiter #

Recruiter is an application for finding jobs and hiring employees.


### Building local Docker image ###

To start build - run in the project directory:
```
$ docker-compose build
```

To run the containers:
```
$ docker-compose up
```

### Deploying ###

Build image for deploy:
```
$ docker build -t squareballoon.com:5000/recruiter .
```

You have to be logged in to private Docker registry(only have to do it once):
```
$ docker login squareballoon.com:5000
```

Push this image to private registry:
```
$ docker push squareballoon.com:5000/recruiter
```

SSH on private server and run the following commands there:
```
$ docker pull squareballoon.com:5000/recruiter
$ sudo systemctl restart recruiter
```
