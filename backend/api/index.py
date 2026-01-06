from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import requests
import random
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/', response_class=HTMLResponse)
def root():
    return """
        <h1>LeetCode Revision API</h1>
        <p>Get random solved LeetCode questions for revision</p>
        
        <hr>
        
        <h2>API Endpoint</h2>
        <p><strong>GET /{leetcodeid}/{n}</strong></p>
        
        <h3>Parameters:</h3>
        <ul>
            <li><strong>leetcodeid</strong> - Your LeetCode username</li>
            <li><strong>n</strong> - Number of random questions to retrieve</li>
        </ul>
        
        <h3>Example:</h3>
        <p><a href="/hrmiitm/5">/hrmiitm/5</a></p>
        
        <hr>
        
        <h2>Response Format</h2>
        <p>Returns a JSON array of random solved problems:</p>
        <pre>
    """


@app.get("/{leetcodeid}/{n}")
def get_random_solved_questions(leetcodeid: str, n: int):
    if n <= 0:
        raise HTTPException(status_code=400, detail="n must be positive")

    url = "https://leetcode.com/graphql"

    query = """
    query recentAcSubmissions($username: String!) {
      recentAcSubmissionList(username: $username, limit: 100) {
        title
        titleSlug
        timestamp
      }
    }
    """

    payload = {
        "query": query,
        "variables": {
            "username": leetcodeid
        }
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Referer": f"https://leetcode.com/{leetcodeid}/"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch data from LeetCode"
        )

    data = response.json()
    submissions = data.get("data", {}).get("recentAcSubmissionList", [])

    if not submissions:
        return []

    # remove duplicates
    unique = {}
    for s in submissions:
        unique[s["titleSlug"]] = s["title"]

    problems = list(unique.items())
    n = min(n, len(problems))

    selected = random.sample(problems, n)

    return [
        {
            "title": title,
            "link": f"https://leetcode.com/problems/{slug}/"
        }
        for slug, title in selected
    ]
