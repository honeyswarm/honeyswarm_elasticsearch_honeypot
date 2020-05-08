#!/usr/bin/python3.8
import os
import json
import aiohttp
import asyncio
import logging
import pprint

from asyncio import wait_for
from aiohttp import web
from aiohttp import client
from hpfeeds.asyncio import ClientSession

HPFSERVER = os.environ.get("HPFSERVER", "172.17.0.1")
HPFPORT = int(os.environ.get("HPFPORT", 20000))
HPFIDENT = os.environ.get("HPFIDENT", "5eb54b585884bc3c412c7e11")
HPFSECRET = os.environ.get("HPFSECRET", "5eb54b585884bc3c412c7e11")
HIVEID = os.environ.get("HIVEID", "UnknownHive")

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Credit for the base of this goes to a stackoverflow question i need to find. 

baseUrl = 'http://0.0.0.0:4444'

async def hpfeeds_publish(event_message):
    async with ClientSession(HPFSERVER, HPFPORT, HPFIDENT, HPFSECRET) as client:
        client.publish('elastic.sessions', json.dumps(event_message).encode('utf-8'))
    return True

async def handler(request):

    # Write the log entry before we sort the response as thats more important


    # Get HTTP as version string
    http_version = "HTTP/{0}.{1}".format(request.version.major, request.version.minor)

    # convert Cookies to a standard dict, We will loose Duplicates
    http_cookies = {}
    for k, v in request.cookies.items():
        http_cookies[k] = v

    # convert Headers to a standard dict, We will loose Duplicates
    http_headers = {}
    for k, v in request.headers.items():
        http_headers[k] = v

    # convert POST to a standard dict, We will loose Duplicates
    http_post = {}
    if request.method == 'POST':
        data = await request.post()
        for key, value in data.items():
            http_post[key] = value

    event_message = {
        "hive_id": HIVEID,
        "source_ip": request.remote,
        "http_remote": request.remote,
        "http_host": request.host,
        "http_version": http_version,
        "http_method": request.method,
        "http_scheme": request.scheme,
        "http_query": request.path_qs,
        "http_post": http_post,
        "http_headers": http_headers,
        "http_path": request.path
    }

    # Send the Broker message
    # Set timeout to 3 seconds in a try: except so we dont kill the http response
    try:
        await wait_for(hpfeeds_publish(event_message), timeout=3)
    except asyncio.TimeoutError:
        print("Unable to connect to hpfeeds broker.")
        pass


    proxyPath = request.path_qs
    reqH = request.headers.copy()


    # We can put something in here so we can set any user / password combination to work. 
    # Essentially edit the POST form and replace the values with whatever we default to admin:admin


    async with client.request(
            request.method,baseUrl+proxyPath,
            headers = reqH,
            allow_redirects=False,
            data = await request.read()
        ) as res:
        headers = res.headers.copy()

        # Get teh body from the upstream
        body = await res.read()

        # If there is a compression header or chunked transfer we need to remove it. 
        # The response body we forward is already decompressed and re assembled
        if 'Content-Encoding' in headers:
            del headers['Content-Encoding']

        if 'Transfer-Encoding' in headers:
            if headers['Transfer-Encoding'] == "chunked":
                del headers['Transfer-Encoding']

        # We need to fix the content length if a reponse was compressed. 
        try:
            if len(body) != headers['Content-Length']:
                headers['Content-Length'] = str(len(body))
        except:
            pass

        # Now return the response
        return web.Response(
            headers = headers,
            status = res.status,
            body = body
        )

app = web.Application(
    client_max_size=10000000
)
app.router.add_route('*','/{proxyPath:.*}', handler)
web.run_app(app,port=9200)