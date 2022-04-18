import os
import shutil
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
        success = True

        for file_group in src_files:
            try:
                in_files = [os.path.join(src_path, file) for file in file_group]
                out_file = os.path.join(self.out_path, file_group[-1].split('.')[0] + '-code.fif')

                print(f'  > compile {out_file}')
                result = check_output([self.func_compiler_path, '-o', out_file, '-SPA', *in_files])
            except Exception as err:
                print('ERROR:', err)
                success = False
                break

        print(f'Compile sources: {success}')
        return True

    def build_templates(self, tif_path, tif_files, **kwargs):
        print(f'Build *.tif templates from {tif_path} ...')
        success = True

        for target_file, base_file in tif_files:
            template_file = os.path.join(tif_path, target_file)
            out_file = os.path.join(self.out_path, target_file.split('.')[0] + '.tif')

            with open(template_file, 'r') as f:
                target_template = f.read()
                success |= self.render_template(os.path.join(tif_path, base_file),
                                                params={'contract_body': target_template},
                                                out_file=out_file)
                if not success:
                    break

        print(f'Build templates: {success}')

    def render_template(self, template_file, params, out_file, decorate_str=False):
        print(f'  > building {out_file} template...')
        success = False

        try:
            if decorate_str:
                for p in params:
                    param = params[p]
                    if isinstance(param, str):
                        params[p] = f'"{param}"'

            with open(template_file, 'r') as f:
                template = f.read()
                result = Template(template).render(**params)

            with open(out_file, 'w') as f:
                f.writelines(result)

            success = True
        except Exception as err:
            print('ERROR:', err)

        print(f'  > building {out_file} template: {success}')
        return success


    def execute_fif(self, fif_file, verbose=False):
        print('  > execute fift script...')
        success = False
        
        try:
            result = check_output([self.fift_executer_path, '-s', fif_file])
            if verbose:
                print(result)
            success = True 
        except Exception as err:
            print('ERROR: ', err)

        print(f'  > execute fift script: {success}')
        return success
