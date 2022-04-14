import json
import requests
import sys
import time
import yaml
from subprocess import check_output
from tqdm import tqdm


RUN_GET_METHOD = 'runGetMethod'



# def main():
#     config_path = sys.argv[1]

#     with open(config_path) as f:
#         config = yaml.safe_load(f)

#     try:
#         check_output(['./compile.sh'])
#     except Exception as err:
#         print(f'ERROR during compilation:\n{err}')


#     for item in tqdm(config['items']):
#         pass

#     print('done')




url = 'https://testnet.toncenter.com/api/v2/runGetMethod'
data = {
    'address': 'EQDPagYDA_O320Ihg8PoTFrC8jEUr6kRNG9qSVotu-D8O6QG',
    'method': 'get_nft_data',
    'stack': []
}

response = requests.post(url, json=data)

result = json.loads(response.text)
if result['ok']:
    result = result['result']
    print(result)

### NFT OLD OWNER: gALMDzhv+VTDezBahDB6pXv+/+nRrUhwF+iKbPwWJ1vj4A==

# url = 'https://testnet.toncenter.com/api/v2/runGetMethod'
# data = {
#     'address': 'kQAWYHnDf8qmG9mC1CGD1Svf9_9OjWpDgL9EU2fgsTrfHyNM',
#     'method': 'seqno',
#     'stack': []
# }

# response = requests.post(url, json=data)

# result = json.loads(response.text)
# if result['ok']:
#     result = result['result']
#     seqno = int(result['stack'][0][1], 16)
#     print(seqno)
    
# if __name__ == '__main__':
#     main()