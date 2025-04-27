import base58
import asyncio
import argparse
from solders.hash import Hash
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.message import Message
from solders.transaction import Transaction
from solders.system_program import TransferParams, transfer
from solana.rpc.async_api import AsyncClient

async def send_solana_transaction(api_key, private_key, nonce_public_key, to_public_key):
    # Initialize clients for different regions
    client_for_blockhash = AsyncClient(f"https://api.mainnet-beta.solana.com")
    de_sender = AsyncClient(f"https://de.0slot.trade?api-key=" + api_key)  # Germany endpoint
    ny_sender = AsyncClient(f"https://ny.0slot.trade?api-key=" + api_key)  # New York endpoint

    # Create keypair from private key
    sender = Keypair.from_bytes(base58.b58decode(private_key))

    # Main recipient address
    receiver = Pubkey.from_string(to_public_key)
    # Our TIP receiving addresses - using different addresses for DE and NY to simulate multiple Landing Services
    de_tip_receiver = Pubkey.from_string("6fQaVhYZA4w3MBSXjJ81Vf6W1EDYeUPXpgVQ6UQyU1Av")
    ny_tip_receiver = Pubkey.from_string("4HiwLEP2Bzqj3hM2ENxJuzhcPCdsafwiet3oGkMkuQY4")
    # Nonce account public key created by sender - must be associated
    # solana-keygen new -o nonce-account.json
    # solana -k sender.json create-nonce-account nonce-account.json 0.0015
    nonce_account_pubkey = Pubkey.from_string(nonce_public_key)

    # Get nonce account info to extract the current nonce value
    get_account_resp = await client_for_blockhash.get_account_info(nonce_account_pubkey)
    await client_for_blockhash.close()

    # The nonce is stored in the account data at bytes 40-72
    # This matches the Rust NonceState structure layout:
    # struct NonceState {
    #     version: u32,          // 4 bytes (offset 0-3)
    #     state: u32,            // 4 bytes (offset 4-7)
    #     authorized_pubkey: Pubkey,  // 32 bytes (offset 8-39)
    #     nonce: Pubkey,         // 32 bytes (offset 40-71) ← we need this
    #     fee_calculator: FeeCalculator,  // 8 bytes (offset 72-79)
    # }
    nonce = get_account_resp.value.data[40:72]
    nonce_hash = Hash.from_bytes(nonce)

    # Create transaction instructions for Germany endpoint
    # Includes:
    # 1. Main transfer (1 lamport)
    # 2. Tip transfer (1,000,000 lamports = 0.001 SOL)
    de_instructions = [
        transfer(
            TransferParams(
                from_pubkey=sender.pubkey(),
                to_pubkey=receiver,
                lamports=1
            )
        ),
        transfer(
            TransferParams(
                from_pubkey=sender.pubkey(),
                to_pubkey=de_tip_receiver,
                lamports=1000000
            )
        )
    ]
    
    # Create transaction instructions for New York endpoint (same structure)
    ny_instructions = [
        transfer(
            TransferParams(
                from_pubkey=sender.pubkey(),
                to_pubkey=receiver,
                lamports=1
            )
        ),
        transfer(
            TransferParams(
                from_pubkey=sender.pubkey(),
                to_pubkey=ny_tip_receiver,
                lamports=100000
            )
        )
    ]
    
    # Create messages with nonce for each transaction
    de_message = Message.new_with_nonce(
        de_instructions,
        payer=sender.pubkey(),
        nonce_account_pubkey=nonce_account_pubkey,
        nonce_authority_pubkey=sender.pubkey(),
    )
    ny_message = Message.new_with_nonce(
        ny_instructions,
        payer=sender.pubkey(),
        nonce_account_pubkey=nonce_account_pubkey,
        nonce_authority_pubkey=sender.pubkey(),
    )

    # Create unsigned transactions
    de_transaction = Transaction.new_unsigned(de_message)
    ny_transaction = Transaction.new_unsigned(ny_message)

    # Sign transactions with the same nonce
    de_transaction.sign([sender], nonce_hash)
    ny_transaction.sign([sender], nonce_hash)

    try:
        # Send both transactions concurrently using asyncio
        de_task = de_sender.send_transaction(de_transaction)
        ny_task = ny_sender.send_transaction(ny_transaction)
        results = await asyncio.gather(
            de_task,
            ny_task,
            return_exceptions=True  # Don't fail if one transaction fails
        )
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Error sending to {'DE' if i == 0 else 'NY'}: {str(result)}")
            else:
                print(f"Transaction signature ({'DE' if i == 0 else 'NY'}):", result.value)
    except Exception as e:
        print("Error:", str(e))
    finally:
        # Clean up connections
        await de_sender.close()
        await ny_sender.close()

async def main():
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description="Send a Solana transaction")
    parser.add_argument("--api_key", required=True, help="Solana API key for accessing the network.")
    parser.add_argument("--private_key", required=True, help="Sender's private key for signing the transaction.")
    parser.add_argument("--nonce_public_key", required=True, help="Sender's nonce account public key")
    parser.add_argument("--to_public_key", required=True, help="Public key of the main receiver.")

    args = parser.parse_args()

    await send_solana_transaction(
        args.api_key,
        args.private_key,
        args.nonce_public_key,
        args.to_public_key,
    )

if __name__ == "__main__":
    asyncio.run(main())
