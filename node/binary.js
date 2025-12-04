const { Connection, Keypair, PublicKey, Transaction, SystemProgram, sendAndConfirmTransaction } = require('@solana/web3.js');
const bs58 = require('bs58');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

async function sendSolanaTransaction(apiKey, privateKey, tipKey, toPublicKey) {
    // Create two separate connections: one for fetching the latest blockhash and another for sending the transaction.
    const connectionForBlockhash = new Connection('https://api.mainnet-beta.solana.com', 'confirmed');

    // Fetch the latest blockhash from the Solana network.
    const { blockhash } = await connectionForBlockhash.getLatestBlockhash();

    // Decode the sender's private key from a base58-encoded string and create a Keypair object.
    const sender = Keypair.fromSecretKey(bs58.decode(privateKey));

    // Create PublicKey objects for the receiver and the tip receiver.
    const receiver = new PublicKey(toPublicKey);
    const tipReceiver = new PublicKey(tipKey);

    // Create transfer instructions for the main transfer and the tip transfer.
    const mainTransferInstruction = SystemProgram.transfer({
        fromPubkey: sender.publicKey,  // Sender's public key.
        toPubkey: receiver,            // Receiver's public key.
        lamports: 1                    // Amount to transfer (1 lamports).
    });
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
    const tipTransferInstruction = SystemProgram.transfer({
        fromPubkey: sender.publicKey,  // Sender's public key.
        toPubkey: tipReceiver,         // Tip receiver's public key.
        lamports: 1000000               // Amount to transfer as a tip (0.001 SOL in this case).
    });

    // Create a transaction containing the instructions.
    const transaction = new Transaction().add(mainTransferInstruction, tipTransferInstruction);

    // Set the recent blockhash and fee payer.
    transaction.recentBlockhash = blockhash;
    transaction.feePayer = sender.publicKey;

    // Sign the transaction with the sender's keypair.
    transaction.sign(sender);

    // Send the transaction to the Solana network.
    try {
        const transactionBuffer = Buffer.from(transaction.serialize());
        // prioritize using the ones provided by the sales team, as HTTP is more efficient than HTTPS
        const response = await fetch(`https://de.0slot.trade/txb?api-key=${apiKey}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'text/plain',
            },
            body: transactionBuffer
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const signature = await response.text();
        console.log('Transaction signature:', signature);  // Print the transaction signature if successful.
    } catch (error) {
        console.error('Error:', error);  // Print any errors that occur during the transaction process.
    }
}

async function main() {
    // Set up command-line argument parsing to accept required inputs.
    const argv = yargs(hideBin(process.argv))
        .option('api_key', { type: 'string', demandOption: true, describe: 'Solana API key for accessing the network.' })
        .option('private_key', { type: 'string', demandOption: true, describe: "Sender's private key for signing the transaction." })
        .option('tip_key', { type: 'string', demandOption: true, describe: 'Public key of the tip receiver.' })
        .option('to_public_key', { type: 'string', demandOption: true, describe: 'Public key of the main receiver.' })
        .argv;

    // Call the `sendSolanaTransaction` function with the provided arguments.
    await sendSolanaTransaction(argv.api_key, argv.private_key, argv.tip_key, argv.to_public_key);
}

main().catch(console.error);