import yaml

from deployer import Deployer


def main():
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    
    deployer = Deployer(**config['env'])

    deployer.clear_out()
    deployer.compile_sources(**config['compile'])
    deployer.build_templates(**config['compile'])

    deployer.generate_collection_deploy_boc(**config['collection_deploy'])


if __name__ == '__main__':
    main()
