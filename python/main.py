import asyncio
import argparse
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.message import Message
from solders.system_program import TransferParams, transfer
from solana.rpc.async_api import AsyncClient
import base58

async def send_solana_transaction(api_key, private_key, tip_key, to_public_key):
    # Create two separate clients: one for fetching the latest blockhash and another for sending the transaction.
    client_for_blockhash = AsyncClient(f"https://api.mainnet-beta.solana.com")
    client_for_send = AsyncClient(f"https://de1.0slot.trade?api-key=" + api_key)

    # Fetch the latest blockhash from the Solana network.
    latest_blockhash = await client_for_blockhash.get_latest_blockhash()
    await client_for_blockhash.close()  # Close the blockhash client after fetching the data.

    # Decode the sender's private key from a base58-encoded string and create a Keypair object.
    sender = Keypair.from_bytes(base58.b58decode(private_key))

    # Create Pubkey objects for the receiver and the tip receiver.
    receiver = Pubkey.from_string(to_public_key)
    tip_receiver = Pubkey.from_string(tip_key)

    # Create transfer instructions for the main transfer and the tip transfer.
    main_transfer_instruction = transfer(
        TransferParams(
            from_pubkey=sender.pubkey(),  # Sender's public key.
            to_pubkey=receiver,           # Receiver's public key.
            lamports=1                    # Amount to transfer (1 lamports).
        )
    )
    # You need to transfer an amount greater than or equal to 0.0001 SOL to any of the following accounts:
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
    tip_transfer_instruction = transfer(
        TransferParams(
            from_pubkey=sender.pubkey(),  # Sender's public key.
            to_pubkey=tip_receiver,       # Tip receiver's public key.
            lamports=100000               # Amount to transfer as a tip (0.0001 SOL in this case).
        )
    )

    # Create a message containing the instructions.
    # The message is required to construct the transaction.
    message = Message.new_with_blockhash(
        [main_transfer_instruction, tip_transfer_instruction],  # List of instructions.
        payer=sender.pubkey(),                                  # Payer's public key.
        blockhash=latest_blockhash.value.blockhash              # Recent blockhash.
    )

    # Create a transaction using the message and the sender's keypair.
    transaction = Transaction.new_unsigned(message)

    # Sign the transaction with the sender's keypair.
    transaction.sign([sender], latest_blockhash.value.blockhash)

    # Send the transaction to the Solana network.
    try:
        result = await client_for_send.send_transaction(transaction)
        print("Transaction signature:", result.value)  # Print the transaction signature if successful.
    except Exception as e:
        print("Error:", str(e))  # Print any errors that occur during the transaction process.
    await client_for_send.close()  # Close the send client after the transaction is complete.

async def main():
    # Set up command-line argument parsing to accept required inputs.
    parser = argparse.ArgumentParser(description="Send a Solana transaction")
    parser.add_argument("--api_key", required=True, help="Solana API key for accessing the network.")
    parser.add_argument("--private_key", required=True, help="Sender's private key for signing the transaction.")
    parser.add_argument("--tip_key", required=True, help="Public key of the tip receiver.")
    parser.add_argument("--to_public_key", required=True, help="Public key of the main receiver.")

    # Parse the command-line arguments.
    args = parser.parse_args()

    # Call the `send_solana_transaction` function with the provided arguments.
    await send_solana_transaction(
        args.api_key,
        args.private_key,
        args.tip_key,
        args.to_public_key,
    )

if __name__ == "__main__":
    # Run the `main` function asynchronously using asyncio.
    asyncio.run(main())
