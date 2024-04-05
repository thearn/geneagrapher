# Use an official Ubuntu base image
FROM python:3.11

# Optionally, set a maintainer or label for the image
LABEL maintainer="tristanhearn@gmail.com"

# Install necessary base packages
RUN apt-get update && apt-get install -y graphviz && \
    rm -rf /var/lib/apt/lists/*

RUN pip install geneagrapher
