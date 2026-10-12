# Forms and Validation: React Hook Form + Zod

> **Purpose**: Typed, accessible forms with schema validation, plus the React 19 native alternative
> **MCP Validated**: 2026-10-02

## When to Use

- Multi-field forms needing client-side validation with typed output.
- Reuse one schema for validation and TypeScript types.

## Implementation

```tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'

const schema = z.object({
  name: z.string().min(1, { message: 'Required' }),
  age: z.number().min(10),
})
type FormValues = z.infer<typeof schema>

export function PersonForm({ onSave }: { onSave: (v: FormValues) => void }) {
  const { register, handleSubmit, formState: { errors, isSubmitting } } =
    useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { name: '', age: 18 } })

  return (
    <form onSubmit={handleSubmit(onSave)} noValidate>
      <label htmlFor="name">Name</label>
      <input id="name" aria-invalid={!!errors.name} {...register('name')} />
      {errors.name && <p role="alert">{errors.name.message}</p>}

      <label htmlFor="age">Age</label>
      <input id="age" type="number" {...register('age', { valueAsNumber: true })} />
      {errors.age && <p role="alert">{errors.age.message}</p>}

      <button type="submit" disabled={isSubmitting}>Save</button>
    </form>
  )
}
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `mode` | `onSubmit` | Also `onBlur`, `onChange` (perf impact), `onTouched`, `all` |
| `resolver` | none | External validator; `zodResolver(schema)` |
| `defaultValues` | none | Avoid `undefined` values (conflicts with controlled inputs); may be async |
| `valueAsNumber` | n/a | Option on `register` for numeric inputs |
| Versions | | react-hook-form 7.89, `@hookform/resolvers` 5.9 (peer zod `^3.25 \|\| ^4`), zod 4.6 (needs TS `strict`, 5.5+) |

Notes: with resolvers, nested fields produce nested `errors` objects. For schemas using `.default()`,
input and output types differ; the resolvers README says to pass explicit generics. Use `Controller`
for UI components that do not expose a ref.

## Example Usage

React 19 alternative for simple forms (no client schema): `<form action={fn}>` with
`useActionState` returning `[state, action, isPending]`. Server validation errors (e.g. 422 from the
API) should be mapped back with `setError(field, { message })`.

## See Also

- [Accessibility](../concepts/accessibility-basics.md) , [React 19 + TS](../concepts/react19-typescript.md)
- [pydantic KB](../../pydantic/index.md) (mirror server-side rules; the server stays authoritative)

## Sources

- https://react-hook-form.com/get-started , https://react-hook-form.com/docs/useform
- https://github.com/react-hook-form/resolvers ; https://zod.dev/ ; https://react.dev/blog/2024/12/05/react-19
- `setError` usage: not re-fetched this session (react-hook-form API; practitioner-level here)
