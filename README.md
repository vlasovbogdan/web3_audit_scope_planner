# web3_audit_scope_planner

This repository contains a small CLI helper called web3_audit_scope_planner.

It estimates how much audit work you might need for a Web3 protocol and how to structure that work across different audit tracks. The model is inspired by:

- Aztec-style zk rollups (privacy-focused, heavy use of zero-knowledge proofs)
- Zama-style FHE stacks (encrypted compute and more complex infrastructure)
- Soundness-focused research labs (formal specifications and correctness-first designs)

There are exactly two files in this repository:

- app.py
- README.md


## Concept

Smart contracts and rollups often launch with incomplete or unstructured audit planning. This tool helps you answer questions like:

- How many audit person-days should we budget for protocol vs circuits vs implementation?
- How does adding FHE or complex zk circuits change the scope?
- What is the relative effort split if we have bridges, governance, or multi-chain deployments?
- In what order should audits be scheduled?

Instead of connecting to a chain or RPC, the planner uses simple multipliers tuned by:

- design style (aztec, zama, soundness)
- presence of zk or FHE
- bridges and governance
- multi-chain complexity
- team size
- maturity (idea, prototype, mainnet)

It then proposes a breakdown of estimated person-days per track and a suggested audit order.


## Tracks

The planner distributes effort across the following conceptual tracks:

- Protocol & Soundness Review  
  Core protocol logic, invariants, liveness and safety properties, cross-domain flows.

- Circuits / Crypto Review  
  ZK and FHE circuits, gadgets, cryptographic assumptions and implementations.

- Implementation Review  
  Smart contracts, rollup contracts, and critical off-chain components that affect correctness.

- Infrastructure & DevOps Review  
  RPC, sequencers, key management, monitoring, logging, deployment pipelines.

- Governance & Upgradeability Review  
  Admin keys, upgrade paths, governance contracts, voting, and timelocks.

Each track starts with a small base number of person-days and is then scaled according to the selected style and flags.


## Installation

Requirements:

- Python 3.10 or newer

Steps:

1. Create a new GitHub repository with any name.
2. Copy app.py and this README.md into the root of the repository.
3. Ensure that python is on your PATH.
4. No external dependencies are required; only the Python standard library is used.


## Usage

From the project root, run:

Basic Aztec-style zk rollup prototype with zk circuits and a bridge:

python app.py --style aztec --zk --bridge --maturity prototype

Zama-style FHE compute stack with FHE and zk components:

python app.py --style zama --fhe --zk --multi-chain --team-size 10 --maturity mainnet

Soundness-first lab working on a new protocol with formal models and governance:

python app.py --style soundness --governance --maturity idea

Request JSON output for dashboards or CI pipelines:

python app.py --style aztec --zk --bridge --maturity mainnet --json


## Parameters

--style  
Base profile: aztec, zama, or soundness. This encodes a different default emphasis on circuits, protocol soundness, and infrastructure.

--zk  
If set, indicates the project uses zero-knowledge proofs for core logic or privacy.

--fhe  
If set, indicates the project uses fully homomorphic encryption (FHE).

--bridge  
If set, indicates there is a bridge or cross-chain messaging component.

--governance  
If set, indicates the presence of governance or upgradeability logic.

--multi-chain  
If set, indicates that the system targets multiple chains or rollups.

--team-size  
Approximate number of engineers involved. Larger teams tend to increase coordination and integration complexity.

--maturity  
Project stage: idea, prototype, or mainnet. Mainnet generally increases recommended audit depth.

--json  
Returns the computed plan as JSON instead of human-readable text.


## Output

In human-readable mode, the planner prints:

- Base style and description
- Project flags and basic attributes
- Total estimated person-days across all audit tracks
- A list of tracks with their individual estimated days and descriptions
- A suggested audit order (for example: protocol first, then circuits, then implementation, then infra, then governance)

In JSON mode, the output contains:

- style, styleName, styleDescription
- usesZk, usesFhe, hasBridge, hasGovernance, multiChain, teamSize, maturity
- tracks: an array with key, name, description, estimatedDays
- totalEstimatedDays
- suggestedOrder: an ordered list of track keys


## Notes

- Numbers are illustrative and meant to start conversations, not to replace professional audit scoping.
- The model is intentionally simple and focused on relative weights between tracks, not real billing rates.
- You should adapt the base days and multipliers to match your organization, auditors, and protocol complexity.
- The planner is especially useful when thinking about audit planning for advanced privacy and soundness-heavy projects similar in spirit to Aztec, Zama, or formally verified Web3 stacks.
