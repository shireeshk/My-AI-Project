import re


PATTERNS = [

    {
        "name": "OOMKilled",
        "severity": "CRITICAL",
        "patterns": [
            r"OOMKilled",
            r"out of memory",
            r"memory cgroup",
            r"memory limit",
        ],
        "cause": "Container likely exceeded its configured memory limit.",
        "commands": [
            "kubectl describe pod <pod>",
            "kubectl top pod <pod>",
            "kubectl get pod <pod> -o yaml",
        ],
    },

    {
        "name": "CrashLoopBackOff",
        "severity": "HIGH",
        "patterns": [
            r"CrashLoopBackOff",
            r"Back-off restarting failed container",
        ],
        "cause": "Container is repeatedly terminating and Kubernetes is backing off restarts.",
        "commands": [
            "kubectl logs <pod> --previous",
            "kubectl describe pod <pod>",
            "kubectl get events --sort-by=.lastTimestamp",
        ],
    },

    {
        "name": "ImagePullBackOff",
        "severity": "HIGH",
        "patterns": [
            r"ImagePullBackOff",
            r"ErrImagePull",
            r"pull access denied",
            r"manifest unknown",
            r"image .* not found",
        ],
        "cause": "Kubernetes could not pull the requested container image.",
        "commands": [
            "kubectl describe pod <pod>",
            "kubectl get events --sort-by=.lastTimestamp",
        ],
    },

    {
        "name": "ProbeFailure",
        "severity": "HIGH",
        "patterns": [
            r"liveness probe failed",
            r"readiness probe failed",
            r"startup probe failed",
            r"probe failed",
        ],
        "cause": "A Kubernetes health probe is failing.",
        "commands": [
            "kubectl describe pod <pod>",
            "kubectl get pod <pod> -o yaml",
        ],
    },

    {
        "name": "DNSFailure",
        "severity": "MEDIUM",
        "patterns": [
            r"temporary failure in name resolution",
            r"Name or service not known",
            r"no such host",
            r"DNS",
        ],
        "cause": "The application appears to have a DNS/service-discovery problem.",
        "commands": [
            "kubectl get svc",
            "kubectl get endpoints",
            "kubectl exec <pod> -- nslookup <service>",
        ],
    },

    {
        "name": "ConnectionFailure",
        "severity": "MEDIUM",
        "patterns": [
            r"connection refused",
            r"connection reset",
            r"connection timed out",
            r"timeout connecting",
        ],
        "cause": "The application appears unable to establish a network connection.",
        "commands": [
            "kubectl get svc",
            "kubectl get endpoints",
            "kubectl describe pod <pod>",
        ],
    },

    {
        "name": "PermissionFailure",
        "severity": "HIGH",
        "patterns": [
            r"permission denied",
            r"operation not permitted",
            r"EACCES",
        ],
        "cause": "The process appears to lack required filesystem or operating-system permissions.",
        "commands": [
            "kubectl describe pod <pod>",
            "kubectl get pod <pod> -o yaml",
        ],
    },

    {
        "name": "ApplicationException",
        "severity": "MEDIUM",
        "patterns": [
            r"Exception",
            r"Traceback",
            r"FATAL",
            r"panic:",
            r"Segmentation fault",
        ],
        "cause": "The application generated an exception or fatal runtime error.",
        "commands": [
            "kubectl logs <pod> --previous",
            "kubectl describe pod <pod>",
        ],
    },
]


def analyze_logs(log_text: str):

    findings = []

    for rule in PATTERNS:

        matched_lines = []

        for line in log_text.splitlines():

            for pattern in rule["patterns"]:

                if re.search(pattern, line, re.IGNORECASE):

                    matched_lines.append(line[:500])
                    break

        if matched_lines:

            findings.append(
                {
                    "issue": rule["name"],
                    "severity": rule["severity"],
                    "cause": rule["cause"],
                    "commands": rule["commands"],
                    "evidence": matched_lines[:10],
                    "match_count": len(matched_lines),
                }
            )

    return findings


def summarize_logs(log_text: str):

    lines = log_text.splitlines()

    errors = [
        line
        for line in lines
        if re.search(
            r"\b(error|exception|fatal|failed|failure|oom|panic)\b",
            line,
            re.IGNORECASE,
        )
    ]

    warnings = [
        line
        for line in lines
        if re.search(
            r"\b(warn|warning)\b",
            line,
            re.IGNORECASE,
        )
    ]

    return {
        "total_lines": len(lines),
        "error_lines": len(errors),
        "warning_lines": len(warnings),
        "errors": errors[:20],
        "warnings": warnings[:20],
    }