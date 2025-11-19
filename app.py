#!/usr/bin/env python3
import argparse
import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, List


@dataclass
class AuditTrack:
    key: str
    name: str
    base_days: float
    description: str


TRACKS: Dict[str, AuditTrack] = {
    "protocol": AuditTrack(
        key="protocol",
        name="Protocol & Soundness Review",
        base_days=10.0,
        description="Core protocol logic, liveness & safety properties, invariants.",
    ),
    "circuits": AuditTrack(
        key="circuits",
        name="Circuits / Crypto Review",
        base_days=12.0,
        description="ZK/FHE circuits, gadgets, and cryptographic assumptions.",
    ),
    "implementation": AuditTrack(
        key="implementation",
        name="Implementation Review",
        base_days=14.0,
        description="Smart contracts, on-chain logic, and critical off-chain components.",
    ),
    "infra": AuditTrack(
        key="infra",
        name="Infrastructure & DevOps Review",
        base_days=6.0,
        description="RPC, sequencers, key management, monitoring, and ops runbooks.",
    ),
    "governance": AuditTrack(
        key="governance",
        name="Governance & Upgradeability Review",
        base_days=4.0,
        description="Admin keys, upgrade paths, governance contracts and voting logic.",
    ),
}


@dataclass
class StyleProfile:
    key: str
    name: str
    description: str
    protocol_multiplier: float
    circuits_multiplier: float
    impl_multiplier: float
    infra_multiplier: float
    gov_multiplier: float


STYLES: Dict[str, StyleProfile] = {
    "aztec": StyleProfile(
        key="aztec",
        name="Aztec-style privacy rollup",
        description="Privacy-first zk rollup with encrypted state and complex circuits.",
        protocol_multiplier=1.2,
        circuits_multiplier=1.5,
        impl_multiplier=1.15,
        infra_multiplier=1.1,
        gov_multiplier=1.0,
    ),
    "zama": StyleProfile(
        key="zama",
        name="Zama-style FHE compute stack",
        description="FHE-heavy stack where on-chain code interacts with encrypted compute.",
        protocol_multiplier=1.15,
        circuits_multiplier=1.6,
        impl_multiplier=1.1,
        infra_multiplier=1.15,
        gov_multiplier=1.0,
    ),
    "soundness": StyleProfile(
        key="soundness",
        name="Soundness-first research lab",
        description="Specification-driven protocols with an emphasis on formal soundness.",
        protocol_multiplier=1.4,
        circuits_multiplier=1.2,
        impl_multiplier=1.1,
        infra_multiplier=1.0,
        gov_multiplier=1.1,
    ),
}


def compute_audit_plan(
    style: StyleProfile,
    uses_zk: bool,
    uses_fhe: bool,
    has_bridge: bool,
    has_governance: bool,
    multi_chain: bool,
    team_size: int,
    maturity: str,
) -> Dict[str, Any]:
    # Start with style-based multipliers
    base_days: Dict[str, float] = {}
    for key, track in TRACKS.items():
        if key == "protocol":
            mult = style.protocol_multiplier
        elif key == "circuits":
            mult = style.circuits_multiplier
        elif key == "implementation":
            mult = style.impl_multiplier
        elif key == "infra":
            mult = style.infra_multiplier
        elif key == "governance":
            mult = style.gov_multiplier
        else:
            mult = 1.0
        base_days[key] = track.base_days * mult

    # Feature-based adjustments
    if uses_zk:
        base_days["circuits"] *= 1.25
    if uses_fhe:
        base_days["circuits"] *= 1.25
        base_days["infra"] *= 1.15
    if has_bridge:
        base_days["protocol"] *= 1.20
        base_days["implementation"] *= 1.15
    if multi_chain:
        base_days["infra"] *= 1.20
        base_days["protocol"] *= 1.10
    if has_governance:
        base_days["governance"] *= 1.5

    # Project maturity (idea/prototype/mainnet)
    maturity_factors = {
        "idea": 0.7,
        "prototype": 1.0,
        "mainnet": 1.2,
    }
    m_factor = maturity_factors.get(maturity, 1.0)
    for k in base_days:
        base_days[k] *= m_factor

    # Very small or very large teams influence throughput rather than risk
    # Treat this as a mild scaling factor
    if team_size <= 3:
        team_factor = 0.9
    elif team_size <= 8:
        team_factor = 1.0
    else:
        team_factor = 1.1

    for k in base_days:
        base_days[k] *= team_factor

    # Round and build structured tracks
    tracks_out: List[Dict[str, Any]] = []
    total_days = 0.0
    for key, track in TRACKS.items():
        days = round(base_days[key], 1)
        total_days += days
        tracks_out.append(
            {
                "key": key,
                "name": track.name,
                "description": track.description,
                "estimatedDays": days,
            }
        )

    tracks_out.sort(key=lambda t: t["estimatedDays"], reverse=True)

    # Suggested order: protocol → circuits → implementation → infra → governance
    key_order = ["protocol", "circuits", "implementation", "infra", "governance"]
    suggested_order = [k for k in key_order if any(t["key"] == k for t in tracks_out)]

    return {
        "style": style.key,
        "styleName": style.name,
        "styleDescription": style.description,
        "usesZk": uses_zk,
        "usesFhe": uses_fhe,
        "hasBridge": has_bridge,
        "hasGovernance": has_governance,
        "multiChain": multi_chain,
        "teamSize": team_size,
        "maturity": maturity,
        "tracks": tracks_out,
        "totalEstimatedDays": round(total_days, 1),
        "suggestedOrder": suggested_order,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="web3_audit_scope_planner",
        description=(
            "Estimate audit tracks and effort for a Web3 project inspired by Aztec-style zk rollups, "
            "Zama-style FHE systems, and soundness-focused protocol labs."
        ),
    )
    parser.add_argument(
        "--style",
        choices=list(STYLES.keys()),
        default="aztec",
        help="Base design style (aztec, zama, soundness).",
    )
    parser.add_argument(
        "--zk",
        action="store_true",
        help="Project uses zk-proofs for core logic or privacy.",
    )
    parser.add_argument(
        "--fhe",
        action="store_true",
        help="Project uses fully homomorphic encryption (FHE).",
    )
    parser.add_argument(
        "--bridge",
        action="store_true",
        help="Project includes a bridge or cross-chain messaging.",
    )
    parser.add_argument(
        "--governance",
        action="store_true",
        help="Project includes governance or upgradeability logic.",
    )
    parser.add_argument(
        "--multi-chain",
        action="store_true",
        help="Project targets multiple chains or rollups.",
    )
    parser.add_argument(
        "--team-size",
        type=int,
        default=5,
        help="Approximate number of engineers working on the core system (default: 5).",
    )
    parser.add_argument(
        "--maturity",
        choices=["idea", "prototype", "mainnet"],
        default="prototype",
        help="Stage of the project (idea, prototype, mainnet).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON instead of human-readable summary.",
    )
    return parser.parse_args()


def print_human(plan: Dict[str, Any]) -> None:
    print("🧮 web3_audit_scope_planner")
    print(f"Base style     : {plan['styleName']} ({plan['style']})")
    print(f"Description    : {plan['styleDescription']}")
    print("")
    print("Project flags:")
    print(f"  Uses zk-proofs        : {'yes' if plan['usesZk'] else 'no'}")
    print(f"  Uses FHE              : {'yes' if plan['usesFhe'] else 'no'}")
    print(f"  Has bridge            : {'yes' if plan['hasBridge'] else 'no'}")
    print(f"  Has governance        : {'yes' if plan['hasGovernance'] else 'no'}")
    print(f"  Multi-chain           : {'yes' if plan['multiChain'] else 'no'}")
    print(f"  Team size             : {plan['teamSize']}")
    print(f"  Maturity              : {plan['maturity']}")
    print("")
    print(f"Total estimated audit effort: {plan['totalEstimatedDays']:.1f} person-days")
    print("")
    print("Tracks (descending effort):")
    for t in plan["tracks"]:
        print(f"  - {t['name']} ({t['key']}): {t['estimatedDays']:.1f} days")
        print(f"    {t['description']}")
    print("")
    print("Suggested order of audits:")
    for idx, key in enumerate(plan["suggestedOrder"], start=1):
        track = next(t for t in plan["tracks"] if t["key"] == key)
        print(f"  {idx}. {track['name']} ({track['key']})")


def main() -> None:
    args = parse_args()
    style = STYLES[args.style]

    plan = compute_audit_plan(
        style=style,
        uses_zk=args.zk,
        uses_fhe=args.fhe,
        has_bridge=args.bridge,
        has_governance=args.governance,
        multi_chain=args.multi_chain,
        team_size=args.team_size,
        maturity=args.maturity,
    )

    if args.json:
        print(json.dumps(plan, indent=2, sort_keys=True))
    else:
        print_human(plan)


if __name__ == "__main__":
    main()
