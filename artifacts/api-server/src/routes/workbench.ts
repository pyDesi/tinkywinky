import { Router, type IRouter } from "express";
import { execFile } from "node:child_process";
import { readFileSync, existsSync } from "node:fs";
import path from "node:path";
import { promisify } from "node:util";
import {
  GetWorkbenchStatusResponse,
  ListScenariosResponse,
  RunScenarioParams,
  RunScenarioResponse,
} from "@workspace/api-zod";

const router: IRouter = Router();
const execute = promisify(execFile);
// The workflow runs in the API artifact; built and source executions share cwd.
const root = path.resolve(process.cwd(), "../..");
const scenarios = ListScenariosResponse.parse(
  JSON.parse(readFileSync(path.join(root, "scripts/tinkar-scenarios.json"), "utf8")),
);
// Coalesce concurrent runs, bounding work to three fixed scenarios and no shell input.
const active = new Map<number, Promise<unknown>>();
let queue: Promise<unknown> = Promise.resolve();

router.get("/workbench/scenarios", (_req, res): void => {
  res.json(scenarios);
});

router.get("/workbench/status", async (_req, res): Promise<void> => {
  let online = false;
  let message = "Tinkar is unavailable or still starting. Try again shortly.";
  try {
    // Avoid competing with scenario searches: the service's search context is shared.
    const response = await fetch("http://localhost:80/tinkar/api-docs", {
      signal: AbortSignal.timeout(8000),
    });
    if (response.ok) {
      const data = await response.json() as { openapi?: string };
      online = typeof data.openapi === "string";
    }
    if (online) message = "REST service is responding. Each scenario checks the Python gRPC client live.";
  } catch { /* Availability is exposed explicitly, never a synthetic successful result. */ }
  res.json(GetWorkbenchStatusResponse.parse({
    online, message, dataset: "GUDID subset", checkedAt: new Date().toISOString(),
  }));
});

router.post("/workbench/scenarios/:id/run", async (req, res): Promise<void> => {
  const parsed = RunScenarioParams.safeParse(req.params);
  if (!parsed.success) {
    res.status(400).json({ error: "Choose scenario 1, 2, or 3." });
    return;
  }
  const id = parsed.data.id;
  const python = path.join(root, ".pythonlibs/bin/python");
  if (!existsSync(python)) {
    res.status(503).json({ error: "Python client environment is missing. Restore it using uv sync before running scenarios." });
    return;
  }
  let pending = active.get(id);
  if (!pending) {
    pending = queue.catch(() => undefined).then(() =>
      execute(python, [path.join(root, "scripts/tinkar_workbench.py"), String(id)], {
        cwd: root, timeout: 150_000, maxBuffer: 12 * 1024 * 1024,
      }).then(({ stdout }) => RunScenarioResponse.parse(JSON.parse(stdout))),
    );
    queue = pending;
    active.set(id, pending);
    // Handle rejection here as well as in every waiting request.
    void pending.finally(() => active.delete(id)).catch(() => undefined);
  }
  try {
    const result = await pending;
    res.set("Cache-Control", "no-store").json(result);
  } catch (err) {
    req.log.error({ err, scenarioId: id }, "Live DeX scenario failed");
    res.status(503).json({ error: "The live scenario could not complete. Check that Tinkar and the Python environment are running, then retry." });
  }
});

export default router;
