#!/bin/bash

mkdir -p rst/images
mkdir -p rst/_images

rsync -av --delete makehuman@www.makehumancommunity.org:www.makehumancommunity.org/files/images/ rst/images/
rsync -av --delete makehuman@www.makehumancommunity.org:www.makehumancommunity.org/root/images/ rst/_images/


