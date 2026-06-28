# containerlab Nornir + Netmiko MCP server

This MCP server exposes Nornir/Netmiko tools for the `mcp-ipclos` lab.

Tools:

- `list_hosts`: show inventory hosts.
- `run_show`: run one operational command.
- `run_show_commands`: run multiple operational commands.
- `run_config`: run configuration commands only when `ALLOW_CONFIG=true`.

Default transport is SSE on `0.0.0.0:8000`.

Example Docker run:

```bash
docker build -t mcp-nornir-netmiko:latest .
docker run --rm -p 8000:8000 --network clab-mgmt mcp-nornir-netmiko:latest
```
