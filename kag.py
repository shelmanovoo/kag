{
  "nodes": [
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO news_articles (title, link, pubdate, content, contentsnippet, guid, isodate, itunes) VALUES ($1, $2, $3, $4, $5, $6, $7, $8) ON CONFLICT (guid) DO NOTHING;",
        "options": {
          "queryReplacement": "={{ $json.title }}, {{ $json.link }}, {{ $json.pubDate }}, {{ $json.content }}, {{ $json.contentSnippet }}, {{ $json.guid }}, {{ $json.isoDate }}, {{ $json.itunes }}"
        }
      },
      "name": "Insert Unique News1",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.6,
      "position": [
        272,
        208
      ],
      "id": "de4d0f47-b6e5-4f7b-8d2a-3711620bcde3",
      "credentials": {
        "postgres": {
          "id": "wujVNwu5jIKjF2n0",
          "name": "Postgres account"
        }
      }
    }
  ],
  "connections": {},
  "pinData": {},
  "meta": {
    "instanceId": "9ce263ea74ac56142ad0b445edd4996f0dce195bb2058608aecc86f0fd24906f"
  }
}