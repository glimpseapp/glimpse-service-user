Glimpse Service User
====================

This service is responsible to write and read the user information into the database


Deploy
------
Build docker image and push to Google container registry
```
docker build -t gcr.io/glimpse-123456/glimpse-service-user .
gcloud docker -- push gcr.io/glimpse-123456/glimpse-service-user
```
*Note: the the*


*Update openapi.yaml and deploy*
```gcloud service-management deploy openapi.yaml```

*Update kubernetes file and deploy*
```
kc apply -f kube-deployment.yaml
kc apply -f kube-service.yaml
```



Run locally
-----------
```docker run -p 5000:80 gcr.io/glimpse-123456/glimpse-service-user```


