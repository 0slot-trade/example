package main

import (
	"context"
	"flag"
	"fmt"
	"log"

	"github.com/gagliardetto/solana-go"
	"github.com/gagliardetto/solana-go/programs/system"
	"github.com/gagliardetto/solana-go/rpc"
)

func main() {
	// Define command line arguments
	apiKey := flag.String("apiKey", "", "API Key for the Solana RPC service")
	yourPrivateKey := flag.String("yourPrivateKey", "", "Your private key")
	tipKey := flag.String("tipKey", "", "Tip key")
	toPublicKey := flag.String("toPublicKey", "", "Recipient's public key")

	// Parse command line arguments
	flag.Parse()

	// Check if all required parameters are provided
	if *apiKey == "" || *yourPrivateKey == "" || *tipKey == "" || *toPublicKey == "" {
		log.Fatalf("All parameters are required")
	}

	// Create a new client
	client := rpc.New("https://api.mainnet-beta.solana.com")

	// Sender's private key
	senderPrivateKey := solana.MustPrivateKeyFromBase58(*yourPrivateKey)
	senderPublicKey := senderPrivateKey.PublicKey()

	
	// tip public key
	tipPublicKey := solana.MustPublicKeyFromBase58(*tipKey)
	// Recipient's public key
	receiverPublicKey := solana.MustPublicKeyFromBase58(*toPublicKey)

	// Get the recent blockhash
	recentBlockhash, err := client.GetLatestBlockhash(context.Background(), rpc.CommitmentFinalized)
	if err != nil {
		log.Fatalf("failed to get recent blockhash: %v", err)
	}
	// You need to transfer an amount greater than or equal to 0.0001 SOL to any of the following accounts:
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
	tip_inst := system.NewTransferInstruction(100000, senderPublicKey, tipPublicKey).Build()

	// Create a transfer instruction
	instruction := system.NewTransferInstruction(1, senderPublicKey, receiverPublicKey).Build()

	// Create a transaction
	tx, err := solana.NewTransaction(
		[]solana.Instruction{tip_inst, instruction},
		recentBlockhash.Value.Blockhash,
		solana.TransactionPayer(senderPublicKey),
	)
	if err != nil {
		log.Fatalf("failed to create transaction: %v", err)
	}

	// Sign the transaction
	_, err = tx.Sign(
		func(key solana.PublicKey) *solana.PrivateKey {
			if key.Equals(senderPublicKey) {
				return &senderPrivateKey
			}
			return nil
		},
	)
	if err != nil {
		log.Fatalf("failed to sign transaction: %v", err)
	}

	// Create a new client
	zeroslot := rpc.New("https://de.0slot.trade?api-key=" + *apiKey)

	// Send the transaction
	txSig, err := zeroslot.SendTransactionWithOpts(
		context.Background(),
		tx,
		rpc.TransactionOpts{},
	)
	if err != nil {
		log.Fatalf("failed to send transaction: %v", err)
	}

	fmt.Printf("Transaction sent successfully. Signature: %s\n", txSig)
}
