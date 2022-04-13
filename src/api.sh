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
    collection_content_uri=$3
    item_content_base_uri=$4
    royalty_base=$5
    royalty_factor=$6
    coll_init_ng=$7
    secret_path=$8
    addr_path=$9
    $FIFT_EXE_PATH -s $REQUESTS_PATH/nft-collection-deploy.fif $seqno $collection_content_uri $item_content_base_uri $royalty_base $royalty_factor $coll_init_ng $secret_path $addr_path
elif [[ $command == "mint" ]]
then
    seqno=$2
    coll_address=$3
    item_index=$4
    coll_ng=$5
    item_ng=$6
    secret_path=$7
    addr_path=$8
    $FIFT_EXE_PATH -s $REQUESTS_PATH/nft-item-mint.fif $seqno $coll_address $item_index $coll_ng $item_ng $secret_path $addr_path
else
    echo "Unknown command"
fi

echo "Done"
