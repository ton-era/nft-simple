import base64

from utils import addr_from_b64
from nft_base import NftBase


class NftItem:
    def __init__(self,
                 core,
                 provider,
                 config,
                 collection,
                 address=None,
                 script_name='nft-item-mint',
                 logger=None,
                 log_path='../../logs'):
        super().__init__(core, provider, config, address, script_name, logger, log_path)

        self.collection = collection


    def get_address(self):
        if self.address is not None:
            return self.address

        index = self.config['index']
        self.address = self.collection.get_nft_address_by_index(index).get('nft_address', None)
        self._check_success(self.address.get('b', None) is not None, 'Can\'t get collection address')

        return self.address


    def get_params(self):
        return {
            'item_index': self.config['item_index'],
            'item_content_uri': base64.b64encode(self.config['item_content_uri'].encode('utf-8')).decode('utf-8'),
            'coll_ng': self.config['coll_ng'],
            'item_ng': self.config['item_ng'],
            'owner_address': self.config['owner_address'],
            'coll_address': self.collection.get_address(),
        }

    # Smart Contract GET methods

    def get_nft_data(self):
        address = self.address or self.get_address().get('b', None)
        self._check_success(self.address is not None, 'Can\'t get nft address')

        result = self.provider.run_get(address, 'get_nft_data')
        nft_data = {}

        if result and len(result) == 5:
            nft_data = {
                'is_init': int(result[0][1], 16) == -1,
                'index': int(result[1][1], 16),
                'collection_address': addr_from_b64(result[2][1]['object']['data']['b64']),
                'owner_address': addr_from_b64(result[3][1]['object']['data']['b64']),
                'content': base64.b64decode(result[4][1]['object']['data']['b64'])[1:].decode('utf-8'),
            }

        return nft_data
