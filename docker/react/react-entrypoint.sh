#!/bin/sh

cd /frontend

npm run docker

until cd /staticfiles
do
    echo "Waiting for static"
    sleep 2
done


if [ -d /staticfiles/react ]; then
  rm  /staticfiles/react/*
else
  mkdir /staticfiles/react
fi

mv /frontend/react/main.js /staticfiles/react/