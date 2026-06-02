"""Deterministic dataset generation for benchmarks.

Provides utilities to generate reproducible test data for benchmark scenarios,
ensuring consistent results across runs and environments.
"""

from __future__ import annotations

import hashlib
import random
from typing import Generator


# Profile sizes
PROFILE_SIZES: dict[str, int] = {
    "tiny": 100,
    "small": 1000,
    "medium": 10000,
    "large": 100000,
    "stress": 1000000,
}


def _deterministic_seed(profile: str, scenario: str) -> int:
    """Generate a deterministic seed from profile and scenario.

    Args:
        profile: Profile name (tiny, small, etc.)
        scenario: Scenario name

    Returns:
        Integer seed for random number generator
    """
    combined = f"{profile}:{scenario}:omnivia-core-v1"
    hash_bytes = hashlib.sha256(combined.encode()).digest()
    return int.from_bytes(hash_bytes[:4], byteorder="big")


def generate_content_seed(index: int, max_index: int) -> str:
    """Generate deterministic content for a given index.

    Args:
        index: Position of the item (0-based)
        max_index: Total number of items

    Returns:
        Deterministic string content
    """
    # Use a portion of the hash for content
    content_base = f"benchmark_content_{index}_of_{max_index}"
    hash_bytes = hashlib.sha256(content_base.encode()).digest()
    short_hash = hash_bytes[:8].hex()

    return f"Memory content {index}: {short_hash}. This is a test memory for performance benchmarking of OmniVia Core memory operations."


def generate_memory_content(index: int, max_index: int) -> str:
    """Generate memory content for benchmark data.

    Args:
        index: Position of the item (0-based)
        max_index: Total number of items

    Returns:
        Content string for a memory
    """
    return generate_content_seed(index, max_index)


def generate_keyword_list(count: int, seed: int) -> list[str]:
    """Generate a list of keywords for search benchmarks.

    Args:
        count: Number of keywords to generate
        seed: Random seed for reproducibility

    Returns:
        List of keyword strings
    """
    rng = random.Random(seed)
    base_words = [
        "benchmark",
        "performance",
        "test",
        "data",
        "memory",
        "search",
        "graph",
        "entity",
        "relationship",
        "workspace",
        "import",
        "export",
        "index",
        "query",
        "filter",
    ]

    keywords = []
    for i in range(count):
        rng.shuffle(base_words)
        keyword = f"keyword_{i}_{base_words[0]}_{base_words[1]}"
        keywords.append(keyword)

    return keywords


def generate_tag_list(count: int, seed: int) -> list[str]:
    """Generate a list of tags for filtering benchmarks.

    Args:
        count: Number of tags to generate
        seed: Random seed for reproducibility

    Returns:
        List of tag strings
    """
    rng = random.Random(seed)
    tag_categories = ["type", "priority", "status", "category", "source"]

    tags = []
    for i in range(count):
        category = tag_categories[i % len(tag_categories)]
        value = rng.randint(1, 10)
        tags.append(f"{category}:{value}")

    return tags


def generate_memory_items(
    profile: str, scenario: str
) -> Generator[dict, None, None]:
    """Generate deterministic memory items for benchmark scenarios.

    Args:
        profile: Profile name (tiny, small, medium, large, stress)
        scenario: Scenario name for seeding

    Yields:
        Dictionary with memory item data
    """
    count = PROFILE_SIZES.get(profile, PROFILE_SIZES["tiny"])
    seed = _deterministic_seed(profile, scenario)
    rng = random.Random(seed)

    for i in range(count):
        keywords = generate_keyword_list(3, rng.randint(0, 2**31))
        tags = generate_tag_list(2, rng.randint(0, 2**31))

        yield {
            "content": generate_memory_content(i, count),
            "keywords": keywords,
            "tags": tags,
            "memory_type": ["general", "decision", "pattern", "constraint"][
                i % 4
            ],
            "index": i,
        }


def get_item_count(profile: str) -> int:
    """Get the number of items for a given profile.

    Args:
        profile: Profile name

    Returns:
        Item count for the profile
    """
    return PROFILE_SIZES.get(profile, PROFILE_SIZES["tiny"])


def iter_profiles() -> Generator[tuple[str, int], None, None]:
    """Iterate over all available profiles and their sizes.

    Yields:
        Tuple of (profile_name, item_count)
    """
    for name, count in PROFILE_SIZES.items():
        yield name, count
