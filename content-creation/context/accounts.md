<!-- creatoros:template -->
# Accounts

> Handles, profile URLs and connections. Archive imports, Metricool, and
> research read this instead of hard-coding any account.

| Platform | Handle | Profile URL | Active | Notes |
|---|---|---|---|---|
| Instagram | <@handle> | <url> | <yes/no> | <business or creator account> |
| LinkedIn | <public id, e.g. jane-doe> | <url> | <yes/no> | <personal profile or company page> |
| X | <@handle> | <url> | <yes/no> | <Premium? long posts allowed?> |
| TikTok | <@handle> | <url> | <yes/no> | |
| YouTube | <@handle / channel id> | <url> | <yes/no> | |
| Medium | <@handle> | <url> | <yes/no> | <Medium user id, if known> |
| Website / newsletter | | <url> | <yes/no> | |

## Metricool

- Brand: <brand label> (blogId `<id>`), timezone `<IANA timezone>`
- Connected networks: <list from get_brands>
- Plan: <Free | Starter | Advanced>, scheduling limit <N posts/month>

## Contact shown on content

- Email: <public contact email, or "none">
- CTA link: <the link that goes in first comments / bio>

## Optional keys (`.env`, never committed)

- `OPENAI_API_KEY`: <set | not set> (AI photos for carousels)
- `APIFY_TOKEN`: <set | not set> (LinkedIn archive import)
