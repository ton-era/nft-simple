import json
import requests
import time


class HttpApiProvider:
    def __init__(self, api_base_url, api_key, wait_sec, wait_max_iters):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.wait_sec = wait_sec
        self.wait_max_iters = wait_max_iters
        self.current_seqnos = {}


    def send_boc(self, boc_b64):
        data = {'boc': boc_b64}
        return self._post('sendBoc', data=data)


    def await_seqno(self, wallet_address):
        # TODO: refactor & lock!!!
        prev_seqno = self.current_seqnos.get(wallet_address, None)
        iter = 0

        while True:
            iter += 1
            curr_seqno = self.get_seqno(wallet_address)
            if (prev_seqno is None) or \
                (prev_seqno < curr_seqno) or \
                (iter > self.wait_max_iters):
                break

            time.sleep(self.wait_sec)
        
        self.current_seqnos[wallet_address] = curr_seqno


    def get_seqno(self, wallet_address):
        result = self.run_get(wallet_address, 'seqno')
        return int(result[0][1], 16)


    def run_get(self, smc_addr, smc_method, stack=None):
        result = self._post('runGetMethod', smc_addr=smc_addr, smc_method=smc_method, stack=stack)
        return result['stack']


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
                if not success:
                    raise Exception(result)

                return result

            raise Exception(response)

        except Exception as err:
            print('ERROR: ', err)
            raise
