# Quickstart

## `staked_conn` interface
The `staked_conn` interface is similar to the RPC interface, primarily providing the `sendTransaction` method, which directly connects to our validator node.

**When calling the `sendTransaction` method of `staked_conn`, please note:**
- A maximum of **5 calls per second** is allowed.
- You need to transfer an amount **greater than or equal to 0.001 SOL** to one of the following accounts:
  - `6fQaVhYZA4w3MBSXjJ81Vf6W1EDYeUPXpgVQ6UQyU1Av` (0slot_dot_trade.sol)
  - `4HiwLEP2Bzqj3hM2ENxJuzhcPCdsafwiet3oGkMkuQY4`(0slot_dot_trade_tip15.sol)
  - `7toBU3inhmrARGngC7z6SjyP85HgGMmCTEwGNRAcYnEK`(0slot_dot_trade_tip16.sol)
  - `8mR3wB1nh4D6J9RUCugxUpc6ya8w38LPxZ3ZjcBhgzws`(0slot_dot_trade_tip17.sol)
  - `6SiVU5WEwqfFapRuYCndomztEwDjvS5xgtEof3PLEGm9`(0slot_dot_trade_tip18.sol)
  - `TpdxgNJBWZRL8UXF5mrEsyWxDWx9HQexA9P1eTWQ42p`(0slot_dot_trade_tip19.sol)
  - `D8f3WkQu6dCF33cZxuAsrKHrGsqGP2yvAHf8mX6RXnwf`(0slot_dot_trade_tip20.sol)
  - `GQPFicsy3P3NXxB5piJohoxACqTvWE9fKpLgdsMduoHE`(0slot_dot_trade_tip21.sol)
  - `Ey2JEr8hDkgN8qKJGrLf2yFjRhW7rab99HVxwi5rcvJE`(0slot_dot_trade_tip22.sol)
  - `4iUgjMT8q2hNZnLuhpqZ1QtiV8deFPy2ajvvjEpKKgsS`(0slot_dot_trade_tip23.sol)
  - `3Rz8uD83QsU8wKvZbgWAPvCNDU6Fy8TSZTMcPm3RB6zt`(0slot_dot_trade_tip24.sol)

## Example for `cmd: curl`:
```bash
curl -X POST 'https://ny.0slot.trade?api-key=$TOKEN' \
-d '{
    "jsonrpc": "2.0",
    "id": $UUID,
    "method": "sendTransaction",
    "params": [ 
        "<base64_encoded_tx>",
        { "encoding": "base64" }
    ] 
}'
```

For better performance and faster speeds, you can test and select the most suitable servers to use
- **New York**: `ny.0slot.trade`
- **Frankfurt**: `de.0slot.trade`
- **Amsterdam**: `ams.0slot.trade`
- **Tokyo**: `jp.0slot.trade`
- **Los Angeles**: `la.0slot.trade`

**You can also contact our sales or technical support team to obtain the servers that best suits your needs.**

## Response: Special Error Codes

- **API Key Expired**
```json
{"id":"1","jsonrpc":"2.0","error":{"code":403,"message":"API key has expired"}}
  ```

- **Non-sendTransaction Method**
```json
{"id":"1","jsonrpc":"2.0","error":{"code":403,"message":"Invalid method"}}
  ```

- **Rate Limit Exceeded**
```json
{"id":"1","jsonrpc":"2.0","error":{"code":419,"message":"Rate limit exceeded"}}
```

## Example

Add an instruction to the Transaction (preferably inserted at the beginning):
```javascript
transaction.addInstruction(SystemProgram.transfer(fromPublicKey, '6fQaVhYZA4w3MBSXjJ81Vf6W1EDYeUPXpgVQ6UQyU1Av', 1000000));
```

We hope the above information helps you better understand and use the staked_conn interface. If you have any questions, please feel free to contact our support team.

Multilingual examples, including Rust, Java, Go, Python, node, how to use the 0slot service
