import re
from typing import Dict, List
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

SHA1_REGEX = re.compile(r"^[0-9a-f]{40}$")

class WorkflowPayload(BaseModel):
    trigger: str
    permissions: Dict[str, str]
    testsPassed: bool
    matrixComplete: bool
    failFast: bool
    actions: List[Dict[str, str]]
    environmentApproval: bool = False

class ImagePayload(BaseModel):
    multiStage: bool
    runsAsRoot: bool
    secretMode: str
    criticalVulnerabilities: int
    digestPinned: bool

class ReleaseGateRequest(BaseModel):
    target: str
    event: str
    ref: str
    workflow: WorkflowPayload
    image: ImagePayload


@app.post("/release-gate")
def release_gate(req: ReleaseGateRequest):
    violations = set()

    # 1. Least-Privilege Permissions Check
    expected_permissions = {
        "contents": "read",
        "packages": "write",
        "id-token": "none"
    }
    if req.workflow.permissions != expected_permissions:
        violations.add("EXCESS_PERMISSION")

    # 2. PR Trigger & Matrix Verification
    if req.event == "pull_request" or req.workflow.trigger == "pull_request":
        if req.workflow.trigger == "pull_request_target":
            violations.add("UNSAFE_PR_TRIGGER")
            
    if not req.workflow.testsPassed or not req.workflow.matrixComplete or req.workflow.failFast:
        violations.add("TESTS_INCOMPLETE")

    # 3. Action Pinning Check
    for action in req.workflow.actions:
        owner = action.get("owner", "")
        ref_val = action.get("ref", "")
        if owner != "actions":
            if not SHA1_REGEX.match(ref_val):
                violations.add("MUTABLE_ACTION")

    # 4. Container Image Hardening
    if not req.image.multiStage:
        violations.add("SINGLE_STAGE_IMAGE")

    if req.image.runsAsRoot:
        violations.add("ROOT_RUNTIME")

    if req.image.secretMode in ("arg", "copy"):
        violations.add("SECRET_IN_LAYER")

    if req.image.criticalVulnerabilities > 0:
        violations.add("CRITICAL_CVE")

    if not req.image.digestPinned:
        violations.add("UNPINNED_IMAGE")

    # 5. Production Protections
    if req.target == "production":
        if req.event != "push" or req.ref != "refs/heads/main":
            violations.add("INVALID_PRODUCTION_REF")

        if not req.workflow.environmentApproval:
            violations.add("APPROVAL_REQUIRED")

    sorted_violations = sorted(list(violations))
    decision = "promote" if len(sorted_violations) == 0 else "block"

    return {
        "decision": decision,
        "violations": sorted_violations
    }
