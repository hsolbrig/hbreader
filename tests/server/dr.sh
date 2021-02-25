docker run -it --rm -d -p 8100:80 -p 8543:443 --name hb_server -v `pwd`/html/:/usr/share/nginx/html hb_server
