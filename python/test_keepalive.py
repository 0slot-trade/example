import time
import base58
import asyncio
import argparse
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.message import Message
from solders.system_program import TransferParams, transfer
from solana.rpc.async_api import AsyncClient

"""
HTTP Keep-Alive Explained
HTTP Keep-Alive is a mechanism that allows multiple HTTP requests/responses to be sent and received over a single TCP connection, rather than establishing a new connection for each request/response.

Basic Principles
Without Keep-Alive:
1. The client establishes a TCP connection with the server.
2. The client sends an HTTP request.
3. The server returns an HTTP response.
4. The TCP connection is closed.
5. The next request requires re-establishing a TCP connection.

With Keep-Alive:
1. The client establishes a TCP connection with the server.
2. The client sends HTTP Request 1.
3. The server returns HTTP Response 1.
4. The connection remains open.
5. The client sends HTTP Request 2.
6. The server returns HTTP Response 2.
... (can continue reusing the connection)
7. The connection is eventually closed.

Main Advantages
- Reduces TCP handshake overhead: Avoids the three-way handshake required to establish a new TCP connection for each request.
- Mitigates the impact of TCP slow start: Reusing an existing connection bypasses the TCP slow start phase.
- Reduces system resource consumption: Decreases the number of simultaneously open connections.
- Improves page load speed: Particularly beneficial for web pages requiring multiple resources.

About 0slot.trade
The maximum duration for a 0slot.trade keep is 65 seconds. It is recommended to perform an access approximately every 60 seconds.
This access is unrestricted in content—any request and any response will not affect the Keep-Alive.
For SDKs: You can call the RPC method getHealth, which will return a correct "OK."
For manual HTTP access: You can execute a GET request or omit the apk-key. The advantage is that this access does not count toward TPS calculations.

getHealth refers to the official HTTP RPC method provided by Solana.
https://solana.com/zh/docs/rpc/http/gethealth

python solana sdk is
AsyncClient.is_connected()

golang solana sdk is
rpc.GetHealth()

node.js solana sdk is
rpc.getHealth()

java solana sdk is
client.getApi().getHealth()

rust solana sdk is
rpcClient.get_health()
"""

async def send_solana_transaction(api_key, private_key, tip_key, to_public_key, keep):
    client_for_blockhash = AsyncClient(f"https://api.mainnet-beta.solana.com")
    client_for_send = AsyncClient(f"https://de.0slot.trade?api-key=" + api_key)

    latest_blockhash = await client_for_blockhash.get_latest_blockhash()
    await client_for_blockhash.close()

    sender = Keypair.from_bytes(base58.b58decode(private_key))
    receiver = Pubkey.from_string(to_public_key)
    tip_receiver = Pubkey.from_string(tip_key)

    main_transfer_instruction = transfer(TransferParams(from_pubkey = sender.pubkey(), to_pubkey = receiver, lamports = 1))
    # You need to transfer an amount greater than or equal to 0.0001 SOL to any of the following accounts:
    # 6fQaVhYZA4w3MBSXjJ81Vf6W1EDYeUPXpgVQ6UQyU1Av
    # 4HiwLEP2Bzqj3hM2ENxJuzhcPCdsafwiet3oGkMkuQY4
    # 7toBU3inhmrARGngC7z6SjyP85HgGMmCTEwGNRAcYnEK
    # 8mR3wB1nh4D6J9RUCugxUpc6ya8w38LPxZ3ZjcBhgzws
    # 6SiVU5WEwqfFapRuYCndomztEwDjvS5xgtEof3PLEGm9
    # TpdxgNJBWZRL8UXF5mrEsyWxDWx9HQexA9P1eTWQ42p
    # D8f3WkQu6dCF33cZxuAsrKHrGsqGP2yvAHf8mX6RXnwf
    # GQPFicsy3P3NXxB5piJohoxACqTvWE9fKpLgdsMduoHE
    # Ey2JEr8hDkgN8qKJGrLf2yFjRhW7rab99HVxwi5rcvJE
    # 4iUgjMT8q2hNZnLuhpqZ1QtiV8deFPy2ajvvjEpKKgsS
    # 3Rz8uD83QsU8wKvZbgWAPvCNDU6Fy8TSZTMcPm3RB6zt
    tip_transfer_instruction = transfer(TransferParams(from_pubkey = sender.pubkey(), to_pubkey = tip_receiver, lamports = 100000))
    message = Message.new_with_blockhash([main_transfer_instruction, tip_transfer_instruction], payer=sender.pubkey(), blockhash=latest_blockhash.value.blockhash)
    transaction = Transaction.new_unsigned(message)
    transaction.sign([sender], latest_blockhash.value.blockhash)

    try:
        """
        Here, for 'keep', after simulating multiple requests, the connection is maintained. It is recommended to execute client_for_send.is_connected() every 60 seconds. Note that executing client_for_send.is_connected() will also consume TPS.
        """
        if keep:
            await client_for_send.is_connected()
        start_time = time.perf_counter()
        result = await client_for_send.send_transaction(transaction)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"Transaction sent successfully in {elapsed_time:.4f} seconds")
        print("Transaction signature:", result.value)
    except Exception as e:
        print("Error:", str(e))
    finally:
        await client_for_send.close()

async def main():
    parser = argparse.ArgumentParser(description="Send a Solana transaction with speed test")
    parser.add_argument("--api_key", required=True, help="Solana API key for accessing the network.")
    parser.add_argument("--private_key", required=True, help="Sender's private key for signing the transaction.")
    parser.add_argument("--tip_key", required=True, help="Public key of the tip receiver.")
    parser.add_argument("--to_public_key", required=True, help="Public key of the main receiver.")
    args = parser.parse_args()

    await send_solana_transaction(args.api_key, args.private_key, args.tip_key, args.to_public_key, False)
    await send_solana_transaction(args.api_key, args.private_key, args.tip_key, args.to_public_key, True)

if __name__ == "__main__":
    asyncio.run(main())
