from dns.resolver import NXDOMAIN, Answer

class resolver:
    @staticmethod
    def query(qname: str) -> Answer: ...
    NXDOMAIN = NXDOMAIN
