#!/usr/bin/env python3
"""
複数ソースからAI・動画制作の最新情報を自動収集
実行: python3 research_collector.py
"""
import requests, json, os, time
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent.parent / "research_output"
OUTPUT_DIR.mkdir(exist_ok=True)

GITHUB_TOKEN = os.environ.get("API_SEARCH_PAT", "")

def fetch_github_trending():
    """GitHubからAI動画自動化系リポジトリを収集"""
    results = []
    queries = [
        "youtube shorts automation python tts",
        "faceless video ai ffmpeg",
        "tiktok reels automation ai script",
        "short video generator edge-tts",
        "ai content creator automation",
    ]
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    for q in queries:
        try:
            r = requests.get(
                "https://api.github.com/search/repositories",
                params={"q": q, "sort": "stars", "order": "desc", "per_page": 5},
                headers=headers, timeout=10
            )
            if r.status_code == 200:
                for repo in r.json().get("items", []):
                    results.append({
                        "source": "github",
                        "name": repo["full_name"],
                        "stars": repo["stargazers_count"],
                        "description": repo["description"],
                        "url": repo["html_url"],
                        "updated": repo["updated_at"],
                    })
            time.sleep(2)
        except Exception as e:
            print(f"GitHub error: {e}")
    return results

def fetch_huggingface_spaces():
    """HuggingFaceからビデオ関連Spaceを収集"""
    results = []
    try:
        r = requests.get(
            "https://huggingface.co/api/spaces",
            params={"filter": "video", "sort": "likes", "limit": 20},
            timeout=10
        )
        if r.status_code == 200:
            for space in r.json()[:20]:
                results.append({
                    "source": "huggingface",
                    "name": space.get("id", ""),
                    "likes": space.get("likes", 0),
                    "description": space.get("cardData", {}).get("title", ""),
                    "url": f"https://huggingface.co/spaces/{space.get('id','')}",
                })
    except Exception as e:
        print(f"HuggingFace error: {e}")
    return results

def fetch_hackernews():
    """Hacker Newsから最新AI記事を収集"""
    results = []
    try:
        r = requests.get("https://hn.algolia.com/api/v1/search",
            params={"query": "AI video automation", "tags": "story", "numericFilters": "points>10"},
            timeout=10)
        if r.status_code == 200:
            for hit in r.json().get("hits", [])[:10]:
                results.append({
                    "source": "hackernews",
                    "title": hit.get("title", ""),
                    "points": hit.get("points", 0),
                    "url": hit.get("url", ""),
                    "date": hit.get("created_at", ""),
                })
    except Exception as e:
        print(f"HackerNews error: {e}")
    return results

def fetch_arxiv():
    """ArxivからAI動画生成関連論文を収集"""
    results = []
    try:
        r = requests.get(
            "http://export.arxiv.org/api/query",
            params={
                "search_query": "ti:video generation AND ti:automation",
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "max_results": 5
            }, timeout=10
        )
        if r.status_code == 200:
            import re
            titles = re.findall(r'<title>(.*?)</title>', r.text)[1:]
            links = re.findall(r'<id>(http://arxiv.*?)</id>', r.text)
            for t, l in zip(titles[:5], links[:5]):
                results.append({
                    "source": "arxiv",
                    "title": t.strip(),
                    "url": l.strip(),
                })
    except Exception as e:
        print(f"Arxiv error: {e}")
    return results

def main():
    print("🔍 AI Conduit リサーチ収集開始...")
    all_results = {
        "collected_at": datetime.now().isoformat(),
        "github": fetch_github_trending(),
        "huggingface": fetch_huggingface_spaces(),
        "hackernews": fetch_hackernews(),
        "arxiv": fetch_arxiv(),
    }

    output_file = OUTPUT_DIR / f"research_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"✅ 収集完了!")
    print(f"   GitHub: {len(all_results['github'])}件")
    print(f"   HuggingFace: {len(all_results['huggingface'])}件")
    print(f"   HackerNews: {len(all_results['hackernews'])}件")
    print(f"   Arxiv: {len(all_results['arxiv'])}件")
    print(f"   保存先: {output_file}")

if __name__ == "__main__":
    main()
