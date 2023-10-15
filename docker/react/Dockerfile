FROM node:18.17.1

RUN mkdir /frontend
RUN mkdir /frontend/node_modules
RUN mkdir /frontend/react


WORKDIR /frontend


ADD ./test-management-system/frontend/package.json .
ADD ./test-management-system/frontend/package-lock.json .
ADD ./test-management-system/frontend/src/ .

RUN npm i webpack webpack-cli --save-dev
RUN npm i @babel/core babel-loader @babel/preset-env @babel/preset-react --save-dev
RUN npm i react react-dom --save-dev

ADD ./test-management-system/frontend/.babelrc .
ADD ./test-management-system/frontend/webpack.config.js .


ADD ./docker /app/docker
RUN chmod +x /app/docker/react/react-entrypoint.sh
