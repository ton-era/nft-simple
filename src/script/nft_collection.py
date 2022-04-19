import os
import base64

from utils import addr_from_file, addr_from_b64
from nft_base import NftBase


class NftCollection(NftBase):
    def __init__(self,
                 core,
                 provider,
                 config,
                 address=None,
                 script_name='nft-collection-deploy',
                 logger=None,
                 log_path='../../logs'):
        super().__init__(core=core, 
                         provider=provider, 
                         config=config, 
                         address=address, 
                         script_name=script_name,
                         logger=logger,
                         log_path=log_path)


    def get_address(self):
        if self.address is not None:
            return self.address

        addr_file = os.path.join(self.core.out_path, self.script_name + '.addr')
        self.address = addr_from_file(addr_file)
        self._check_success(self.address['b'] is not None, 'Can\'t get collection address')

        return self.address


    def get_params(self):
        return {
            'collection_content_uri': base64.b64encode(self.config['collection_content_uri'].encode('utf-8')).decode('utf-8'),
            'item_content_base_uri': base64.b64encode(self.config['item_content_base_uri'].encode('utf-8')).decode('utf-8'),
            'royalty_base': self.config['royalty_base'],
            'royalty_factor': self.config['royalty_factor'],
            'coll_init_ng': self.config['coll_init_ng'],
            'owner_address': self.config['owner_address'],
            'royalty_address': self.config['royalty_address'],
        }

    # Smart Contract API

    def deploy_one_nft(self, nft):
        pass

    # Smart Contract GET methods
    
    def get_collection_data(self):
        result = self.provider.run_get(self.get_address(), 'get_collection_data')

        if result and len(result) == 4:
            return {
                'next_item_index': int(result[0][1], 16),
                'collection_data': base64.b64decode(result[1][1]['object']['data']['b64'])[1:].decode('utf-8'),
                'owner_address': addr_from_b64(result[2][1]['object']['data']['b64']),
                'main_answer': int(result[3][1], 16),
            }

        return None


    def royalty_params(self):
        result = self.provider.run_get(self.get_address()['b'], 'royalty_params')

        if result and len(result) == 3:
            return {
                'royalty_factor': int(result[0][1], 16),
                'royalty_base': int(result[1][1], 16),
                'royalty_address': addr_from_b64(result[2][1]['object']['data']['b64']),
            }

        return None


    def get_nft_address_by_index(self, index):
        result = self.provider.run_get(self.get_address()['b'], 
                                       'get_nft_address_by_index',
                                       stack=[['num', index]])

        if result and len(result) == 1:
            return {
                'nft_address': addr_from_b64(result[0][1]['object']['data']['b64']),
            }

        return None


    def get_nft_content(self, index):
        # TODO: tvm.Cell = nftData.contentCell.toBoc
        # A BUG, not ready yet: https://t.me/tondev/66903
        result = self.provider.run_get(self.get_address()['b'],
                                       'get_nft_content',
                                       stack=[['num', index], ['tvm.Cell', None]])

        if result and len(result) == 1:
            return {
                'collection_data': base64.b64decode(result[1][1]['object']['data']['b64'])[1:].decode('utf-8'),
                'nft_address': addr_from_b64(result[0][1]['object']['data']['b64']),
            }

        return None
