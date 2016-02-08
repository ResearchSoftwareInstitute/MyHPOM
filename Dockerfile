FROM mjstealey/hs_docker_base:1.6.5
MAINTAINER Michael J. Stealey <stealey@renci.org>

### Begin - HydroShare Development Image Additions ###
RUN pip uninstall -y django-celery
RUN pip install -U kombu==3.0.33
RUN pip install -U celery==3.1.20
RUN pip install -U pylint==1.5.0
RUN pip install -U OWSLib==0.10.3
### End - HydroShare Development Image Additions ###

USER root
WORKDIR /home/docker/hydroshare

CMD ["/bin/bash"]