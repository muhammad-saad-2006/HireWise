"""
mailer.py — Gmail API Email Sender (stub for Day 1)
Full implementation: Day 5
"""

def send_result_email(to_email: str, passed: bool, score: float,
                      role: str, report_path: str | None) -> None:
    """
    Stub: prints email details to console.
    Replace on Day 5 with Gmail API / SMTP.
    """
    status = "INVITE" if passed else "REJECTION"
    print(f"[mailer] STUB — Would send {status} email to {to_email} | "
          f"role={role} | score={score:.2%} | report={report_path}")
