#!/bin/bash

cd $REPO

docker build -t molo.servicedirectory .

#docker tag -f molo.servicedirectory <todo fill in url>

#docker push <todo fill in url>
