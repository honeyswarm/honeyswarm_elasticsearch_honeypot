# honeyswarm_elasticsearch
ElasticSearch Honeypot for HoneySwarm


There are some manual build steps in here. 
I may look at other ways to automate the build. Possible host the container tar on S3

Run the data import script

`python3.8 fake_data.py`

Jump in to the container and:

- Set the http.port to 4444 in config.elasticsearch.yml
- tar the config directory

`tar zcf elasticsearch.tar.gz /elasticsearch` 

Copy the container out

`docker cp reverent_curie:/usr/share/elasticsearch.tar.gz .`
