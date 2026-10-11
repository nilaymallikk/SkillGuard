# File that identifies a skill and carries its front-matter manifest
SKILL_MANIFEST_NAME: str = "SKILL.md"

# Extensions whose contents can execute; drives the 1.3x risk multiplier
EXECUTABLE_EXTENSIONS: frozenset[str] = frozenset(
    {".py", ".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs", ".ts", ".rb", ".pl", ".ps1", ".bat"}
)
