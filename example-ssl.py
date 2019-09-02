from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import logging

RPC_USER = 'change_me'
RPC_PASSWORD = 'change_me'
BITCOIN_SERVER = 'change_me:443'
AUTHSERV = 'https://' + RPC_USER + ':' + RPC_PASSWORD + '@' + BITCOIN_SERVER
print "AUTHSERV: %s" % (AUTHSERV)

# set logging to debug
logging.basicConfig()
logging.getLogger("BitcoinRPC").setLevel(logging.DEBUG)

# rpc_user and rpc_password are set in the bitcoin.conf file
rpc_connection = AuthServiceProxy(AUTHSERV)
best_block_hash = rpc_connection.getbestblockhash()
print(rpc_connection.getblock(best_block_hash))

# batch support : print timestamps of blocks 0 to 99 in 2 RPC round-trips:
commands = [ [ "getblockhash", height] for height in range(100) ]
block_hashes = rpc_connection.batch_(commands)
blocks = rpc_connection.batch_([ [ "getblock", h ] for h in block_hashes ])
block_times = [ block["time"] for block in blocks ]
print(block_times)

