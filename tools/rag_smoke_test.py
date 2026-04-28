#!/usr/bin/env python3
"""Smoke-test the local RAG routing corpus.

This checks the structural guarantees that the Claude Code skills depend on:
- `insights/_routing.md` exists and has usable categories.
- Priority files referenced from `_routing.md` exist.
- Each category can provide at least five priority files.
- Representative user themes route to expected categories by keyword matching.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTING_FILE = ROOT / "insights" / "_routing.md"
MIN_PRIORITY_FILES = 5
CATEGORY_TIEBREAK_PRIORITY = [
    "リスク・炎上・撤退・法制度",
    "SNS・インフルエンサー・動画",
    "コピー・LP・言葉・オファー",
    "商品設計・コンセプト・価格",
    "顧客心理・ファン化・体験価値",
    "営業・DM・プレゼン・名刺",
    "外注・AI・効率化",
    "集客・PR・低コスト施策",
    "トレンド・ブーム予測",
    "経営者思考・習慣・学習",
]
SPECIAL_ROUTE_RULES = [
    ("外注・AI・効率化", "リスク・炎上・撤退・法制度", ("直美",)),
    ("外注・AI・効率化", "リスク・炎上・撤退・法制度", ("直接", "美容", "雇用")),
]


@dataclass
class Category:
    name: str
    keywords: list[str]
    priority_files: list[str]


@dataclass
class RouteResult:
    primary: Category | None
    secondary: Category | None
    scores: list[tuple[str, int]]
    reason: str


def parse_categories(text: str) -> list[Category]:
    blocks = re.split(r"(?m)^## ", text)
    categories: list[Category] = []

    for block in blocks:
        if not block.strip():
            continue

        lines = block.splitlines()
        name = lines[0].strip()
        body = "\n".join(lines[1:])

        keyword_match = re.search(
            r"### 反応キーワード\s*\n(?P<keywords>.*?)(?=\n### |\n## |\Z)",
            body,
            re.S,
        )
        files_match = re.search(
            r"### 優先して読むファイル\s*\n(?P<files>.*?)(?=\n### |\n## |\Z)",
            body,
            re.S,
        )

        if not keyword_match or not files_match:
            continue

        keywords = [
            keyword.strip()
            for keyword in re.split(r"[、,\n]", keyword_match.group("keywords"))
            if keyword.strip() and not keyword.strip().startswith("#")
        ]
        priority_files = re.findall(r"^- `([^`]+)`", files_match.group("files"), re.M)

        categories.append(Category(name=name, keywords=keywords, priority_files=priority_files))

    return categories


def tie_priority(category_name: str) -> int:
    try:
        return CATEGORY_TIEBREAK_PRIORITY.index(category_name)
    except ValueError:
        return len(CATEGORY_TIEBREAK_PRIORITY)


def find_category(categories: list[Category], name: str | None) -> Category | None:
    if name is None:
        return None
    return next((category for category in categories if category.name == name), None)


def route_topic(topic: str, categories: list[Category]) -> RouteResult:
    scores: list[tuple[str, int]] = []
    best: Category | None = None
    best_score = 0
    best_tie_priority = len(CATEGORY_TIEBREAK_PRIORITY)
    reason = "keyword score"

    for category in categories:
        matched_keywords = [keyword for keyword in category.keywords if keyword and keyword in topic]
        score = sum(len(keyword) for keyword in matched_keywords)
        current_tie_priority = tie_priority(category.name)
        scores.append((category.name, score))
        if score > best_score or (score == best_score and score > 0 and current_tie_priority < best_tie_priority):
            best = category
            best_score = score
            best_tie_priority = current_tie_priority

    sorted_scores = sorted(scores, key=lambda item: (item[1], -tie_priority(item[0])), reverse=True)
    secondary = find_category(categories, sorted_scores[1][0]) if len(sorted_scores) > 1 and sorted_scores[1][1] > 0 else None

    for category_name, secondary_name, required_terms in SPECIAL_ROUTE_RULES:
        if all(term in topic for term in required_terms):
            special = find_category(categories, category_name)
            if special is not None:
                best = special
                secondary = find_category(categories, secondary_name)
                reason = f"special rule: {' + '.join(required_terms)}"
                break

    if secondary is not None and best is not None and secondary.name == best.name:
        secondary = None

    return RouteResult(primary=best, secondary=secondary, scores=sorted_scores, reason=reason)


def validate_categories(categories: list[Category]) -> list[str]:
    errors: list[str] = []

    if not categories:
        return ["No RAG categories with keywords and priority files were parsed."]

    for category in categories:
        if len(category.priority_files) < MIN_PRIORITY_FILES:
            errors.append(
                f"{category.name}: priority files are too few "
                f"({len(category.priority_files)} < {MIN_PRIORITY_FILES})"
            )

        for relative_path in category.priority_files:
            path = ROOT / relative_path
            if not path.is_file():
                errors.append(f"{category.name}: missing priority file: {relative_path}")

    return errors


def run_fixture_tests(categories: list[Category]) -> list[str]:
    fixtures = [
        ("グリークヨーグルトはなぜ流行っているのか？", "トレンド・ブーム予測"),
        ("相席寿司屋さんは、なぜ伸びているのか？", "トレンド・ブーム予測"),
        ("2025年のSNSはどう変わるのか？", "SNS・インフルエンサー・動画"),
        ("広告費をかけずに集客したい", "集客・PR・低コスト施策"),
        ("紹介でお客様を増やすキャンペーンを作りたい", "集客・PR・低コスト施策"),
        ("レビューを増やして知名度を上げたい", "集客・PR・低コスト施策"),
        ("InstagramとYouTubeどっちをやるべき？", "SNS・インフルエンサー・動画"),
        ("インフルエンサーを使って商品を広めたい", "SNS・インフルエンサー・動画"),
        ("動画投稿しているのに売上につながらない", "SNS・インフルエンサー・動画"),
        ("LPを作ったのに売れない", "コピー・LP・言葉・オファー"),
        ("無料オファーで見込み客を集めたい", "コピー・LP・言葉・オファー"),
        ("商品名と強烈なワードで反応率を上げたい", "コピー・LP・言葉・オファー"),
        ("値上げしても売れる価格設定を考えたい", "商品設計・コンセプト・価格"),
        ("売れ残り商品を値下げせずに売りたい", "商品設計・コンセプト・価格"),
        ("ロングセラー商品を作るには何が必要？", "商品設計・コンセプト・価格"),
        ("お客様をファン化したい", "顧客心理・ファン化・体験価値"),
        ("リピーターが生まれる体験を設計したい", "顧客心理・ファン化・体験価値"),
        ("店舗の滞在時間を伸ばして客単価を上げたい", "顧客心理・ファン化・体験価値"),
        ("DMの反応率を上げたい", "営業・DM・プレゼン・名刺"),
        ("商談で刺さるプレゼンを作りたい", "営業・DM・プレゼン・名刺"),
        ("名刺を営業資産として活用したい", "営業・DM・プレゼン・名刺"),
        ("経営者として毎日何を勉強すべき？", "経営者思考・習慣・学習"),
        ("仕事ができるマーケターの習慣を知りたい", "経営者思考・習慣・学習"),
        ("自己投資と時間の使い方を見直したい", "経営者思考・習慣・学習"),
        ("炎上しないためのリスク管理をしたい", "リスク・炎上・撤退・法制度"),
        ("景表法違反にならない広告表現を考えたい", "リスク・炎上・撤退・法制度"),
        ("スパイ防止法について経営者目線で話したい", "リスク・炎上・撤退・法制度"),
        ("AIで業務効率化したい", "外注・AI・効率化"),
        ("ChatGPTでコピーを自動化したい", "外注・AI・効率化"),
        ("外注と業務委託で固定費を下げたい", "外注・AI・効率化"),
        ("直美（直接美容雇用）は、なぜダメなのか？", "外注・AI・効率化"),
    ]
    errors: list[str] = []

    for topic, expected in fixtures:
        route = route_topic(topic, categories)
        actual = route.primary.name if route.primary else "NONE"
        if actual != expected:
            top_scores = ", ".join(f"{name}={score}" for name, score in route.scores[:3])
            errors.append(
                f"fixture route mismatch: {topic!r}: expected {expected!r}, "
                f"got {actual!r} ({top_scores})"
            )

    return errors


def print_topic_probe(topic: str, categories: list[Category]) -> None:
    route = route_topic(topic, categories)
    if route.primary is None:
        print(f"topic: {topic}")
        print("route: no keyword match")
        return

    print(f"topic: {topic}")
    print(f"primary route: {route.primary.name}")
    print(f"secondary route: {route.secondary.name if route.secondary else 'なし'}")
    print(f"reason: {route.reason}")
    print("top scores:")
    for name, score in route.scores[:5]:
        print(f"  - {name}: {score}")
    print("first priority files:")
    for relative_path in route.primary.priority_files[:8]:
        status = "OK" if (ROOT / relative_path).is_file() else "MISSING"
        print(f"  - [{status}] {relative_path}")
    if route.secondary:
        print("secondary priority files:")
        for relative_path in route.secondary.priority_files[:2]:
            status = "OK" if (ROOT / relative_path).is_file() else "MISSING"
            print(f"  - [{status}] {relative_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test koyama-rag-x routing.")
    parser.add_argument("--topic", help="Probe routing for a custom topic.")
    args = parser.parse_args()

    if not ROUTING_FILE.is_file():
        print(f"FAIL: missing {ROUTING_FILE.relative_to(ROOT)}", file=sys.stderr)
        return 1

    categories = parse_categories(ROUTING_FILE.read_text(encoding="utf-8"))
    errors = validate_categories(categories)
    errors.extend(run_fixture_tests(categories))

    if args.topic:
        print_topic_probe(args.topic, categories)

    if errors:
        print("\nFAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nPASS")
    print(f"- categories parsed: {len(categories)}")
    print("- priority file references exist")
    print("- fixture topics route to expected categories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
