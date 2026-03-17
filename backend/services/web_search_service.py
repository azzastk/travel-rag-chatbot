import requests

def search_web(query: str) -> str:
    try:
        # DuckDuckGo Instant Answer API
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_redirect": "1",
            "no_html": "1",
            "skip_disambig": "1",
        }

        res = requests.get(url, params=params, timeout=5)
        res.raise_for_status()
        data = res.json()

        # ✅ Thử nhiều field hơn vì AbstractText thường rỗng
        result = (
            data.get("AbstractText")
            or data.get("Answer")
            or data.get("Definition")
            or ""
        )

        # Lấy thêm từ RelatedTopics nếu vẫn rỗng
        if not result and data.get("RelatedTopics"):
            snippets = []
            for topic in data["RelatedTopics"][:3]:
                if isinstance(topic, dict) and topic.get("Text"):
                    snippets.append(topic["Text"])
            result = "\n".join(snippets)

        return result

    except requests.exceptions.Timeout:
        print("[WebSearch] Request timed out.")
        return ""
    except requests.exceptions.RequestException as e:
        print(f"[WebSearch] Request failed: {e}")
        return ""
    except Exception as e:
        print(f"[WebSearch] Unexpected error: {e}")
        return ""