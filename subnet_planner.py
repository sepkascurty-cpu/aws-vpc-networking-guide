#!/usr/bin/env python3
"""Subnet planner for AWS VPCs.

Slices a VPC CIDR into public/private subnet pairs across N availability
zones, printing a ready-to-use layout plus usable host counts.

Usage:
    python3 subnet_planner.py --cidr 10.0.0.0/16 --azs 2 --bits 24
"""

import argparse
import ipaddress
import sys


def plan(vpc_cidr: str, azs: int, new_bits: int) -> list[dict]:
    """Return one public + one private subnet per AZ, in order."""
    vpc = ipaddress.ip_network(vpc_cidr, strict=True)
    if new_bits <= vpc.prefixlen:
        raise ValueError(f"--bits must be larger than VPC prefix /{vpc.prefixlen}")
    subnets = list(vpc.subnets(new_prefix=new_bits))
    needed = azs * 2
    if len(subnets) < needed:
        raise ValueError(
            f"/{new_bits} yields {len(subnets)} subnets, but {needed} are needed "
            f"({azs} AZs x public/private). Use a smaller --bits value."
        )
    plan_rows = []
    for az in range(azs):
        plan_rows.append({"az": az + 1, "type": "public", "cidr": str(subnets[az * 2])})
        plan_rows.append({"az": az + 1, "type": "private", "cidr": str(subnets[az * 2 + 1])})
    return plan_rows


def usable_hosts(prefix: int) -> int:
    # AWS reserves 5 addresses per subnet (network, VPC router, DNS, future use, broadcast)
    return max(2 ** (32 - prefix) - 5, 0)


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan AWS VPC subnets.")
    parser.add_argument("--cidr", default="10.0.0.0/16", help="VPC CIDR block")
    parser.add_argument("--azs", type=int, default=2, help="Number of AZs")
    parser.add_argument("--bits", type=int, default=24, help="Subnet prefix length")
    args = parser.parse_args()

    try:
        rows = plan(args.cidr, args.azs, args.bits)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"VPC {args.cidr}  ->  {args.azs} AZs x (public + private) at /{args.bits}\n")
    for row in rows:
        hosts = usable_hosts(args.bits)
        print(f"  az-{row['az']}  {row['type']:<7} {row['cidr']:<16} ({hosts} usable IPs)")
    print("\nTip: route public subnets to the IGW, private subnets to the NAT Gateway.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
