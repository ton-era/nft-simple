from abc import abstractmethod


class NftBase:
    def __init__(self,
                 core,
                 provider,
                 config,
                 address=None,
                 logger=None,
                 log_path='../../logs'):
        self.logger = logger  # TODO
        self.core = core
        self.provider = provider
        self.config = config
        self.address = address


    @abstractmethod
    def get_address(self):
        pass


    def api(self, params, script_name, send):
        seqno = self.provider.get_seqno(self.core.wallet_address)
        boc_b64 = self.core.create_boc(script_name, params, seqno)

        if send:
            self.provider.send_boc(boc_b64)
