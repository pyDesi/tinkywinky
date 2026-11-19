import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import net from "node:net";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { setTimeout as delay } from "node:timers/promises";
import { test } from "node:test";

const artifact = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const root = path.resolve(artifact, "../..");
const bundle = path.join(artifact, "dist/index.mjs");

async function unusedPort() {
  const server = net.createServer();
  server.listen(0, "127.0.0.1");
  await once(server, "listening");
  const port = server.address().port;
  await new Promise((resolve) => server.close(resolve));
  return port;
}

for (const [label, cwd] of [["workspace root", root], ["artifact directory", artifact]]) {
  test(`production bundle starts from ${label}`, { timeout: 20_000 }, async () => {
    const port = await unusedPort();
    const child = spawn(process.execPath, [bundle], {
      cwd,
      env: { ...process.env, PORT: String(port), NODE_ENV: "production" },
      stdio: ["ignore", "pipe", "pipe"],
    });
    let output = "";
    child.stdout.on("data", chunk => { output += chunk; });
    child.stderr.on("data", chunk => { output += chunk; });
    const exited = once(child, "exit");
    try {
      let ready = false;
      const deadline = Date.now() + 12_000;
      while (Date.now() < deadline) {
        assert.equal(child.exitCode, null, `API exited during startup:\n${output}`);
        try {
          const response = await fetch(`http://127.0.0.1:${port}/api/healthz`, {
            signal: AbortSignal.timeout(500),
          });
          if (response.ok) { ready = true; break; }
        } catch { /* The isolated process may not have bound its test port yet. */ }
        await delay(100);
      }
      assert.ok(ready, `API did not become ready:\n${output}`);
      const response = await fetch(`http://127.0.0.1:${port}/api/workbench/scenarios`);
      assert.equal(response.status, 200);
      const scenarios = await response.json();
      assert.deepEqual(scenarios.map(s => s.id), [1, 2, 3]);
      assert.deepEqual(scenarios.map(s => s.deviceCount), [1, 4, 12]);
    } finally {
      child.kill("SIGTERM");
      await exited;
    }
  });
}
