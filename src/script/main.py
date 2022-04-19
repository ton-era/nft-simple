import yaml
import time
import pprint

from core import Core
from http_api_provider import HttpApiProvider
from nft_collection import NftCollection
from nft_item import NftItem


def main():
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    
    core = Core(**config['core'])
    provider = HttpApiProvider(**config['providers']['http_api_provider'])

    ## core.clear_out()
    core.compile_sources(**config['compile'])
    core.build_templates(**config['compile'])

    with open('deploy.yaml') as f:
        deploy = yaml.safe_load(f)
    
    collection = NftCollection(core, provider, config=deploy['collection'])


    # print('\n>>>>>>>>>>>>>>>>>>>>>>>> BUILD >>>>>>>>>>>>>>>>>>>>>>>>\n')
    # collection.build()


    # print('\n>>>>>>>>>>>>>>>>>>>>>>>> DEPLOY >>>>>>>>>>>>>>>>>>>>>>>>')
    # collection.deploy()


    # time.sleep(10)  # wait some time for smc to be deployed in bc

    # print('\n>>>>>>>>>>>>>>>>>>>>>>>> GET: COLLECION DATA >>>>>>>>>>>>>>>>>>>>>>>>')
    # result = collection.get_collection_data()
    # pprint.pprint(result)


    # print('\n>>>>>>>>>>>>>>>>>>>>>>>> GET: ROYALTY DATA >>>>>>>>>>>>>>>>>>>>>>>>')
    # result = collection.royalty_params()
    # pprint.pprint(result)


    # print('\n>>>>>>>>>>>>>>>>>>>>>>>> GET: NFT ADDRESS >>>>>>>>>>>>>>>>>>>>>>>>')
    # result = collection.get_nft_address_by_index(123)
    # pprint.pprint(result)
    

    # # print('\n>>>>>>>>>>>>>>>>>>>>>>>> GET: NFT CONTENT >>>>>>>>>>>>>>>>>>>>>>>>')
    # # result = collection.get_nft_content(123)
    # # pprint.pprint(result)


    print('\n>>>>>>>>>>>>>>>>>>>>>>>> DEPLOY NFT >>>>>>>>>>>>>>>>>>>>>>>>')
    config = deploy['items']
    nfts = []
    for item_config in config['list']:
        print(f'\n  >>>>>>>>>>>>>>>>>>>>>>>> DEPLOY {item_config["item_index"]} >>>>>>>>>>>>>>>>>>>>>>>>')
        nft_config = config.copy()
        del nft_config['list']
        nft_config = {**nft_config, **item_config}

        nft = NftItem(core, provider, nft_config, collection)
        print(nft.get_address())

        nft.build()
        # nft.deploy()
        # print(f'awaiting wallet seqno update: {provider.get_seqno(core.wallet_address)}...')
        # provider.await_seqno(core.wallet_address)
        # print(f'awaiting wallet seqno update: {provider.get_seqno(core.wallet_address)}: DONE')

        nfts.append(nft)
        

    print('\n>>>>>>>>>>>>>>>>>>>>>>>> GET: NFT DATA >>>>>>>>>>>>>>>>>>>>>>>>')
    nft = nfts[2]
    result = nft.get_nft_data()
    pprint.pprint(result)





if __name__ == '__main__':
    main()
