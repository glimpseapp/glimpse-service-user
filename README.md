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
kc delete deployment glimpse-service-user
kc delete service glimpse-service-user
kc create -f container-engine.yaml
```



Run locally
-----------
```docker run -p 5000:80 glimpse-service-user```


