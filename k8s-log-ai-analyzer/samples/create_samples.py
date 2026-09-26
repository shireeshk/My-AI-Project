from pathlib import Path


BASE = Path(__file__).parent


samples = {

    "crashloopbackoff.log": """
2026-09-25T20:01:11Z INFO Starting payment-service
2026-09-25T20:01:12Z INFO Loading configuration
2026-09-25T20:01:12Z ERROR DATABASE_URL environment variable is missing
2026-09-25T20:01:12Z FATAL Unable to initialize database connection
2026-09-25T20:01:12Z ERROR Application startup failed
2026-09-25T20:01:12Z INFO Process exited with code 1
""",

    "oomkilled.log": """
2026-09-25T20:11:01Z INFO Starting analytics-worker
2026-09-25T20:11:05Z INFO Loading dataset
2026-09-25T20:11:15Z INFO Dataset size: 4.8 GB
2026-09-25T20:11:21Z ERROR Java heap allocation failed
2026-09-25T20:11:22Z FATAL Process terminated
State: Terminated
Reason: OOMKilled
Exit Code: 137
Restart Count: 8
Memory Limit: 1Gi
""",

    "imagepullbackoff.log": """
Warning Failed
Failed to pull image "company/payment-service:9.9.99"
rpc error:
code = NotFound
message = failed to resolve reference
manifest unknown
Back-off pulling image
""",

    "healthy-pod.log": """
2026-09-25T20:30:01Z INFO Application started
2026-09-25T20:30:02Z INFO HTTP server listening on port 8080
2026-09-25T20:30:05Z INFO Health check passed
2026-09-25T20:30:10Z INFO Processing request
2026-09-25T20:30:11Z INFO Request completed status=200
""",

    "describe-crashloop.txt": """
Name: payment-service-7d8c7f9f5d-x2k7p
Namespace: production

Containers:
  payment-service:
    Image: company/payment-service:2.4.1

    State:
      Waiting
        Reason: CrashLoopBackOff

    Last State:
      Terminated
        Reason: Error
        Exit Code: 1

    Restart Count: 17

Events:
  Warning BackOff
  Back-off restarting failed container
""",
}


for filename, content in samples.items():

    path = BASE / filename

    path.write_text(
        content.strip() + "\n",
        encoding="utf-8",
    )

    print(f"Created {path}")