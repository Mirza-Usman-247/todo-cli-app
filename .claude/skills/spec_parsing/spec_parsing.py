"""
Spec Parsing Skill Implementation

This skill ensures accurate interpretation of Spec‑Kit Plus specifications
and treats them as the single source of truth for all development activities.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Specification:
    """Represents a parsed specification file."""
    path: str
    content: str
    features: List[str]
    ambiguities: List[str]
    constraints: List[str]


class SpecParser:
    """
    A parser class that handles reading, parsing, and validating specifications.
    """

    def __init__(self, specs_dir: str = "./specs"):
        self.specs_dir = Path(specs_dir)
        self.specifications = {}

    def find_spec_files(self) -> List[Path]:
        """
        Find all specification files in the specs directory.

        Returns:
            List[Path]: Paths to all spec files matching *.md pattern
        """
        if not self.specs_dir.exists():
            return []

        spec_files = list(self.specs_dir.rglob("*.md"))
        return spec_files

    def read_spec_file(self, spec_path: Path) -> str:
        """
        Read the content of a specification file.

        Args:
            spec_path: Path to the specification file

        Returns:
            str: Content of the specification file
        """
        with open(spec_path, 'r', encoding='utf-8') as file:
            return file.read()

    def extract_features_from_spec(self, content: str) -> List[str]:
        """
        Extract features mentioned in the specification.

        Args:
            content: Content of the specification file

        Returns:
            List[str]: List of features identified in the spec
        """
        features = []

        # Look for feature-related patterns in the content
        feature_patterns = [
            r'#\s*(?:feature|functionality|capability)',  # Feature headers
            r'-\s*\*\*(?:add|implement|create)\*\*\s+(.+?)(?:\n|$)',  # Bullet points with bold add/implement
            r'as\s+a\s+\w+(?:\s+\w+)*,\s*i\s+want(?:\s+to)?\s+(.+?)(?:\n|so)',  # User story format
            r'(?:must|should|shall)\s+(?:be\s+able\s+to|support|have)\s+(.+?)(?:\n|\.|,)',  # Requirement patterns
        ]

        for pattern in feature_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            features.extend([match.strip() for match in matches if match.strip()])

        # Remove duplicates while preserving order
        unique_features = []
        for feature in features:
            if feature.lower() not in [f.lower() for f in unique_features]:
                unique_features.append(feature)

        return unique_features

    def identify_ambiguities(self, content: str) -> List[str]:
        """
        Identify potential ambiguities in the specification.

        Args:
            content: Content of the specification file

        Returns:
            List[str]: List of identified ambiguities
        """
        ambiguities = []

        # Look for ambiguity indicators
        ambiguity_patterns = [
            (r'(?:may|might|could|possibly|perhaps|sometimes)', 'Vague modality words'),
            (r'(?:etc\.|and so on|and others)', 'Non-exhaustive lists'),
            (r'(?:but|however|yet)', 'Contradictory statements'),
            (r'(?:some|certain|various)', 'Undefined quantities'),
            (r'(?:soon|later|eventually|in future)', 'Undefined timing'),
            (r'(?:efficient|fast|good|better)', 'Subjective qualities without metrics'),
            (r'(?:etc|and more)', 'Unspecified continuations'),
        ]

        for pattern, description in ambiguity_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                ambiguities.append(f"{description}: Found '{matches[0]}'")

        # Check for undefined terms
        undefined_terms = re.findall(r'(?<!\w)([A-Z]{2,}|[A-Z][a-z]+[A-Z]\w*)(?!\w)', content)
        if undefined_terms:
            ambiguities.append(f"Potential undefined acronyms/technical terms: {', '.join(set(undefined_terms[:5]))}")

        return list(set(ambiguities))  # Remove duplicate ambiguities

    def extract_constraints(self, content: str) -> List[str]:
        """
        Extract constraints from the specification.

        Args:
            content: Content of the specification file

        Returns:
            List[str]: List of constraints identified in the spec
        """
        constraints = []

        constraint_patterns = [
            r'(?:must\s+not|should\s+not|shall\s+not|cannot|never)\s+(.+?)(?:\n|\.|,)',
            r'(?:only\s+when|except\s+when|unless)\s+(.+?)(?:\n|\.|,)',
            r'(?:limited\s+to|restricted\s+to|up\s+to)\s+(.+?)(?:\n|\.|,)',
            r'(?:requires|needs|depends\s+on)\s+(.+?)(?:\n|\.|,)',
        ]

        for pattern in constraint_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            constraints.extend([match.strip() for match in matches if match.strip()])

        return constraints

    def parse_specification(self, spec_path: Path) -> Specification:
        """
        Parse a specification file completely.

        Args:
            spec_path: Path to the specification file

        Returns:
            Specification: Parsed specification object
        """
        content = self.read_spec_file(spec_path)

        features = self.extract_features_from_spec(content)
        ambiguities = self.identify_ambiguities(content)
        constraints = self.extract_constraints(content)

        spec = Specification(
            path=str(spec_path),
            content=content,
            features=features,
            ambiguities=ambiguities,
            constraints=constraints
        )

        self.specifications[str(spec_path)] = spec

        return spec

    def load_all_specs(self) -> Dict[str, Specification]:
        """
        Load and parse all specification files in the specs directory.

        Returns:
            Dict[str, Specification]: Mapping of file paths to parsed specifications
        """
        spec_files = self.find_spec_files()

        for spec_file in spec_files:
            self.parse_specification(spec_file)

        return self.specifications

    def validate_implementation_vs_spec(self, implementation_description: str, spec_path: str) -> Tuple[bool, List[str]]:
        """
        Validate that an implementation aligns with the specification.

        Args:
            implementation_description: Description of what's being implemented
            spec_path: Path to the specification to validate against

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_issues)
        """
        if spec_path not in self.specifications:
            return False, ["Specification not loaded"]

        spec = self.specifications[spec_path]
        issues = []

        # Check if implementation matches any features in the spec
        implementation_lower = implementation_description.lower()
        found_feature_match = False

        for feature in spec.features:
            if feature.lower() in implementation_lower:
                found_feature_match = True
                break

        if not found_feature_match:
            issues.append("Implementation does not clearly correspond to any feature in the specification")

        return len(issues) == 0, issues


class SpecParsingSkill:
    """
    Main class for the Spec Parsing Skill that enforces spec compliance.
    """

    def __init__(self):
        self.parser = SpecParser()
        self.current_specs = {}
        self.enforcement_active = True

    def ensure_specs_loaded(self) -> bool:
        """
        Ensure that specification files are loaded before proceeding with coding.

        Returns:
            bool: True if specs are loaded, False otherwise
        """
        if not self.current_specs:
            self.current_specs = self.parser.load_all_specs()

        return len(self.current_specs) > 0

    def check_before_coding(self) -> Tuple[bool, List[str]]:
        """
        Check if specs are properly loaded and understood before coding.

        Returns:
            Tuple[bool, List[str]]: (ready_to_code, list_of_issues_or_warnings)
        """
        issues = []

        if not self.ensure_specs_loaded():
            issues.append("No specification files found in ./specs/")
            return False, issues

        # Check for ambiguities in specs
        for spec_path, spec in self.current_specs.items():
            if spec.ambiguities:
                issues.extend([
                    f"Ambiguity in {spec_path}: {ambiguity}"
                    for ambiguity in spec.ambiguities
                ])

        # If there are critical issues (like no specs found), return False
        # Otherwise return True but with warnings about ambiguities
        has_critical_issues = any("No specification files found" in issue for issue in issues)

        if has_critical_issues:
            return False, issues
        elif issues:
            # Has warnings but can proceed with caution
            return True, issues
        else:
            # Clean specs, ready to proceed
            return True, []

    def validate_feature_implementation(self, feature_description: str) -> Tuple[bool, List[str]]:
        """
        Validate that a feature implementation is present in the specifications.

        Args:
            feature_description: Description of the feature being implemented

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_issues)
        """
        if not self.ensure_specs_loaded():
            return False, ["Specifications not loaded - cannot validate feature"]

        issues = []

        # Check if the feature exists in any of the loaded specs
        found_in_specs = False
        for spec_path, spec in self.current_specs.items():
            for feature in spec.features:
                if feature_description.lower() in feature.lower() or \
                   feature.lower() in feature_description.lower():
                    found_in_specs = True
                    break
            if found_in_specs:
                break

        if not found_in_specs:
            issues.append(f"Feature '{feature_description}' not found in any specification")

        return found_in_specs, issues

    def flag_ambiguities(self) -> List[str]:
        """
        Identify and return all ambiguities found in the specifications.

        Returns:
            List[str]: List of all ambiguities found
        """
        ambiguities = []

        for spec_path, spec in self.current_specs.items():
            for ambiguity in spec.ambiguities:
                ambiguities.append(f"{spec_path}: {ambiguity}")

        return ambiguities

    def enforce_spec_compliance(self, activity: str, details: str) -> Tuple[bool, List[str]]:
        """
        Enforce that all activities comply with the specification requirements.

        Args:
            activity: Type of activity ('coding', 'feature_implementation', etc.)
            details: Details about the activity

        Returns:
            Tuple[bool, List[str]]: (compliant, list_of_issues)
        """
        if activity == "coding" or activity == "implementation":
            return self.check_before_coding()
        elif activity == "feature_creation":
            return self.validate_feature_implementation(details)
        else:
            # For other activities, just ensure specs are loaded
            return self.ensure_specs_loaded(), []

    def get_spec_summary(self) -> Dict[str, any]:
        """
        Get a summary of loaded specifications.

        Returns:
            Dict[str, any]: Summary information about loaded specs
        """
        if not self.current_specs:
            self.current_specs = self.parser.load_all_specs()

        summary = {
            "spec_count": len(self.current_specs),
            "total_features": sum(len(spec.features) for spec in self.current_specs.values()),
            "total_ambiguities": sum(len(spec.ambiguities) for spec in self.current_specs.values()),
            "total_constraints": sum(len(spec.constraints) for spec in self.current_specs.values()),
            "spec_paths": list(self.current_specs.keys())
        }

        return summary


# Global instance for easy access
skill = SpecParsingSkill()


def apply_spec_parsing_skill(activity: str, details: str = "") -> Tuple[bool, List[str]]:
    """
    Apply the Spec Parsing skill to ensure spec compliance.

    Args:
        activity: Type of activity being performed
        details: Additional details about the activity

    Returns:
        Tuple[bool, List[str]]: (compliant, list_of_issues)
    """
    return skill.enforce_spec_compliance(activity, details)