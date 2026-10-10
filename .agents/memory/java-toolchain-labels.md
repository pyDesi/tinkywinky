---
name: Java toolchain labels
description: GraalVM module labels can be mistaken for Java language versions.
---

Verify the actual JDK with `java -version`; do not interpret a GraalVM module's version label as a Java language version.

**Why:** The Java module labeled GraalVM 22.3 installed an older Java language runtime than the label suggested and could not meet the service's compiler requirement.

**How to apply:** Check both the project's compiler release and the selected executable's Java version before attempting a build. When using an alternate official toolchain, select it explicitly through JAVA_HOME and PATH and verify its checksum.
