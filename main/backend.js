// Backend process setup and management
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const config = require('./config');

let backendProcess = null;
let fileWatcher = null;
let restartTimeout = null;

// Watch backend files for changes and restart
function watchBackendFiles() {
  if (process.env.NODE_ENV !== 'development' || fileWatcher) return;

  const backendDir = path.join(__dirname, '..', 'backend');

  fileWatcher = fs.watch(backendDir, { recursive: true }, (eventType, filename) => {
    if (!filename || !filename.endsWith('.py')) return;
    if (filename.includes('venv') || filename.includes('__pycache__')) return;

    console.log(`Backend file changed: ${filename}`);

    // Debounce restart to avoid multiple rapid restarts
    if (restartTimeout) {
      clearTimeout(restartTimeout);
    }

    restartTimeout = setTimeout(() => {
      console.log('Restarting backend...');
      restartBackend();
    }, 500);
  });
}

// Start backendProcess and handle console logs
function startBackend() {
  // Always spawn the backend process
  const options = config.backend.stdio ? { stdio: config.backend.stdio } : {};
  backendProcess = spawn(config.backend.pythonCommand, config.backend.args, options);

  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend stdout: ${data}`);
  });

  backendProcess.stderr.on('data', (data) => {
    console.log(`Backend stderr: ${data}`);
  });

  backendProcess.on('error', (err) => {
    console.error(`Backend process error: ${err}`);
  });

  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
  });

  // Start watching for file changes in development
  watchBackendFiles();

  return backendProcess;
}

// Restart backend process
function restartBackend() {
  stopBackend();
  startBackend();
}

// Check if backendProcess exists, if so kill it
function stopBackend() {
  if (restartTimeout) {
    clearTimeout(restartTimeout);
    restartTimeout = null;
  }

  if (backendProcess) {
    // Check if process is still alive before killing
    if (!backendProcess.killed) {
      backendProcess.kill('SIGTERM');
      console.log('Backend process stopped');
    }
    backendProcess = null;
  }

  if (fileWatcher) {
    fileWatcher.close();
    fileWatcher = null;
  }
}

module.exports = {
  startBackend,
  stopBackend,
  restartBackend
};