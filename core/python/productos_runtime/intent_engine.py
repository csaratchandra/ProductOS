from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class IntentEngine:
    """Decomposes natural language product intent into structured architecture.

    Supports deterministic (rule-based) decomposition for offline use and
    LLM-assisted enhancement when a provider is available.
    """

    DOMAIN_KEYWORDS: Dict[str, List[str]] = {
        "healthcare": [
            "hipaa", "fhir", "prior auth", "prior authorization", "provider",
            "payer", "patient", "clinical", "ehr", "emr", "cms", "health",
            "medical", "hospital", "physician", "doctor", "nurse", "medicare",
            "medicaid", "x12", "837", "835", "278", "icd-10", "cpt", "hcpcs",
            "ncpdp", "hitech", "telehealth", "virtual consultation",
            "records", "diagnosis", "prescription", "lab", "pharmacy",
        ],
        "finance": [
            "sec", "finra", "cftc", "mifid", "emir", "trading", "trade",
            "payment", "fintech", "banking", "capital markets", "derivatives",
            "clearing", "settlement", "pci-dss", "swift", "aml", "kyc",
            "fix protocol", "order management", "risk", "underwriting",
            "collateral", "margin", "liquidity", "lending", "credit",
        ],
        "enterprise_saas": [
            "saas", "b2b", "enterprise", "workflow", "automation",
            "dashboard", "analytics", "reporting", "integration",
            "multi-tenant", "role-based", "sso", "audit",
        ],
        "ecommerce": [
            "ecommerce", "e-commerce", "retail", "marketplace", "shop",
            "cart", "checkout", "payment", "inventory", "order",
            "fulfillment", "shipping", "catalog", "product listing",
        ],
    }

    COMPLIANCE_KEYWORDS: Dict[str, List[str]] = {
        "hipaa": ["hipaa", "phi", "protected health", "health privacy", "patient data"],
        "gdpr": ["gdpr", "general data protection", "data privacy", "right to be forgotten"],
        "pci_dss": ["pci", "pci-dss", "cardholder data", "payment data", "credit card"],
        "sox": ["sox", "sarbanes-oxley", "financial reporting", "audit trail"],
        "cms": ["cms", "medicare", "medicaid", "prior auth", "72 hour"],
    }

    ARCHETYPE_KEYWORDS: Dict[str, List[str]] = {
        "buyer": ["buyer", "purchaser", "procurement", "decision-maker"],
        "user": ["user", "end-user", "operator", "practitioner", "staff"],
        "champion": ["champion", "advocate", "evangelist", "sponsor"],
        "blocker": ["blocker", "compliance", "legal", "risk", "security", "it"],
        "operator": ["operator", "admin", "administrator", "manager", "supervisor"],
        "executive": ["executive", "ceo", "cto", "cio", "vice president", "vp"],
        "influencer": ["influencer", "consultant", "advisor", "analyst"],
    }

    def __init__(self, provider: Any = None):
        self._provider = provider

    def decompose(self, intent_text: str) -> Dict[str, Any]:
        if not intent_text or len(intent_text.strip()) < 10:
            raise ValueError("Intent text must be at least 10 characters")

        text = intent_text.strip()

        problem = self._extract_problem(text)
        outcomes = self._extract_outcomes(text)
        personas = self._infer_personas(text)
        domain_match = self._classify_domain(text)
        constraints = self._extract_constraints(text)
        ambiguity_flags = self._detect_ambiguities(text, domain_match)
        clarifications = [f["suggested_clarification"] for f in ambiguity_flags]
        archetype_gaps = self._detect_archetype_gaps(personas)

        confidence_scores = self._compute_confidence(text, problem, personas, domain_match)

        return {
            "schema_version": "1.0.0",
            "intent_decomposition_id": f"id_{uuid.uuid4().hex[:12]}",
            "raw_text": text,
            "extracted_problem": problem,
            "extracted_outcomes": outcomes,
            "inferred_personas": personas,
            "implied_constraints": constraints,
            "domain_match": domain_match,
            "archetype_gaps": archetype_gaps,
            "ambiguity_flags": ambiguity_flags,
            "suggested_clarifications": clarifications,
            "confidence_scores": confidence_scores,
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }

    def _extract_problem(self, text: str) -> str:
        """Extract or infer the core problem statement from intent text."""
        patterns = [
            r"(?:reduce|eliminate|solve|address|improve|streamline|simplify)\s+(.+?)(?:\.|$|for|to|with|using)",
            r"(?:struggle|fight|battle|deal)\s+with\s+(.+?)(?:\.|$|by|through|using)",
            r"(?:problem|challenge|issue|pain|friction)\s+(?:is|of|:)\s+(.+?)(?:\.|$|for|to)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip().capitalize()

        if len(text) > 30:
            return text[:text.rfind(" ", 0, 200)].strip() + "."
        return text

    def _extract_outcomes(self, text: str) -> List[Dict[str, Any]]:
        """Extract SMART-format business outcomes from intent."""
        outcomes: List[Dict[str, Any]] = []
        seen: set = set()

        outcome_patterns = [
            r"(?:reduce|decrease|cut)\s+(.+?)(?:\s+by\s+|\s+to\s+)(\d+%?[\d\s%]*)",
            r"(?:increase|improve|grow|boost|raise)\s+(.+?)(?:\s+by\s+|\s+to\s+)(\d+%?[\d\s%]*)",
            r"(?:achieve|reach|accomplish|deliver)\s+(.+?)(?:\.|$|with|through|using)",
            r"(?:enable|allow|empower)\s+(.+?)(?:\.|$|to|by)",
        ]

        for pattern in outcome_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                description = match.group(0).strip().capitalize()
                if description not in seen:
                    seen.add(description)
                    outcomes.append({
                        "outcome_id": f"out_{len(outcomes) + 1:03d}",
                        "description": description,
                        "measurement": self._infer_measurement(description),
                        "confidence": 0.6 if "by" in description.lower() else 0.4,
                    })

        if not outcomes:
            outcomes.append({
                "outcome_id": "out_001",
                "description": f"Deliver a solution that addresses: {text[:100].strip()}",
                "measurement": "TBD — outcome not explicitly quantified",
                "confidence": 0.3,
            })

        return outcomes

    def _infer_measurement(self, description: str) -> str:
        """Infer a measurement method from an outcome description."""
        measurement_map = {
            "time": "Average processing time per unit",
            "cost": "Total cost per transaction",
            "rate": "Percentage rate measured weekly",
            "error": "Error rate per thousand transactions",
            "speed": "Completion time in seconds",
            "accuracy": "Accuracy percentage measured against ground truth",
            "adoption": "Monthly active users",
            "revenue": "Monthly recurring revenue",
            "satisfaction": "Net Promoter Score (NPS)",
        }
        for key, measurement in measurement_map.items():
            if key in description.lower():
                return measurement
        return "TBD — measurement to be defined"

    def _infer_personas(self, text: str) -> List[Dict[str, Any]]:
        """Infer target personas from intent text."""
        personas: List[Dict[str, Any]] = []
        seen_ids: set = set()

        persona_patterns = [
            (r"(?:for|by|among|between)\s+(.+?)(?:and|,|\s+to\s+|\.|$)", 0.7),
            (r"(?:providers?|doctors?|physicians?|clinicians?)", 0.9),
            (r"(?:payers?|insurers?|insurance\s+companies?)", 0.9),
            (r"(?:patients?|consumers?|customers?|end[-\s]?users?)", 0.85),
            (r"(?:admins?|administrators?|operators?|managers?)", 0.8),
            (r"(?:executives?|leadership|ceo|cto|cio|vp)", 0.75),
            (r"(?:compliance|legal|risk|security)\s+(?:officers?|teams?|staff?)", 0.7),
        ]

        for pattern, base_confidence in persona_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for raw in matches:
                if isinstance(raw, tuple):
                    raw = raw[0]
                raw = raw.strip().rstrip(",").strip()
                if not raw or len(raw) < 3:
                    continue
                pid = raw.lower().replace(" ", "_").replace("-", "_")[:20]
                if pid not in seen_ids:
                    seen_ids.add(pid)
                    archetype = self._infer_archetype(raw)
                    personas.append({
                        "persona_id": pid,
                        "label": raw.title(),
                        "role_description": f"Primary {raw.lower()} involved in the workflow",
                        "confidence": min(base_confidence + 0.1 * len(raw.split()), 0.98),
                        "archetype_type": archetype,
                    })

        if not personas:
            personas.append({
                "persona_id": "pers_unknown",
                "label": "End User",
                "role_description": "Primary user of the product — role to be clarified",
                "confidence": 0.3,
                "archetype_type": "unknown",
            })

        return personas

    def _infer_archetype(self, raw: str) -> str:
        raw_lower = raw.lower()
        for archetype, keywords in self.ARCHETYPE_KEYWORDS.items():
            for kw in keywords:
                if kw in raw_lower:
                    return archetype
        if raw_lower in ["provider", "doctor", "physician", "nurse", "clinician"]:
            return "user"
        if raw_lower in ["payer", "insurer", "reviewer"]:
            return "operator"
        if raw_lower in ["patient", "consumer", "customer"]:
            return "user"
        return "unknown"

    def _classify_domain(self, text: str) -> Dict[str, Any]:
        """Classify domain from intent text using keyword matching."""
        text_lower = text.lower()
        scores: Dict[str, float] = {}
        matched_keywords: Dict[str, List[str]] = {}

        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = 0.0
            matched: List[str] = []
            for kw in keywords:
                if kw in text_lower:
                    score += 1.0
                    matched.append(kw)
            if matched:
                scores[domain] = score / max(len(keywords) * 0.15, 1)
                matched_keywords[domain] = matched

        if not scores:
            return {"domain": "general", "sub_domains": [], "regions": [], "confidence": 0.1}

        best_domain = max(scores, key=scores.get)
        confidence = min(scores[best_domain], 0.98)
        sub_domains = self._infer_sub_domains(text, best_domain, matched_keywords.get(best_domain, []))
        regions = self._infer_regions(text)

        return {
            "domain": best_domain,
            "sub_domains": sub_domains,
            "regions": regions,
            "confidence": confidence,
        }

    def _infer_sub_domains(self, text: str, domain: str, keywords: List[str]) -> List[str]:
        sub_map: Dict[str, List[str]] = {
            "healthcare": [
                ("prior auth", "prior_authorization"),
                ("clinical", "clinical_workflow"),
                ("patient", "patient_facing"),
                ("ehr", "ehr_integration"),
                ("billing", "revenue_cycle"),
                ("telehealth", "telehealth"),
            ],
            "finance": [
                ("trading", "trading"),
                ("payment", "payments"),
                ("lending", "lending"),
                ("risk", "risk_management"),
                ("compliance", "regulatory_compliance"),
            ],
        }
        text_lower = text.lower()
        found: List[str] = []
        for pattern, sub in sub_map.get(domain, []):
            if pattern in text_lower:
                found.append(sub)
        return found

    def _infer_regions(self, text: str) -> List[str]:
        text_lower = text.lower()
        region_patterns = [
            (["us", "united states", "usa", "america", "hipaa", "cms", "fda"], "us"),
            (["eu", "europe", "european", "gdpr", "mifid"], "eu"),
            (["uk", "united kingdom", "britain"], "uk"),
            (["canada", "canadian", "phipa"], "ca"),
            (["australia", "australian"], "au"),
            (["asia", "apac", "singapore", "japan"], "apac"),
        ]
        regions = []
        for patterns, region in region_patterns:
            for p in patterns:
                if p in text_lower:
                    regions.append(region)
                    break
        return regions

    def _extract_constraints(self, text: str) -> List[Dict[str, Any]]:
        """Extract implied constraints from intent text."""
        constraints: List[Dict[str, Any]] = []
        text_lower = text.lower()

        for reg, keywords in self.COMPLIANCE_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    constraints.append({
                        "type": "compliance",
                        "description": f"Must comply with {reg.upper()} regulatory requirements",
                        "confidence": 0.85 if kw == reg else 0.6,
                    })
                    break

        scale_patterns = [
            (r"(\d+[\s]*(?:million|billion|k|thousand|users?|customers?|transactions?))", "scale"),
            (r"(enterprise|large|high[\s-]?volume|millions?|billions?)", "scale"),
        ]
        for pattern, ctype in scale_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                constraints.append({
                    "type": ctype,
                    "description": f"Product must handle scale implied by: {re.search(pattern, text, re.IGNORECASE).group(0)}",
                    "confidence": 0.5,
                })
                break

        geo_patterns = [
            (r"(?:in|across|covering|serving)\s+(.+?)(?:\.|$|with|and)", "geographic"),
        ]
        for pattern, ctype in geo_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                region = match.group(1).strip()
                constraints.append({
                    "type": ctype,
                    "description": f"Geographic scope: {region}",
                    "confidence": 0.6,
                })

        return constraints

    def _detect_ambiguities(self, text: str, domain_match: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect ambiguous statements requiring PM clarification."""
        flags: List[Dict[str, Any]] = []
        text_lower = text.lower()

        if domain_match["confidence"] < 0.3:
            flags.append({
                "statement": text[:100],
                "reason": "No clear domain identified — cannot determine regulatory or compliance context",
                "suggested_clarification": "What industry or domain does this product serve? (e.g., healthcare, finance, enterprise SaaS)",
            })

        persona_keywords = ["provider", "payer", "patient", "user", "customer", "admin", "manager"]
        found_personas = sum(1 for k in persona_keywords if k in text_lower)
        if found_personas < 2:
            flags.append({
                "statement": text[:100],
                "reason": "Fewer than 2 distinct personas detected — complex workflows typically need multiple personas",
                "suggested_clarification": "Who are the key personas involved? (e.g., providers submitting requests, payers reviewing them)",
            })

        if "healthcare" in text_lower and "hipaa" not in text_lower:
            flags.append({
                "statement": "healthcare",
                "reason": "Healthcare intent detected but no compliance framework specified",
                "suggested_clarification": "Does this product need HIPAA compliance, or is it non-clinical (e.g., practice management)?",
            })

        if "ai" in text_lower or "artificial intelligence" in text_lower:
            if not any(term in text_lower for term in ["review", "assist", "automate", "recommend", "predict"]):
                flags.append({
                    "statement": "AI/artificial intelligence",
                    "reason": "AI mentioned but use case is unclear",
                    "suggested_clarification": "How should AI be used? (e.g., AI-assisted review, automated recommendations, predictive analytics)",
                })

        if any(term in text_lower for term in ["global", "worldwide", "multi-region", "international"]):
            pass
        elif domain_match.get("regions") and len(domain_match["regions"]) > 1:
            flags.append({
                "statement": f"Regions detected: {', '.join(domain_match['regions'])}",
                "reason": "Multiple regions detected — verify cross-region compliance requirements",
                "suggested_clarification": f"Is the product intended for all detected regions ({', '.join(domain_match['regions'])}) or a subset?",
            })

        return flags

    def _detect_archetype_gaps(self, personas: List[Dict[str, Any]]) -> List[str]:
        """Detect personas whose archetype is unknown (not in known archetypes)."""
        return [p["persona_id"] for p in personas if p.get("archetype_type") == "unknown"]

    def _compute_confidence(
        self,
        text: str,
        problem: str,
        personas: List[Dict[str, Any]],
        domain_match: Dict[str, Any],
    ) -> Dict[str, float]:
        """Compute per-field confidence scores."""
        text_len = len(text.strip())
        problem_confidence = min(0.3 + 0.005 * len(problem), 0.95)
        persona_confidences = [p["confidence"] for p in personas]
        personas_confidence = sum(persona_confidences) / len(persona_confidences) if persona_confidences else 0.0

        has_quantified = bool(re.search(r"\d+%", text))
        outcomes_confidence = 0.5 if has_quantified else 0.3

        constraints_confidence = 0.7 if domain_match["confidence"] > 0.5 else 0.3

        weights = {"problem": 0.25, "personas": 0.25, "domain": 0.25, "outcomes": 0.15, "constraints": 0.1}
        overall = (
            weights["problem"] * problem_confidence
            + weights["personas"] * personas_confidence
            + weights["domain"] * domain_match["confidence"]
            + weights["outcomes"] * outcomes_confidence
            + weights["constraints"] * constraints_confidence
        )

        return {
            "overall": round(overall, 2),
            "problem": round(problem_confidence, 2),
            "personas": round(personas_confidence, 2),
            "domain": round(domain_match["confidence"], 2),
            "outcomes": round(outcomes_confidence, 2),
            "constraints": round(constraints_confidence, 2),
        }

    def generate_master_prd(self, decomposition: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-generate a master PRD from an intent decomposition."""
        problem = decomposition["extracted_problem"]
        personas = decomposition["inferred_personas"]
        outcomes = decomposition["extracted_outcomes"]
        domain = decomposition["domain_match"]
        constraints = decomposition["implied_constraints"]

        scope_boundaries = []
        for c in constraints:
            if c["type"] == "compliance":
                scope_boundaries.append(f"Must comply with {c['description']}")
            elif c["type"] == "geographic":
                scope_boundaries.append(f"Geographic scope: {c['description']}")

        persona_coverage = []
        for p in personas:
            persona_coverage.append({
                "persona_ref": p["persona_id"],
                "label": p["label"],
                "archetype": p["archetype_type"],
                "coverage_status": "primary" if p["confidence"] > 0.7 else "secondary",
            })

        return {
            "schema_version": "1.0.0",
            "master_prd_id": f"mprd_{uuid.uuid4().hex[:12]}",
            "title": f"Product Architecture: {problem[:60].strip()}...",
            "executive_summary": problem,
            "problem_statement": problem,
            "opportunity_statement": f"Build a solution that addresses: {problem}",
            "business_outcomes": outcomes,
            "success_metrics": [{"metric": o["measurement"], "outcome_ref": o["outcome_id"]} for o in outcomes],
            "scope_boundaries": scope_boundaries,
            "persona_coverage_map": persona_coverage,
            "domain_context": domain,
            "cross_component_dependency_hypothesis": [],
            "assumptions": self._generate_assumptions(decomposition),
            "generated_from_intent": decomposition.get("intent_decomposition_id", ""),
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }

    def _generate_assumptions(self, decomposition: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Categorize assumptions by confidence provenance."""
        cs = decomposition["confidence_scores"]
        assumptions = []
        for field, label in [("problem", "Problem extraction"), ("personas", "Persona identification"),
                              ("domain", "Domain classification"), ("outcomes", "Outcome extraction"),
                              ("constraints", "Constraint inference")]:
            score = cs.get(field, 0.0)
            if score >= 0.8:
                provenance = "observed"
            elif score >= 0.5:
                provenance = "inferred"
            else:
                provenance = "assumed"
            assumptions.append({
                "field": field,
                "label": label,
                "confidence": score,
                "provenance": provenance,
            })
        return assumptions
