# L3 Egress Enforcement Design Note

L3 is a network-layer backstop for agent workspaces. Unlike L1 prompt constraints and L2 AST auditing, it is not implemented inside the LLM agent loop. The policy is enforced by an external egress gateway, switch, secure web gateway, or transparent proxy that validates outbound TLS behavior independently of the generated application code.

## Intended Behavior

The egress control should block outbound connections when the remote endpoint presents an invalid TLS certificate, including:

- self-signed certificates not anchored in the workspace trust policy,
- hostname mismatch,
- untrusted local issuer,
- protocol confusion on a TLS-designated port.

When possible, the gateway should return a clear policy failure rather than silently dropping packets. Clear feedback helps prevent agents from misattributing the event to transient network instability and retrying indefinitely.

## Release Scope

This artifact does not include a production switch or gateway implementation. The paper's L3 evaluation used local infrastructure controls outside the Python benchmark code. For release, we document the enforcement point and expected behavior without publishing environment-specific network configuration.

## Minimal Pseudocode

```text
for each outbound TLS connection:
    inspect server certificate and handshake metadata
    if certificate chain or hostname validation fails:
        terminate the connection
        return a policy error to the sandbox when supported
    otherwise:
        allow the connection
```

## Relationship to L1/L2

L3 provides the strongest physical guarantee because it does not rely on the model respecting prompts or on static rules matching every code pattern. In practice it should be deployed with L1/L2-style feedback so the agent receives a deterministic security explanation instead of treating the block as ordinary network friction.
