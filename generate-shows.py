#!/usr/bin/env python3
"""generate-shows.py — Bake upcoming Songkick shows into index.html.

Fetches the band's calendar from the same public endpoint the Songkick
widget uses, then rewrites two marked regions of index.html:

  <!-- events-jsonld:start --> ... <!-- events-jsonld:end -->   (in <head>)
      one schema.org MusicEvent JSON-LD block per upcoming show
  <!-- shows-list:start --> ... <!-- shows-list:end -->         (in #shows)
      a static, crawlable list where each show has id="show-YYYY-MM-DD"

Past and cancelled shows are left out. Rerun this whenever shows change,
then commit the result — the JSON-LD must be in the initial HTML, not
injected by JavaScript.

Usage:
    ./generate-shows.py              # fetch from Songkick and rewrite index.html
    ./generate-shows.py --from FILE  # use a saved Songkick JSON response instead
    ./generate-shows.py --check      # exit 1 if index.html would change (no write)
"""
import json
import re
import sys
import urllib.request
from datetime import date, datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

SITE = "https://tablemountainstringband.com"
BAND_ID = f"{SITE}/#band"
BAND_NAME = "Table Mountain String Band"
SONGKICK_ARTIST_ID = "10334263"
SONGKICK_ARTIST_URL = f"https://www.songkick.com/artists/{SONGKICK_ARTIST_ID}"
CALENDAR_URL = f"https://widget-app.songkick.com/api/calendar/{SONGKICK_ARTIST_ID}"
IMAGE = f"{SITE}/res/tablemountainstringband-preview.png"
TZ = ZoneInfo("Europe/Prague")
INDEX = Path(__file__).resolve().parent / "index.html"

COUNTRY_CODES = {
    "Czech Republic": "CZ", "Czechia": "CZ", "Germany": "DE", "Austria": "AT",
    "Slovakia": "SK", "Poland": "PL", "Hungary": "HU", "US": "US", "UK": "GB",
}
STATUS = {
    "ok": "https://schema.org/EventScheduled",
    "postponed": "https://schema.org/EventPostponed",
    "rescheduled": "https://schema.org/EventRescheduled",
}
MONTHS_CS = ["led", "úno", "bře", "dub", "kvě", "čvn", "čvc", "srp", "zář", "říj", "lis", "pro"]


def fetch_calendar(path=None):
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    req = urllib.request.Request(CALENDAR_URL, headers={"Accept": "application/json", "User-Agent": "tablemountainstringband.com build"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def strip_utm(url):
    return re.sub(r"\?utm_[^#]*", "", url) if url else None


def iso_start(start):
    """Songkick gives '2026-11-24T19:45:00+0100'; schema.org wants a colon in the offset."""
    dt = start.get("datetime")
    if dt:
        return re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", dt)
    return start["date"]


def upcoming_events(data):
    today = datetime.now(TZ).date()
    out = []
    for perf in data["resultsPage"]["results"].get("performance") or []:
        ev = perf["event"]
        if ev.get("status") == "cancelled" or ev.get("flaggedAsEnded"):
            continue
        if date.fromisoformat(ev["start"]["date"]) < today:
            continue
        out.append((perf, ev))
    out.sort(key=lambda pe: pe[1]["start"]["date"])
    # Unique anchor per show, even for two shows on one day.
    seen = {}
    for perf, ev in out:
        base = f"show-{ev['start']['date']}"
        seen[base] = seen.get(base, 0) + 1
        ev["_anchor"] = base if seen[base] == 1 else f"{base}-{seen[base]}"
    return out


def event_jsonld(perf, ev):
    venue = ev.get("venue") or {}
    metro = venue.get("metroArea") or {}
    city = metro.get("displayName") or (ev.get("location") or {}).get("city", "")
    country = (metro.get("country") or {}).get("displayName", "")
    venue_name = venue.get("displayName") or city
    online = ev.get("type") == "LiveStreamConcert"

    place = {
        "@type": "Place",
        "name": venue_name,
        "address": {"@type": "PostalAddress", "addressLocality": city, "addressCountry": COUNTRY_CODES.get(country, country)},
    }
    if venue.get("lat") and venue.get("lng"):
        place["geo"] = {"@type": "GeoCoordinates", "latitude": venue["lat"], "longitude": venue["lng"]}
    if venue.get("uri"):
        place["sameAs"] = strip_utm(venue["uri"])

    item = {
        "@context": "https://schema.org",
        "@type": "MusicEvent",
        "name": f"{BAND_NAME} at {venue_name}",
        "description": f"{BAND_NAME} plays old-time American fiddle tunes and folk songs live at {venue_name}, {city}.",
        "startDate": iso_start(ev["start"]),
        "url": f"{SITE}/#{ev['_anchor']}",
        "image": IMAGE,
        "eventStatus": STATUS.get(ev.get("status"), STATUS["ok"]),
        "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode" if online else "https://schema.org/OfflineEventAttendanceMode",
        "location": place,
        "performer": {"@type": "MusicGroup", "@id": BAND_ID, "name": BAND_NAME},
        "organizer": {"@type": "MusicGroup", "@id": BAND_ID, "name": BAND_NAME},
    }
    if ev.get("uri"):
        item["sameAs"] = strip_utm(ev["uri"])
    ticket = perf.get("directTicketLink")
    if ticket:
        item["offers"] = {"@type": "Offer", "url": ticket, "availability": "https://schema.org/InStock"}
    return item


def show_html(perf, ev):
    venue = ev.get("venue") or {}
    metro = venue.get("metroArea") or {}
    city = metro.get("displayName") or (ev.get("location") or {}).get("city", "")
    d = date.fromisoformat(ev["start"]["date"])
    time_ = (ev["start"].get("time") or "")[:5]
    link = perf.get("directTicketLink") or strip_utm(ev.get("uri")) or SONGKICK_ARTIST_URL
    label_en, label_cz = ("Tickets", "Vstupenky") if perf.get("directTicketLink") else ("Details", "Podrobnosti")
    return f"""                    <li class="show" id="{ev['_anchor']}">
                        <time class="show-date" datetime="{escape(iso_start(ev['start']))}">
                            <span class="show-day">{d.day}</span>
                            <span class="show-month"><span class="lang-en-content">{d.strftime('%b')}</span><span class="lang-cz-content">{MONTHS_CS[d.month - 1]}</span> {d.year}</span>
                        </time>
                        <div class="show-info">
                            <h3 class="show-venue">{escape(venue.get('displayName') or city)}</h3>
                            <p class="show-meta">{escape(city)}{' &middot; ' + time_ if time_ else ''}</p>
                        </div>
                        <a class="show-link" href="{escape(link)}" target="_blank" rel="noopener">
                            <span class="lang-en-content">{label_en}</span><span class="lang-cz-content">{label_cz}</span>
                        </a>
                    </li>"""


def render_list(events):
    if not events:
        return """                <p class="shows-empty">
                    <span class="lang-en-content">No upcoming shows right now.</span>
                    <span class="lang-cz-content">Momentálně nejsou naplánované žádné koncerty.</span>
                </p>"""
    return '                <ul class="shows-list">\n' + "\n".join(show_html(p, e) for p, e in events) + "\n                </ul>"


def render_jsonld(events):
    return "\n".join(
        '        <script type="application/ld+json">\n'
        + "\n".join(" " * 8 + line for line in json.dumps(event_jsonld(p, e), ensure_ascii=False, indent=2).splitlines())
        + "\n        </script>"
        for p, e in events
    )


def replace_region(html, name, body):
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    pattern = re.compile(r"( *)" + re.escape(start) + r".*?" + re.escape(end), re.S)
    m = pattern.search(html)
    if not m:
        sys.exit(f"index.html is missing the {start} / {end} markers")
    indent = m.group(1)
    replacement = indent + start + "\n" + (body + "\n" if body else "") + indent + end
    return pattern.sub(lambda _: replacement, html, count=1)


def main(argv):
    src = argv[argv.index("--from") + 1] if "--from" in argv else None
    events = upcoming_events(fetch_calendar(src))
    html = INDEX.read_text(encoding="utf-8")
    new = replace_region(html, "events-jsonld", render_jsonld(events))
    new = replace_region(new, "shows-list", render_list(events))
    if "--check" in argv:
        if new != html:
            sys.exit("index.html is out of date; run ./generate-shows.py")
        print("index.html is up to date")
        return
    INDEX.write_text(new, encoding="utf-8")
    print(f"Wrote {len(events)} upcoming show(s) to {INDEX.name}")


if __name__ == "__main__":
    main(sys.argv[1:])
