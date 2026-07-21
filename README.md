<p align="center">
  <img src="readme/logo.png" height="80" alt="Cascade logo">
</p>
<p align="center">
    <em>A compiled-transpiled strictly-typed programming language.</em>
</p>
<p align="center">
  <img src="https://img.shields.io/badge/status-active-brightgreen" alt="Project Status">
  <img src="https://img.shields.io/github/license/BFSDK/Cascade" alt="License">
  <img src="https://img.shields.io/github/v/release/BFSDK/Cascade?include_prereleases" alt="GitHub release (latest by date including pre-releases)">
  <img src="https://img.shields.io/github/last-commit/BFSDK/Cascade" alt="GitHub last commit">
</p>

---

**Cascade** is a strongly-typed programming language that transpiles directly into optimized Windows Batch (`.cmd` / `.bat`) scripts before compiling to .exe. It provides static type checking, clean function declarations, control flow structures, and modular imports without requiring complex runtime dependencies.

## Key Features
* **Static Type Checking** — Catches type mismatches and argument errors at compile time before execution.
* **Modern Syntax** — Supports structured functions, typed parameters, explicit return types, and clean variable definitions.
* **Batch Transpilation** — Output runs natively on any Windows command line environment without extra runtimes.
* **Standard Library Support** — Import pre-built standard modules using standard syntax.

## Code Examples

_Hello, world!_
```cascade
use <std>

func main() {
    std::echo("Hello, World!")
    std::pause()
}

```

*Functions and Type Checking*

```cascade
use <std>

func greeting(name : str, age : num) -> str {
    return "Hello, !name!! You are !age! years old."
}

pre func main() {
    set user_name : str = "John"
    set user_age : num = 14

    set message : str = greeting(user_name, user_age)
    std::echo(message)
    std::pause()
}

```

*Loops and Counter*

```cascade
use <std>

func main() {
    for i : 1 to 10 {
        writeln(i)
    }
    std::pause()
}

```

## Compilation & Usage

To compile a Cascade script (`.csc` or `.cas`) into executable .exe, run the transpiler CLI:

```powershell
csc script.csc

```

This generates a compiled `.cmd` file ready to run directly on Windows systems.

```

```
