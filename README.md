# bts-ce-reports

Boda Telecom Suite Reporting Services. This runs scheduled reports, sends emails, generates downloads in different formats

## Built With
- [Python](https://www.python.org)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/)

## Running docker container manually

### Gitlab container registry
```
docker run \
--name bts-ce-reports \
-e BTS_DB_HOST='192.168.99.100' \
-e BTS_DB_NAME='bts' \
-e BTS_DB_USER='bodastage' \
-e BTS_DB_PASS='password' \
-e BTS_DB_PORT='5432' \
\
-e BTS_MQ_HOST='192.168.99.100' \
-e BTS_MQ_NAME='generate_reports' \
-e BTS_MQ_USER='btsuser' \
-e BTS_MQ_PASS='Password@7' \
-e BTS_MQ_VHOST='/bs' \
-v `pwd`:/app \
registry.gitlab.com/bts-ee/bts-ee-reports
```

## Resources

* [Online Documentation](http://docs.bodastage.com)

## Copyright / License
Copyright 2017 - 2019 [Bodastage Solutions](http://www.bodastage.com)

Licensed under the Apache License, Version 2.0 ; you may not use this work except in compliance with the License. You may obtain a copy of the License in the LICENSE file, or at:

https://www.apache.org/licenses/LICENSE-2.0
