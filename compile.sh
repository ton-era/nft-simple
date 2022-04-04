FUNC="/opt/ton/build/crypto/func"
FIFT_EXE_PATH="/opt/ton/build/crypto/fift"
STD_LIB="./stdlib.fc"
OUT_PATH="build"


rm $OUT_PATH/nft-item-code.fif
rm $OUT_PATH/nft-item-editable-code.fif
rm $OUT_PATH/nft-collection-code.fif
rm $OUT_PATH/nft-collection-editable-code.fif
rm $OUT_PATH/nft-marketplace-code.fif
rm $OUT_PATH/nft-sale-code.fif

$FUNC -o $OUT_PATH/nft-item-code.fif -SPA $STD_LIB params.fc op-codes.fc nft-item.fc
$FUNC -o $OUT_PATH/nft-item-editable-code.fif -SPA $STD_LIB params.fc op-codes.fc nft-item-editable-DRAFT.fc
$FUNC -o $OUT_PATH/nft-collection-code.fif -SPA $STD_LIB params.fc op-codes.fc nft-collection.fc
$FUNC -o $OUT_PATH/nft-collection-editable-code.fif -SPA $STD_LIB params.fc op-codes.fc nft-collection-editable.fc
$FUNC -o $OUT_PATH/nft-marketplace-code.fif -SPA $STD_LIB op-codes.fc nft-marketplace.fc
$FUNC -o $OUT_PATH/nft-sale-code.fif -SPA $STD_LIB op-codes.fc nft-sale.fc

$FIFT_EXE_PATH -s build/print-hex.fif
