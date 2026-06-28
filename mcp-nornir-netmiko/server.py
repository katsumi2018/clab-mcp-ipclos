from __future__ import annotations

import argparse
import os
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from nornir import InitNornir
from nornir.core.inventory import Host
from nornir.core.task import AggregatedResult, MultiResult
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config


NORNIR_CONFIG = os.getenv("NORNIR_CONFIG", "/app/inventory/config.yaml")
ALLOW_CONFIG = os.getenv("ALLOW_CONFIG", "false").lower() in {"1", "true", "yes", "on"}

mcp = FastMCP(
    "containerlab-nornir-netmiko",
    transport_security=TransportSecuritySettings(allowed_hosts=["127.0.0.1:*", "localhost:*", "[::1]:*", "192.168.0.192:*"]),
    instructions=(
        "Run read-only show commands against the mcp-ipclos containerlab devices "
        "through Nornir and Netmiko. Config changes are disabled unless "
        "ALLOW_CONFIG=true is set in the container environment."
    ),
)


def _nr():
    return InitNornir(config_file=NORNIR_CONFIG)


def _select_hosts(hosts: list[str] | None = None, groups: list[str] | None = None):
    nr = _nr()

    if hosts:
        missing = sorted(set(hosts) - set(nr.inventory.hosts))
        if missing:
            raise ValueError(f"Unknown host(s): {', '.join(missing)}")
        nr = nr.filter(filter_func=lambda host: host.name in hosts)

    if groups:
        nr = nr.filter(filter_func=lambda host: bool(set(groups) & {group.name for group in host.groups}))

    if not nr.inventory.hosts:
        raise ValueError("No hosts matched the requested filter.")

    return nr


def _host_summary(host: Host) -> dict[str, Any]:
    return {
        "name": host.name,
        "hostname": host.hostname,
        "platform": host.platform,
        "groups": [group.name for group in host.groups],
        "port": host.port,
        "username": host.username,
    }


def _result_to_dict(result: AggregatedResult) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for host_name, multi in result.items():
        host_items = []
        failed = False
        for item in multi:
            item_failed = bool(getattr(item, "failed", False))
            failed = failed or item_failed
            host_items.append(
                {
                    "name": item.name,
                    "failed": item_failed,
                    "changed": bool(getattr(item, "changed", False)),
                    "result": "" if item.result is None else str(item.result),
                    "exception": None if item.exception is None else repr(item.exception),
                }
            )
        output[host_name] = {"failed": failed or bool(multi.failed), "tasks": host_items}
    return output


@mcp.tool()
def list_hosts() -> dict[str, Any]:
    """List Nornir inventory hosts, platforms, and groups."""
    nr = _nr()
    return {"hosts": [_host_summary(host) for host in nr.inventory.hosts.values()]}


@mcp.tool()
def run_show(
    command: str,
    hosts: list[str] | None = None,
    groups: list[str] | None = None,
    read_timeout: int = 30,
) -> dict[str, Any]:
    """Run one operational/show command on selected hosts."""
    nr = _select_hosts(hosts=hosts, groups=groups)
    result = nr.run(
        task=netmiko_send_command,
        command_string=command,
        read_timeout=read_timeout,
    )
    return _result_to_dict(result)


def _run_one_command(task, command: str, read_timeout: int):
    return task.run(
        task=netmiko_send_command,
        name=command,
        command_string=command,
        read_timeout=read_timeout,
    )


@mcp.tool()
def run_show_commands(
    commands: list[str],
    hosts: list[str] | None = None,
    groups: list[str] | None = None,
    read_timeout: int = 30,
) -> dict[str, Any]:
    """Run multiple operational/show commands on selected hosts."""
    if not commands:
        raise ValueError("commands must not be empty.")

    nr = _select_hosts(hosts=hosts, groups=groups)
    result = nr.run(
        task=lambda task: [_run_one_command(task, command, read_timeout) for command in commands],
        name="run_show_commands",
    )
    return _result_to_dict(result)


@mcp.tool()
def run_config(
    commands: list[str],
    hosts: list[str],
) -> dict[str, Any]:
    """Run configuration commands. Disabled unless ALLOW_CONFIG=true."""
    if not ALLOW_CONFIG:
        return {
            "failed": True,
            "error": "Configuration changes are disabled. Set ALLOW_CONFIG=true to enable this tool.",
        }
    if not commands:
        raise ValueError("commands must not be empty.")
    if not hosts:
        raise ValueError("hosts must be specified for config changes.")

    nr = _select_hosts(hosts=hosts)
    result = nr.run(task=netmiko_send_config, config_commands=commands)
    return _result_to_dict(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["stdio", "sse", "streamable-http"], default=os.getenv("MCP_TRANSPORT", "stdio"))
    parser.add_argument("--host", default=os.getenv("MCP_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("MCP_PORT", "8000")))
    args = parser.parse_args()

    # FastMCP keeps host/port in settings for SSE transport in current Python SDKs.
    if hasattr(mcp, "settings"):
        mcp.settings.host = args.host
        mcp.settings.port = args.port

    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
