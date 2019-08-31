from bitcoinrpc.authproxy import AuthServiceProxy
import collectd
import sys, traceback


RPC_USER = 'change_me'
RPC_PASSWORD = 'change_me'
BITCOIN_SERVER = '127.0.0.1:8332'
AUTHSERV = 'http://' + RPC_USER + ':' + RPC_PASSWORD + '@' + BITCOIN_SERVER


def new_proxy():
    """
    Creates and returns a new proxy object that talks to the specified bitcoin
    node. Calls sometimes time out. If this happens the connection stays stuck.
    We need to create a new connection for each read call to ensure continuous
    reading of data even in the event of a temporary timeout which would throw
    an exception.
    """
    return AuthServiceProxy(AUTHSERV)


def read_nettotals():
    proxy = new_proxy()
    response = proxy.getnettotals()
    funcname = str('getnettotals')
    for subkey in ['totalbytesrecv', 'totalbytessent']:
        total_bytes = response[subkey]
        val = collectd.Values(type='counter',
                              host='',
                              plugin='bitcoind',
                              time=0)
        val.plugin_instance = funcname
        val.type_instance = subkey
        val.dispatch(values=[total_bytes])


def read_networkinfo():
    proxy = new_proxy()
    response = proxy.getnetworkinfo()
    funcname = str('getnetworkinfo')
    subkey = str('connections')
    number_of_connections = response[subkey]
    val = collectd.Values(type='gauge',
                          host='',
                          plugin='bitcoind',
                          time=0)
    val.plugin_instance = funcname
    val.type_instance = subkey
    val.dispatch(values=[number_of_connections])


def read_mempoolinfo():
    proxy = new_proxy()
    response = proxy.getmempoolinfo()
    funcname = str('getmempoolinfo')
    for subkey in ['size', 'bytes']:
        funccat = (str(funcname) + '_' + str(subkey))
        info = response[subkey]
        val = collectd.Values(type='gauge',
                              host='',
                              plugin='bitcoind',
                              time=0)
        val.plugin_instance = funccat
        val.type_instance = subkey
        val.dispatch(values=[info])


def read_estimatesmartfee():
    # Starting with v0.17 only estimatesmartfee call is supported.
    # Estimate cost to include the transaction within 6 blocks.
    # We convert this value to Satoshis to make it an integer
    proxy = new_proxy()
    response = proxy.estimatesmartfee(6)
    funcname = str('estimatesmartfee')
    feerate = response['feerate']
    feerate_in_satoshi = feerate * 100000000
    val = collectd.Values(type='gauge',
                          host='',
                          plugin='bitcoind',
                          time=0)
    val.plugin_instance = funcname
    val.type_instance = str('Satoshi')
    val.dispatch(values=[feerate_in_satoshi])


def read_blockcount():
    proxy = new_proxy()
    # get size, height, diff of the last block
    response = proxy.getblockcount()
    blockcount = response
    # get hash of last block
    response = proxy.getblockhash(blockcount)
    blockhash = response
    # get info from blockhash
    response = proxy.getblock(blockhash)
    funcname = str('getblock')
    for subkey in ['size', 'height', 'difficulty']:
        funccat = (str(funcname) + '_' + str(subkey))
        value = response[subkey]
        val = collectd.Values(type='gauge',
                              host='',
                              plugin='bitcoind',
                              time=0)
        val.plugin_instance = funccat
        val.type_instance = subkey
        val.dispatch(values=[value])


def read_networkhashps():
    # network hashrate
    proxy = new_proxy()
    response = proxy.getnetworkhashps()
    funcname = str('getnetworkhashps')
    networkhashps = response
    val = collectd.Values(type='gauge',
                          host='',
                          plugin='bitcoind',
                          time=0)
    val.plugin_instance = funcname
    val.type_instance = funcname
    val.dispatch(values=[networkhashps])


def read_func():
    try:
        read_nettotals()
    except Exception:
        collectd.error('bitcoin plugin: exception reading nettotals value!')
        exc_type, exc_value, exc_traceback = sys.exc_info()
        collectd.error(repr(traceback.format_exception(exc_type, exc_value,
                                                       exc_traceback)))

    try:
        read_networkinfo()
    except Exception:
        collectd.error('bitcoin plugin: exception reading networkinfo!')
        exc_type, exc_value, exc_traceback = sys.exc_info()
        collectd.error(repr(traceback.format_exception(exc_type, exc_value,
                                                       exc_traceback)))

    try:
        read_mempoolinfo()
    except Exception:
        collectd.error('bitcoin plugin: exception reading mempoolinfo!')
        exc_type, exc_value, exc_traceback = sys.exc_info()
        collectd.error(repr(traceback.format_exception(exc_type, exc_value,
                                                       exc_traceback)))

    try:
        read_estimatesmartfee()
    except Exception:
        collectd.error('bitcoin plugin: exception reading estimatesmartfee!')
        exc_type, exc_value, exc_traceback = sys.exc_info()
        collectd.error(repr(traceback.format_exception(exc_type, exc_value,
                                                       exc_traceback)))

    try:
        read_blockcount()
    except Exception:
        collectd.error('bitcoin plugin: exception reading blockcount!')
        exc_type, exc_value, exc_traceback = sys.exc_info()
        collectd.error(repr(traceback.format_exception(exc_type, exc_value,
                                                       exc_traceback)))

    try:
        read_networkhashps()
    except Exception:
        collectd.error('bitcoin plugin: exception reading networkhasps!')
        exc_type, exc_value, exc_traceback = sys.exc_info()
        collectd.error(repr(traceback.format_exception(exc_type, exc_value,
                                                       exc_traceback)))

def main():
    print("Bitcoin Stats")
    print ("networkinfo: " + read_networkinfo())

if __name__ == '__main__':
    main()
