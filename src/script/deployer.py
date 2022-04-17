import os
import json
import pprint
import shutil
import requests
import base64
from subprocess import check_output
from jinja2 import Template

from utils import addr_from_file


class Deployer:
    def __init__(self, 
                 api_base_url, 
                 api_token,
                 fift_path,
                 fift_executer_path,
                 func_compiler_path, 
                 out_path, 
                 secret_path, 
                 wallet_address,
                 log_path='../../logs'):
        self.api_base_url = api_base_url 
        self.api_token = api_token
        self.fift_path = fift_path
        self.fift_executer_path = fift_executer_path
        self.func_compiler_path = func_compiler_path
        self.out_path = out_path
        self.secret_path = secret_path
        self.wallet_address = wallet_address

        os.environ['FIFTPATH'] = os.path.join(self.fift_path, 'lib')

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

    
    def process_collection_deploy(
            self,
            script_name,
            collection_content_uri,
            item_content_base_uri,
            royalty_base,
            royalty_factor,
            coll_init_ng,
            owner_address,
            royalty_address,
            build=True,
            run=True):
        print(f'Process {script_name} .boc file (build={build}, run={run})...')

        fif_file = None
        boc_file = None

        # get current wallet seqno  
        seqno = self.get_seqno()
        print(f'  > actual seqno: {seqno}')
        if seqno is None:
            print('  > unable to get wallet seqno')
            print('BREAK')
            return None

        if build:
            # fill template with params
            params = {
                'script_name': script_name,
                'seqno': seqno,
                'collection_content_uri': base64.b64encode(collection_content_uri.encode('utf-8')).decode('utf-8'),
                'item_content_base_uri': base64.b64encode(item_content_base_uri.encode('utf-8')).decode('utf-8'),
                'royalty_base': royalty_base,
                'royalty_factor': royalty_factor,
                'coll_init_ng': coll_init_ng,
                'owner_address': owner_address,
                'royalty_address': royalty_address,
                'wallet_address': self.wallet_address,
                'secret_path': self.secret_path,
                'build_path': self.out_path,
            }
            print(f'  > script params:\n{pprint.pformat(params)}')

            print(f'  > fill template for "{script_name}"')
            for p in params:
                params[p] = f'"{params[p]}"'
            with open(os.path.join(self.out_path, script_name + '.tif'), 'r') as f:
                fif_template = f.read()

            try:
                fif_result = Template(fif_template).render(**params)
            except Exception as err:
                print('ERROR: ', err)
                return None

            fif_file = os.path.join(self.out_path, script_name + '.fif')
            print(f'  > fif generated: {fif_file}')
            with open(fif_file, 'w') as f:
                f.writelines(fif_result)

            # execute fif to get .boc
            print('  > execute fift script...')
            try:
                result = check_output([self.fift_executer_path, '-s', fif_file])
            except Exception as err:
                print('ERROR: ', err)
                return None

        # get collection address
        addr_file = os.path.join(self.out_path, script_name + '.addr')
        coll_address = addr_from_file(addr_file)
        if not coll_address:
            print('  > no collection .addr file found. Run build first.')
            return None
        print(f'  > collection address: {coll_address}')

        if run:
            boc_file = os.path.join(self.out_path, script_name + '-query.boc')

            print(f'  > sending .boc file {boc_file}...')
            with open(boc_file, 'rb') as f:
                boc_b64 = base64.b64encode(f.read()).decode('utf8')
                self.send_boc(boc_b64)

        print(f'Generate .boc file: DONE')

        return {
            'seqno': seqno,
            'fif_file': fif_file,
            'boc_file': boc_file,
            'coll_address': coll_address,
        }


    def send_boc(self, boc_b64):
        try:
            data = {'boc': boc_b64}
            result = self._post(api_method='sendBoc', data=data)
            return result
        except Exception as err:
            print('ERROR: ', err)
            return None


    def get_seqno(self):
        try:
            result = self._post(smc_addr=self.wallet_address, smc_method='seqno')
            seqno = int(result[0][1], 16)
            return seqno
        except Exception as err:
            print('ERROR: ', err)
            return None


    def _post(self, api_method='runGetMethod', data=None, smc_addr=None, smc_method=None, stack=None):
        url = f'{self.api_base_url}{api_method}?api_key={self.api_token}'
        data = data or {
            'address': smc_addr,
            'method': smc_method,
            'stack': stack or []
        }

        response = requests.post(url, json=data)
        response = json.loads(response.text)
        print(response)
        if response.get('ok', None) and response.get('result', None):
            result = response['result']
            return result['stack']
