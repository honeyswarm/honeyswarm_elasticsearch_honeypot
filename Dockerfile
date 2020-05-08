FROM docker.elastic.co/elasticsearch/elasticsearch:7.6.2
ENV discovery.type=single-node
ENV cluster.name=sales_records

RUN yum install -y python3 python3-pip
RUN python3 -m pip install hpfeeds requests aiohttp

ADD --chown=elasticsearch:elasticsearch elasticsearch.tar.gz /usr/share/

ADD prox.py /opt/prox.py
ADD startup.sh /opt/startup.sh

CMD ["/bin/bash", "/opt/startup.sh"]