#!/bin/bash

FIFT_PATH="/opt/ton/ton/crypto/fift"
FIFT_EXE_PATH="/opt/ton/build/crypto/fift"
REQUESTS_PATH="requests"


export FIFTPATH=$FIFT_PATH/lib

# compile project
./compile.sh

# create init *.boc file
echo "Deploying..."

$FIFT_EXE_PATH -s $REQUESTS_PATH/new-nft-collection.fif

echo "Deploy done"
