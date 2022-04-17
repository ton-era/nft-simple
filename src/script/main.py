import yaml
import pprint

from deployer import Deployer


def main():
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    
    deployer = Deployer(**config['settings'])

    deployer.clear_out()
    deployer.compile_sources(**config['compile'])
    deployer.build_templates(**config['compile'])

    result = deployer.process_collection_deploy(**config['collection_deploy'])

    print('\nRESULT:')
    pprint.pprint(result)

if __name__ == '__main__':
    main()
