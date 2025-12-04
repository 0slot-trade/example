package main

import (
	"bytes"
	"context"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"

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
	tip_inst := system.NewTransferInstruction(1000000, senderPublicKey, tipPublicKey).Build()

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
	zeroTxSignArr, err := tx.Sign(
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

	httpClient := &http.Client{
		Transport: &http.Transport{
			MaxIdleConns:        7,
			MaxIdleConnsPerHost: 3,
			IdleConnTimeout:     410 * time.Second,
		},
		Timeout: 30 * time.Second,
	}

	// prioritize using the ones provided by the sales team, as HTTP is more efficient than HTTPS
	zeroslot := "https://de.0slot.trade/txb?api-key=" + *apiKey

	//"keepalive_timeout" is configured to 415 seconds. As long as the access frequency does not exceed 415 seconds, no separate call is needed.
	keepAlived(context.Background(), httpClient, "https://de.0slot.trade/health")

	// Send the transaction
	sendBinaryTx(context.Background(), httpClient, zeroslot, tx)

	fmt.Printf("Transaction sent successfully %v\n", zeroTxSignArr[0])
}

func keepAlived(ctx context.Context, client *http.Client, nozomiEndpoint string) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, nozomiEndpoint, nil)
	if err != nil {
		fmt.Printf("failed to create request: %v", err)
	}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("failed to send transaction: %v", err)
	}
	defer resp.Body.Close()
}

func sendBinaryTx(ctx context.Context, client *http.Client, nozomiEndpoint string, tx *solana.Transaction) {
	txBytes, err := tx.MarshalBinary()
	if err != nil {
		fmt.Printf("failed to marshal transaction: %v", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, nozomiEndpoint, bytes.NewBuffer(txBytes))
	if err != nil {
		fmt.Printf("failed to create request: %v", err)
	}
	req.Header = http.Header{}
	req.Header.Set("User-Agent", "")

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("failed to send transaction: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		body, _ := io.ReadAll(resp.Body)
		fmt.Printf("code %d, body %s", resp.StatusCode, string(body))
	}

}
