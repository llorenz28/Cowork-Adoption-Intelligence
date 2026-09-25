#!/usr/bin/env python3
"""Cowork Purview preprocessing utility for Power BI."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import time
import uuid
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

VERSION = "0.1.0"
MANIFEST_FORMAT = "cowork-python-preprocessor-manifest-v1"
AUDIT_REQUIRED = {"Operation", "AuditData", "UserId", "CreationDate", "RecordId"}
USAGE_REQUIRED = {
    "UserPrincipalName", "DisplayName", "TotalTasks", "ScheduledTasks",
    "UserInitiatedTasks", "ActiveDays", "LastActivityDate",
}
CONSUMPTION_REQUIRED = {
    "Display Name", "User Principal Name", "Monthly credit limit",
    "Monthly credits used", "User ID", "Microsoft 365 Copilot license",
    "Last activity date", "Session Count", "% Used",
}
IDENTITY_REQUIRED = {"id", "displayName", "userPrincipalName"}
ORG_REQUIRED = {
    "userPrincipalName", "displayName", "department", "jobTitle", "jobFamily",
    "city", "country", "costCenter", "manager", "businessUnit",
}

ENTITY_FIELDS: dict[str, list[str]] = {
    "Dim_User": [
        "UserKey", "UserPrincipalName", "DisplayName", "UserID", "CopilotLicense",
        "LicenseSKU", "IdentityDataQuality", "DemographicDataQuality",
    ],
    "Fact_CopilotAuditRaw": [
        "RecordId", "CreationDateParsed", "DateKey", "Audit_UserId",
        "Audit_UserId_Normalized", "UserKey", "Workload", "ClientRegion",
        "AppIdentity", "AppHost", "ThreadId", "LicenseType", "Message_Count",
        "Message_PromptCount", "Plugin_Count", "Plugin_FirstId",
        "Plugin_FirstName", "Resource_Count", "AccessedResource_FirstSiteUrl",
        "AccessedResource_FirstAction", "ModelProviderName",
    ],
    "CoworkClassification": [
        "RecordId", "ThreadId", "Category", "CategoryKey", "CategorySignal",
        "MappingConfidence", "SkillDisplayName", "ActivityDetail", "CategoryPriority",
    ],
    "Bridge_CoworkPlugin": [
        "RecordId", "ThreadId", "DateKey", "UserKey", "PluginName", "PluginId",
    ],
    "Bridge_CoworkResource": [
        "RecordId", "ThreadId", "DateKey", "UserKey", "SiteUrl", "ResType",
        "ResAction", "SensitivityLabelId", "IsCoworkArtifact", "ArtifactExt",
    ],
    "Fact_CoworkThread": [
        "ThreadId", "UserKey", "DateKey", "WeekStartDate", "StartedAt", "EndedAt",
        "RecordCount", "PromptCount", "ResourceCount", "PluginCount", "DurationMin",
        "PrimarySkill", "PrimaryBusinessTool", "PrimarySkillDisplayName",
        "BusinessBehavior", "BehaviorConfidence", "PrimaryCategory", "ThreadCategory",
        "ThreadCategoryKey", "TaskClassification", "BusinessToolCount",
        "UnclassifiedToolCount", "OrchestrationToolCount",
    ],
    "Fact_CoworkUsage": [
        "UserPrincipalName", "DisplayName", "UserKey", "TotalTasks", "ScheduledTasks",
        "UserInitiatedTasks", "ActiveDays", "LastActivityDate", "DataQuality",
    ],
    "Dim_UserOrg": [
        "UserPrincipalName", "UserKey", "DisplayName", "Department", "JobTitle",
        "JobFamily", "City", "Country", "CostCenter", "Manager", "BusinessUnit",
        "DataQuality",
    ],
    "Fact_Consumption": [
        "UserKey", "ServiceKey", "DateKey", "CreditsUsed", "CreditLimit",
        "SessionCount", "LastActivityDate", "DaysSinceActivity", "RecencyBucket",
        "RecencyBucketSort", "BudgetSegment", "CohortRank", "CohortBand",
        "ConsumptionDataQuality",
    ],
    "Fact_CoworkUserDayModel": [
        "UserKey", "Audit_UserId", "Audit_UserId_Normalized", "DateKey",
        "WeekStartDate", "ModelProviderName", "InteractionCount", "PromptCount",
        "UserDateKey",
    ],
    "Fact_Tasks": [
        "ThreadId", "UserKey", "CategoryKey", "DateKey", "Tasks", "Model",
        "PrimaryBusinessTool", "PrimarySkillDisplayName", "BusinessBehavior",
        "TaskClassification", "LowMin", "MidMin", "HighMin",
    ],
    "Dim_CoworkSkill": [
        "PluginName", "SkillDisplayName", "Category", "CategoryKey", "IsMapped",
        "ToolRole", "BusinessBehavior", "MappingConfidence", "AttributionPriority",
        "IsBusinessTool", "LowMin", "MidMin", "HighMin",
    ],
    "Dim_ModelProvider": ["Model", "HasModelData"],
}

INT_FIELDS = {
    "_RowId", "ActiveDays", "AttributionPriority", "BusinessToolCount",
    "CategoryKey", "CategoryPriority", "CohortRank", "DateKey",
    "DaysSinceActivity", "HighMin", "InteractionCount", "LowMin", "Message_Count",
    "Message_PromptCount", "MidMin", "OrchestrationToolCount", "Plugin_Count",
    "PluginCount", "PromptCount", "RecordCount", "RecencyBucketSort",
    "Resource_Count", "ResourceCount", "ScheduledTasks", "ServiceKey", "Tasks",
    "ThreadCategoryKey", "TotalTasks", "UnclassifiedToolCount",
    "UserInitiatedTasks", "UserKey",
}
FLOAT_FIELDS = {"CreditLimit", "CreditsUsed", "DurationMin", "SessionCount"}
BOOL_FIELDS = {"HasModelData", "IsBusinessTool", "IsCoworkArtifact", "IsMapped"}
DATETIME_FIELDS = {"CreationDateParsed", "EndedAt", "LastActivityDate", "StartedAt"}
DATE_FIELDS = {"WeekStartDate"}


class PreprocessorError(RuntimeError):
    pass


def norm(value: Any) -> str:
    return "" if value is None else str(value).strip().lower()


def text(value: Any) -> str | None:
    return None if value is None else str(value)


def parse_datetime(value: Any) -> dt.datetime | None:
    raw = "" if value is None else str(value).strip()
    if not raw:
        return None
    candidate = raw[:-1] + "+00:00" if raw.endswith(("Z", "z")) else raw
    try:
        parsed = dt.datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo:
        parsed = parsed.astimezone(dt.timezone.utc).replace(tzinfo=None)
    return parsed


def required_source_datetime(value: Any, label: str) -> dt.datetime | None:
    raw = "" if value is None else str(value).strip()
    parsed = parse_datetime(raw)
    if raw and parsed is None:
        raise PreprocessorError(f"{label} contains invalid datetime value {raw!r}.")
    return parsed


def descending_datetime_key(value: Any, label: str) -> tuple[int, int, int, int, int, int, int]:
    parsed = required_source_datetime(value, label)
    if parsed is None:
        return (1, 0, 0, 0, 0, 0, 0)
    return (
        0, -parsed.year, -parsed.month, -parsed.day,
        -parsed.hour, -parsed.minute, -parsed.second,
    )


def iso(value: dt.datetime | dt.date | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, dt.datetime):
        return value.isoformat(timespec="seconds")
    return value.isoformat()


def integer(value: Any, label: str) -> int | None:
    raw = "" if value is None else str(value).strip()
    if raw == "":
        return None
    try:
        return int(raw)
    except ValueError as exc:
        raise PreprocessorError(f"{label} contains non-integer value {raw!r}.") from exc


def file_identity(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    stat = path.stat()
    return {
        "path": str(path),
        "bytes": stat.st_size,
        "modified_utc": dt.datetime.fromtimestamp(
            stat.st_mtime, dt.timezone.utc
        ).isoformat(),
        "sha256": digest.hexdigest(),
    }


def discover_csvs(input_dir: Path) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for path in sorted(input_dir.rglob("*"), key=lambda p: str(p).lower()):
        if not path.is_file() or path.suffix.lower() != ".csv":
            continue
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as stream:
                header = next(csv.reader(stream), [])
        except (OSError, UnicodeError, csv.Error) as exc:
            raise PreprocessorError(f"Cannot read CSV header {path}: {exc}") from exc
        found.append({"path": path, "headers": [h.strip() for h in header]})
    return found


def pick_source(
    catalog: list[dict[str, Any]], preferred: list[str], required: set[str]
) -> dict[str, Any] | None:
    preferred_lower = [name.lower() for name in preferred]
    matches = [entry for entry in catalog if required <= set(entry["headers"])]
    if not matches:
        return None
    def key(entry: dict[str, Any]) -> tuple[int, str, str]:
        name = entry["path"].name.lower()
        rank = preferred_lower.index(name) if name in preferred_lower else 9999
        return rank, str(entry["path"].parent).lower(), name
    return sorted(matches, key=key)[0]


def read_rows(entry: dict[str, Any] | None) -> list[dict[str, str]] | None:
    if entry is None:
        return None
    try:
        with entry["path"].open("r", encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))
    except (OSError, UnicodeError, csv.Error) as exc:
        raise PreprocessorError(f"Cannot parse CSV {entry['path']}: {exc}") from exc


def best_rows(
    rows: list[dict[str, str]] | None,
    upn_column: str,
    ranking: Any,
) -> tuple[dict[str, dict[str, str]], int]:
    if rows is None:
        return {}, 0
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = norm(row.get(upn_column))
        if key:
            groups[key].append(row)
    winners: dict[str, dict[str, str]] = {}
    duplicates = 0
    for key, values in groups.items():
        duplicates += max(0, len(values) - 1)
        winners[key] = sorted(values, key=ranking)[0]
    return winners, duplicates


def classify(name: str, rules: list[dict[str, Any]]) -> dict[str, Any] | None:
    value = norm(name)
    for rule in rules:
        pattern = rule["pattern"]
        if (
            (rule["match"] == "exact" and value == pattern)
            or (rule["match"] == "prefix" and value.startswith(pattern))
            or (rule["match"] == "contains" and pattern in value)
        ):
            return rule
    return None


def artifact_category(resources: list[dict[str, Any]]) -> str | None:
    urls = [
        str(resource.get("SiteUrl") or "").lower()
        for resource in resources
        if "/documents/cowork/" in str(resource.get("SiteUrl") or "").lower()
    ]
    extensions = [url.rsplit(".", 1)[-1] for url in urls if "." in url]
    if any(ext in {"py", "ps1", "js", "ts", "sql", "ipynb", "yml", "yaml"} for ext in extensions):
        return "Write or debug code"
    if any(ext in {"xlsx", "xlsm", "csv", "tsv", "pbix", "pbit"} for ext in extensions):
        return "Analysis & Research"
    if any(ext in {"docx", "pptx", "pdf", "md", "html", "page", "png", "jpg"} for ext in extensions):
        return "Document & content creation"
    return None


def week_start(value: dt.datetime | None) -> dt.date | None:
    return None if value is None else value.date() - dt.timedelta(days=value.weekday())


class EntityWriter:
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.handles: dict[str, Any] = {}
        self.writers: dict[str, csv.DictWriter] = {}
        self.counts: Counter[str] = Counter()
        for entity, fields in ENTITY_FIELDS.items():
            handle = (temp_dir / f"entity-{entity}.csv").open(
                "w", encoding="utf-8", newline=""
            )
            writer = csv.DictWriter(
                handle, fieldnames=["_Entity", "_RowId", *fields],
                extrasaction="ignore", lineterminator="\n",
            )
            writer.writeheader()
            self.handles[entity] = handle
            self.writers[entity] = writer

    def write(self, entity: str, row: dict[str, Any]) -> None:
        self.counts[entity] += 1
        rendered = {"_Entity": entity, "_RowId": self.counts[entity]}
        for field in ENTITY_FIELDS[entity]:
            value = row.get(field)
            if isinstance(value, (dt.datetime, dt.date)):
                value = iso(value)
            elif isinstance(value, bool):
                value = "true" if value else "false"
            rendered[field] = "" if value is None else value
        self.writers[entity].writerow(rendered)

    def close(self) -> None:
        for handle in self.handles.values():
            handle.close()


def ingest_audit(
    connection: sqlite3.Connection,
    audit_files: list[dict[str, Any]],
    timings: dict[str, float],
) -> dict[str, int]:
    started = time.perf_counter()
    connection.execute(
        """CREATE TABLE raw(
            record_id TEXT PRIMARY KEY, payload TEXT NOT NULL, user_id TEXT,
            creation_date TEXT, source_path TEXT, source_row INTEGER
        )"""
    )
    raw_rows = selected_rows = duplicates = 0
    blank_samples: list[str] = []
    conflict_samples: list[str] = []
    for entry in audit_files:
        path = entry["path"]
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                for row_number, row in enumerate(reader, 1):
                    raw_rows += 1
                    if row.get("Operation") != "CopilotInteraction":
                        continue
                    selected_rows += 1
                    record_id = (row.get("RecordId") or "").strip()
                    if not record_id:
                        if len(blank_samples) < 10:
                            blank_samples.append(f"{path.name}:{row_number}")
                        continue
                    payload = row.get("AuditData") or ""
                    current = connection.execute(
                        "SELECT payload FROM raw WHERE record_id=?", (record_id,)
                    ).fetchone()
                    if current:
                        duplicates += 1
                        if current[0] != payload and len(conflict_samples) < 10:
                            conflict_samples.append(record_id)
                        continue
                    connection.execute(
                        "INSERT INTO raw VALUES(?,?,?,?,?,?)",
                        (
                            record_id, payload, row.get("UserId"),
                            row.get("CreationDate"), str(path), row_number,
                        ),
                    )
        except (OSError, UnicodeError, csv.Error) as exc:
            raise PreprocessorError(f"Cannot parse audit CSV {path}: {exc}") from exc
        connection.commit()
    if blank_samples:
        raise PreprocessorError(
            f"CopilotInteraction rows contain blank RecordId values; "
            f"sample locations: {', '.join(blank_samples)}"
        )
    if conflict_samples:
        raise PreprocessorError(
            "Duplicate RecordId values contain different AuditData payloads; "
            f"sample RecordIds: {', '.join(conflict_samples)}"
        )
    timings["audit_ingest_seconds"] = round(time.perf_counter() - started, 3)
    return {
        "raw_audit_rows": raw_rows,
        "copilot_interaction_rows": selected_rows,
        "deduplicated_rows": connection.execute("SELECT COUNT(*) FROM raw").fetchone()[0],
        "identical_duplicate_rows_removed": duplicates,
    }


def parse_audit(
    connection: sqlite3.Connection, timings: dict[str, float]
) -> tuple[set[str], list[dict[str, Any]], int]:
    started = time.perf_counter()
    connection.execute(
        """CREATE TABLE audit(
            record_id TEXT PRIMARY KEY, created TEXT, date_key INTEGER,
            audit_user TEXT, upn TEXT, workload TEXT, client_region TEXT,
            app_identity TEXT, app_host TEXT, thread_id TEXT, license_type TEXT,
            message_count INTEGER, prompt_count INTEGER, plugin_count INTEGER,
            plugin_first_id TEXT, plugin_first_name TEXT, resource_count INTEGER,
            resource_first_url TEXT, resource_first_action TEXT,
            model_provider TEXT, nested TEXT
        )"""
    )
    cowork_upns: set[str] = set()
    parse_errors: list[dict[str, Any]] = []
    cowork_count = 0
    reader = connection.execute(
        "SELECT record_id,payload,user_id,creation_date,source_path,source_row "
        "FROM raw ORDER BY record_id"
    )
    batch: list[tuple[Any, ...]] = []
    for record_id, payload, user_id, creation_date, source_path, source_row in reader:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            if len(parse_errors) < 20:
                parse_errors.append({
                    "record_id": record_id, "file": source_path, "row": source_row,
                    "error": str(exc),
                })
            continue
        ced = data.get("CopilotEventData")
        ced = ced if isinstance(ced, dict) else {}
        def array(name: str) -> list[dict[str, Any]]:
            value = ced.get(name)
            return value if isinstance(value, list) else []
        messages = array("Messages")
        plugins = array("AISystemPlugin")
        resources = array("AccessedResources")
        models = array("ModelTransparencyDetails")
        created = parse_datetime(creation_date)
        date_key = int(created.strftime("%Y%m%d")) if created else None
        audit_user = "" if user_id is None else str(user_id).strip()
        upn = audit_user.lower()
        app_host = text(ced.get("AppHost"))
        first_resource = resources[0] if resources else {}
        first_action = first_resource.get("Action")
        if first_action is None:
            first_action = first_resource.get("Type")
        nested = None
        if norm(app_host) == "cowork":
            cowork_count += 1
            cowork_upns.add(upn)
            nested = json.dumps(
                {
                    "plugins": plugins, "resources": resources,
                    "messages": messages, "models": models,
                },
                ensure_ascii=False, separators=(",", ":"),
            )
        batch.append((
            record_id, iso(created), date_key, audit_user, upn,
            text(data.get("Workload")), text(data.get("ClientRegion")),
            text(data.get("AppIdentity")), app_host, text(ced.get("ThreadId")),
            text(ced.get("LicenseType")), len(messages),
            sum(1 for message in messages if message.get("isPrompt") is True),
            len(plugins), text(plugins[0].get("Id")) if plugins else None,
            text(plugins[0].get("Name")) if plugins else None, len(resources),
            text(first_resource.get("SiteUrl")) if resources else None,
            text(first_action), text(models[0].get("ModelProviderName")) if models else None,
            nested,
        ))
        if len(batch) >= 5000:
            connection.executemany("INSERT INTO audit VALUES(" + ",".join("?" * 21) + ")", batch)
            connection.commit()
            batch.clear()
    if batch:
        connection.executemany("INSERT INTO audit VALUES(" + ",".join("?" * 21) + ")", batch)
        connection.commit()
    if parse_errors:
        raise PreprocessorError(
            f"{len(parse_errors)} sample(s) of invalid AuditData JSON; first: "
            f"{parse_errors[0]}"
        )
    connection.execute("DROP TABLE raw")
    connection.commit()
    timings["json_parse_seconds"] = round(time.perf_counter() - started, 3)
    return cowork_upns, parse_errors, cowork_count


def process(
    input_dir: Path, output_dir: Path, validate_only: bool, quiet: bool
) -> dict[str, Any]:
    overall = time.perf_counter()
    if not input_dir.is_dir():
        raise PreprocessorError(f"Input folder does not exist: {input_dir}")
    if input_dir.resolve() == output_dir.resolve():
        raise PreprocessorError("Input and output folders must be different.")
    if output_dir.resolve().is_relative_to(input_dir.resolve()):
        raise PreprocessorError("Output folder must not be inside the input folder.")
    if output_dir.exists():
        validate_existing(output_dir)
    script_dir = Path(__file__).resolve().parent
    contract_path = script_dir / "cowork-contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    rules = contract["skill_rules"]
    orchestration = set(contract["orchestration_skills"])
    categories = {item["category"]: item for item in contract["categories"]}
    category_by_key = {item["key"]: item for item in contract["categories"]}
    human_baselines = contract["human_baselines"]
    timings: dict[str, float] = {}
    discover_started = time.perf_counter()
    catalog = discover_csvs(input_dir)
    audit_files = [entry for entry in catalog if AUDIT_REQUIRED <= set(entry["headers"])]
    if not audit_files:
        raise PreprocessorError(
            "No CSV with required Purview headers was found: "
            + ", ".join(sorted(AUDIT_REQUIRED))
        )
    usage_entry = pick_source(
        catalog, ["CoworkUserDetails.csv", "Cowork Usage.csv"], USAGE_REQUIRED
    )
    consumption_entry = pick_source(
        catalog, ["CoworkConsumptionDetails.csv", "Consumption - Users.csv"],
        CONSUMPTION_REQUIRED,
    )
    identity_entry = pick_source(catalog, ["cowork_users.csv"], IDENTITY_REQUIRED)
    org_entry = pick_source(
        catalog, ["CoworkUserOrgDetails.csv", "Cowork User Organization.csv"],
        ORG_REQUIRED,
    )
    timings["discovery_seconds"] = round(time.perf_counter() - discover_started, 3)
    selected_entries = []
    selected_paths: set[Path] = set()
    for entry in [*audit_files, usage_entry, consumption_entry, identity_entry, org_entry]:
        if entry is not None:
            path = entry["path"].resolve()
            if path not in selected_paths:
                selected_entries.append(entry)
                selected_paths.add(path)
    input_identities = [file_identity(entry["path"]) for entry in selected_entries]

    usage_rows = read_rows(usage_entry)
    consumption_rows = read_rows(consumption_entry)
    identity_rows = read_rows(identity_entry)
    org_rows = read_rows(org_entry)
    usage, usage_duplicates = best_rows(
        usage_rows, "UserPrincipalName",
        lambda row: (
            descending_datetime_key(
                row.get("LastActivityDate"), "Cowork usage LastActivityDate"
            ),
            -(integer(row.get("TotalTasks"), "TotalTasks") or 0),
            row.get("UserPrincipalName") or "",
        ),
    )
    consumption, consumption_duplicates = best_rows(
        consumption_rows, "User Principal Name",
        lambda row: (
            descending_datetime_key(
                row.get("Last activity date"), "Consumption Last activity date"
            ),
            -(integer(row.get("Monthly credits used"), "Monthly credits used") or 0),
            -(integer(row.get("Session Count"), "Session Count") or 0),
            row.get("User Principal Name") or "",
        ),
    )

    output_parent = output_dir.parent
    output_parent.mkdir(parents=True, exist_ok=True)
    temp_dir = output_parent / f".{output_dir.name}.building-{uuid.uuid4().hex}"
    temp_dir.mkdir()
    work_db = temp_dir / ".work.sqlite"
    connection = sqlite3.connect(work_db)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=NORMAL")
    try:
        reconciliation = ingest_audit(connection, audit_files, timings)
        cowork_upns, parse_errors, cowork_detail_count = parse_audit(connection, timings)
        known_upns = sorted(cowork_upns | set(usage))

        identity_map: dict[str, dict[str, str]] = {}
        for row in identity_rows or []:
            identity_map.setdefault(norm(row.get("userPrincipalName")), row)
        users: list[dict[str, Any]] = []
        user_by_upn: dict[str, dict[str, Any]] = {}
        for index, upn in enumerate(known_upns, 1):
            identity = identity_map.get(upn)
            usage_row = usage.get(upn)
            if identity:
                quality = "Real (confirmed via Entra export)"
                principal = identity.get("userPrincipalName")
                display = identity.get("displayName")
                user_id = identity.get("id")
            elif upn in cowork_upns:
                quality = "Real Cowork activity (Purview); no matching Entra identity record found"
                principal = (usage_row or {}).get("UserPrincipalName") or upn
                display = (usage_row or {}).get("DisplayName") or upn
                user_id = None
            else:
                quality = "Real Cowork activity (admin center usage); no matching Entra identity record found"
                principal = (usage_row or {}).get("UserPrincipalName") or upn
                display = (usage_row or {}).get("DisplayName") or upn
                user_id = None
            copilot = (consumption.get(upn) or {}).get("Microsoft 365 Copilot license")
            copilot = copilot if copilot and copilot.strip() else "Unknown"
            user = {
                "UserKey": index, "UserPrincipalName": principal, "DisplayName": display,
                "UserID": user_id, "CopilotLicense": copilot, "LicenseSKU": None,
                "IdentityDataQuality": quality,
                "DemographicDataQuality":
                    "Unavailable - no production license-assignment source connected"
                    if copilot == "Unknown"
                    else "Real - loaded from Consumption - Users export",
                "_upn": upn,
            }
            users.append(user)
            user_by_upn[upn] = user

        writer = EntityWriter(temp_dir)
        for user in users:
            writer.write("Dim_User", user)

        audit_columns = [
            "record_id", "created", "date_key", "audit_user", "upn", "workload",
            "client_region", "app_identity", "app_host", "thread_id", "license_type",
            "message_count", "prompt_count", "plugin_count", "plugin_first_id",
            "plugin_first_name", "resource_count", "resource_first_url",
            "resource_first_action", "model_provider", "nested",
        ]
        cowork_events: list[dict[str, Any]] = []
        for values in connection.execute("SELECT * FROM audit ORDER BY record_id"):
            raw = dict(zip(audit_columns, values))
            user = user_by_upn.get(raw["upn"])
            fact = {
                "RecordId": raw["record_id"], "CreationDateParsed": raw["created"],
                "DateKey": raw["date_key"], "Audit_UserId": raw["audit_user"],
                "Audit_UserId_Normalized": raw["upn"],
                "UserKey": user["UserKey"] if user else None,
                "Workload": raw["workload"], "ClientRegion": raw["client_region"],
                "AppIdentity": raw["app_identity"], "AppHost": raw["app_host"],
                "ThreadId": raw["thread_id"], "LicenseType": raw["license_type"],
                "Message_Count": raw["message_count"],
                "Message_PromptCount": raw["prompt_count"],
                "Plugin_Count": raw["plugin_count"],
                "Plugin_FirstId": raw["plugin_first_id"],
                "Plugin_FirstName": raw["plugin_first_name"],
                "Resource_Count": raw["resource_count"],
                "AccessedResource_FirstSiteUrl": raw["resource_first_url"],
                "AccessedResource_FirstAction": raw["resource_first_action"],
                "ModelProviderName": raw["model_provider"],
            }
            writer.write("Fact_CopilotAuditRaw", fact)
            if raw["nested"] is not None:
                nested = json.loads(raw["nested"])
                fact["_plugins"] = nested["plugins"]
                fact["_resources"] = nested["resources"]
                fact["_messages"] = nested["messages"]
                fact["_models"] = nested["models"]
                fact["_created"] = parse_datetime(raw["created"])
                cowork_events.append(fact)

        plugin_rows: list[dict[str, Any]] = []
        resource_rows: list[dict[str, Any]] = []
        classifications: dict[str, dict[str, Any]] = {}
        for event in cowork_events:
            classified_plugins: list[dict[str, Any]] = []
            for ordinal, plugin in enumerate(event["_plugins"]):
                name = text(plugin.get("Name"))
                key = norm(name)
                rule = classify(key, rules)
                role = (
                    "Orchestration" if key in orchestration
                    else "Business" if rule else "Unclassified"
                )
                row = {
                    "RecordId": event["RecordId"], "ThreadId": event["ThreadId"],
                    "DateKey": event["DateKey"], "UserKey": event["UserKey"],
                    "PluginName": name, "PluginId": text(plugin.get("Id")),
                    "_key": key, "_ordinal": ordinal, "_role": role, "_rule": rule,
                    "_priority": rule["priority"] if rule else 9999,
                }
                plugin_rows.append(row)
                classified_plugins.append(row)
                writer.write("Bridge_CoworkPlugin", row)
            candidates = [row for row in classified_plugins if row["_role"] != "Orchestration"]
            candidates.sort(key=lambda row: (
                row["_priority"], row["_ordinal"], row["PluginName"] or ""
            ))
            best = candidates[0] if candidates else None
            resources = event["_resources"]
            artifact = artifact_category(resources)
            best_rule = best["_rule"] if best else None
            if artifact:
                category = artifact
                signal = "Artifact written"
                confidence = "Observed"
            elif best_rule and best_rule["category"] != "General assistance / Other":
                category = best_rule["category"]
                signal = "Skill invoked"
                confidence = best_rule["confidence"]
            elif event["Resource_Count"] > 0:
                category = "Analysis & Research"
                signal = "Content accessed"
                confidence = "None"
            elif best_rule:
                category = best_rule["category"]
                signal = "General skill"
                confidence = best_rule["confidence"]
            else:
                category = "General assistance / Other"
                signal = "No signal"
                confidence = "None"
            display = (
                best_rule["friendly_name"] if best_rule else
                (best["PluginName"] if best and best["PluginName"] else "Unspecified Skill")
            )
            details: list[str] = []
            if candidates:
                details.append(display + (f" + {len(candidates)-1} more" if len(candidates) > 1 else ""))
            if artifact:
                details.append("created a file in OneDrive")
            if event["Resource_Count"] > 0:
                details.append(f"{event['Resource_Count']} file(s) referenced")
            if event["Message_PromptCount"] > 0:
                details.append(f"{event['Message_PromptCount']} prompt(s)")
            classification = {
                "RecordId": event["RecordId"], "ThreadId": event["ThreadId"],
                "Category": category, "CategoryKey": categories[category]["key"],
                "CategorySignal": signal, "MappingConfidence": confidence,
                "SkillDisplayName": display, "ActivityDetail": " | ".join(details),
                "CategoryPriority": best_rule["priority"] if best_rule else 9999,
            }
            classifications[event["RecordId"]] = classification
            writer.write("CoworkClassification", classification)
            for resource in resources:
                url = text(resource.get("SiteUrl"))
                owned = bool(url and "/documents/cowork/" in url.lower())
                extension = None
                if url and "." in url:
                    candidate = url.rsplit(".", 1)[-1]
                    extension = candidate.lower() if len(candidate) <= 5 else None
                resource_row = {
                    "RecordId": event["RecordId"], "ThreadId": event["ThreadId"],
                    "DateKey": event["DateKey"], "UserKey": event["UserKey"],
                    "SiteUrl": url, "ResType": text(resource.get("Type")),
                    "ResAction": text(resource.get("Action")),
                    "SensitivityLabelId": text(resource.get("SensitivityLabelId")),
                    "IsCoworkArtifact": owned, "ArtifactExt": extension,
                }
                resource_rows.append(resource_row)
                writer.write("Bridge_CoworkResource", resource_row)

        thread_events: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for event in cowork_events:
            if event["ThreadId"] and str(event["ThreadId"]).strip():
                thread_events[event["ThreadId"]].append(event)
        thread_plugins: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in plugin_rows:
            if row["ThreadId"] and str(row["ThreadId"]).strip():
                thread_plugins[row["ThreadId"]].append(row)

        threads: list[dict[str, Any]] = []
        for thread_id in sorted(thread_events):
            events = thread_events[thread_id]
            created_values = [event["_created"] for event in events if event["_created"]]
            started = min(created_values) if created_values else None
            ended = max(created_values) if created_values else None
            model_groups: dict[str, list[str]] = defaultdict(list)
            for event in events:
                model = (
                    str(event["ModelProviderName"]).strip()
                    if event["ModelProviderName"] and str(event["ModelProviderName"]).strip()
                    else "(Model data not available)"
                )
                model_groups[model].append(event["RecordId"])
            model = sorted(
                model_groups,
                key=lambda key: (-len(model_groups[key]), min(model_groups[key]), key),
            )[0]
            grouped_plugins: dict[tuple[Any, ...], dict[str, Any]] = {}
            for plugin in thread_plugins.get(thread_id, []):
                rule = plugin["_rule"] or {}
                key = (
                    plugin["PluginName"], plugin["_key"], plugin["_role"],
                    bool(plugin["_rule"]), plugin["_priority"],
                    rule.get("friendly_name"), rule.get("business_behavior"),
                )
                group = grouped_plugins.setdefault(
                    key, {"row": plugin, "count": 0, "first": plugin["RecordId"]}
                )
                group["count"] += 1
                group["first"] = min(group["first"], plugin["RecordId"])
            specific = [
                group for group in grouped_plugins.values()
                if group["row"]["_role"] != "Orchestration"
            ]
            specific.sort(key=lambda group: (
                group["row"]["_priority"], -group["count"], group["first"],
                group["row"]["PluginName"] or "",
            ))
            primary = specific[0]["row"] if specific else None
            primary_rule = primary["_rule"] if primary else None
            role = primary["_role"] if primary else None
            thread_classes = [classifications[event["RecordId"]] for event in events]
            thread_classes.sort(key=lambda item: (
                item["CategoryPriority"], item["RecordId"]
            ))
            thread_category = thread_classes[0]["Category"] if thread_classes else "General assistance / Other"
            row = {
                "ThreadId": thread_id,
                "UserKey": max(
                    (event["UserKey"] for event in events if event["UserKey"] is not None),
                    default=None,
                ),
                "DateKey": min(
                    (event["DateKey"] for event in events if event["DateKey"] is not None),
                    default=None,
                ),
                "WeekStartDate": week_start(started), "StartedAt": started, "EndedAt": ended,
                "RecordCount": len(events),
                "PromptCount": sum(event["Message_PromptCount"] for event in events),
                "ResourceCount": sum(event["Resource_Count"] for event in events),
                "PluginCount": sum(event["Plugin_Count"] for event in events),
                "DurationMin": ((ended - started).total_seconds() / 60) if started and ended else None,
                "Model": model,
                "PrimarySkill": primary["PluginName"] if primary else None,
                "PrimaryBusinessTool":
                    primary["PluginName"] if primary and role == "Business"
                    else "No business tool identified",
                "PrimarySkillDisplayName":
                    (primary_rule["friendly_name"] if primary_rule else primary["PluginName"])
                    if primary else "General request",
                "BusinessBehavior":
                    primary_rule["business_behavior"] if primary_rule else "Unmapped behavior",
                "BehaviorConfidence": "Mapped" if primary_rule else "Unmapped",
                "PrimaryCategory": thread_category, "ThreadCategory": thread_category,
                "ThreadCategoryKey": categories[thread_category]["key"],
                "TaskClassification":
                    "Business classified" if role == "Business"
                    else "Unclassified" if role == "Unclassified"
                    else "Orchestration only" if any(
                        group["row"]["_role"] == "Orchestration"
                        for group in grouped_plugins.values()
                    )
                    else "No tool observed",
                "BusinessToolCount": sum(
                    1 for group in grouped_plugins.values()
                    if group["row"]["_role"] == "Business"
                ),
                "UnclassifiedToolCount": sum(
                    1 for group in grouped_plugins.values()
                    if group["row"]["_role"] == "Unclassified"
                ),
                "OrchestrationToolCount": sum(
                    1 for group in grouped_plugins.values()
                    if group["row"]["_role"] == "Orchestration"
                ),
                "_mapped_behavior": primary_rule["business_behavior"] if primary_rule else None,
            }
            threads.append(row)
            writer.write("Fact_CoworkThread", row)

        activity_by_user: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for event in cowork_events:
            if event["UserKey"] is not None:
                activity_by_user[event["UserKey"]].append(event)
        if usage_rows is None or not usage:
            for user_key in sorted(activity_by_user):
                events = activity_by_user[user_key]
                user = users[user_key - 1]
                writer.write("Fact_CoworkUsage", {
                    "UserPrincipalName": user["UserPrincipalName"],
                    "DisplayName": user["DisplayName"], "UserKey": user_key,
                    "TotalTasks": len(set(event["ThreadId"] for event in events)),
                    "ScheduledTasks": None, "UserInitiatedTasks": None,
                    "ActiveDays": len(set(event["DateKey"] for event in events)),
                    "LastActivityDate": max(event["_created"] for event in events),
                    "DataQuality":
                        "Real - derived from the Purview audit log (Fact_CopilotAuditRaw); "
                        "admin center usage export not connected or has zero rows -- "
                        "Scheduled/User-Initiated split unavailable from this source",
                })
        else:
            for upn in sorted(usage):
                source = usage[upn]
                user = user_by_upn.get(upn)
                quality = (
                    "Real - loaded from CoworkUsageCsvPath, matched to a real Cowork user"
                    if user else
                    "Real - loaded from CoworkUsageCsvPath, but UserPrincipalName did not match any known Cowork user"
                )
                if usage_duplicates:
                    quality += (
                        f"; selected the latest row per user and removed "
                        f"{usage_duplicates} duplicate snapshot row(s)"
                    )
                writer.write("Fact_CoworkUsage", {
                    "UserPrincipalName": source.get("UserPrincipalName"),
                    "DisplayName": source.get("DisplayName"),
                    "UserKey": user["UserKey"] if user else None,
                    "TotalTasks": integer(source.get("TotalTasks"), "TotalTasks"),
                    "ScheduledTasks": integer(source.get("ScheduledTasks"), "ScheduledTasks"),
                    "UserInitiatedTasks": integer(source.get("UserInitiatedTasks"), "UserInitiatedTasks"),
                    "ActiveDays": integer(source.get("ActiveDays"), "ActiveDays"),
                    "LastActivityDate": required_source_datetime(
                        source.get("LastActivityDate"), "Cowork usage LastActivityDate"
                    ),
                    "DataQuality": quality,
                })

        effective_org = org_rows if org_rows is not None else identity_rows
        org_seen: set[str] = set()
        for source in effective_org or []:
            principal = source.get("userPrincipalName")
            if principal in org_seen:
                continue
            org_seen.add(principal or "")
            user = user_by_upn.get(norm(principal))
            if not user:
                continue
            writer.write("Dim_UserOrg", {
                "UserPrincipalName": principal, "UserKey": user["UserKey"],
                "DisplayName": source.get("displayName"),
                "Department": source.get("department"), "JobTitle": source.get("jobTitle"),
                "JobFamily": source.get("jobFamily"), "City": source.get("city"),
                "Country": source.get("country"), "CostCenter": source.get("costCenter"),
                "Manager": source.get("manager"), "BusinessUnit": source.get("businessUnit"),
                "DataQuality":
                    "Real - loaded from OrgCsvPath, matched to a real Cowork user"
                    if org_rows is not None else
                    "Real - partial organization attributes loaded from Entra identity export; unavailable fields remain blank",
            })

        last_activity: dict[str, dt.datetime] = {}
        for upn, user in user_by_upn.items():
            observations: list[dt.datetime] = []
            observations.extend(
                event["_created"] for event in activity_by_user.get(user["UserKey"], [])
                if event["_created"]
            )
            for source, field in (
                (usage.get(upn), "LastActivityDate"),
                (consumption.get(upn), "Last activity date"),
            ):
                parsed = (
                    required_source_datetime(source.get(field), field)
                    if source else None
                )
                if parsed:
                    observations.append(parsed)
            if observations:
                last_activity[upn] = max(observations)
        observed_as_of = max(last_activity.values()).date() if last_activity else None
        consumption_facts: list[dict[str, Any]] = []
        for user in users:
            upn = user["_upn"]
            source = consumption.get(upn)
            limit = integer(source.get("Monthly credit limit"), "Monthly credit limit") if source else None
            used = integer(source.get("Monthly credits used"), "Monthly credits used") if source else None
            sessions = integer(source.get("Session Count"), "Session Count") if source else None
            latest = last_activity.get(upn)
            days = (observed_as_of - latest.date()).days if latest and observed_as_of else None
            recency = (
                "Unknown" if days is None else "0-7 days" if days <= 7
                else "8-30 days" if days <= 30 else "31-60 days" if days <= 60
                else "60+ days"
            )
            budget = None
            if limit is not None and used is not None:
                budget = (
                    "Unassigned" if limit == 0 else "Over allowance" if used / limit > 1
                    else "Near limit" if used / limit >= .85
                    else "Healthy 25-85%" if used / limit >= .25 else "Under 25%"
                )
            quality = (
                "Unavailable - Consumption - Users export is missing or does not match the required schema"
                if consumption_rows is None else
                "Real - loaded from CreditCsvPath (customer-provided MAC 'Consumption - Users' export)"
                if any(value is not None for value in (limit, used, sessions)) else
                "Unavailable - no matching row in the loaded Consumption - Users export"
            )
            if consumption_rows is not None and source and consumption_duplicates:
                quality += (
                    f"; selected the latest row per user and removed "
                    f"{consumption_duplicates} duplicate snapshot row(s)"
                )
            consumption_facts.append({
                "UserKey": user["UserKey"], "ServiceKey": 1,
                "DateKey": int(latest.strftime("%Y%m%d")) if latest else None,
                "CreditsUsed": used, "CreditLimit": limit, "SessionCount": sessions,
                "LastActivityDate": latest, "DaysSinceActivity": days,
                "RecencyBucket": recency,
                "RecencyBucketSort":
                    {"0-7 days": 1, "8-30 days": 2, "31-60 days": 3, "60+ days": 4}.get(recency, 5),
                "BudgetSegment": budget, "ConsumptionDataQuality": quality,
            })
        consumption_facts.sort(
            key=lambda row: (
                row["CreditsUsed"] is None,
                -(row["CreditsUsed"] or 0),
                row["UserKey"],
            )
        )
        has_consumption = any(row["CreditsUsed"] is not None for row in consumption_facts)
        count = len(consumption_facts)
        for rank, row in enumerate(consumption_facts, 1):
            row["CohortRank"] = rank
            if not has_consumption:
                row["CohortBand"] = "Unavailable - connect customer consumption export"
            elif count < 20:
                row["CohortBand"] = f"Insufficient sample (n={count})"
            else:
                percentile = (rank - 1) / count
                row["CohortBand"] = (
                    "90%+" if percentile < .10 else "75-90%" if percentile < .25
                    else "50-75%" if percentile < .50 else "25-50%" if percentile < .75
                    else "0-25%"
                )
            writer.write("Fact_Consumption", row)

        user_day: dict[tuple[Any, ...], dict[str, Any]] = {}
        for event in cowork_events:
            if event["UserKey"] is None or event["DateKey"] is None:
                continue
            key = (
                event["UserKey"], event["Audit_UserId"], event["Audit_UserId_Normalized"],
                event["DateKey"], event["ModelProviderName"],
            )
            result = user_day.setdefault(key, {
                "UserKey": event["UserKey"], "Audit_UserId": event["Audit_UserId"],
                "Audit_UserId_Normalized": event["Audit_UserId_Normalized"],
                "DateKey": event["DateKey"], "ModelProviderName": event["ModelProviderName"],
                "InteractionCount": 0, "PromptCount": 0,
            })
            result["InteractionCount"] += 1
            result["PromptCount"] += event["Message_PromptCount"]
        for key in sorted(user_day, key=lambda item: tuple("" if x is None else x for x in item)):
            row = user_day[key]
            day = dt.datetime.strptime(str(row["DateKey"]), "%Y%m%d")
            row["WeekStartDate"] = week_start(day)
            row["UserDateKey"] = f"{row['UserKey']}|{row['DateKey']}"
            writer.write("Fact_CoworkUserDayModel", row)

        models: set[str] = set()
        for thread in threads:
            category = category_by_key[thread["ThreadCategoryKey"]]
            mid = human_baselines.get(thread["_mapped_behavior"], category["mid"])
            task = {
                "ThreadId": thread["ThreadId"], "UserKey": thread["UserKey"],
                "CategoryKey": thread["ThreadCategoryKey"], "DateKey": thread["DateKey"],
                "Tasks": 1, "Model": thread["Model"],
                "PrimaryBusinessTool": thread["PrimaryBusinessTool"],
                "PrimarySkillDisplayName": thread["PrimarySkillDisplayName"],
                "BusinessBehavior": thread["BusinessBehavior"],
                "TaskClassification": thread["TaskClassification"],
                "LowMin": min(category["low"], mid), "MidMin": mid,
                "HighMin": max(category["high"], mid),
            }
            models.add(thread["Model"])
            writer.write("Fact_Tasks", task)

        skill_by_name: dict[str | None, dict[str, Any]] = {}
        for plugin in plugin_rows:
            skill_by_name.setdefault(plugin["PluginName"], plugin)
        sentinel_rule = classify("no business tool identified", rules)
        skill_by_name.setdefault("No business tool identified", {
            "PluginName": "No business tool identified",
            "_key": "no business tool identified", "_rule": sentinel_rule,
            "_role": "Business" if sentinel_rule else "Unclassified",
        })
        for plugin_name in sorted(skill_by_name, key=lambda value: value or ""):
            plugin = skill_by_name[plugin_name]
            rule = plugin.get("_rule")
            category_name = rule["category"] if rule else "General assistance / Other"
            category = categories[category_name]
            writer.write("Dim_CoworkSkill", {
                "PluginName": plugin_name or "",
                "SkillDisplayName": rule["friendly_name"] if rule else (plugin_name or "Unspecified Skill"),
                "Category": category_name, "CategoryKey": category["key"],
                "IsMapped": bool(rule),
                "ToolRole": plugin.get("_role") or "Unclassified",
                "BusinessBehavior": rule["business_behavior"] if rule else "",
                "MappingConfidence": rule["confidence"] if rule else "None",
                "AttributionPriority": rule["priority"] if rule else 9999,
                "IsBusinessTool": plugin.get("_role") == "Business",
                "LowMin": category["low"], "MidMin": category["mid"], "HighMin": category["high"],
            })
        for model in sorted(models):
            writer.write("Dim_ModelProvider", {
                "Model": model, "HasModelData": model != "(Model data not available)"
            })
        writer.close()
        connection.close()
        work_db.unlink(missing_ok=True)
        (temp_dir / ".work.sqlite-wal").unlink(missing_ok=True)
        (temp_dir / ".work.sqlite-shm").unlink(missing_ok=True)

        entity_counts = dict(writer.counts)
        reconciliation.update({
            "cowork_detail_rows": cowork_detail_count,
            "cowork_thread_tasks": len(threads),
            "active_users": len({
                event["UserKey"] for event in cowork_events if event["UserKey"] is not None
            }),
            "prompt_count": sum(event["Message_PromptCount"] for event in cowork_events),
            "entity_rows": entity_counts,
        })
        schema = {
            entity: {
                "columns": ["_Entity", "_RowId", *fields],
                "types": {
                    field:
                        "int64" if field in INT_FIELDS
                        else "double" if field in FLOAT_FIELDS
                        else "boolean" if field in BOOL_FIELDS
                        else "datetime" if field in DATETIME_FIELDS
                        else "date" if field in DATE_FIELDS else "string"
                    for field in ["_Entity", "_RowId", *fields]
                },
            }
            for entity, fields in ENTITY_FIELDS.items()
        }
        timings["total_seconds"] = round(time.perf_counter() - overall, 3)
        manifest = {
            "format": MANIFEST_FORMAT,
            "preprocessor_version": VERSION,
            "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "input_folder": str(input_dir.resolve()),
            "output_folder": str(output_dir.resolve()),
            "input_files": input_identities,
            "selected_sources": {
                "audit": [str(entry["path"]) for entry in audit_files],
                "usage": str(usage_entry["path"]) if usage_entry else None,
                "consumption": str(consumption_entry["path"]) if consumption_entry else None,
                "identity": str(identity_entry["path"]) if identity_entry else None,
                "organization": str(org_entry["path"]) if org_entry else None,
            },
            "parse_errors": parse_errors,
            "duplicate_snapshot_rows": {
                "usage": usage_duplicates, "consumption": consumption_duplicates,
            },
            "timings": timings,
            "reconciliation": reconciliation,
            "schema": schema,
        }
        (temp_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        validate_output(temp_dir, manifest)
        if validate_only:
            shutil.rmtree(temp_dir)
        else:
            if output_dir.exists():
                backup = output_parent / f".{output_dir.name}.previous-{uuid.uuid4().hex}"
                output_dir.replace(backup)
                temp_dir.replace(output_dir)
                shutil.rmtree(backup)
            else:
                temp_dir.replace(output_dir)
        if not quiet:
            print(json.dumps({
                "status": "validated" if validate_only else "complete",
                "manifest": None if validate_only else str(output_dir / "manifest.json"),
                "timings": timings, "reconciliation": reconciliation,
            }, indent=2))
        return manifest
    except Exception:
        connection.close()
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def validate_output(folder: Path, manifest: dict[str, Any]) -> None:
    errors: list[str] = []
    counts: dict[str, int] = {}
    for entity, fields in ENTITY_FIELDS.items():
        path = folder / f"entity-{entity}.csv"
        if not path.is_file():
            errors.append(f"Missing {path.name}")
            continue
        with path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.reader(stream)
            header = next(reader, [])
            expected = ["_Entity", "_RowId", *fields]
            if header != expected:
                errors.append(f"{path.name} header mismatch")
            count = sum(1 for _ in reader)
            counts[entity] = count
            expected_count = manifest["reconciliation"]["entity_rows"].get(entity, 0)
            if count != expected_count:
                errors.append(
                    f"{path.name} has {count} rows; manifest says {expected_count}"
                )
    if counts.get("Fact_CoworkThread") != counts.get("Fact_Tasks"):
        errors.append("Fact_CoworkThread and Fact_Tasks grain counts differ")
    if counts.get("CoworkClassification") != manifest["reconciliation"]["cowork_detail_rows"]:
        errors.append("CoworkClassification count differs from Cowork detail count")
    if errors:
        raise PreprocessorError("Output validation failed: " + "; ".join(errors))


def validate_existing(output_dir: Path) -> dict[str, Any]:
    if not output_dir.is_dir():
        raise PreprocessorError(f"Output path is not a folder: {output_dir}")
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.is_file():
        raise PreprocessorError(
            "Existing output folder is not owned by this preprocessor because "
            f"its manifest is missing: {manifest_path}"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("format") != MANIFEST_FORMAT:
        raise PreprocessorError(
            "Existing output folder has an unsupported or foreign manifest format."
        )
    validate_output(output_dir, manifest)
    return manifest


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Preprocess Cowork Purview and optional supporting CSVs."
    )
    result.add_argument("--input", type=Path, help="Read-only input folder")
    result.add_argument("--output", type=Path, help="Separate output folder")
    result.add_argument(
        "--validate", action="store_true",
        help="Validate/reconcile processing without retaining generated output",
    )
    result.add_argument(
        "--validate-output", type=Path,
        help="Validate an existing preprocessed output folder",
    )
    result.add_argument("--quiet", action="store_true")
    result.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.validate_output:
            manifest = validate_existing(args.validate_output.resolve())
            if not args.quiet:
                print(json.dumps({
                    "status": "valid",
                    "reconciliation": manifest["reconciliation"],
                }, indent=2))
            return 0
        if args.input is None or args.output is None:
            parser().error("--input and --output are required for processing")
        process(
            args.input.resolve(), args.output.resolve(),
            validate_only=args.validate, quiet=args.quiet,
        )
        return 0
    except (PreprocessorError, OSError, sqlite3.Error, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
