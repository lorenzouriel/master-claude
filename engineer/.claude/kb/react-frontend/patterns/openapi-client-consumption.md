# Consuming a Generated OpenAPI TypeScript Client

> **Purpose**: Generate typed API code from the backend OpenAPI spec and use it with TanStack Query
> **MCP Validated**: 2026-10-02

## When to Use

- A backend (e.g. FastAPI) publishes an OpenAPI schema and the UI must stay in sync.
- You want compile-time errors when an endpoint's request/response shape changes.

## Implementation

Two common generators (neutral):

| Option | What it produces | Notes |
|--------|------------------|-------|
| `@hey-api/openapi-ts` (npm 0.99.x) | SDK functions, types, optional plugins (fetch/axios clients, TanStack Query, more) | Pre-1.0: docs say pin exact versions (`npm i -D -E`); breaking changes may occur |
| `openapi-typescript` + `openapi-fetch` (0.17.x) | `paths` types + a thin typed fetch wrapper (~6 KB) | `createClient<paths>()`; `GET/POST...` return `{ data, error, response }`; middleware for auth/logging |

```ts
// openapi-ts.config.ts  (hey-api)
import { defineConfig } from '@hey-api/openapi-ts'
export default defineConfig({
  input: 'http://localhost:8000/openapi.json',   // or a committed file
  output: 'src/generated',
  plugins: ['@hey-api/client-fetch', '@tanstack/react-query'],  // fetch client is the default and bundled in openapi-ts (no separate install)
})
```

```ts
// TanStack Query plugin naming: [op]Options(), [op]QueryKey(), [op]Mutation()
const { data } = useQuery({ ...getCaseOptions({ path: { id } }) })
const create = useMutation({ ...createCaseMutation() })
create.mutate({ body: { title: 'x' } })
```

```ts
// openapi-fetch alternative
import createClient from 'openapi-fetch'
import type { paths } from '@/generated/schema'     // npx openapi-typescript spec.yaml -o src/generated/schema.d.ts
export const api = createClient<paths>({ baseUrl: import.meta.env.VITE_API_URL })
const { data, error } = await api.GET('/cases/{id}', { params: { path: { id } } })
```

## Configuration

| Setting | Description |
|---------|-------------|
| `input` / `output` | Spec source and generated directory (`src/generated`) |
| `plugins` | Opt-in extras; exact plugin option names: check heyapi.dev for your installed version (plugin config shape not verified here) |
| npm script | `"openapi-ts": "openapi-ts"` then run on spec change |
| `VITE_API_URL` | Only non-secret values are safe in `VITE_` vars |

## Example Usage

Practitioner notes: commit generated output or regenerate in CI and fail on diff so drift is caught;
never hand-edit `generated/`; wrap the generated client in one `shared/api` module that attaches
auth headers; convert backend errors to a single UI error type.

## See Also

- [Server state](../concepts/server-state-tanstack-query.md) , [Feature folders](feature-folders-role-areas.md)
- [pydantic KB](../../pydantic/index.md) (schema source on the Python side)

## Sources

- https://heyapi.dev/openapi-ts/get-started , https://heyapi.dev/openapi-ts/plugins/tanstack-query
- https://openapi-ts.dev/openapi-fetch/ ; npm registry versions (2026-10-02)
