#!/bin/bash

FIFT_PATH="/opt/ton/crypto/fift"
FIFT_EXE_PATH="/opt/liteclient-build/crypto/fift"
REQUESTS_PATH="requests"


export FIFTPATH=$FIFT_PATH/lib

# compile project
./compile.sh

# running command
command=$1
echo
echo "Running command: " $command " ..."
echo

if [[ $command == "deploy" ]]
then
    seqno=$2
    coll_init_ng=$3
    $FIFT_EXE_PATH -s $REQUESTS_PATH/nft-collection-deploy.fif $seqno $coll_init_ng
elif [[ $command == "mint" ]]
then
    seqno=$2
    item_init_ng=$3
    $FIFT_EXE_PATH -s $REQUESTS_PATH/nft-item-mint.fif $seqno $item_init_ng
else
    echo "Unknown command"
fi

echo "Done"
