"""
orders.py  -  build_orders(case, attribution, triage, sla, grievance) -> dict
Owner: Person C  (Merchant Evidence and Draft Documents)

Returns exactly:
    {"restoration_order_html", "indemnity_bond_html", "edd_packet_html"}

Each value is a complete, self-contained HTML draft document.
Rules:
  - Every piece of user-supplied text is HTML-escaped.
  - No money arithmetic; only amounts already present in the input dicts.
  - No JavaScript, no external links, no images.
  - Every document prominently says DRAFT.
  - Indian rupee grouping format via inr() helper (string/Decimal only, no float).
Standard library only.
"""

import html
from decimal import Decimal, ROUND_HALF_UP

# ── INR formatter ─────────────────────────────────────────────────────────────

def inr(s):
    """
    Format a money string in Indian grouping with the rupee sign.
    e.g. "150000.00" -> "₹1,50,000.00"
         "873.00"    -> "₹873.00"
         "0.00"      -> "₹0.00"
    Uses Decimal for safety; never float.
    """
    d = Decimal(str(s))
    # Separate integer and fractional parts
    d_rounded = d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    sign, digits_tuple, exp = d_rounded.as_tuple()
    # Build the integer-part string
    # exp is negative (e.g., -2 for two decimal places)
    frac_len = -exp  # should be 2
    all_digits = "".join(str(dig) for dig in digits_tuple)
    # Pad so that we always have at least frac_len+1 digits
    while len(all_digits) <= frac_len:
        all_digits = "0" + all_digits
    int_part = all_digits[:-frac_len]
    frac_part = all_digits[-frac_len:]

    # Indian grouping: last 3 digits of int_part, then groups of 2
    if len(int_part) <= 3:
        grouped = int_part
    else:
        # last 3 digits
        last3 = int_part[-3:]
        rest = int_part[:-3]
        # group rest in pairs from the right
        pairs = []
        while len(rest) > 2:
            pairs.append(rest[-2:])
            rest = rest[:-2]
        pairs.append(rest)
        pairs.reverse()
        grouped = ",".join(pairs) + "," + last3

    prefix = "-" if sign else ""
    return "\u20b9" + prefix + grouped + "." + frac_part


# ── CSS (shared inline) ───────────────────────────────────────────────────────

_CSS = """
    body { font-family: Arial, sans-serif; font-size: 13px; color: #111; margin: 30px; }
    h1 { font-size: 18px; }
    h2 { font-size: 15px; margin-top: 24px; }
    .draft-banner {
        background: #ffd700; color: #7a0000; font-weight: bold;
        font-size: 15px; padding: 10px 16px; border: 2px solid #b00;
        margin-bottom: 20px; text-align: center;
    }
    table { border-collapse: collapse; width: 100%; margin: 12px 0; }
    th { background: #ddeeff; text-align: left; padding: 6px 8px; border: 1px solid #aaa; }
    td { padding: 5px 8px; border: 1px solid #ccc; vertical-align: top; }
    .chip { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; }
    .chip-matched   { background: #c8f7c8; color: #1a5e1a; }
    .chip-partial   { background: #fff3cd; color: #7a5100; }
    .chip-no_invoice{ background: #f0f0f0; color: #555; }
    .chip-not_matched { background: #ffe0e0; color: #8b0000; }
    .chip-on_track  { background: #c8f7c8; color: #1a5e1a; }
    .chip-due_soon  { background: #fff3cd; color: #7a5100; }
    .chip-overdue   { background: #ffe0e0; color: #8b0000; }
    .chip-completed { background: #dde8ff; color: #003080; }
    .chip-not_started { background: #f0f0f0; color: #555; }
    .info-box { background: #f8f9fa; border: 1px solid #ccc; padding: 10px 14px; margin: 10px 0; }
    .sig-block { margin-top: 32px; }
    .sig-line { border-top: 1px solid #333; width: 260px; margin-top: 40px; margin-bottom: 4px; }
    .footer { margin-top: 36px; font-size: 11px; color: #555; border-top: 1px solid #ccc; padding-top: 8px; }
    @media print { body { margin: 15mm; } .draft-banner { -webkit-print-color-adjust: exact; } }
"""

_DRAFT_BANNER = (
    '<div class="draft-banner">'
    "DRAFT &mdash; NOT VALID UNTIL REVIEWED AND SIGNED BY THE INVESTIGATING OFFICER"
    "</div>"
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _e(v):
    """HTML-escape a value (convert to str first)."""
    return html.escape(str(v), quote=True)


def _verdict_chip(verdict):
    cls = "chip-" + verdict.lower().replace("_", "_")
    return '<span class="chip %s">%s</span>' % (cls, _e(verdict))


def _status_chip(status):
    cls = "chip-" + status.lower()
    label = status.replace("_", " ").title()
    return '<span class="chip %s">%s</span>' % (cls, _e(label))


def _bool_yn(v):
    return "Yes" if v else "No"


def _method_words(method):
    return {"DIRECT": "Direct attribution", "PRO_RATA": "Pro-rata (equitable)",
            "INTACT": "Intact (full amount in account)"}.get(method, _e(method))


def _sla_clock(sla_list, key):
    """Return the SLA clock dict matching `key`, or None."""
    for clk in sla_list:
        if clk.get("key") == key:
            return clk
    return None


def _html_doc(title, body_content):
    """Wrap body content in a complete HTML document."""
    return (
        "<!DOCTYPE html><html lang=\"en\"><head>"
        '<meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        "<title>%s</title>"
        "<style>%s</style>"
        "</head><body>"
        "%s"
        "</body></html>"
    ) % (_e(title), _CSS, body_content)


# ── Document 1: Restoration Order ────────────────────────────────────────────

def _restoration_order(case, attribution, triage, sla, grievance):
    case_id    = _e(case["case_id"])
    account_id = _e(case["account"]["account_id"])
    holder     = _e(case["account"]["holder_name"])
    as_of      = _e(case.get("demo_today", ""))
    rec        = triage.get("recommendation", "")

    victims = attribution.get("victims", [])
    restorable_victims = [v for v in victims if Decimal(str(v.get("restorable_amount", "0.00"))) > Decimal("0.00")]
    n_restorable = len(restorable_victims)

    # Basis paragraph
    if n_restorable >= 2:
        basis_cite = (
            "Attribution follows SOP Para 5(xiii)(a)/(b) and Annexure-V. "
            "Multiple victims with restorable amounts: "
            "<em>SOP Para 11, Process 2 (multiple victims, S.106 BNSS)</em>."
        )
        process_ref = "Process 2(h) (multiple victims)"
        process_single = False
    elif n_restorable == 1:
        basis_cite = (
            "Attribution follows SOP Para 5(xiii)(a)/(b) and Annexure-V. "
            "Single victim with restorable amount: "
            "<em>Process 1 (single victim, S.106(3) BNSS)</em>."
        )
        process_ref = "Process 1(v) (single victim)"
        process_single = True
    else:
        basis_cite = (
            "Attribution follows SOP Para 5(xiii)(a)/(b) and Annexure-V. "
            "No money is restorable from this account based on current attribution."
        )
        process_ref = ""
        process_single = False

    # Schedule table
    rows = []
    for v in victims:
        method = v.get("attribution_method", "")
        fw_traces = v.get("forwarded_trace", [])
        fw_utrs = "; ".join(_e(t.get("debit_utr", "")) for t in fw_traces) if fw_traces else "—"
        fw_amt = inr(v.get("forwarded_downstream", "0.00"))
        retention = ""
        if method == "PRO_RATA":
            retention = _e(v.get("retention_ratio", ""))

        rows.append(
            "<tr>"
            "<td>%s</td>"
            "<td>%s</td>"
            "<td>%s</td>"
            "<td><strong>%s</strong></td>"
            "<td>%s<br><small>Debit UTR(s): %s</small>"
            "<br><small>Note: this schema does not verify the receiving account.</small></td>"
            "<td>%s</td>"
            "</tr>"
            % (
                _e(v.get("victim_label", "")),
                inr(v.get("disputed_amount", "0.00")),
                _method_words(method),
                inr(v.get("restorable_amount", "0.00")),
                fw_amt,
                fw_utrs,
                retention if retention else "—",
            )
        )

    table_html = (
        "<table>"
        "<thead><tr>"
        "<th>Victim</th><th>Disputed Amount</th><th>Attribution Method</th>"
        "<th>Amount to Restore</th><th>Forwarded to Outgoing Debits</th><th>Retention Ratio (PRO_RATA only)</th>"
        "</tr></thead>"
        "<tbody>%s</tbody>"
        "</table>"
    ) % "".join(rows)

    clean = inr(attribution.get("clean_ring_fenced", "0.00"))

    instruction = ""
    if process_ref:
        instruction = (
            "<h2>Instruction to Bank</h2>"
            "<p>Remit the scheduled amounts to the victims&#39; accounts as notified on CFCFRMS, "
            "against an indemnity bond, within <strong>15 calendar days</strong> of receipt of this order "
            "(SOP Para 11, %s). "
            "Prior approval of the jurisdictional SP/DCP is required (SOP Process 1(iv)).</p>"
        ) % _e(process_ref)

    sig_block = (
        "<div class='sig-block'>"
        "<p><div class='sig-line'></div>Investigating Officer &nbsp;&nbsp;&nbsp; Date: ___________</p>"
        "<p><div class='sig-line'></div>SP/DCP Approval &nbsp;&nbsp;&nbsp; Date: ___________</p>"
        "<p><div class='sig-line'></div>Bank Nodal Officer &nbsp;&nbsp;&nbsp; Date: ___________</p>"
        "</div>"
    )

    footer = (
        "<div class='footer'>"
        "Figures computed deterministically by Mercy Ledger from the bank statement. "
        "Decision-support output; the officer retains final authority."
        "</div>"
    )

    body = (
        _DRAFT_BANNER
        + "<h1>Restoration Order under Section 106(3) BNSS (Draft)</h1>"
        + "<div class='info-box'>"
        + "<b>Case ID:</b> %s &nbsp; <b>Account:</b> %s &nbsp; <b>Holder:</b> %s &nbsp; <b>As of:</b> %s"
        % (case_id, account_id, holder, as_of)
        + "</div>"
        + "<h2>Basis</h2><p>%s</p>" % basis_cite
        + "<h2>Restoration Schedule</h2>"
        + table_html
        + "<p><strong>Clean (innocent) balance outside this order: %s</strong><br>" % clean
        + "Continuation of any restriction on this clean balance is a separate decision of the "
          "Investigating Officer (SOP Para 5(viii), 5(ix)).</p>"
        + instruction
        + sig_block
        + footer
    )

    return _html_doc("Restoration Order under Section 106(3) BNSS (Draft)", body)


# ── Document 2: Indemnity Bond ────────────────────────────────────────────────

def _indemnity_bond(case, attribution, triage, sla, grievance):
    case_id    = _e(case["case_id"])
    account_id = _e(case["account"]["account_id"])
    holder     = _e(case["account"]["holder_name"])

    victims = attribution.get("victims", [])
    restorable_victims = [v for v in victims if Decimal(str(v.get("restorable_amount", "0.00"))) > Decimal("0.00")]

    sections = []
    if not restorable_victims:
        sections.append("<p>No victim has a restorable amount in this account. No indemnity bond schedule is generated.</p>")
    else:
        for v in restorable_victims:
            label = _e(v.get("victim_label", ""))
            amount = inr(v.get("restorable_amount", "0.00"))
            sections.append(
                "<div class='info-box'>"
                "<h2>Victim: %s</h2>"
                "<p><b>Amount to be released:</b> %s</p>"
                "<p><b>Undertaking (template &mdash; to be vetted by legal/prosecuting team):</b></p>"
                "<blockquote>"
                "I/We, the recipient named above, hereby undertake to produce the amount of %s "
                "before the court as and when required, and to give full effect to the further "
                "orders of the jurisdictional court as to its disposal, in accordance with "
                "SOP Process 1(iv) / Process 2."
                "</blockquote>"
                "<p>Recipient signature: <span style='border-bottom:1px solid #333;display:inline-block;width:220px'>&nbsp;</span> "
                "Date: ___________</p>"
                "<p>Witness: <span style='border-bottom:1px solid #333;display:inline-block;width:220px'>&nbsp;</span> "
                "Date: ___________</p>"
                "</div>"
                % (label, amount, amount)
            )

    body = (
        _DRAFT_BANNER
        + "<h1>Indemnity Bond Schedule (Draft)</h1>"
        + "<div class='info-box'>"
        + "<b>Case ID:</b> %s &nbsp; <b>Account:</b> %s &nbsp; <b>Holder:</b> %s"
        % (case_id, account_id, holder)
        + "</div>"
        + "<p><em>Template wording to be vetted by the prosecuting/legal team before use. "
          "These are draft documents for officer review only; they are not legally operative.</em></p>"
        + "".join(sections)
        + "<div class='sig-block'>"
          "<p><div class='sig-line'></div>Investigating Officer &nbsp;&nbsp;&nbsp; Date: ___________</p>"
          "<p><div class='sig-line'></div>Bank Nodal Officer &nbsp;&nbsp;&nbsp; Date: ___________</p>"
          "</div>"
    )

    return _html_doc("Indemnity Bond Schedule (Draft)", body)


# ── Document 3: EDD Packet ────────────────────────────────────────────────────

def _edd_packet(case, attribution, triage, sla, grievance):
    case_id    = _e(case["case_id"])
    account_id = _e(case["account"]["account_id"])
    holder     = _e(case["account"]["holder_name"])

    # Deadline box: BANK_GRIEVANCE_7D clock
    clk = _sla_clock(sla, "BANK_GRIEVANCE_7D")
    if clk:
        status = clk.get("status", "")
        days_left = clk.get("days_left")
        deadline = clk.get("deadline") or "—"
        sop_ref = _e(clk.get("sop_reference", ""))
        label_txt = _e(clk.get("label", ""))
        days_str = "Not started" if status == "NOT_STARTED" else (str(days_left) if days_left is not None else "—")
        clk_html = (
            "<div class='info-box'>"
            "<b>%s</b><br>"
            "Deadline: <b>%s</b> &nbsp; Status: %s &nbsp; Days left: <b>%s</b><br>"
            "SOP Reference: %s"
            "</div>"
            % (label_txt, _e(str(deadline)), _status_chip(status), _e(days_str), sop_ref)
        )
    else:
        clk_html = "<div class='info-box'>BANK_GRIEVANCE_7D clock not found in SLA data.</div>"

    # Document verification table from grievance results
    griev_results = grievance.get("results", [])
    griev_disclaimer = _e(grievance.get("disclaimer", ""))

    griev_rows = []
    for r in griev_results:
        chk = r.get("checks", {})
        reasons_txt = _e("; ".join(r.get("reasons", [])))
        griev_rows.append(
            "<tr>"
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td>"
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td>"
            "<td>%s</td><td>%s</td>"
            "</tr>"
            % (
                _e(r.get("complaint_id", "")),
                _e(r.get("disputed_utr", "")),
                inr(r.get("disputed_amount", "0.00")),
                _e(r.get("invoice_id") or "—"),
                _bool_yn(chk.get("utr_match")),
                _bool_yn(chk.get("amount_match")),
                _bool_yn(chk.get("date_within_1_day")),
                _bool_yn(chk.get("gstin_format_valid")),
                _verdict_chip(r.get("verdict", "")),
                reasons_txt,
            )
        )

    griev_table = (
        "<table>"
        "<thead><tr>"
        "<th>Complaint ID</th><th>Disputed UTR</th><th>Disputed Amount</th><th>Invoice ID</th>"
        "<th>UTR Match</th><th>Amount Match</th><th>Date &le;1 Day</th><th>GSTIN Format</th>"
        "<th>Verdict</th><th>Reasons</th>"
        "</tr></thead>"
        "<tbody>%s</tbody>"
        "</table>"
        "<p><em>%s</em></p>"
    ) % ("".join(griev_rows), griev_disclaimer)

    # Recommendation from triage
    rec = _e(triage.get("recommendation", ""))
    score = _e(str(triage.get("score", "")))
    rationale = _e(triage.get("rationale", ""))
    citations = triage.get("citations", [])
    cit_items = "".join("<li>%s</li>" % _e(c) for c in citations)
    human_so = triage.get("human_signoff_required", True)

    rec_html = (
        "<div class='info-box'>"
        "<b>Recommendation:</b> %s &nbsp; <b>Score:</b> %s<br>"
        "<b>Rationale:</b> %s<br>"
        "<b>Citations:</b><ul>%s</ul>"
        "<b>Human sign-off required:</b> %s"
        "</div>"
        % (rec, score, rationale, cit_items, "Yes" if human_so else "No")
    )

    body = (
        _DRAFT_BANNER
        + "<h1>7-Day Bank EDD Clearance Packet (Draft)</h1>"
        + "<div class='info-box'>"
        + "<b>Case ID:</b> %s &nbsp; <b>Account:</b> %s &nbsp; <b>Holder:</b> %s"
        % (case_id, account_id, holder)
        + "</div>"
        + "<h2>SLA Deadline &mdash; Bank Grievance Submission (7 days)</h2>"
        + clk_html
        + "<h2>Document Verification (Invoice vs. Ledger)</h2>"
        + griev_table
        + "<h2>Triage Recommendation</h2>"
        + rec_html
        + "<div class='sig-block'>"
          "<p><div class='sig-line'></div>Bank Nodal Officer &nbsp;&nbsp;&nbsp; Date: ___________</p>"
          "</div>"
    )

    return _html_doc("7-Day Bank EDD Clearance Packet (Draft)", body)


# ── public API ────────────────────────────────────────────────────────────────

def build_orders(case, attribution, triage, sla, grievance):
    """
    Build three draft HTML documents for officer review.
    No money arithmetic is performed here; all amounts come from the inputs.
    All user-supplied text is HTML-escaped.
    Returns dict with keys:
        restoration_order_html, indemnity_bond_html, edd_packet_html
    """
    return {
        "restoration_order_html": _restoration_order(case, attribution, triage, sla, grievance),
        "indemnity_bond_html":    _indemnity_bond(case, attribution, triage, sla, grievance),
        "edd_packet_html":        _edd_packet(case, attribution, triage, sla, grievance),
    }
