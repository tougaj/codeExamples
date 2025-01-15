#!/usr/bin/env bash

# docker pull libretranslate/libretranslate
#
docker run -ti --rm \
        -p 5001:5000 \
        -v $(pwd)/lt-local:/home/libretranslate/.local:z \
        libretranslate/libretranslate