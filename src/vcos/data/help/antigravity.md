# Connecting to Antigravity

Antigravity is your strategic AI agent. You can hook it up to your VCoS memory to give it full context on your project history and advisory style.

## 1. Get the Config
Run this command in your terminal:
```bash
vcos config mcp
```

## 2. Update Antigravity Config
- Find your `mcp_config.json` used by Antigravity.
- Add the `vcos-memory` server block provided by the command above.

## 3. Use Antigravity as a Chief of Staff
Once connected, you can give Antigravity higher-level strategic complex tasks like:
> "Antigravity, review my recent meeting notes in VCoS and suggest a strategy for the next SCEH phase."

Antigravity will use `vcos retrieve` and `vcos compose` internally to build its response.
