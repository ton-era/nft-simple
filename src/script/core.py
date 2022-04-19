import os
import shutil
import pprint
import base64
from subprocess import check_output
from jinja2 import Template


class Core:
    def __init__(self, 
                 fift_path,
                 fift_executer_path,
                 func_compiler_path, 
                 out_path, 
                 secret_path, 
                 wallet_address,
                 logger=None,
                 log_path='../../logs'):
        self.logger = logger  # TODO
        self.fift_path = fift_path
        self.fift_executer_path = fift_executer_path
        self.func_compiler_path = func_compiler_path
        self.out_path = out_path
        self.secret_path = secret_path
        self.wallet_address = wallet_address

        os.environ['FIFTPATH'] = os.path.join(self.fift_path, 'lib')


    def clear_out(self):
        print(f'Clear output dir {self.out_path}...')
        if os.path.exists(self.out_path):
            shutil.rmtree(self.out_path)
        os.mkdir(self.out_path)


    def compile_sources(self, src_path, src_files, **kwargs):
        print(f'Compile *.fc sources from {src_path} ...')

        for file_group in src_files:
            in_files = [os.path.join(src_path, file) for file in file_group]
            out_file = os.path.join(self.out_path, file_group[-1].split('.')[0] + '-code.fif')

            print(f'  > compile {out_file}')
            check_output([self.func_compiler_path, '-o', out_file, '-SPA', *in_files])

        print('Compile sources: DONE')


    def create_boc(self, script_name, params, seqno):
        print(f'Build {script_name} script...')

        tpl_file = os.path.join(self.out_path, script_name + '.tif')
        fif_file = os.path.join(self.out_path, script_name + '.fif')
        boc_file = os.path.join(self.out_path, script_name + '-query.boc')

        # fill template with params
        params['seqno'] = seqno
        params['script_name'] = script_name
        params['secret_path'] = self.secret_path
        params['wallet_address'] = self.wallet_address
        params['build_path'] = self.out_path

        print(f'  > script params:\n{pprint.pformat(params)}')
        print(f'  > fill template for "{script_name}"')

        # pass params to tif template
        self.render_template(tpl_file, 
                             params=params,
                             out_file=fif_file,
                             decorate_str=True)

        # execute fif to get .boc
        self.execute_fif(fif_file)
        print(f'  > boc generated: {boc_file}')

        with open(boc_file, 'rb') as f:
            boc_b64 = base64.b64encode(f.read()).decode('utf8')

        print('Build: DONE')

        return boc_b64


    def build_templates(self, tif_path, tif_files, **kwargs):
        print(f'Build *.tif templates from {tif_path} ...')

        for target_file, base_file in tif_files:
            tpl_file = os.path.join(tif_path, target_file)
            out_file = os.path.join(self.out_path, target_file.split('.')[0] + '.tif')

            with open(tpl_file, 'r') as f:
                target_template = f.read()
                self.render_template(os.path.join(tif_path, base_file),
                                     params={'contract_body': target_template},
                                     out_file=out_file)

        print('Build templates: DONE')


    def render_template(self, tpl_file, params, out_file, decorate_str=False):
        print(f'  > building {out_file} template...')

        if decorate_str:
            for p in params:
                param = params[p]
                if isinstance(param, str):
                    params[p] = f'"{param}"'

        with open(tpl_file, 'r') as f:
            template = f.read()
            result = Template(template).render(**params)

        with open(out_file, 'w') as f:
            f.writelines(result)

        print(f'  > building {out_file} template: DONE')


    def execute_fif(self, fif_file, verbose=False):
        print('  > execute fift script...')
    
        result = check_output([self.fift_executer_path, '-s', fif_file])
        if verbose:
            print(result)

        print('  > execute fift script: DONE')
