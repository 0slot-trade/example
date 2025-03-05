The usage of the staked_conn interface is similar to the RPC interface, primarily providing the sendTransaction method, which directly connects to our validator node.

When calling the sendTransaction method of staked_conn, please note the following:

- A maximum of 5 calls per second is allowed.
- You need to transfer an amount greater than or equal to 0.0001 SOL to any of the following accounts:
  - 4HiwLEP2Bzqj3hM2ENxJuzhcPCdsafwiet3oGkMkuQY4
  - 7toBU3inhmrARGngC7z6SjyP85HgGMmCTEwGNRAcYnEK
  - 8mR3wB1nh4D6J9RUCugxUpc6ya8w38LPxZ3ZjcBhgzws
  - 6SiVU5WEwqfFapRuYCndomztEwDjvS5xgtEof3PLEGm9
  - TpdxgNJBWZRL8UXF5mrEsyWxDWx9HQexA9P1eTWQ42p
  - D8f3WkQu6dCF33cZxuAsrKHrGsqGP2yvAHf8mX6RXnwf
  - GQPFicsy3P3NXxB5piJohoxACqTvWE9fKpLgdsMduoHE
  - Ey2JEr8hDkgN8qKJGrLf2yFjRhW7rab99HVxwi5rcvJE
  - 4iUgjMT8q2hNZnLuhpqZ1QtiV8deFPy2ajvvjEpKKgsS
  - 3Rz8uD83QsU8wKvZbgWAPvCNDU6Fy8TSZTMcPm3RB6zt

### Special Error Codes ###

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

### Example ###

Add an instruction to the Transaction (preferably inserted at the beginning):
```javascript
transaction.addInstruction(fromPublicKey, '6fQaVhYZA4w3MBSXjJ81Vf6W1EDYeUPXpgVQ6UQyU1Av', 100000);
```

We hope the above information helps you better understand and use the staked_conn interface. If you have any questions, please feel free to contact our support team.

Multilingual examples, including Rust, Java, Go, Python, node, how to use the 0slot service
