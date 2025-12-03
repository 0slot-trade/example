package trade.zeroslot.example;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import org.p2p.solanaj.core.Account;
import org.p2p.solanaj.core.PublicKey;
import org.p2p.solanaj.core.Transaction;
import org.p2p.solanaj.programs.SystemProgram;
import org.p2p.solanaj.rpc.RpcClient;

public class ZeroSlotBinaryExample {

    private static final long LAMPORTS = 1000000l; //0.001
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

    public static void main(String[] args) throws Exception {
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

        // 创建OkHttpClient实例（推荐使用单例模式）
        OkHttpClient client = new OkHttpClient.Builder()
                .connectTimeout(10, java.util.concurrent.TimeUnit.SECONDS)
                .readTimeout(10, java.util.concurrent.TimeUnit.SECONDS)
                .writeTimeout(10, java.util.concurrent.TimeUnit.SECONDS)
                .build();

        long lamports = 1L;

        PublicKey fromPublicKey = new PublicKey(youPublicKey);
        Account signer = Account.fromBase58PrivateKey(youPrivateKey);
        PublicKey tipKey = new PublicKey(tipKeyStr);
        PublicKey toPublicKey = new PublicKey(toPublicKeyStr);

        // Create and populate the transaction
        Transaction transaction = new Transaction();
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
        transaction.addInstruction(SystemProgram.transfer(fromPublicKey, tipKey, LAMPORTS));
        // add your instruction
        transaction.addInstruction(SystemProgram.transfer(fromPublicKey, toPublicKey, lamports));

        // Get the recent block hash
        String blockHash = getRecentBlockHash();

        // Send the transaction and measure the time taken
        long startTime = System.currentTimeMillis();
//        String signature = client.getApi().sendTransaction(transaction, signer, blockHash);
        transaction.setRecentBlockHash(blockHash);
        transaction.sign(signer);
        byte[] serializedTransaction = transaction.serialize();
        RequestBody body = RequestBody.create(serializedTransaction);

        Request request = new Request.Builder()
                .url("https://de.0slot.trade/txb?api-key=" + apiKey)
                .post(body)
                .addHeader("Content-Type", "text/plain; charset=utf-8")
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                System.out.println("Unexpected code: " + response);
            } else {
                System.out.println(response.body().string());
            }
        }
        long endTime = System.currentTimeMillis();
        // Log the results
        System.out.println("sendTransaction time " + (endTime - startTime) + "ms");
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