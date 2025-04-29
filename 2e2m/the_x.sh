#!/bin/bash

rm -rf /tmp/.X99-lock
Xvfb :99 -ac -screen 0 1920x1080x24 &