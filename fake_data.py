from elasticsearch import Elasticsearch

import random
from random import randint
from faker import Faker

fake = Faker()

es_host = "172.17.0.2"
es = Elasticsearch(es_host)

# OK so this is sales records

for i in range(2680):

    profile = fake.simple_profile()

    json_docs = {
        "full_name": profile['name'],
        "gender": profile['sex'],
        "email": profile['mail'],
        "billing_address": profile['address'],
        "EAN-8": [fake.ean8() for i in range(randint(1,6))],
        "credit_card_number": fake.credit_card_number(),
        "credit_card_expire": fake.credit_card_expire()
    }

    es.index(index="billing_details", doc_type="record", body=json_docs)
