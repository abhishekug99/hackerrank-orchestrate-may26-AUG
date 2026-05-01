from __future__ import annotations

from schema import Ticket
from utils import contains_any, normalize


def deterministic_response(ticket: Ticket, company: str, product_area: str, status: str) -> str:
    text = normalize(ticket.issue + " " + ticket.subject)

    if status == "escalated":
        if company == "HackerRank" and contains_any(text, ["score", "rejected", "review my answers", "increase my score"]):
            return "I can’t change assessment scores, review a completed test on behalf of a recruiter, or influence the hiring decision. This should be routed to the hiring company or a human support specialist for review."
        if company == "HackerRank" and contains_any(text, ["refund", "payment", "order id", "subscription", "pause"]):
            return "This involves billing or subscription changes, so I’m escalating it to a human support specialist rather than making unsupported changes or promises."
        if company == "HackerRank" and contains_any(text, ["reschedule"]):
            return "Assessment scheduling is controlled by the hiring company, so this should be escalated or handled through the recruiter/company that invited you."
        if company == "Claude" and contains_any(text, ["workspace", "seat", "admin", "restore my access"]):
            return "I can’t restore access or override workspace owner/admin controls. Please contact your workspace owner or IT admin; I’m escalating this because it involves account permissions."
        if company == "Claude" and contains_any(text, ["security vulnerability", "bug bounty"]):
            return "This should be escalated to the security reporting process. Do not share exploit details in a general support thread; a human/security team should review it."
        if company == "Claude" and contains_any(text, ["all requests are failing", "stopped working completely"]):
            return "Because this sounds like a broad service outage or severe degradation, I’m escalating it to a human support specialist."
        if company == "Visa" and contains_any(text, ["identity", "stolen"]):
            return "Identity theft is urgent and sensitive. Contact your card issuer/bank immediately using the number on your card or statement, and I’m escalating this rather than attempting to resolve it here."
        if company == "Visa" and contains_any(text, ["dispute", "charge", "refund", "merchant", "wrong product"]):
            return "For disputes or merchant issues, contact the financial institution that issued your Visa card. Visa does not directly reverse charges or ban merchants from this support flow, so this is escalated for careful handling."
        if company == "Visa" and contains_any(text, ["cash"]):
            return "For emergency cash needs, contact your card issuer or Visa Global Customer Assistance. Because this may involve emergency financial support, I’m escalating it."
        if contains_any(text, ["down", "not working", "all requests", "submissions"]):
            return "This appears to be a service-impacting bug or outage, so I’m escalating it to a human support specialist."
        return "Escalate to a human support specialist."

    if company == "HackerRank":
        if contains_any(text, ["remove an interviewer", "remove a user", "employee has left"]):
            return "To remove a user from a HackerRank hiring account, an account admin should manage users from the account settings or team/user management area. If the option is not visible, confirm that you have admin permissions; otherwise ask an admin or support to remove the user."
        if contains_any(text, ["compatible check", "zoom"]):
            return "For compatibility check issues, retry the system check after verifying browser permissions, camera/microphone access, network access, and Zoom connectivity. If the check still fails and blocks a live assessment, contact the hiring company or support with the exact error."
        if contains_any(text, ["apply tab"]):
            return "If the Apply tab is missing in HackerRank Community, make sure you are signed in to the correct account and viewing a supported challenge or jobs area. If the option still does not appear, share the page and account details with support."
        if "certificate" in text and "name" in text:
            return "For a certificate name correction, verify your profile name first and then contact HackerRank support with the assessment/certificate details so the certificate record can be reviewed."
        if contains_any(text, ["infosec", "forms"]):
            return "For an information security review, share the required forms through the appropriate HackerRank sales or support channel so the correct team can respond with approved security documentation."
        if contains_any(text, ["inactivity", "screen share", "lobby"]):
            return "Inactivity behavior during interviews can depend on the interview setup and participant activity. Because this may affect live interviews, confirm the current settings with HackerRank support and include details about candidate/interviewer behavior and screen sharing."
        return "I can help with HackerRank support questions when they can be grounded in the provided documentation. Please provide the exact workflow, account type, and error message if the issue continues."

    if company == "Claude":
        if contains_any(text, ["stop crawling", "website"]):
            return "To manage Claude-related crawling or use of website content, follow Claude’s documented website data controls and privacy guidance. If you need a domain-specific block reviewed, escalate with the site details."
        if contains_any(text, ["data to improve", "how long"]):
            return "Claude privacy settings and data-use retention depend on the plan and setting selected. Review the privacy/data controls in the provided Claude documentation; if the exact retention period is not confirmed there, escalate rather than guessing."
        if contains_any(text, ["bedrock", "aws"]):
            return "For Claude on Amazon Bedrock failures, check the Bedrock configuration, model access, region, credentials, request format, and service errors. If all requests fail, include request IDs and error messages when escalating."
        if contains_any(text, ["lti", "professor", "students"]):
            return "For Claude for Education and LTI setup, use the Claude education/admin documentation and coordinate with your institution’s administrator. If you need keys provisioned, this should be handled through the approved admin setup flow."
        return "I can answer Claude support questions when the provided corpus supports the answer. For account access, billing, security, or admin-only actions, a human/admin should handle it."

    if company == "Visa":
        if contains_any(text, ["minimum", "spend"]):
            return "Some merchants may set purchase minimums based on their own acceptance rules or local practices. If you believe a merchant is improperly refusing your Visa card, contact the card issuer or Visa support with the merchant details."
        if contains_any(text, ["blocked", "voyage", "travel"]):
            return "For a blocked Visa card while traveling, contact the financial institution that issued your card or Visa Global Customer Assistance. Do not share card details in chat; use the official phone support route."
        return "For Visa card account, charge, card block, or emergency issues, contact the financial institution that issued your Visa card because it controls the account and cardholder actions."

    if contains_any(text, ["thank you", "thanks"]):
        return "Happy to help."
    return "I’m sorry, this is outside the supported HackerRank, Claude, and Visa support domains."
