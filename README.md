Glimpse Service User
====================

This service is responsible to write and read the user information into the database


Install
-------
Install virtualenv and python dependencies
```
virtualenv -p python3 venv
. venv/bin/activate
```


Deploy
------
Build docker image and push to Google container registry
```
docker build -t gcr.io/glimpse-123456/glimpse-service-user .
gcloud docker -- push gcr.io/glimpse-123456/glimpse-service-user
```
*Note: the the*


*Update openapi.yaml and deploy*
```gcloud service-management deploy openapi.json```

After you run the command above get the CONFIG_ID of the service you just deployed, it looks something like 2017-08-10r6. 
Add the CONFIG_ID to the kube-deployment.yaml into the -v argument:
```
      - name: esp
        image: gcr.io/endpoints-release/endpoints-runtime:1
        args: [
          "-p", "8081",
          "-a", "127.0.0.1:5000",
          "-s", "glimpse-service-user.endpoints.glimpse-123456.cloud.goog",
          "-v", "[CONFIG_ID]",
        ]
``` 

*Update kubernetes file and deploy*
```
kubectl apply -f kube-deployment.yaml
kubectl apply -f kube-service.yaml
```


Run locally
-----------
```docker run -p 5000:80 gcr.io/glimpse-123456/glimpse-service-user```

You may have also to port forward the services used by this microservice e.g.:
```
kubectl get pod
kubectl port-forward [CASSANDRA_POD_NAME] 9042:9042
```


