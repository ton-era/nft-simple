import json
import requests


class HttpApiProvider:
    def __init__(self, api_base_url, api_key):
        self.api_base_url = api_base_url
        self.api_key = api_key


    def send_boc(self, boc_b64):
        data = {'boc': boc_b64}
        return self._post('sendBoc', data=data)


    def get_seqno(self, wallet_address):
        result = self.run_get(wallet_address, 'seqno')
        return int(result[0][1], 16) if result else None


    def run_get(self, smc_addr, smc_method, stack=None):
        success, result = self._post('runGetMethod', smc_addr=smc_addr, smc_method=smc_method, stack=stack)
        return result.get('stack', None) if success else None


    def _post(self, api_method, data=None, smc_addr=None, smc_method=None, stack=None):
        try:
            url = f'{self.api_base_url}{api_method}?api_key={self.api_key}'
            data = data or {
                'address': smc_addr,
                'method': smc_method,
                'stack': stack or []
            }

            response = requests.post(url, json=data)
            response = json.loads(response.text)

            if response.get('ok', None) and response.get('result', None):
                result = response['result']
                success = (result.get('@type', 'ok') == 'ok') and (result.get('exit_code', 0) <= 0)
                return (success, result)

            return (False, response)

        except Exception as err:
            print('ERROR: ', err)
            return (False, None)
