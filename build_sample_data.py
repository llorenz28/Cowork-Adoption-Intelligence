#!/usr/bin/env python3
"""Build deterministic sample data for Cowork Adoption Intelligence."""

from __future__ import annotations

import csv
import hashlib
import json
import random
import uuid
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


SEED = 20260907
USER_COUNT = 72
THREAD_COUNT = 900
AS_OF = datetime(2026, 9, 6, 18, 0, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "sample_data"
AUDIT_OUT = OUT / "purview_audit"

FIRST_NAMES = [
    "Avery", "Blake", "Casey", "Dakota", "Emerson", "Finley", "Harper", "Hayden",
    "Jordan", "Kai", "Logan", "Morgan", "Parker", "Quinn", "Reese", "Riley",
    "Rowan", "Sage", "Skyler", "Taylor", "Alex", "Cameron", "Drew", "Elliot",
]
LAST_NAMES = [
    "Adams", "Bennett", "Carter", "Diaz", "Edwards", "Foster", "Garcia", "Hughes",
    "Ibrahim", "Jensen", "Kim", "Lopez", "Martin", "Nguyen", "Owens", "Patel",
    "Reed", "Singh", "Turner", "Wright", "Young", "Zhang", "Brooks", "Clark",
]

ORG_ROWS = [
    ("Customer Success", "Field", "Seattle", "United States", "CS100"),
    ("Sales", "Field", "Chicago", "United States", "SL200"),
    ("Marketing", "Growth", "New York", "United States", "MK300"),
    ("Finance", "Corporate", "London", "United Kingdom", "FN400"),
    ("People", "Corporate", "Toronto", "Canada", "HR500"),
    ("Engineering", "Product", "Dublin", "Ireland", "EN600"),
    ("Operations", "Operations", "Austin", "United States", "OP700"),
    ("Legal", "Corporate", "Amsterdam", "Netherlands", "LG800"),
]

SKILLS = [
    ("Word", "Document & content creation", 1.15),
    ("PowerPoint", "Document & content creation", 0.80),
    ("PDF", "Document & content creation", 0.50),
    ("Adaptive Cards", "Document & content creation", 0.25),
    ("Excel", "Analysis & Research", 1.05),
    ("Enterprise Search", "Analysis & Research", 1.00),
    ("Deep Research", "Analysis & Research", 0.70),
    ("Read", "Analysis & Research", 0.70),
    ("Email", "Email workflows", 0.95),
    ("Communications", "Communication workflows", 0.75),
    ("Scheduling", "Meeting workflows", 0.65),
    ("Calendar Management", "Meeting workflows", 0.55),
    ("Meetings", "Meeting workflows", 0.55),
    ("Daily Briefing", "Meeting workflows", 0.35),
    ("TaskUpdate", "Specialized workflows", 0.45),
    ("Glob", "Specialized workflows", 0.30),
    ("BuiltIn", "General assistance / Other", 0.35),
    ("report_intent", "General assistance / Other", 0.25),
]

MODELS = [
    ("Synthetic Model - Fast", 0.72, 1.18),
    ("Synthetic Model - Balanced", 1.00, 1.00),
    ("Synthetic Model - Efficient", 1.18, 0.72),
]


def stable_uuid(namespace: str, value: str) -> str:
    return str(uuid.uuid5(uuid.uuid5(uuid.NAMESPACE_DNS, namespace), value))


def write_csv(path: Path, headers: list[str], rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        writer.writerows(rows)


def weighted_choice(rng: random.Random, items: list[tuple], weight_index: int):
    return rng.choices(items, weights=[item[weight_index] for item in items], k=1)[0]


def build_users(rng: random.Random) -> list[dict]:
    users = []
    used_upns: set[str] = set()
    for index in range(USER_COUNT):
        first = FIRST_NAMES[index % len(FIRST_NAMES)]
        last = LAST_NAMES[(index * 5 + index // len(FIRST_NAMES)) % len(LAST_NAMES)]
        base = f"{first}.{last}".lower()
        upn = f"{base}@example.com"
        suffix = 1
        while upn in used_upns:
            suffix += 1
            upn = f"{base}{suffix}@example.com"
        used_upns.add(upn)

        department, business_unit, city, country, cost_center = ORG_ROWS[index % len(ORG_ROWS)]
        job_family = {
            "Engineering": "Engineering",
            "Sales": "Sales",
            "Marketing": "Marketing",
            "Finance": "Finance",
            "People": "Human Resources",
            "Legal": "Legal",
            "Operations": "Operations",
            "Customer Success": "Customer Success",
        }[department]
        title = rng.choice(
            ["Specialist", "Senior Specialist", "Manager", "Principal", "Program Manager"]
        )
        users.append(
            {
                "id": stable_uuid("cowork-value-intelligence-user", upn),
                "display": f"{first} {last}",
                "upn": upn,
                "department": department,
                "business_unit": business_unit,
                "city": city,
                "country": country,
                "cost_center": cost_center,
                "job_family": job_family,
                "job_title": f"{job_family} {title}",
            }
        )

    for index, user in enumerate(users):
        manager = users[(index // 9) * 9]
        user["manager"] = manager["display"] if manager is not user else "Executive Sponsor"
    return users


def build_activity(rng: random.Random, users: list[dict]):
    audit_rows: list[list[object]] = []
    user_threads: dict[str, set[str]] = defaultdict(set)
    user_dates: dict[str, set[str]] = defaultdict(set)
    user_last: dict[str, datetime] = {}
    user_model_mix: dict[str, Counter] = defaultdict(Counter)
    user_duration: dict[str, float] = defaultdict(float)
    user_prompts: dict[str, int] = defaultdict(int)
    scheduled_threads: set[str] = set()

    audit_headers = [
        "RecordId", "CreationDate", "RecordType", "Operation", "UserId", "AuditData",
        "AssociatedAdminUnits", "AssociatedAdminUnitsNames",
    ]

    month_starts = [
        datetime(2026, month, 1, 8, 0, tzinfo=timezone.utc)
        for month in range(3, 10)
    ]
    month_weights = [0.65, 0.76, 0.88, 1.00, 1.14, 1.30, 1.48]

    for thread_index in range(THREAD_COUNT):
        user = rng.choices(
            users,
            weights=[1.0 + ((i * 17) % 11) / 6 for i in range(len(users))],
            k=1,
        )[0]
        month_start = rng.choices(month_starts, weights=month_weights, k=1)[0]
        day = rng.randint(0, 26)
        hour = rng.randint(7, 18)
        minute = rng.randint(0, 59)
        started = month_start + timedelta(days=day, hours=hour, minutes=minute)
        if started > AS_OF:
            started = AS_OF - timedelta(days=rng.randint(0, 5), hours=rng.randint(0, 8))

        primary_skill = weighted_choice(rng, SKILLS, 2)
        model = rng.choices(MODELS, weights=[0.34, 0.43, 0.23], k=1)[0]
        step_count = rng.choices([2, 3, 4, 5, 6], weights=[0.18, 0.31, 0.27, 0.16, 0.08], k=1)[0]
        base_duration = rng.uniform(3.2, 18.0) * model[1]
        duration = max(1.2, min(34.0, base_duration + (step_count - 3) * 1.1))
        thread_id = stable_uuid("cowork-value-intelligence-thread", str(thread_index))
        is_scheduled = rng.random() < (0.10 + (thread_index % 7) * 0.012)
        if is_scheduled:
            scheduled_threads.add(thread_id)

        chained_skills = [primary_skill]
        if step_count >= 4 and rng.random() < 0.72:
            secondary = weighted_choice(rng, SKILLS, 2)
            if secondary[0] != primary_skill[0]:
                chained_skills.append(secondary)
        if step_count >= 5 and rng.random() < 0.30:
            tertiary = weighted_choice(rng, SKILLS, 2)
            if tertiary[0] not in {skill[0] for skill in chained_skills}:
                chained_skills.append(tertiary)

        for step in range(step_count):
            at = started + timedelta(minutes=duration * step / max(step_count - 1, 1))
            skill = chained_skills[min(step * len(chained_skills) // step_count, len(chained_skills) - 1)]
            prompt_count = 1 if step == 0 or rng.random() < 0.55 else 0
            messages = [{"isPrompt": True, "sequence": step + 1}] if prompt_count else []
            if rng.random() < 0.72:
                messages.append({"isPrompt": False, "sequence": step + 1})

            plugins = [
                {
                    "Name": skill[0],
                    "Id": stable_uuid("cowork-value-intelligence-skill", skill[0]),
                }
            ]
            if len(chained_skills) > 1 and step == step_count - 1:
                plugins.append(
                    {
                        "Name": chained_skills[-1][0],
                        "Id": stable_uuid(
                            "cowork-value-intelligence-skill", chained_skills[-1][0]
                        ),
                    }
                )

            resources = []
            if rng.random() < 0.62:
                extension = rng.choice(["docx", "pptx", "xlsx", "pdf"])
                action = "Create" if rng.random() < 0.46 else "Read"
                folder = "Cowork" if action == "Create" else "Reference"
                resources.append(
                    {
                        "SiteUrl": (
                            "https://tenant.example.com/Documents/"
                            f"{folder}/Synthetic-{thread_index + 1:04d}.{extension}"
                        ),
                        "Type": "File",
                        "Action": action,
                        "SensitivityLabelId": "",
                    }
                )

            audit_data = {
                "Workload": "MicrosoftCopilot",
                "ClientRegion": rng.choice(["NAM", "EUR", "APAC"]),
                "AppIdentity": "Microsoft 365 Copilot",
                "CopilotEventData": {
                    "AppHost": "cowork",
                    "ThreadId": thread_id,
                    "LicenseType": "Microsoft 365 Copilot",
                    "TriggerType": "Scheduled" if is_scheduled else "UserInitiated",
                    "Messages": messages,
                    "AISystemPlugin": plugins,
                    "AccessedResources": resources,
                    "ModelTransparencyDetails": [
                        {
                            "ModelProviderName": model[0],
                            "DataClassification": "Synthetic demonstration value",
                        }
                    ],
                },
            }
            record_id = stable_uuid(
                "cowork-value-intelligence-record", f"{thread_index}-{step}"
            )
            audit_rows.append(
                [
                    record_id,
                    at.isoformat().replace("+00:00", "Z"),
                    "CopilotInteraction",
                    "CopilotInteraction",
                    user["upn"],
                    json.dumps(audit_data, separators=(",", ":"), sort_keys=True),
                    "",
                    "",
                ]
            )
            user_prompts[user["upn"]] += prompt_count

        user_threads[user["upn"]].add(thread_id)
        user_dates[user["upn"]].add(started.date().isoformat())
        user_last[user["upn"]] = max(started, user_last.get(user["upn"], started))
        user_model_mix[user["upn"]][model[0]] += 1
        user_duration[user["upn"]] += duration

    audit_rows.sort(key=lambda row: (row[1], row[0]))
    midpoint = len(audit_rows) // 2
    write_csv(AUDIT_OUT / "CoworkAudit-Synthetic-Part01.csv", audit_headers, audit_rows[:midpoint])
    write_csv(AUDIT_OUT / "CoworkAudit-Synthetic-Part02.csv", audit_headers, audit_rows[midpoint:])
    return (
        user_threads,
        user_dates,
        user_last,
        user_model_mix,
        user_duration,
        user_prompts,
        scheduled_threads,
    )


def build_dimension_and_usage_files(
    rng: random.Random,
    users: list[dict],
    activity,
) -> None:
    (
        user_threads,
        user_dates,
        user_last,
        user_model_mix,
        user_duration,
        user_prompts,
        scheduled_threads,
    ) = activity

    identity_rows = [[u["id"], u["display"], u["upn"]] for u in users]
    write_csv(
        OUT / "cowork_users.csv",
        ["id", "displayName", "userPrincipalName"],
        identity_rows,
    )

    org_rows = [
        [
            u["upn"], u["display"], u["department"], u["job_title"], u["job_family"],
            u["city"], u["country"], u["cost_center"], u["manager"], u["business_unit"],
        ]
        for u in users
    ]
    write_csv(
        OUT / "CoworkUserOrgDetails.csv",
        [
            "userPrincipalName", "displayName", "department", "jobTitle", "jobFamily",
            "city", "country", "costCenter", "manager", "businessUnit",
        ],
        org_rows,
    )

    usage_rows = []
    consumption_rows = []
    for user_index, user in enumerate(users):
        upn = user["upn"]
        total = len(user_threads[upn])
        scheduled = sum(1 for thread in user_threads[upn] if thread in scheduled_threads)
        initiated = total - scheduled
        active_days = len(user_dates[upn])
        last = user_last[upn].isoformat().replace("+00:00", "Z") if total else ""
        usage_rows.append(
            [upn, user["display"], total, scheduled, initiated, active_days, last]
        )

        dominant_model = user_model_mix[upn].most_common(1)[0][0] if total else MODELS[1][0]
        model_credit_factor = next(model[2] for model in MODELS if model[0] == dominant_model)
        credits_used = round(
            max(0, total * model_credit_factor * rng.uniform(7.5, 11.5) + user_prompts[upn] * 0.6)
        )
        if user_index % 10 == 0:
            limit_factor = 0.78
        elif user_index % 7 == 0:
            limit_factor = 1.08
        else:
            limit_factor = 1.35
        credit_limit = max(50, int(((credits_used * limit_factor + 49) // 50) * 50))
        sessions = total
        pct = round(credits_used / credit_limit * 100, 1) if credit_limit else ""
        consumption_rows.append(
            [
                user["display"], upn, credit_limit, credits_used, user["id"], "Yes",
                user_last[upn].date().isoformat() if total else "", sessions, pct,
            ]
        )

    write_csv(
        OUT / "CoworkUserDetails.csv",
        [
            "UserPrincipalName", "DisplayName", "TotalTasks", "ScheduledTasks",
            "UserInitiatedTasks", "ActiveDays", "LastActivityDate",
        ],
        usage_rows,
    )
    write_csv(
        OUT / "CoworkConsumptionDetails.csv",
        [
            "Display Name", "User Principal Name", "Monthly credit limit",
            "Monthly credits used", "User ID", "Microsoft 365 Copilot license",
            "Last activity date", "Session Count", "% Used",
        ],
        consumption_rows,
    )


def verify() -> list[str]:
    failures: list[str] = []
    expected = {
        OUT / "cowork_users.csv",
        OUT / "CoworkUserOrgDetails.csv",
        OUT / "CoworkUserDetails.csv",
        OUT / "CoworkConsumptionDetails.csv",
        AUDIT_OUT / "CoworkAudit-Synthetic-Part01.csv",
        AUDIT_OUT / "CoworkAudit-Synthetic-Part02.csv",
    }
    missing = [str(path.relative_to(ROOT)) for path in expected if not path.exists()]
    if missing:
        failures.append("Missing files: " + ", ".join(missing))

    for path in sorted(OUT.rglob("*.csv")):
        with path.open(newline="", encoding="utf-8") as handle:
            for row_number, row in enumerate(csv.DictReader(handle), start=2):
                for key, value in row.items():
                    if key and ("user" in key.lower() or key in {"UserId", "manager"}):
                        if "@" in (value or "") and not value.lower().endswith("@example.com"):
                            failures.append(
                                f"{path.relative_to(ROOT)}:{row_number} has non-example identity"
                            )
                serialized = json.dumps(row, ensure_ascii=True).lower()
                if "@microsoft.com" in serialized:
                    failures.append(
                        f"{path.relative_to(ROOT)}:{row_number} contains prohibited token"
                    )
    return failures


def write_manifest_and_zip() -> None:
    csv_files = sorted(OUT.rglob("*.csv"))
    manifest_lines = [
        "# Deterministic synthetic sample data",
        f"seed={SEED}",
        f"generated_as_of={AS_OF.isoformat()}",
        "identity_rule=all user email addresses end with @example.com",
        "",
    ]
    for path in csv_files:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_lines.append(f"{digest}  {path.relative_to(OUT).as_posix()}")
    (OUT / "_VERIFY.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    zip_targets = [
        (
            ROOT / "release" / "Cowork-Adoption-Intelligence-Sample-Data.zip",
            Path(),
        ),
    ]
    fixed_time = (
        AS_OF.year,
        AS_OF.month,
        AS_OF.day,
        AS_OF.hour,
        AS_OF.minute,
        AS_OF.second,
    )
    for zip_path, prefix in zip_targets:
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        zip_path.unlink(missing_ok=True)
        with zipfile.ZipFile(
            zip_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as archive:
            for path in sorted(OUT.rglob("*")):
                if not path.is_file():
                    continue
                archive_name = (prefix / path.relative_to(OUT)).as_posix()
                info = zipfile.ZipInfo(archive_name, fixed_time)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(
                    info,
                    path.read_bytes(),
                    compress_type=zipfile.ZIP_DEFLATED,
                    compresslevel=9,
                )


def write_sample_readme() -> None:
    (OUT / "README.md").write_text(
        """# Synthetic sample data

This folder is generated by `build_sample_data.py` for Cowork Adoption
Intelligence.

- Every person is fictional.
- Every user email address ends in `@example.com`.
- Model names are explicitly labeled `Synthetic Model`.
- Resource URLs use `tenant.example.com`.
- No tenant export, employee record, credential, or customer content is included.

## Load it

Set `DataFolderPath` to this folder, or extract the dedicated ZIP under
`release/` and select the extraction folder.

See [Path A in the setup guide](../SETUP.md#path-a-try-the-report-with-fabricated-data)
for exact values and verification steps.

Run `python .\\build_sample_data.py` from the repository root only when you need
to regenerate the files. The generator writes a SHA-256 manifest to
`_VERIFY.txt` and a matching ZIP to `release\\`.
""",
        encoding="utf-8",
    )


def main() -> None:
    if OUT.exists():
        for path in sorted(OUT.rglob("*"), key=lambda item: len(item.parts), reverse=True):
            if path.is_file():
                path.unlink()
            elif path != AUDIT_OUT:
                try:
                    path.rmdir()
                except OSError:
                    pass
    AUDIT_OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    users = build_users(rng)
    activity = build_activity(rng, users)
    build_dimension_and_usage_files(rng, users, activity)
    write_sample_readme()
    failures = verify()
    if failures:
        raise SystemExit("Sample data verification failed:\n- " + "\n- ".join(failures))
    write_manifest_and_zip()
    print(
        json.dumps(
            {
                "status": "success",
                "seed": SEED,
                "users": USER_COUNT,
                "threads": THREAD_COUNT,
                "auditRows": sum(
                    1
                    for path in AUDIT_OUT.glob("*.csv")
                    for _ in path.open(encoding="utf-8")
                )
                - len(list(AUDIT_OUT.glob("*.csv"))),
                "identityDomain": "example.com",
                "output": str(OUT),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
