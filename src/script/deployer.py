import os
import json
import pprint
import shutil
import requests
from subprocess import check_output
from jinja2 import Template


class Deployer:
    def __init__(self, 
                 api_base_url, 
                 api_token, 
                 func_compiler_path, 
                 fift_executer_path,
                 out_path, 
                 secret_path, 
                 wallet_addr,
                 log_path='../../logs'):
        self.api_base_url = api_base_url 
        self.api_token = api_token 
        self.func_compiler_path = func_compiler_path
        self.fift_executer_path = fift_executer_path
        self.out_path = out_path
        self.secret_path = secret_path
        self.wallet_addr = wallet_addr
        
        self.logger = None  # TODO


    def clear_out(self):
        print(f'Clear output dir {self.out_path}...')
        if os.path.exists(self.out_path):
            shutil.rmtree(self.out_path)
        os.mkdir(self.out_path)


    def compile_sources(self, src_path, src_files, **kwargs):
        print(f'Compile *.fc sources from {src_path}...')

        for file_group in src_files:
            try:
                in_files = [os.path.join(src_path, file) for file in file_group]
                out_file = os.path.join(self.out_path, file_group[-1].split('.')[0] + '-code.fif')
                print(f'  > compile {out_file}')
                result = check_output([self.func_compiler_path, '-o', out_file, '-SPA', *in_files])
            except Exception as err:
                print('ERROR:', err)
                return False

        print(f'Compile sources: DONE')

        return True

    def build_templates(self, tif_path, tif_files, **kwargs):
        print(f'Build *.tif templates from {tif_path} ...')

        for target_file, base_file in tif_files:
            try:
                print(f'  > building {target_file} template')

                with open(os.path.join(tif_path, target_file), 'r') as f:
                    target_template = f.read()
                with open(os.path.join(tif_path, base_file), 'r') as f:
                    base_template = f.read()

                result_template = Template(base_template).render(contract_body=target_template)

                out_file = os.path.join(self.out_path, target_file.split('.')[0] + '.tif')
                print(out_file)
                with open(out_file, 'w') as f:
                    f.writelines(result_template)
            except Exception as err:
                print('ERROR:', err)
                return False

        print('Build templates: DONE')

    
    def generate_collection_deploy_boc(self,
                                       collection_content_uri,
                                       item_content_base_uri,
                                       royalty_base,
                                       royalty_factor,
                                       coll_init_ng,
                                       owner_addr,
                                       royalty_addr,
                                       run=True):
        print(f'Generate collection deploy .boc file (run={run})...')
        
        # get current wallet seqno  
        seqno = self.get_seqno()
        print(f'  > actual seqno: {seqno}')
        if seqno is None:
            print('  > unable to get wallet seqno')
            print('BREAK')
            return

        # fill template with params
        params = {
            'script_name': 'nft-collection-deploy',
            'seqno': seqno,
            'collection_content_uri': collection_content_uri,
            'item_content_base_uri': item_content_base_uri,
            'royalty_base': royalty_base,
            'royalty_factor': royalty_factor,
            'coll_init_ng': coll_init_ng,
            'owner_addr': owner_addr,
            'royalty_addr': royalty_addr,
            'wallet_address': self.wallet_addr,
            'secret_path': self.secret_path,
            'build_path': self.out_path,
        }
        print(f'  > script params:\n{pprint.pformat(params)}')
        
        

        if run:
            pass

        print(f'Generate .boc file: DONE')

    def get_seqno(self):
        url = f'{self.api_base_url}runGetMethod&api_key={self.api_token}'
        data = {
            'address': self.wallet_addr,
            'method': 'seqno',
            'stack': []
        }

        result = self._post(self.wallet_addr, 'seqno')
        if not result:
            return None

        seqno = int(result[0][1], 16)
        return seqno
            

    def _post(self, smc_addr, smc_method, api_method='runGetMethod', stack=None):
        url = f'{self.api_base_url}{api_method}?api_key={self.api_token}'
        data = {
            'address': smc_addr,
            'method': smc_method,
            'stack': stack or []
        }

        try:
            response = requests.post(url, json=data)
            response = json.loads(response.text)
            if response.get('ok', None) and response.get('result', None):
                result = response['result']
                return result['stack']
        except Exception as err:
            print('ERROR: ', err)
            return None
