#  Contributing Guide

Thank you for your interest in improving the COCO_CODE CLI!

## How to Contribute

### 1. Adding a New Framework

The easiest way to extend the tool without touching Python code!

#### Step 1: Update config.json

```json
{
  "frameworks": {
    ...
    "astro": {
      "packages": ["astro"],
      "devDependencies": ["@astrojs/react"],
      "description": "Astro the web framework",
      "configFile": "astro.config.mjs"
    }
  }
}
```

**Fields:**

- `packages`: Production dependencies (installed without --save-dev)
- `devDependencies`: Development dependencies (installed with --save-dev)
- `description`: Shown in CLI menu
- `configFile`: Optional - helps generate config file

#### Step 2: Test it

```bash
python main.py
# Select your new framework when prompted
```

### 2. Adding Styling Options

Add CSS frameworks and preprocessors:

```json
{
  "styling": {
    ...
    "unocss": {
      "packages": ["unocss"],
      "devDependencies": [],
      "description": "Instant on-demand atomic CSS engine"
    }
  }
}
```

### 3. Adding Database Support

```json
{
  "databases": {
    ...
    "prisma": {
      "packages": ["@prisma/client"],
      "devDependencies": ["prisma"],
      "description": "Modern ORM for Node.js and TypeScript"
    }
  }
}
```

### 4. Adding Utilities/Tools

```json
{
  "utilities": {
    ...
    "vitest": {
      "packages": [],
      "devDependencies": ["vitest"],
      "description": "Unit testing framework powered by Vite"
    }
  }
}
```

## Advanced: Modifying Python Code

### Adding Config File Generation

If a new framework needs special config file generation:

**1. Add to config_generator.py:**

```python
def generate_astro_config(self, project_path: str) -> bool:
    """Generate astro.config.mjs"""
    config_path = os.path.join(project_path, "astro.config.mjs")

    content = '''import { defineConfig } from 'astro/config';

export default defineConfig({
  // Configuration options here
});
'''

    try:
        with open(config_path, "w") as f:
            f.write(content)
        self.logger.step("Generated astro.config.mjs")
        return True
    except Exception as e:
        raise FileOperationError(f"Failed to generate astro config: {e}")
```

**2. Call it in CLI:**

```python
# In cli.py execute_setup() method
if "astro" in selections.get("frameworks", []):
    self.config_generator.generate_astro_config(project_path)
```

### Adding Starter File Templates

Modify `project_generator.py` to add framework-specific starter files:

```python
def _create_frontend_index(self, project_path: str, ext: str, frameworks: List[str]) -> None:
    """Create frontend index file"""
    file_path = os.path.join(project_path, f"src/index{ext}")

    if "astro" in frameworks:
        content = '''---
// Astro component (stateless by default)
import Layout from '../layouts/Layout.astro';
---

<Layout title="Welcome to Astro.">
  <h1>Welcome to Astro</h1>
  <p>Learn about Astro on their docs</p>
</Layout>
'''
    elif "react" in frameworks:
        # ... existing code
```

## Code Organization

```
src/
 cli.py                 # Main CLI interface
 logger.py              # Logging utilities
 validator.py           # Input validation
 error_handler.py       # Exception handling
 package_manager.py     # Package resolution
 package_installer.py   # npm operations
 project_generator.py   # File/folder creation
 config_generator.py    # Config file generation
```

### When to Modify Each File

| File                 | Purpose           | When to Edit            |
| -------------------- | ----------------- | ----------------------- |
| config.json          | Package mappings  | Adding new frameworks   |
| cli.py               | User interaction  | Changing prompts/flow   |
| config_generator.py  | Config generation | New config file support |
| project_generator.py | File creation     | New starter files       |
| package_installer.py | npm operations    | Changing npm behavior   |
| logger.py            | Console output    | Changing log format     |
| validator.py         | Input validation  | Changing rules          |

## Testing Your Changes

### Manual Testing

1. Make your changes
2. Run the tool:
   ```bash
   python main.py
   ```
3. Test your new option works end-to-end
4. Verify generated files are correct

### Testing Specific Scenarios

```bash
# Test TypeScript + Tailwind + React
# Answer: react, tailwind, typescript

# Test Backend + PostgreSQL
# Answer: backend, typescript, express, postgresql

# Test Custom Packages
# Answer: any selection + custom packages
```

## Code Style Guidelines

### Python Conventions

- Use 4-space indentation
- Follow PEP 8 style guide
- Add docstrings to all functions:

  ```python
  def my_function(arg1: str) -> bool:
      """
      Short description.

      Args:
          arg1: Description of argument

      Returns:
          Description of return value
      """
      pass
  ```

### Logging

Always use the logger from imports:

```python
self.logger.success("Operation completed")
self.logger.error("Something failed")
self.logger.step("Processing step")
self.logger.debug("Debug info") # Only shows in verbose mode
```

### Error Handling

Use custom exceptions from error_handler.py:

```python
try:
    result = some_operation()
except Exception as e:
    raise PackageInstallationError(f"Failed to install: {e}")
```

## Pull Request Process

1. **Fork the repository** (if using GitHub)
2. **Create a feature branch**
   ```bash
   git checkout -b feature/add-astro-support
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Update documentation**
6. **Submit a pull request** with:
   - Clear title: "Add Astro framework support"
   - Description of changes
   - Steps to test
   - Screenshots if UI changed

## Reporting Issues

If you find a bug:

1. **Check if it's already reported** in Issues
2. **Create a detailed issue** with:
   - Clear title
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Python version
   - Node.js version

Example:

```
Title: TypeError when selecting multiple databases

Steps:
1. Run main.py
2. Select project type: fullstack
3. Select databases: mongodb postgresql
4. Continue with setup

Error:
TypeError: unsupported operand type(s) for +: 'dict' and 'dict'
```

## Feature Requests

Have an idea? Create an issue with:

```
Title: [FEATURE] AI-powered framework suggestions

Description:
When user describes their project, suggest frameworks automatically.

Example:
"I want to build a real-time chat app"
 Suggests: next, socket.io, tailwind, mongodb, redis
```

## Documentation Updates

### Updating README.md

If you add a new framework:

1. Update the "Adding New Frameworks" section
2. Add it to example sessions
3. Test that examples still work

### Updating config.json Comments

Consider adding brief comments:

```json
{
  "frameworks": {
    "astro": {
      "packages": ["astro"],
      "devDependencies": ["@astrojs/react"],
      "description": "Static site generator for content-heavy sites"
    }
  }
}
```

## Common Patterns

### Adding a New Framework Category

1. Add to config.json structure:

   ```json
   {
     "cms": {
       "contentful": { ... },
       "strapi": { ... }
     }
   }
   ```

2. Update package_manager.py to recognize it

3. Update config_generator.py if special config needed

4. Update CLI prompts in cli.py

### Conditional Configuration

Generate config files only if needed:

```python
if "tailwind" in selections.get("styling", []):
    self.config_generator.generate_tailwind_config(...)

if language.lower() == "typescript":
    self.config_generator.generate_tsconfig(...)
```

## Questions?

- Check existing issues for answers
- Read through the codebase
- Check module docstrings
- Review EXAMPLES.md for usage patterns

## Thank You!

Your contributions make this tool better for everyone. Whether it's fixing bugs, adding features, or improving documentation, your help is appreciated!

---

**Happy Contributing!** 


