# Docker test server
This docker image serves whatever is in the html directory through ports 8100 (http:) and 8543 (https:).  We use
it to test the Honey Badger's ability to ignore SSL certificates (HB Don't care)

## Starting the docker web server
```bash
> cd tests/server
> ./db.sh
Step 9/9 : EXPOSE 80 443
 ---> Using cache
 ---> 19c5600029ca
Successfully built 19c5600029ca
Successfully tagged hb_server:latest
>
# Edit the port assignments in dr.sh if 8100 or 8543 are in use
> ./dr.sh 
06a8e67bad5887a3300c8c1710615ea0328d478c5b361c33e60e8b8869eaa964
>
# After you finished testing
> ./ds.sh
hb_server
>
```
To test that the server is running:
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

