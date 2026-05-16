import sys
import urllib.error
import urllib.request

from bs4 import BeautifulSoup, Tag

DISTILL_DOMAINS = ("distill.pub", "transformer-circuits.pub")
STRIP_TAGS = ("d-bibliography", "d-appendix", "d-citation", "nav", "header", "footer",
              "d-byline", "d-title", "d-toc")
VISUALIZATION_SIZE_THRESHOLD = 200  # lines — strip prose-free divs larger than this


def _is_distill_url(url: str) -> bool:
    return any(d in url for d in DISTILL_DOMAINS)


def _fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "cc-tools/cc-distill-fetch"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise RuntimeError(str(e.reason))


def _convert_math(soup: BeautifulSoup) -> None:
    for tag in soup.find_all("d-math"):
        latex = tag.get_text()
        is_block = tag.get("block") is not None or tag.get("display") is not None
        replacement = f"\n\n$${latex}$$\n\n" if is_block else f"${latex}$"
        tag.replace_with(replacement)


def _strip_boilerplate(soup: BeautifulSoup) -> None:
    for tag_name in STRIP_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()


def _strip_large_non_prose_divs(soup: BeautifulSoup) -> None:
    for tag in soup.find_all(["div", "figure", "d-figure"]):
        text = tag.get_text(separator="\n")
        lines = [l for l in text.splitlines() if l.strip()]
        prose = [l for l in lines if len(l.split()) > 3]
        if len(lines) > VISUALIZATION_SIZE_THRESHOLD and len(prose) < len(lines) * 0.2:
            tag.decompose()


def _node_to_markdown(tag: Tag, depth: int = 0) -> str:
    if isinstance(tag, str):
        return tag

    name = tag.name if hasattr(tag, "name") else None
    if name is None:
        return tag.get_text()

    children = "".join(_node_to_markdown(c, depth) for c in tag.children)

    if name in ("h1", "h2", "h3", "h4"):
        level = int(name[1])
        return f"\n\n{'#' * level} {children.strip()}\n\n"
    if name == "p":
        return f"\n\n{children.strip()}\n\n"
    if name in ("strong", "b"):
        return f"**{children.strip()}**"
    if name in ("em", "i"):
        return f"*{children.strip()}*"
    if name == "code":
        return f"`{children.strip()}`"
    if name == "pre":
        return f"\n\n```\n{children.strip()}\n```\n\n"
    if name == "a":
        href = tag.get("href", "")
        text = children.strip()
        return f"[{text}]({href})" if href else text
    if name in ("ul", "ol"):
        return f"\n{children}\n"
    if name == "li":
        return f"- {children.strip()}\n"
    if name == "blockquote":
        lines = children.strip().splitlines()
        return "\n" + "\n".join(f"> {l}" for l in lines) + "\n"
    if name in ("section", "article", "d-article", "d-body", "body", "main"):
        return children
    if name in ("span", "div"):
        return children
    if name == "br":
        return "\n"
    if name in ("script", "style", "svg", "figure", "img"):
        return ""

    return children


def _extract(html: str, url: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    _strip_boilerplate(soup)
    _strip_large_non_prose_divs(soup)
    _convert_math(soup)

    title_tag = soup.find("d-title") or soup.find("title")
    title = title_tag.get_text().strip() if title_tag else ""

    article = (soup.find("d-article") or soup.find("article")
               or soup.find("main") or soup.find("body"))
    if not article:
        raise RuntimeError("no article content found")

    body = _node_to_markdown(article)

    import re
    body = re.sub(r"\n{3,}", "\n\n", body)
    body = body.strip()

    header = f"URL Source: {url}\n"
    if title:
        header += f"Title: {title}\n"
    return header + "\n" + body + "\n"


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: cc-distill-fetch <url>", file=sys.stderr)
        print("Fetch a Distill-template publication (distill.pub, transformer-circuits.pub).",
              file=sys.stderr)
        print("Extracts <d-math> LaTeX directly, strips interactive visualizations.",
              file=sys.stderr)
        print("Output is written to stdout.", file=sys.stderr)
        sys.exit(0 if "--help" in sys.argv else 1)

    url = sys.argv[1]

    if not _is_distill_url(url):
        print(f"cc-distill-fetch: warning: {url} is not a known Distill domain "
              f"({', '.join(DISTILL_DOMAINS)}) — proceeding anyway", file=sys.stderr)

    try:
        html = _fetch_html(url)
        result = _extract(html, url)
    except RuntimeError as e:
        print(f"cc-distill-fetch: {e}", file=sys.stderr)
        sys.exit(1)

    print(result)
