#!/usr/bin/env bash

rsync -avz src web mta_static requirements.txt spike@scpike.com:apps/trains/
