#!/bin/bash

mkdir -p rst/images
mkdir -p rst/_images

rsync -av --delete makehuman@www.makehuman.org:www.makehuman.org/files/images/ rst/images/
rsync -av --delete makehuman@www.makehuman.org:www.makehuman.org/root/images/ rst/_images/


