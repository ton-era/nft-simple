import yaml
import pprint

from core import Core
from http_api_provider import HttpApiProvider
from nft_collection import NftCollection


def main():
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    
    core = Core(**config['core'])
    provider = HttpApiProvider(**config['providers']['http_api_provider'])

    with open('deploy.yaml') as f:
        deploy = yaml.safe_load(f)
        collection = NftCollection(core, provider, config=deploy['collection'])

    ## core.clear_out()
    # core.compile_sources(**config['compile'])
    # core.build_templates(**config['compile'])

    # seqno = provider.get_seqno(core.wallet_address)
    # result = collection.build(seqno)
    # print('\n>>>>>>>>>>>>>>>>>>>>>>>> BUILD >>>>>>>>>>>>>>>>>>>>>>>>\n')
    # pprint.pprint(result)

    # if not result['ok']:
    #     return

    # result = collection.deploy()
    # print('\n>>>>>>>>>>>>>>>>>>>>>>>> DEPLOY >>>>>>>>>>>>>>>>>>>>>>>>')
    # pprint.pprint(result)

    # if not result['ok']:
    #     return

    result = collection.get_collection_data()
    print('\n>>>>>>>>>>>>>>>>>>>>>>>> COLLECION DATA >>>>>>>>>>>>>>>>>>>>>>>>')
    pprint.pprint(result)


if __name__ == '__main__':
    main()
