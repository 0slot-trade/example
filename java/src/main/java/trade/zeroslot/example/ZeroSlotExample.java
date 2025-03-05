package trade.zeroslot.example;

import org.p2p.solanaj.core.Account;
import org.p2p.solanaj.core.PublicKey;
import org.p2p.solanaj.core.Transaction;
import org.p2p.solanaj.programs.SystemProgram;
import org.p2p.solanaj.rpc.RpcClient;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * ZeroSlotExample demonstrates concurrent Solana transactions using multiple RPC endpoints.
 * It showcases how to send transactions with minimal latency across different geographic locations.
 */
public class ZeroSlotExample {

    private static final int NUM_THREADS = 3;
    private static final long LAMPORTS = 100000l; //0.0001
    private static String apiKey;
    private static String rpcUrl;

    /**
     * Public key of the transaction sender
     */
    private static String youPublicKey;

    /**
     * Private key of the transaction sender
     */
    private static String youPrivateKey;

    /**
     * Public key for the tip recipient
     */
    private static String tipKeyStr;
    private static String toPublicKeyStr;

    public static void main(String[] args) {
        if (args.length != 6) {
            System.out.println("Command line arguments: [apiKey, rpcUrl, yourPublicKey, yourPrivateKey, tipKey, toPublicKey]");
            return;
        }
        apiKey = args[0];
        rpcUrl = args[1];
        youPublicKey = args[2];
        youPrivateKey = args[3];
        tipKeyStr = args[4];
        toPublicKeyStr = args[5];

        // Set up thread pool and synchronization primitives
        ExecutorService executor = Executors.newFixedThreadPool(NUM_THREADS);
        CountDownLatch startSignal = new CountDownLatch(1);
        CountDownLatch doneSignal = new CountDownLatch(NUM_THREADS);
        long lamports = 1L;

        // Add executors for different geographic endpoints
        addExecutor(executor, startSignal, doneSignal, "de.0slot.trade", "https://de.0slot.trade?api-key=" + apiKey, ++lamports);
        addExecutor(executor, startSignal, doneSignal, "ny.0slot.trade", "https://ny.0slot.trade?api-key=" + apiKey, ++lamports);
        addExecutor(executor, startSignal, doneSignal, "ams.0slot.trade", "https://ams.0slot.trade?api-key=" + apiKey, ++lamports);

        try {
            System.out.println("Starting all threads...");
            startSignal.countDown(); // Signal all threads to start
            doneSignal.await(); // Wait for all threads to complete
        } catch (InterruptedException e) {
            e.printStackTrace();
        } finally {
            executor.shutdown();
        }
    }

    /**
     * Adds a new executor to the thread pool for sending a transaction.
     *
     * @param executor    The ExecutorService to submit the task to
     * @param startSignal CountDownLatch for synchronizing the start of all threads
     * @param doneSignal  CountDownLatch for tracking completion of all threads
     * @param name        Name identifier for the executor (typically the endpoint name)
     * @param url         The RPC endpoint URL
     * @param lamports    The amount of lamports to transfer in the transaction
     */
    private static void addExecutor(ExecutorService executor, CountDownLatch startSignal, CountDownLatch doneSignal, String name, String url, long lamports) {
        executor.submit(() -> {
            try {
                // Initialize RPC client and transaction details
                RpcClient client = new RpcClient(url);
                PublicKey fromPublicKey = new PublicKey(youPublicKey);
                Account signer = Account.fromBase58PrivateKey(youPrivateKey);
                PublicKey tipKey = new PublicKey(tipKeyStr);
                PublicKey toPublicKey = new PublicKey(toPublicKeyStr);

                // Create and populate the transaction
                Transaction transaction = new Transaction();
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
                transaction.addInstruction(SystemProgram.transfer(fromPublicKey, tipKey, LAMPORTS));
                // add your instruction
                transaction.addInstruction(SystemProgram.transfer(fromPublicKey, toPublicKey, lamports));

                // Get the recent block hash
                String blockHash = getRecentBlockHash();

                // Wait for the start signal
                startSignal.await();

                // Send the transaction and measure the time taken
                long startTime = System.currentTimeMillis();
                String signature = client.getApi().sendTransaction(transaction, signer, blockHash);
                long endTime = System.currentTimeMillis();

                // Log the results
                System.out.println(name + " " + signature);
                System.out.println(name + " sendTransaction time " + (endTime - startTime) + "ms");
            } catch (Exception e) {
                e.printStackTrace();
            } finally {
                doneSignal.countDown();
            }
        });
    }

    /**
     * Retrieves the most recent block hash from the main RPC endpoint.
     *
     * @return The recent block hash as a String
     * @throws Exception If there's an error retrieving the block hash
     */
    private static String getRecentBlockHash() throws Exception {
        RpcClient client = new RpcClient(rpcUrl);
        return client.getApi().getLatestBlockhash().getValue().getBlockhash();
    }
}