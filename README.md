# COCO_CODE CLI

A powerful, extensible Python CLI tool that generates complete web projects dynamically. No hardcoding, pure dynamic configuration!

## Features

**Dynamic Package Selection**

- Select from predefined frameworks, styling, databases, and utilities
- Add custom npm packages on the fly
- Smart package dependency resolution

**Automatic Project Structure**

- Create proper folder hierarchies for different project types
- Generate starter files based on selected frameworks
- Support for frontend, backend, fullstack, and mobile projects

**Configuration Generation**

- `tsconfig.json` for TypeScript projects
- `tailwind.config.js` and `postcss.config.js` for Tailwind CSS
- `vite.config.js` for Vite builds
- `.gitignore` and `.env.example` templates
- Intelligent script generation in package.json

**Package Management**

- Automatic npm initialization
- Smart dependency installation (dev vs production)
- Duplicate detection and removal
- Framework package mapping

**Extensibility**

- All frameworks/libraries defined in `config.json`
- Add new packages without touching Python code
- Easy to customize for your team's needs

## Installation & Setup

### Prerequisites

- Python 3.7+
- Node.js and npm installed and in PATH
- Windows, macOS, or Linux

### Quick Start

```bash
# Clone the project
cd COCO_CODE

# Run the CLI
python main.py
```

## Public GitHub Launch

To publish COCO_CODE as a public repository and grow adoption quickly, follow:

- [GITHUB_LAUNCH.md](GITHUB_LAUNCH.md)

That guide includes:

- Local folder rename to COCO_CODE
- Public GitHub repo creation steps
- Release and visibility checklist
- A 30-day growth plan for star velocity

## Usage Guide

### Basic Workflow

1. **Run the tool**

   ```bash
   python main.py
   ```

2. **Answer the prompts**
   - Project name (e.g., `my-react-app`)
   - Project type (frontend, backend, fullstack, mobile)
   - Language (JavaScript or TypeScript)

3. **Select packages**
   - Choose from available frameworks
   - Select styling solutions
   - Pick database options
   - Add utilities and tools
   - Option to add custom npm packages

4. **Review and confirm**
   - Verify your selections
   - Confirm the package list
   - Let the tool create your project!

### Example Session

```
 COCO_CODE CLI
=================

 Project name: my-chat-app
Select project type:
  1. frontend
  2. backend
  3. fullstack
  4. mobile
Select (1-4): 3

Select language:
  1. javascript
  2. typescript
Select (1-2): 2

 Available Frameworks:
  1. react - React library for building UI
  2. next - Next.js React framework
  3. vue - Vue.js framework
  4. express - Express.js backend framework

Select frameworks: next express

 Available Styling Options:
  1. tailwind - Tailwind CSS utility framework
  2. scss - Sass CSS preprocessor

Select styling: tailwind

 Available Databases:
  1. mongodb - MongoDB with Mongoose
  2. firebase - Firebase backend
  3. postgresql - PostgreSQL with Sequelize

Select databases: mongodb

 Available Utilities:
  1. axios - HTTP client library
  2. dotenv - Environment variable management
  3. typescript - TypeScript support

Select utilities: axios dotenv typescript

 Custom packages: socket.io
```

## Configuration Structure

### Understanding `config.json`

The configuration file defines all available packages and their npm equivalents:

```json
{
  "frameworks": {
    "react": {
      "packages": ["react", "react-dom"],
      "devDependencies": ["@types/react", "@types/react-dom"],
      "description": "React library for building UI"
    }
  },
  "styling": {
    "tailwind": {
      "packages": ["tailwindcss", "postcss", "autoprefixer"],
      "devDependencies": [],
      "description": "Tailwind CSS utility framework"
    }
  },
  "databases": { ... },
  "utilities": { ... },
  "projectTemplates": { ... }
}
```

### Adding New Frameworks

1. Open `config.json`
2. Add to the appropriate category:
   ```json
   "yourframework": {
     "packages": ["npm-package-1", "npm-package-2"],
     "devDependencies": ["dev-package-1"],
     "description": "Your framework description",
     "configFile": "optional-config-file.js"
   }
   ```
3. Save and the tool will automatically recognize it!

## Generated Project Structure

### Frontend Project

```
my-react-app/
 src/
    components/
    pages/
    styles/
    index.tsx
 public/
 package.json
 tsconfig.json
 tailwind.config.js
 postcss.config.js
 vite.config.js
 .gitignore
 .env.example
```

### Backend Project

```
my-api/
 src/
    routes/
    controllers/
    models/
    middleware/
    config/
    server.ts
 public/
 package.json
 tsconfig.json
 .gitignore
 .env.example
```

### Fullstack Project

```
my-app/
 src/
    components/
    pages/
    styles/
    routes/
    controllers/
    models/
    index.tsx
 server/
 package.json
 tsconfig.json
 .gitignore
 .env.example
```

## Advanced Features

### Custom Scripts in package.json

The tool automatically generates appropriate scripts:

**For React/Vue projects:**

```json
{
  "dev": "vite",
  "build": "vite build",
  "preview": "vite preview",
  "typecheck": "tsc --noEmit"
}
```

**For Next.js projects:**

```json
{
  "dev": "next dev",
  "build": "next build",
  "start": "next start"
}
```

**For Express projects:**

```json
{
  "dev": "ts-node src/server.ts",
  "build": "tsc",
  "start": "node dist/server.js"
}
```

### TypeScript Configuration

When TypeScript is selected:

- Generates `tsconfig.json` with strict type checking
- Adds TypeScript and type definitions to devDependencies
- Configures JSX support for React frameworks
- Enables source maps for debugging

### Environment Variables

A `.env.example` file is created with common variables:

```
PORT=5000
NODE_ENV=development
DATABASE_URL=your_database_url_here
API_KEY=your_api_key_here
```

Copy to `.env.local` and fill in your actual values.

## Project Structure

```
COCO_CODE/
 main.py                    # Entry point
 config.json                # Framework & package configuration
 README.md                  # This file
 EXAMPLES.md               # Usage examples
 src/
     cli.py                # Interactive CLI interface
     logger.py             # Logging system
     validator.py          # Input validation
     error_handler.py      # Error handling
     package_manager.py    # Package resolution
     package_installer.py  # npm installation
     project_generator.py  # Folder & file creation
     config_generator.py   # Config file generation
```

## Module Overview

### `cli.py`

Interactive CLI that collects user input and orchestrates the setup process.

### `logger.py`

Formatted console output with progress indicators and colored messages.

### `validator.py`

Input validation for project names, selections, and library inputs.

### `error_handler.py`

Graceful error handling with custom exceptions and error context.

### `package_manager.py`

Resolves user selections to actual npm packages using config.json.

### `package_installer.py`

Handles npm operations: init, install, and dependency management.

### `project_generator.py`

Creates project folder structure and starter files based on type.

### `config_generator.py`

Generates configuration files: tsconfig.json, tailwind.config.js, etc.

## Troubleshooting

### "npm is not installed"

- Install Node.js from https://nodejs.org/
- Add npm to PATH
- Restart your terminal

### "Configuration file not found"

- Ensure `config.json` is in the same directory as `main.py`
- Check the file exists and is valid JSON

### "Package installation failed"

- Check internet connection
- Try `npm cache clean --force` then run again
- Some packages may have platform-specific issues

### Project name validation fails

- Names must start with a letter or underscore
- Only alphanumeric, hyphens, and underscores allowed
- Must be 2-50 characters

## Examples

### React + Tailwind Frontend

```
Project name: my-portfolio
Type: frontend
Language: typescript
Frameworks: react
Styling: tailwind
Utilities: axios typescript
```

### Next.js Fullstack App

```
Project name: nextjs-todo
Type: fullstack
Language: typescript
Frameworks: next
Styling: tailwind
Database: mongodb
Utilities: axios dotenv typescript
```

### Express Backend API

```
Project name: rest-api
Type: backend
Language: typescript
Frameworks: express
Database: postgresql
Utilities: dotenv jest eslint typescript
```

## Contributing

Want to add support for new frameworks?

1. **Update `config.json`**

   ```json
   "newframework": {
     "packages": ["npm-package"],
     "devDependencies": ["dev-package"],
     "description": "Your description"
   }
   ```

2. **Optional: Add template files**
   - Edit `project_generator.py` to add starter file templates

3. **Test your changes**
   ```bash
   python main.py
   ```

## Future Enhancements

**AI Package Suggestions** - Describe your project, get smart recommendations
**Project Analytics** - Track which frameworks are most popular
**Remote Config** - Load configurations from a server
**Template Library** - Download community templates
**Integration Templates** - Auth, payments, search, etc.

## License

MIT - Create amazing projects freely!

## Support

- Check [EXAMPLES.md](EXAMPLES.md) for more usage examples
- Follow [GITHUB_LAUNCH.md](GITHUB_LAUNCH.md) for public release and growth
- Review module docstrings for detailed API documentation
- Modify `config.json` to customize for your needs

## Quick Reference

| Command              | Purpose                      |
| -------------------- | ---------------------------- |
| `python main.py`     | Run the interactive setup    |
| Edit `config.json`   | Add/remove framework support |
| Check `src/` modules | Understand the architecture  |
| Review logs          | Debug setup issues           |

---

**Happy Building! **

Made with by developers, for developers
