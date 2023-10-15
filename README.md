# Cucumber test management system

Web app for managing cucumber tests. Tool gives opportunity to create projects and version instances related to git repositories and theirs commit and branches. It automatically pulls and parses .feature files from project repository and allows testers to mark what tests were passed or failed and write comments to this test cases.

Smart mode is a still developing tool that analyzes what tests are covered automatically and marks them.

## Building in docker:


* Make .env file in root:
```
DJANGO_SECRET_KEY=<Your Django secret key>
ADMIN_EMAIL=<Email of admin user>
ADMIN_PASSWORD=<Password of admin user>
```
[You can generate Django secret key here](https://djecrety.ir/)


* Build and run containers:

  `sudo docker-compose up --build -d`
