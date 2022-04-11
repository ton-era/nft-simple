#!/bin/bash

FUNC="/opt/liteclient-build/crypto/func"
FIFT_EXE_PATH="/opt/liteclient-build/crypto/fift"
OUT_PATH="build"


rm $OUT_PATH/nft-item-code.fif
rm $OUT_PATH/nft-collection-code.fif
rm $OUT_PATH/nft-marketplace-code.fif
rm $OUT_PATH/nft-sale-code.fif

$FUNC -o $OUT_PATH/nft-item-code.fif        -SPA code/stdlib.fc code/params.fc code/op-codes.fc code/nft-item.fc
$FUNC -o $OUT_PATH/nft-collection-code.fif  -SPA code/stdlib.fc code/params.fc code/op-codes.fc code/nft-collection.fc
$FUNC -o $OUT_PATH/nft-marketplace-code.fif -SPA code/stdlib.fc code/op-codes.fc code/nft-marketplace.fc
$FUNC -o $OUT_PATH/nft-sale-code.fif        -SPA code/stdlib.fc code/op-codes.fc code/nft-sale.fc

$FIFT_EXE_PATH -s ./utils/print-hex.fif $OUT_PATH
