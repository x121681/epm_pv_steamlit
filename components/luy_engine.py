# components/luy_engine.py
import csv
import re
from collections import defaultdict

class LuyEngine:
    """
    Rule-based minimal intelligence for domain & capability classification,
    fully CSV-driven. BOM handling included.
    """

    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.DOMAIN_KEYWORDS = {}
        self.CAPABILITY_KEYWORDS = {}
        self.load_csv()

    # ---------------------------------------------------------
    # CSV Loader
    # ---------------------------------------------------------
    def load_csv(self):
        """Load domains and capabilities from CSV with BOM handling."""
        with open(self.csv_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')

            # Normalize headers (remove quotes, lowercase, strip)
            reader.fieldnames = [h.strip().strip('"').lower() for h in reader.fieldnames]

            for row in reader:
                # Normalize keys & values
                row = {k.strip().strip('"').lower(): (v.strip().strip('"') if v else "") for k, v in row.items()}

                name = row.get("name", "")
                description = row.get("description", "").lower()

                if not name:
                    continue

                # Extract keywords: split on commas or newlines, remove empties
                keywords = [kw.strip() for kw in re.split(r"[,\n]", description) if kw.strip()]

                # Identify as domain or capability based on prefix
                if name.lower().startswith("domain"):
                    domain_name = name.split("–")[-1].strip() if "–" in name else name
                    self.DOMAIN_KEYWORDS[domain_name] = keywords
                elif name.lower().startswith("capability"):
                    cap_name = name.split("–")[-1].strip() if "–" in name else name
                    self.CAPABILITY_KEYWORDS[cap_name] = keywords
                else:
                    # fallback to domain if no prefix
                    self.DOMAIN_KEYWORDS[name] = keywords

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------
    def _clean(self, text):
        if not text:
            return ""
        return text.lower().strip()

    def _match_score(self, text, keywords):
        """Simple keyword matching: count words present in text."""
        score = 0
        text_words = re.findall(r"\w+", text.lower())
        for kw in keywords:
            kw_words = re.findall(r"\w+", kw.lower())
            if any(w in text_words for w in kw_words):
                score += 1
        return score

    # ---------------------------------------------------------
    # Domain Matching
    # ---------------------------------------------------------
    def get_domain_suggestions(self, software_name, description, use_case=""):
        text = self._clean(f"{software_name} {description} {use_case}")
        scores = defaultdict(int)
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            scores[domain] = self._match_score(text, keywords)
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results if sorted_results else [("Unknown", 0)]

    # ---------------------------------------------------------
    # Capability Matching
    # ---------------------------------------------------------
    def get_capability_suggestions(self, software_name, description, use_case=""):
        text = self._clean(f"{software_name} {description} {use_case}")
        scores = defaultdict(int)
        for cap, keywords in self.CAPABILITY_KEYWORDS.items():
            scores[cap] = self._match_score(text, keywords)
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results if sorted_results else [("Unspecified", 0)]

    # ---------------------------------------------------------
    # Main classification helper
    # ---------------------------------------------------------
    def classify_software(self, software_name, description, use_case=""):
        domains = self.get_domain_suggestions(software_name, description, use_case)
        capabilities = self.get_capability_suggestions(software_name, description, use_case)
        return {
            "domains": domains,
            "capabilities": capabilities
        }
