const { spawn } = require('child_process');
const path = require('path');
const config = require('./config');

let backendProcess = null;

function startBackend() {
  // Start the FastAPI backend
  backendProcess = spawn(config.backend.pythonCommand, config.backend.args, {
    cwd: path.join(__dirname, '..'),
    ...config.backend.stdio && { stdio: config.backend.stdio }
  });

  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend stdout: ${data}`);
  });

  backendProcess.stderr.on('data', (data) => {
    console.log(`Backend stderr: ${data}`);
  });

  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
  });

  return backendProcess;
}

function stopBackend() {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
    console.log('Backend process stopped');
  }
}

function getBackendProcess() {
  return backendProcess;
}

module.exports = {
  startBackend,
  stopBackend,
  getBackendProcess
};