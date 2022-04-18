from inspect import stack
import os
import pprint
import base64
from subprocess import check_output

from utils import addr_from_file, addr_from_b64


class NftCollection:
    def __init__(self,
                 core,
                 provider,
                 config,
                 address=None,
                 script_name='nft-collection-deploy',
                 logger=None,
                 log_path='../../logs'):
        self.logger = logger  # TODO
        self.script_name = script_name
        self.core = core
        self.provider = provider
        self.config = config

        self.address = address
        self.template_file = os.path.join(self.core.out_path, self.script_name + '.tif')
        self.fif_file = os.path.join(self.core.out_path, self.script_name + '.fif')
        self.boc_file = os.path.join(self.core.out_path, self.script_name + '-query.boc')

    def build(self, seqno):
        print(f'Build NFT collection (seqno={seqno})...')
        success = True

        # fill template with params
        params = {
            'seqno': seqno,
            'script_name': self.script_name,
            'collection_content_uri': base64.b64encode(self.config['collection_content_uri'].encode('utf-8')).decode('utf-8'),
            'item_content_base_uri': base64.b64encode(self.config['item_content_base_uri'].encode('utf-8')).decode('utf-8'),
            'royalty_base': self.config['royalty_base'],
            'royalty_factor': self.config['royalty_factor'],
            'coll_init_ng': self.config['coll_init_ng'],
            'owner_address': self.config['owner_address'],
            'royalty_address': self.config['royalty_address'],
            'wallet_address': self.core.wallet_address,
            'secret_path': self.core.secret_path,
            'build_path': self.core.out_path,
        }
        print(f'  > script params:\n{pprint.pformat(params)}')
        print(f'  > fill template for "{self.script_name}"')

        success |= self.core.render_template(self.template_file, params, self.fif_file, decorate_str=True)

        # execute fif to get .boc
        success |= self.core.execute_fif(self.fif_file)

        if success:
            self.address = self.get_address()
        print(f'  > collection address: {self.address}')

        print(f'Build NFT collection: {success}')
        return {
            'ok': success,
            'address': self.address,
            'fif_file': self.fif_file,
            'boc_file': self.boc_file,
        }


    def get_address(self):
        addr_file = os.path.join(self.core.out_path, self.script_name + '.addr')
        address = addr_from_file(addr_file)
        return address

    
    def deploy(self):
        print(f'Deploy {self.boc_file} .boc file...')
        success = True

        print(f'  > sending .boc file {self.boc_file} to blockchain...')
        with open(self.boc_file, 'rb') as f:
            boc_b64 = base64.b64encode(f.read()).decode('utf8')
            success, result = self.provider.send_boc(boc_b64)

        print(f'Deploy {self.boc_file} .boc file: {success}')

        return {
            'ok': success,
            'result': result,
        }

    
    def get_collection_data(self):
        address = self.address or self.get_address().get('b', None)
        if not address:
            print('  > no collection address found. Run build first.')
            return {'ok': False}

        result = self.provider.run_get(address, 'get_collection_data')
        coll_data = {}

        if result and len(result) == 4:
            coll_data = {
                'collection_address': address,
                'next_item_index': int(result[0][1], 16),
                'collection_data': base64.b64decode(result[1][1]['object']['data']['b64'])[1:].decode('utf-8'),
                'owner_address': addr_from_b64(result[2][1]['object']['data']['b64'])['b'],
                'main_answer': int(result[3][1], 16),
            }

        return coll_data


    def royalty_params(self):
        address = self.address or self.get_address().get('b', None)
        if not address:
            print('  > no collection address found. Run build first.')
            return {'ok': False}

        result = self.provider.run_get(address, 'royalty_params')
        coll_data = {}

        if result and len(result) == 3:
            coll_data = {
                'collection_address': address,
                'royalty_factor': int(result[0][1], 16),
                'royalty_base': int(result[1][1], 16),
                'royalty_address': addr_from_b64(result[2][1]['object']['data']['b64'])['b'],
            }

        return coll_data


    def get_nft_address_by_index(self, index):
        address = self.address or self.get_address().get('b', None)
        if not address:
            print('  > no collection address found. Run build first.')
            return {'ok': False}

        result = self.provider.run_get(address, 'get_nft_address_by_index', stack=[['num', index]])
        coll_data = {}

        if result and len(result) == 1:
            coll_data = {
                'collection_address': address,
                'nft_index': index,
                'nft_address': addr_from_b64(result[0][1]['object']['data']['b64'])['b'],
            }

        return coll_data


    def get_nft_content(self, index):
        address = self.address or self.get_address().get('b', None)
        if not address:
            print('  > no collection address found. Run build first.')
            return {'ok': False}

        import json 

        # TODO: tvm.Cell = nftData.contentCell.toBoc
        result = self.provider.run_get(address, 'get_nft_content', stack=[['num', index], ['tvm.Cell', None]])
        coll_data = {}

        if result and len(result) == 1:
            coll_data = {
                'collection_address': address,
                'nft_index': index,
                'collection_data': base64.b64decode(result[1][1]['object']['data']['b64'])[1:].decode('utf-8'),
                'nft_address': addr_from_b64(result[0][1]['object']['data']['b64'])['b'],
            }

        return coll_data
