import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

/**
 * Resolve project assets relative to the module, not the launch directory.
 * Source modules and the bundled dist/index.mjs both live below the workspace.
 */
export function resolveWorkspaceRoot(moduleUrl: string = import.meta.url): string {
  let directory = path.dirname(fileURLToPath(moduleUrl));
  while (true) {
    if (
      existsSync(path.join(directory, "pnpm-workspace.yaml")) &&
      existsSync(path.join(directory, "scripts/tinkar-scenarios.json"))
    ) {
      return directory;
    }
    const parent = path.dirname(directory);
    if (parent === directory) {
      throw new Error(
        "Cannot locate the Tinkar workspace. Include pnpm-workspace.yaml and scripts/tinkar-scenarios.json in the published application.",
      );
    }
    directory = parent;
  }
}
