SSL Certificates
================

This folder contains a set of very insecure SSL certificates to be used for 
running the server in SSL.

As you can see the private key and everything is here. This is absolutely not 
done for anything that smells production ready.

However with a CA and a SSL certificate we can have an SSL connection between 
all servers in this example setup.

Below a summary of how these certificates where created so I can redo whenever 
I need it.

1. Create CA key


    $ openssl genrsa -out ca.key 2048

2. Create CA certificate


    $ openssl req -x509 -new -nodes -key ca.key -sha256 -days 1825 -out ca.pem
    
    
3. Generate private key and CSR

    
    $ openssl req -out localhost.yarf.nl.csr -newkey rsa:2048 -nodes -keyout localhost.yarf.nl.key
    
    
4. Sign with the CA certificate

    
    $ openssl x509 -req -in localhost.yarf.nl.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out localhost.yarf.nl.cert -days 1825 -sha256 -extfile ssl.ext


5. Verify the certifcate


    $ openssl x509 -noout -text -in localhost.yarf.nl.cert


6. Add `ca.pem` to your browser's set of trusted CA's