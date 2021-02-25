# Docker test server
This docker image serves whatever is in the html directory through ports 8000 (http:) and 8443 (https:).  We use
it to test the Honey Badger's ability to ignore SSL certificates (HB Don't care)

## Starting the docker web server
```bash
> cd tests/server
> docker image build . -t hb_server
> docker run -it --rm -d -p 8100:80 -p 8543:443 --name hb_server -v `pwd`/html/:/usr/share/nginx/html hb_server 
# After you finished testing
> docker stop hb_server
```
To test that the server is running:5
```bash
> curl -k https://localhost:8543/schema.context.jsonld
{
   "_comments": "Auto generated from termci_schema.yaml by jsonldcontextgen.py version: 0.1.1\nGeneration date: 2021-02-12 11:24\nSchema: termci_schema\n\nid: https://w3id.org/termci_schema\ndescription: Terminology Code Index model\nlicense: https://creativecommons.org/publicdomain/zero/1.0/\n",
   "@context": {
      "type": "@type",
      "biolinkml": "https://w3id.org/biolink/biolinkml/",
      "dc": "http://purl.org/dc/elements/1.1/",
      "sct": "http://snomed.info/id/",
      "sh": "http://www.w3.org/ns/shacl#",
      "skos": "http://www.w3.org/2004/02/skos/core#",
      "termci": "https://hotecosystem.org/termci/",
      "@vocab": "https://hotecosystem.org/termci/",
      "code": {
         "@id": "skos:notation"
      },

> curl http://localhost:8100/schema.context.jsonld
{
   "_comments": "Auto generated from termci_schema.yaml by jsonldcontextgen.py version: 0.1.1\nGeneration date: 2021-02-12 11:24\nSchema: termci_schema\n\nid: https://w3id.org/termci_schema\ndescription: Terminology Code Index model\nlicense: https://creativecommons.org/publicdomain/zero/1.0/\n",
   "@context": {
    ...
>
```
The ports that you select for `http:` and `https:` can be assigned however you wish, but if you pick something the
ones above, you will need to edit [tests/test_ssl.py]() and change the lines:

```python
HTTP_TEST_PORT = 8100
HTTPS_TEST_PORT = 8543
```

