use std::str::FromStr;

use bs58;
use base64;
use reqwest::Client;
use serde_json::json;
use solana_client::rpc_client::RpcClient;
use solana_sdk::{
    pubkey::Pubkey,
    signature::{Keypair, Signer},
    system_instruction,
    transaction::Transaction,
};
use structopt::StructOpt;
use tokio;

#[derive(Debug, StructOpt)]
#[structopt(
    name = "send_solana_transaction",
    about = "Send a Solana transaction with a tip."
)]
struct Opt {
    #[structopt(long, help = "Solana API key for accessing the network.")]
    api_key: String,

    #[structopt(long, help = "Sender's private key for signing the transaction.")]
    private_key: String,

    #[structopt(long, help = "Public key of the tip receiver.")]
    tip_key: String,

    #[structopt(long, help = "Public key of the main receiver.")]
    to_public_key: String,
}

async fn send_solana_transaction(
    api_key: &str,
    private_key: &str,
    tip_key: &str,
    to_public_key: &str,
) -> Result<(), Box<dyn std::error::Error>> {
    // Create a reqwest client
    let client = Client::new();

    // Create an RPC client for fetching the latest blockhash
    let connection_for_blockhash = RpcClient::new("https://api.mainnet-beta.solana.com".to_string());

    // Fetch the latest blockhash from the Solana network
    let blockhash = connection_for_blockhash
        .get_latest_blockhash()
        .expect("Failed to get latest blockhash");

    // Decode the sender's private key from a base58-encoded string and create a Keypair object
    let private_key_bytes = bs58::decode(private_key).into_vec().unwrap();
    let sender = Keypair::from_bytes(&private_key_bytes).unwrap();

    // Create PublicKey objects for the receiver and the tip receiver
    let receiver = Pubkey::from_str(to_public_key).unwrap();
    let tip_receiver = Pubkey::from_str(tip_key).unwrap();

    // Create transfer instructions for the main transfer and the tip transfer
    let main_transfer_instruction = system_instruction::transfer(
        &sender.pubkey(), // Sender's public key
        &receiver,        // Receiver's public key
        1,                // Amount to transfer (1 lamports)
    );
    // You need to transfer an amount greater than or equal to 0.001 SOL to any of the following accounts:
    // 4HiwLEP2Bzqj3hM2ENxJuzhcPCdsafwiet3oGkMkuQY4
    // 7toBU3inhmrARGngC7z6SjyP85HgGMmCTEwGNRAcYnEK
    // 8mR3wB1nh4D6J9RUCugxUpc6ya8w38LPxZ3ZjcBhgzws
    // 6SiVU5WEwqfFapRuYCndomztEwDjvS5xgtEof3PLEGm9
    // TpdxgNJBWZRL8UXF5mrEsyWxDWx9HQexA9P1eTWQ42p
    // D8f3WkQu6dCF33cZxuAsrKHrGsqGP2yvAHf8mX6RXnwf
    // GQPFicsy3P3NXxB5piJohoxACqTvWE9fKpLgdsMduoHE
    // Ey2JEr8hDkgN8qKJGrLf2yFjRhW7rab99HVxwi5rcvJE
    // 4iUgjMT8q2hNZnLuhpqZ1QtiV8deFPy2ajvvjEpKKgsS
    // 3Rz8uD83QsU8wKvZbgWAPvCNDU6Fy8TSZTMcPm3RB6zt
    let tip_transfer_instruction = system_instruction::transfer(
        &sender.pubkey(), // Sender's public key
        &tip_receiver,    // Tip receiver's public key
        1000000,           // Amount to transfer as a tip (0.001 SOL in this case)
    );

    // Create a transaction containing the instructions
    let mut transaction = Transaction::new_with_payer(
        &[main_transfer_instruction, tip_transfer_instruction],
        Some(&sender.pubkey()),
    );

    // Sign the transaction with the sender's keypair
    transaction.try_sign(&[&sender], blockhash).expect("Failed to sign transaction");

    // Serialize the transaction to a base64-encoded string
    let serialized_transaction = bincode::serialize(&transaction).unwrap();
    let base64_encoded_transaction = base64::encode(serialized_transaction);

    // Build the JSON-RPC request
    let request_body = json!({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "sendTransaction",
        "params": [
            base64_encoded_transaction,
            {
                "encoding": "base64",
                "skipPreflight": true,
            }
        ]
    });

    // Send the request
    let response = client.post(format!("https://de.0slot.trade?api-key={}", api_key))
        .json(&request_body)
        .send()
        .await?;

    // Parse the response
    let response_json: serde_json::Value = response.json().await?;
    if let Some(result) = response_json.get("result") {
        println!("Transaction sent successfully: {}", result);
    } else if let Some(error) = response_json.get("error") {
        eprintln!("Failed to send transaction: {}", error);
    }

    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let opt = Opt::from_args();

    send_solana_transaction(
        &opt.api_key,
        &opt.private_key,
        &opt.tip_key,
        &opt.to_public_key,
    )
    .await?;

    Ok(())
}