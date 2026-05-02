#!/usr/bin/env python3
"""
Parse the synthed CDK template for DeployStack and emit a mermaid diagram
between <!-- ARCH:START --> / <!-- ARCH:END --> markers in README.md.

Reads cdk.out/DeployStack.template.json (run `cd packages/deploy && cdk synth` first
if missing or stale).
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = REPO_ROOT / "cdk.out" / "DeployStack.template.json"
README_PATH = REPO_ROOT / "README.md"

START_MARKER = "<!-- ARCH:START -->"
END_MARKER = "<!-- ARCH:END -->"

NODE_TYPES = {
    "AWS::Lambda::Function": ("lambda", "Lambda"),
    "AWS::S3::Bucket": ("bucket", "S3"),
    "AWS::RDS::DBInstance": ("database", "RDS"),
    "AWS::CloudFront::Distribution": ("cdn", "CloudFront"),
    "AWS::ApiGatewayV2::Api": ("api", "API Gateway"),
    "AWS::SQS::Queue": ("queue", "SQS"),
    "AWS::Events::Rule": ("schedule", "EventBridge"),
}

PATH_SKIP_PATTERNS = (
    re.compile(r"AWSCDK"),
    re.compile(r"S3AutoDeleteObjects"),
    re.compile(r"CrossRegionExport"),
    re.compile(r"framework-onEvent"),
    re.compile(r"AccessLogBucket"),
    re.compile(r"LogRetention"),
)

SHAPES = {
    "lambda": ("[", "]"),
    "bucket": ("[(", ")]"),
    "database": ("[(", ")]"),
    "cdn": ("{{", "}}"),
    "api": ("([", "])"),
    "queue": (">", "]"),
    "schedule": ("(", ")"),
}


def should_skip(cdk_path: str) -> bool:
    return any(pattern.search(cdk_path) for pattern in PATH_SKIP_PATTERNS)


GENERIC_LEAF_NAMES = {
    "Handler",
    "Function",
    "Resource",
    "Distribution",
    "Bucket",
    "Instance",
}


def derive_node_id(cdk_path: str) -> str:
    parts = [part for part in cdk_path.split("/") if part not in ("Resource", "DeployStack")]
    if not parts:
        return cdk_path
    leaf = re.sub(r"Function$", "", parts[-1]) or parts[-1]
    if leaf in GENERIC_LEAF_NAMES and len(parts) >= 2:
        return parts[-2]
    return leaf


def collect_refs(value, refs: set[str]) -> None:
    if isinstance(value, dict):
        for key, val in value.items():
            if key == "Ref" and isinstance(val, str):
                refs.add(val)
            elif key == "Fn::GetAtt" and isinstance(val, list) and val:
                refs.add(val[0])
            else:
                collect_refs(val, refs)
    elif isinstance(value, list):
        for item in value:
            collect_refs(item, refs)


def find_referenced(properties, known_logical_ids: set[str]) -> set[str]:
    refs: set[str] = set()
    collect_refs(properties, refs)
    return refs & known_logical_ids


def build_graph(template: dict) -> tuple[dict[str, dict], list[tuple[str, str]]]:
    resources = template["Resources"]
    nodes: dict[str, dict] = {}

    for logical_id, resource in resources.items():
        type_info = NODE_TYPES.get(resource["Type"])
        if type_info is None:
            continue
        kind, service_label = type_info
        cdk_path = resource.get("Metadata", {}).get("aws:cdk:path", logical_id)
        if should_skip(cdk_path):
            continue
        node_id = derive_node_id(cdk_path)
        nodes[logical_id] = {
            "id": node_id,
            "kind": kind,
            "service": service_label,
            "in_vpc": "VpcConfig" in resource.get("Properties", {}),
        }

    known = set(nodes.keys())
    edges: set[tuple[str, str]] = set()

    for logical_id, resource in resources.items():
        resource_type = resource["Type"]
        properties = resource.get("Properties", {})

        if logical_id in nodes and resource_type == "AWS::Lambda::Function":
            env_vars = properties.get("Environment", {}).get("Variables", {})
            for target in find_referenced(env_vars, known):
                if target != logical_id:
                    edges.add((logical_id, target))

        if resource_type == "AWS::Lambda::EventSourceMapping":
            queue_refs = find_referenced(properties.get("EventSourceArn"), known)
            function_refs = find_referenced(properties.get("FunctionName"), known)
            for queue in queue_refs:
                for function in function_refs:
                    edges.add((queue, function))

        if resource_type == "AWS::Events::Rule":
            for target in properties.get("Targets", []):
                target_refs = find_referenced(target.get("Arn"), known)
                for ref in target_refs:
                    if logical_id in nodes:
                        edges.add((logical_id, ref))

        if resource_type == "AWS::ApiGatewayV2::Integration":
            api_refs = find_referenced(properties.get("ApiId"), known)
            uri_refs = find_referenced(properties.get("IntegrationUri"), known)
            for api in api_refs:
                for target in uri_refs:
                    edges.add((api, target))

        if resource_type == "AWS::CloudFront::Distribution":
            if logical_id in nodes:
                origins = properties.get("DistributionConfig", {}).get("Origins", [])
                for origin in origins:
                    for target in find_referenced(origin, known):
                        edges.add((logical_id, target))

    return nodes, sorted(edges)


def render_mermaid(nodes: dict[str, dict], edges: list[tuple[str, str]]) -> str:
    in_vpc = {lid for lid, node in nodes.items() if node["in_vpc"]}
    rds_ids = {lid for lid, node in nodes.items() if node["kind"] == "database"}
    in_vpc |= rds_ids

    lines = ["```mermaid", "graph LR"]

    def render_node(logical_id: str) -> str:
        node = nodes[logical_id]
        open_shape, close_shape = SHAPES[node["kind"]]
        label = f"\"{node['id']}<br/><i>{node['service']}</i>\""
        return f"  {logical_id}{open_shape}{label}{close_shape}"

    if in_vpc:
        lines.append("  subgraph VPC")
        for logical_id in sorted(in_vpc):
            lines.append("  " + render_node(logical_id))
        lines.append("  end")

    for logical_id in sorted(set(nodes) - in_vpc):
        lines.append(render_node(logical_id))

    for source, target in edges:
        lines.append(f"  {source} --> {target}")

    lines.append("```")
    return "\n".join(lines)


def update_readme(diagram: str) -> bool:
    if not README_PATH.exists():
        sys.exit(f"README not found at {README_PATH}")

    text = README_PATH.read_text()
    block = f"{START_MARKER}\n{diagram}\n{END_MARKER}"

    if START_MARKER in text and END_MARKER in text:
        pattern = re.compile(
            re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
            re.DOTALL,
        )
        new_text = pattern.sub(block, text)
    else:
        section = f"\n## Architecture\n\n_Auto-generated from `cdk.out/DeployStack.template.json` — run `pnpm arch:diagram` to refresh._\n\n{block}\n"
        new_text = text.rstrip() + "\n" + section

    if new_text == text:
        return False
    README_PATH.write_text(new_text)
    return True


def main() -> None:
    if not TEMPLATE_PATH.exists():
        sys.exit(
            f"Template not found at {TEMPLATE_PATH}.\n"
            "Run `cd packages/deploy && cdk synth` first."
        )

    template = json.loads(TEMPLATE_PATH.read_text())
    nodes, edges = build_graph(template)
    diagram = render_mermaid(nodes, edges)

    check_only = "--check" in sys.argv
    if check_only:
        text = README_PATH.read_text()
        if f"{START_MARKER}\n{diagram}\n{END_MARKER}" in text:
            print("Architecture diagram is up to date.")
            return
        sys.exit(
            "Architecture diagram in README.md is out of sync with cdk.out.\n"
            "Run `pnpm arch:diagram` to update it."
        )

    changed = update_readme(diagram)
    if changed:
        print(f"Updated {README_PATH}")
    else:
        print("Diagram already up to date.")


if __name__ == "__main__":
    main()
