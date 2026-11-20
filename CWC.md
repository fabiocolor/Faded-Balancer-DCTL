<!-- cwc-generated-client-help -->
# Faded-Balancer-DCTL — CWC client notes

This file is generated. Do not edit it by hand.
Refresh from the CWC checkout:

```text
cwc-refresh-client-help
```

Live contract: `http://100.109.144.91:8799/help` (`GET /api/help`).
Schema: `cwc_client_help_v1`. Digest: `270cd6bc5caa8c7f`.
If this digest disagrees with `GET /api/help`, trust the live API.

This checkout lives on the JIMINY Syncthing hub at `S:\REPOS\Faded-Balancer-DCTL`.
Files already here are canonical shared storage. Send them to CWC as:

```json
{
  "shared_storage_id": "jiminy-syncthing",
  "relative_path": "REPOS/Faded-Balancer-DCTL/..."
}
```

Do not send `S:\...`, UNC paths, worker IDs, MinIO credentials, or client-chosen object keys.
Client-owned files that are not on this hub use `POST /api/uploads` and the returned `uploads/` `object_key`.

---

# CWC client job contract

Schema: `cwc_client_help_v1`

CWC is the only control plane for shared ComfyUI workers. Client projects submit jobs, poll CWC, and download CWC artifacts. CWC chooses the worker, dispatch route, preparation path, and completion truth.

## Live copies

- HTML: `http://100.109.144.91:8799/help`
- JSON: `http://100.109.144.91:8799/api/help`
- Resilient HTML: `https://jimin-mm2018.tailf7c46.ts.net/help`
- Resilient JSON: `https://jimin-mm2018.tailf7c46.ts.net/api/help`
- Base URL: `http://100.109.144.91:8799`

The running API is the teaching authority. Refresh offline copies with `cwc-refresh-client-help`. If a snapshot disagrees with `GET /api/help`, trust the live API.

## Authentication

Send `X-API-Key` on every non-help, non-health request.

- Ask the CWC operator for a project-specific client key.
- Store it only in ignored local secrets such as CWC_API_KEY.
- Client keys can submit jobs, poll, download artifacts, and create install requests.
- Client keys cannot enable, disable, wake, restart, qualify, or otherwise operate workers.

## Client rules

- Send work to CWC, never to a worker ComfyUI /prompt endpoint.
- Route with capability_tag. Never send worker IDs as scheduling instructions.
- Use only named_workflow, reviewed script_job, or typed storage_operation. raw_workflow is rejected.
- Resolve, Phoenix, and Nuke application operations never run through CWC. A project may directly own a bounded test only through an exact Global Operations Desk whole-worker/application resource fence.
- A job is complete only when CWC status is completed and artifacts are listed by CWC.
- Download results from CWC artifact endpoints or the CWC-issued direct_download_url. Never from the worker.
- Never send UNC paths, host addresses, SMB credentials, MinIO credentials, or client-chosen object keys.
- Never operate ComfyUI workers from a client project, dashboard, or MCP session. Resolve, Phoenix, and Nuke use the separate exact Operations direct-ownership fence described above.

## Send a job

`POST /jobs`

Modes:

- `named_workflow`: Registered graph in CWC config/workflows.json. Send workflow_id plus input_payload bindings only.
- `script_job`: Reviewed GPU script. Requires script.profile_id that exactly matches config/script_profiles.json.
- `storage_operation`: Typed CPU preparation on an allowlisted storage agent. Most clients see these as CWC-created parents.

Lifecycle:

1. POST /jobs and save job_id.
2. Poll GET /jobs/{job_id} until status is completed or failed.
3. execution_stage is finer progress: queued, staging, running, finalizing, completed, or failed.
4. On completed, list artifacts then download each needed file.
5. On failed, read failure_category, failure_retryable, failure_action, and failure_details. Do not bypass CWC.

Public intake rejects:

- `raw_workflow`
- `runtime_bindings`
- `workflow_input_overrides`
- `workflow_node_overrides`
- preferred or excluded worker hints
- CWC-owned metadata namespaces: cwc_*, preparation_*, bundle_*, imagine_*

Bundles:

- Submit: `/bundles`, `/action-bundles`, `/jobs/bundles`
- Poll: `GET /bundles/{bundle_id}`
- Each jobs[] child uses the same public intake contract. Artifacts still come from per-job endpoints.

## Receive results

- List: `GET /jobs/{job_id}/artifacts`
- Download: `GET /jobs/{job_id}/artifacts/{artifact_id}`
- Acknowledge: `POST /jobs/{job_id}/artifacts/acknowledge`
- Direct large-file download: Artifacts at least 8 MiB are mirrored under artifacts/ and include object_key plus a short-lived direct_download_url. Dependents that need that mirror stay queued until the key exists. The bucket is a staging cache; CWC SQLite plus artifact_root remain the source of truth.

Notes:

- Presigned URLs are bearer credentials. Do not log the query string.
- The Python SDK download_artifact_to_file uses direct_download_url when present.
- preparation_job_ids in metadata identifies CWC-created storage parents. The returned job_id is still the compute child.

## Storage rules

Choose one input style:

- **Small measured payload, a few megabytes**: image_base64, video_base64, file_base64, or script data_base64
  - Limit: Embedded aggregates above 128 MiB or 512 files are rejected. Use POST /api/uploads instead.
- **Client-owned large file already on the caller machine**: POST /api/uploads, PUT the returned upload_url, then submit object_key under uploads/
  - Limit: CWC measures the object with authenticated HEAD. Clients do not choose keys, endpoints, or credentials.
- **File already on a canonical JIMINX, JIMINY, or Harrow share**: shared_storage_id plus relative_path
  - Limit: Relative paths only. No '.', '..', UNC, or hostnames. Supply size_bytes and sha256 when known.

Object-key namespaces CWC owns:

- `shared/<storage_id>/...`
- `uploads/<upload_id>/...`
- `artifacts/<job_id>/<artifact_id>/...`

Placement:

- A known aggregate at or below 128 MiB and 512 files may remain flexible across sites.
- Larger or unknown aggregates stay at their declared site even if a remote worker is idle.
- A source at least 1 GiB or 1,000 files requires local or storage-side handling.
- Worker staging uses CWC-owned MinIO only. A storage ID without a seed root fails closed.
- CWC must not fall back to worker SMB. Direct SMB or mounted-share reads are only the measured, receipt-bound worker-preparation exception.
- MinIO is never a fallback around site locality.
- jimin-m5pro-london10tb has no MinIO seed source. Do not seed London data through JIMINX.
- Current typed storage-operation agents cover allowlisted JIMINX sources only. JIMINY and Harrow preparation waits or fails closed until a same-site agent and sink exist.

Shared storage IDs:

- `jiminx-source-media` (lima_lab): Canonical JIMINX source and original media.
- `jiminx-restoration-renders` (lima_lab): Canonical JIMINX restoration and final-render share.
- `jiminx-copycat-trials` (lima_lab): JIMINX Copycat trials and workspace share.
- `jiminy-syncthing` (lima_lab): JIMINY Syncthing hub. Relative paths start at the hub root (for example REPOS/...). A Mac-only file is not on this storage unless it is actually synced.
- `jiminy-phoenix` (lima_lab): JIMINY Phoenix project share.
- `jimin-m5pro-london10tb` (harrow): Harrow/London share. No MinIO seed source. Ordinary staging fails closed. Do not seed London data through JIMINX.

Named-workflow large inputs use `type: "shared_storage"` with `shared_storage_id`, `relative_path`.

## Examples

### Named workflow

```json
{
  "mode": "named_workflow",
  "workflow_id": "generic.qwen_image_edit",
  "capability_tag": "qwen_image_edit_2511_fp8mixed",
  "priority": "normal",
  "input_payload": {
    "input_image": {
      "type": "image_base64",
      "filename": "source.png",
      "data_base64": "<base64>"
    },
    "prompt": "edit this image",
    "filename_prefix": "client-job"
  },
  "metadata": {
    "source_project": "example-project"
  }
}
```

### Shared storage binding

```json
{
  "type": "shared_storage",
  "shared_storage_id": "jiminx-source-media",
  "relative_path": "07_TINTERILLO/training/dataset.zip",
  "filename": "dataset.zip",
  "size_bytes": 123456789012,
  "sha256": "<64-char-hex>"
}
```

### Client-owned large upload

1. POST /api/uploads {"filename": "big-file.zip"}
2. PUT bytes to the returned upload_url
3. Submit object_key "uploads/<upload_id>/big-file.zip" with filename and size_bytes

## Endpoints

- `GET /healthz` — Reachability, no API key.
- `GET /help` — This teaching page.
- `GET /api/help` — Machine-readable copy of this contract.
- `POST /jobs` — Submit one job.
- `GET /jobs/{job_id}` — Poll status until completed or failed.
- `GET /jobs/{job_id}/artifacts` — List finalized artifacts.
- `GET /jobs/{job_id}/artifacts/{artifact_id}` — Download one artifact through CWC.
- `POST /jobs/{job_id}/artifacts/acknowledge` — Acknowledge receipt after download.
- `POST /api/uploads` — Issue a client upload ticket and uploads/ object_key.
- `POST /bundles` — Submit several jobs as one bundle.
- `GET /bundles/{bundle_id}` — Poll bundle child status.
- `GET /workers` — Inspect enabled workers and advertised capabilities. Not a routing API.
- `GET /capabilities` — List capability tags and catalog views.
- `POST /install-requests` — Ask CWC to install missing nodes or assets. Do not operate the worker yourself.

## Python SDK

Use `comfy_worker_client.WorkerControlClient`. Helpful methods: `submit_job`, `wait_for_completion`, `list_artifacts`, `download_artifact`, `download_artifact_to_file`, `create_upload`, `upload_file`, `client_help`.

```python
from comfy_worker_client import WorkerControlClient

client = WorkerControlClient("http://100.109.144.91:8799", api_key=CWC_API_KEY)
help_doc = client.client_help()
job = client.submit_job({...})
completed = client.wait_for_completion(job["job_id"], timeout_sec=600)
artifacts = client.list_artifacts(job["job_id"])
content = client.download_artifact(job["job_id"], artifacts[0]["artifact_id"])
```

## MCP

Call the `client_help` tool on `cwc-mcp-server` before submitting work. Setup: `docs/client-mcp-setup.md`.
