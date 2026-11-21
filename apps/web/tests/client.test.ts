import { describe, expect, it, vi } from "vitest";
import { api } from "../src/api/client";

describe("typed API client", () => {
  it("returns the backend envelope", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ data: [], data_as_of: "now", is_demo: true }), { status: 200 })));
    const result = await api.crops();
    expect(result.is_demo).toBe(true);
    expect(result.data).toEqual([]);
  });
  it("surfaces API errors", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ message: "offline" }), { status: 503 })));
    await expect(api.crops()).rejects.toThrow("offline");
  });
});
