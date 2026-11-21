export function LoadingState({ label = "Loading…" }: { label?: string }) { return <div className="state" aria-live="polite"><span className="spinner" />{label}</div> }
export function EmptyState({ label = "No data available yet." }: { label?: string }) { return <div className="state">{label}</div> }
export function ErrorState({ error, retry }: { error: Error; retry: () => void }) { return <div className="state error"><strong>{error.message}</strong><button onClick={retry}>Try again</button></div> }
