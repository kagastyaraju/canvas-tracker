from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import requests
from icalendar import Calendar


def fetch_assignments(ical_url: str, course_filter: Optional[str] = None) -> list[dict]:
    """Fetch and parse upcoming assignments from a Canvas iCal feed."""
    response = requests.get(ical_url, timeout=10)
    response.raise_for_status()

    cal = Calendar.from_ical(response.content)
    now = datetime.now(timezone.utc)
    assignments = []

    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        # Only grab assignments, not class sessions or other events
        uid = str(component.get("UID", ""))
        if not uid.startswith("event-assignment-"):
            continue

        summary = str(component.get("SUMMARY", "Untitled"))

        # Parse course code from "[MGT71R_SP26_A00]" at end of summary
        course = "Unknown"
        if "[" in summary and "]" in summary:
            course = summary[summary.rfind("[") + 1 : summary.rfind("]")]
            # Strip term/section suffix: MGT71R_SP26_A00 -> MGT71R
            course = course.split("_")[0]

        # Strip the [COURSE] tag from the assignment name
        name = summary[: summary.rfind("[")].strip() if "[" in summary else summary

        # Parse due date
        dtstart = component.get("DTSTART")
        if dtstart is None:
            continue
        due: datetime = dtstart.dt
        if not isinstance(due, datetime):
            due = datetime(due.year, due.month, due.day, tzinfo=timezone.utc)
        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)

        # Skip anything already past
        if due <= now:
            continue

        if course_filter and course_filter.lower() not in course.lower():
            continue

        assignments.append({
            "name": name,
            "course": course,
            "due": due,
            "url": str(component.get("URL", "")),
        })

    assignments.sort(key=lambda a: a["due"])
    return assignments