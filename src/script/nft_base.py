from abc import abstractmethod
import os
import shutil
import pprint
import base64


class NftBase:
    def __init__(self,
                 core,
                 provider,
                 config,
                 script_name,
                 address=None,
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
        self.fif_unique_file = os.path.join(self.core.out_path, self.script_name + '_{addr}.fif')
        self.boc_file = os.path.join(self.core.out_path, self.script_name + '-query.boc')

    @abstractmethod
    def get_address(self):
        pass


    @abstractmethod
    def get_params(self):
        pass


    def build(self):
        print(f'Build {self.script_name}...')

        # get wallet current seqno 
        seqno = self.provider.get_seqno(self.core.wallet_address)
        self._check_success(seqno is not None, 'Can\'t get wallet actual seqno')

        # fill template with params
        params = self.get_params()
        params['seqno'] = seqno
        params['script_name'] = self.script_name
        params['secret_path'] = self.core.secret_path
        params['wallet_address'] = self.core.wallet_address
        params['build_path'] = self.core.out_path

        print(f'  > script params:\n{pprint.pformat(params)}')
        print(f'  > fill template for "{self.script_name}"')

        success = self.core.render_template(self.template_file, params, self.fif_file, decorate_str=True)
        self._check_success(success, 'Can\'t render template')

        # execute fif to get .boc
        success = self.core.execute_fif(self.fif_file)
        self._check_success(success, 'Can\'t execute FIFT script')

        # get new smc address
        self.address = self.get_address()
        print(f'  > smart contract address: {self.address}')

        # copy unique smc fift file
        unique_file = self.fif_unique_file.format(addr=self.address['b'])
        shutil.copyfile(self.fif_file, unique_file)
        print(f'  > unique fift file: {unique_file}')

        print('Build: DONE')


    def deploy(self):
        print(f'Deploy {self.boc_file} .boc file...')

        print(f'  > sending .boc file {self.boc_file} to blockchain...')
        with open(self.boc_file, 'rb') as f:
            boc_b64 = base64.b64encode(f.read()).decode('utf8')
            success, result = self.provider.send_boc(boc_b64)
            self._check_success(success, f'Can\'t send BOC: {str(result)}')

        print(f'Deploy {self.boc_file} .boc file: DONE')


    def _check_success(self, success, payload):
        if not success:
            raise Exception(payload)
