"""
Project generator module.
Handles project folder creation and starter file generation.
"""

import os
from pathlib import Path
from typing import List
from src.logger import Logger
from src.error_handler import ProjectCreationError


class ProjectGenerator:
    """Generates project folder structure and starter files."""

    def __init__(self, logger: Logger):
        self.logger = logger

    def create_project_folder(self, project_path: str) -> bool:
        """Create project root folder."""
        try:
            Path(project_path).mkdir(parents=True, exist_ok=True)
            self.logger.success(f"Created project folder: {project_path}")
            return True
        except Exception as e:
            raise ProjectCreationError(f"Failed to create project folder: {e}")

    def create_folder_structure(
        self, project_path: str, project_type: str, language: str
    ) -> bool:
        """Create folder structure based on project type."""
        try:
            project_type = (project_type or "").lower()

            if project_type == "mobile":
                folders = ["src", "assets"]
            elif project_type == "backend":
                folders = [
                    "src",
                    "src/routes",
                    "src/controllers",
                    "src/models",
                    "src/middleware",
                    "src/config",
                ]
            elif project_type == "fullstack":
                folders = [
                    "src",
                    "public",
                    "src/routes",
                    "src/controllers",
                    "src/models",
                    "src/middleware",
                    "src/config",
                    "server",
                ]
            else:
                # Frontend default style scaffold.
                folders = ["src", "public"]

            for folder in folders:
                folder_path = os.path.join(project_path, folder)
                Path(folder_path).mkdir(parents=True, exist_ok=True)

            self.logger.step(f"Created folder structure for {project_type} project")
            return True

        except Exception as e:
            raise ProjectCreationError(f"Failed to create folder structure: {e}")

    def create_starter_files(
        self,
        project_path: str,
        project_name: str,
        language: str,
        project_type: str,
        frameworks: List[str],
        styling: List[str] = None,
    ) -> bool:
        """Create starter files based on project configuration."""
        try:
            styling = styling or []
            framework_set = {fw.lower() for fw in frameworks}
            ext = ".ts" if (language or "").lower() == "typescript" else ".js"
            project_type = (project_type or "").lower()

            if project_type == "mobile" or "react-native" in framework_set:
                self._create_mobile_files(project_path, ext)
            elif project_type == "frontend":
                self._create_frontend_index(project_path, ext, framework_set, styling)
            elif project_type == "backend":
                self._create_backend_index(project_path, ext, framework_set)
            elif project_type == "fullstack":
                self._create_fullstack_files(project_path, ext, project_name, framework_set)

            self._create_gitignore(project_path)
            self._create_env_example(project_path)

            self.logger.step("Created starter files")
            return True

        except Exception as e:
            raise ProjectCreationError(f"Failed to create starter files: {e}")

    def _create_frontend_index(
        self,
        project_path: str,
        ext: str,
        frameworks: set,
        styling: List[str] = None,
    ) -> None:
        """Create frontend starter files for selected framework."""
        styling = styling or []
        is_tailwind = "tailwind" in [s.lower() for s in styling]

        if "next" in frameworks:
            self._create_next_starter(project_path, ext, is_tailwind)
            return

        if "react" in frameworks:
            self._create_react_starter(project_path, ext, is_tailwind)
            return

        if "vue" in frameworks:
            self._create_vue_starter(project_path, ext, is_tailwind)
            return

        if "svelte" in frameworks:
            self._create_svelte_starter(project_path, ext, is_tailwind)
            return

        file_path = os.path.join(project_path, f"src/index{ext}")
        content = f'''// {ext[1:].upper()} starter file
console.log('Project initialized successfully!');

// Start building your amazing project here!
'''
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        self._create_index_html(project_path, f"/src/index{ext}", mount_id="root")

    def _create_react_starter(self, project_path: str, ext: str, is_tailwind: bool) -> None:
        """Create React starter files."""
        entry_ext = ".tsx" if ext == ".ts" else ".jsx"
        entry_path = os.path.join(project_path, f"src/main{entry_ext}")
        app_path = os.path.join(project_path, f"src/App{entry_ext}")
        styles_path = os.path.join(project_path, "src/index.css")

        if entry_ext == ".tsx":
            entry_content = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''
        else:
            entry_content = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''

        if is_tailwind:
            app_content = '''function App() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto flex max-w-4xl flex-col items-start gap-6 px-6 py-20">
        <p className="rounded-full border border-cyan-400/40 bg-cyan-400/10 px-3 py-1 text-xs uppercase tracking-[0.2em] text-cyan-300">
          React Starter
        </p>
        <h1 className="text-4xl font-bold leading-tight md:text-6xl">It works.</h1>
        <p className="max-w-2xl text-lg text-slate-300">
          Generated by the setup CLI with React and Tailwind.
        </p>
      </section>
    </main>
  );
}

export default App;
'''
            styles_content = '''@import "tailwindcss";

:root {
  font-family: Inter, system-ui, sans-serif;
}

body {
  margin: 0;
}
'''
        else:
            app_content = '''function App() {
  return (
    <main style={{ minHeight: '100vh', padding: 24 }}>
      <h1>React Starter</h1>
      <p>Generated by the setup CLI.</p>
    </main>
  );
}

export default App;
'''
            styles_content = '''body {
  margin: 0;
  font-family: Inter, system-ui, sans-serif;
}
'''

        with open(entry_path, "w", encoding="utf-8") as f:
            f.write(entry_content)
        with open(app_path, "w", encoding="utf-8") as f:
            f.write(app_content)
        with open(styles_path, "w", encoding="utf-8") as f:
            f.write(styles_content)

        if entry_ext == ".tsx":
            vite_env_path = os.path.join(project_path, "src/vite-env.d.ts")
            vite_env_content = '''/// <reference types="vite/client" />

declare module "*.css";
'''
            with open(vite_env_path, "w", encoding="utf-8") as f:
                f.write(vite_env_content)

        self._create_index_html(project_path, f"/src/main{entry_ext}", mount_id="root")

    def _create_vue_starter(self, project_path: str, ext: str, is_tailwind: bool) -> None:
        """Create Vue starter files."""
        entry_ext = ".ts" if ext == ".ts" else ".js"
        entry_path = os.path.join(project_path, f"src/main{entry_ext}")
        app_path = os.path.join(project_path, "src/App.vue")
        style_path = os.path.join(project_path, "src/style.css")

        entry_content = f'''import {{ createApp }} from 'vue';
import App from './App.vue';
import './style.css';

createApp(App).mount('#app');
'''

        app_content = '''<template>
  <main class="app">
    <h1>Vue Starter</h1>
    <p>Generated by the setup CLI.</p>
  </main>
</template>
'''

        if is_tailwind:
            style_content = '@import "tailwindcss";\n\nbody {\n  margin: 0;\n  font-family: Inter, system-ui, sans-serif;\n}\n'
        else:
            style_content = 'body {\n  margin: 0;\n  font-family: Inter, system-ui, sans-serif;\n}\n.app {\n  padding: 24px;\n}\n'

        with open(entry_path, "w", encoding="utf-8") as f:
            f.write(entry_content)
        with open(app_path, "w", encoding="utf-8") as f:
            f.write(app_content)
        with open(style_path, "w", encoding="utf-8") as f:
            f.write(style_content)

        if entry_ext == ".ts":
          env_path = os.path.join(project_path, "src", "vue-env.d.ts")
          env_content = '''declare module '*.vue' {
      import type { DefineComponent } from 'vue';
      const component: DefineComponent<{}, {}, any>;
      export default component;
    }
    '''
          with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_content)

        self._create_index_html(project_path, f"/src/main{entry_ext}", mount_id="app")

    def _create_svelte_starter(self, project_path: str, ext: str, is_tailwind: bool) -> None:
        """Create Svelte starter files."""
        entry_ext = ".ts" if ext == ".ts" else ".js"
        entry_path = os.path.join(project_path, f"src/main{entry_ext}")
        app_path = os.path.join(project_path, "src/App.svelte")
        style_path = os.path.join(project_path, "src/app.css")

        if entry_ext == ".ts":
            entry_content = '''import './app.css';
import { mount } from 'svelte';
import App from './App.svelte';

const app = mount(App, {
  target: document.getElementById('app')!,
});

export default app;
'''
        else:
            entry_content = '''import './app.css';
import { mount } from 'svelte';
import App from './App.svelte';

const app = mount(App, {
  target: document.getElementById('app'),
});

export default app;
'''

        app_content = '''<main class="app">
  <h1>Svelte Starter</h1>
  <p>Generated by the setup CLI.</p>
</main>
'''

        if is_tailwind:
            style_content = '@import "tailwindcss";\n\nbody {\n  margin: 0;\n  font-family: Inter, system-ui, sans-serif;\n}\n'
        else:
            style_content = 'body {\n  margin: 0;\n  font-family: Inter, system-ui, sans-serif;\n}\n.app {\n  padding: 24px;\n}\n'

        with open(entry_path, "w", encoding="utf-8") as f:
            f.write(entry_content)
        with open(app_path, "w", encoding="utf-8") as f:
            f.write(app_content)
        with open(style_path, "w", encoding="utf-8") as f:
            f.write(style_content)

        if entry_ext == ".ts":
          env_path = os.path.join(project_path, "src", "svelte-env.d.ts")
          env_content = "declare module '*.svelte';\n"
          with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_content)

        self._create_index_html(project_path, f"/src/main{entry_ext}", mount_id="app")

    def _create_next_starter(self, project_path: str, ext: str, is_tailwind: bool) -> None:
        """Create Next.js app router starter files."""
        page_ext = ".tsx" if ext == ".ts" else ".js"
        app_dir = os.path.join(project_path, "src", "app")
        Path(app_dir).mkdir(parents=True, exist_ok=True)

        layout_path = os.path.join(app_dir, f"layout{page_ext}")
        page_path = os.path.join(app_dir, f"page{page_ext}")
        globals_css_path = os.path.join(app_dir, "globals.css")

        if page_ext == ".tsx":
            layout_content = '''import './globals.css';
import type { ReactNode } from 'react';

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
'''
            page_content = '''export default function HomePage() {
  return (
    <main style={{ padding: 24 }}>
      <h1>Next.js Starter</h1>
      <p>Generated by the setup CLI.</p>
    </main>
  );
}
'''

            next_env_path = os.path.join(project_path, "next-env.d.ts")
            next_env_content = '''/// <reference types="next" />
/// <reference types="next/image-types/global" />

// NOTE: This file should not be edited.
'''
            with open(next_env_path, "w", encoding="utf-8") as f:
                f.write(next_env_content)
        else:
            layout_content = '''import './globals.css';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
'''
            page_content = '''export default function HomePage() {
  return (
    <main style={{ padding: 24 }}>
      <h1>Next.js Starter</h1>
      <p>Generated by the setup CLI.</p>
    </main>
  );
}
'''

        if is_tailwind:
            globals_css_content = '@import "tailwindcss";\n\nbody {\n  margin: 0;\n}\n'
        else:
            globals_css_content = 'body {\n  margin: 0;\n  font-family: Inter, system-ui, sans-serif;\n}\n'

        with open(layout_path, "w", encoding="utf-8") as f:
            f.write(layout_content)
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(page_content)
        with open(globals_css_path, "w", encoding="utf-8") as f:
            f.write(globals_css_content)

    def _create_mobile_files(self, project_path: str, ext: str) -> None:
        """Create mobile (React Native/Expo) starter files."""
        app_ext = ".tsx" if ext == ".ts" else ".js"
        app_path = os.path.join(project_path, f"App{app_ext}")
        app_json_path = os.path.join(project_path, "app.json")
        babel_config_path = os.path.join(project_path, "babel.config.js")

        if app_ext == ".tsx":
            app_content = '''import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View } from 'react-native';

export default function App() {
  return (
    <View style={styles.container}>
      <Text>React Native Starter</Text>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});
'''
        else:
            app_content = '''import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View } from 'react-native';

export default function App() {
  return (
    <View style={styles.container}>
      <Text>React Native Starter</Text>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});
'''

        app_json_content = '''{
  "expo": {
    "name": "mobile-app",
    "slug": "mobile-app",
    "version": "1.0.0"
  }
}
'''

        babel_config_content = '''module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
  };
};
'''

        with open(app_path, "w", encoding="utf-8") as f:
            f.write(app_content)
        with open(app_json_path, "w", encoding="utf-8") as f:
            f.write(app_json_content)
        with open(babel_config_path, "w", encoding="utf-8") as f:
            f.write(babel_config_content)

    def _create_index_html(
        self,
        project_path: str,
        entry_file: str,
        mount_id: str = "root",
    ) -> None:
        """Create index.html for Vite-based frontend projects."""
        index_html_path = os.path.join(project_path, "index.html")
        content = f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>COCO_CODE CLI App</title>
  </head>
  <body>
    <div id="{mount_id}"></div>
    <script type="module" src="{entry_file}"></script>
  </body>
</html>
'''

        with open(index_html_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _create_backend_index(
        self, project_path: str, ext: str, frameworks: set
    ) -> None:
        """Create backend server/app starter file."""
        if "fastapi" in frameworks:
            file_path = os.path.join(project_path, "src/main.py")
            content = '''from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}
'''
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            req_path = os.path.join(project_path, "requirements.txt")
            with open(req_path, "w", encoding="utf-8") as f:
                f.write("fastapi\nuvicorn\n")
            return

        if "django" in frameworks:
            file_path = os.path.join(project_path, "src/manage.py")
            content = '''#!/usr/bin/env python
"""Django starter entrypoint.
Run: django-admin startproject config .
Then use: python src/manage.py runserver
"""

print("Initialize Django project: django-admin startproject config .")
'''
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            req_path = os.path.join(project_path, "requirements.txt")
            with open(req_path, "w", encoding="utf-8") as f:
                f.write("django\n")
            return

        file_path = os.path.join(project_path, f"src/server{ext}")

        if "express" in frameworks:
            content = '''import express from 'express';
import cors from 'cors';
import helmet from 'helmet';

const app = express();
const PORT = process.env.PORT || 5000;

app.use(helmet());
app.use(cors());
app.use(express.json());

app.get('/api/health', (req, res) => {
  res.json({ status: 'Server is running!' });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
'''
        else:
            content = '''// Backend server starter
const PORT = process.env.PORT || 5000;
console.log(`Server starting on port ${PORT}`);
'''

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _create_fullstack_files(
        self,
        project_path: str,
        ext: str,
        project_name: str,
        frameworks: set,
    ) -> None:
        """Create fullstack starter files."""
        self._create_frontend_index(project_path, ext, frameworks, [])

        # For Next.js fullstack we avoid adding an extra standalone server file by default.
        if "next" in frameworks:
            api_dir = os.path.join(project_path, "src", "app", "api", "health")
            Path(api_dir).mkdir(parents=True, exist_ok=True)
            route_ext = ".ts" if ext == ".ts" else ".js"
            route_path = os.path.join(api_dir, f"route{route_ext}")
            route_content = '''export async function GET() {
  return Response.json({ status: 'ok' });
}
'''
            with open(route_path, "w", encoding="utf-8") as f:
                f.write(route_content)
            return

        self._create_backend_index(project_path, ext, frameworks)

    def _create_gitignore(self, project_path: str) -> None:
        """Create .gitignore file."""
        gitignore_path = os.path.join(project_path, ".gitignore")
        content = '''# Dependencies
node_modules/
npm-debug.log
yarn-error.log
pnpm-debug.log

# Python
__pycache__/
*.pyc
.venv/
venv/

# Environment variables
.env
.env.local
.env.*.local

# Build outputs
dist/
build/
.next/
out/

# Expo
.expo/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Testing
coverage/
.nyc_output/

# Misc
.cache/
.log
'''
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _create_env_example(self, project_path: str) -> None:
        """Create .env.example file."""
        env_path = os.path.join(project_path, ".env.example")
        content = '''# Environment Configuration Example
# Copy this file to .env and fill in your values

# Server
PORT=5000
NODE_ENV=development

# Database
DATABASE_URL=your_database_url_here

# API Keys (if needed)
API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
'''
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(content)

