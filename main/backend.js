// Backend process setup and management
const { spawn } = require('child_process');
const config = require('./config');

let backendProcess = null;

// Start backendProcess and handle console logs
function startBackend() {
  if (config.backend.stdio) {
    backendProcess = spawn(config.backend.pythonCommand, config.backend.args, {stdio: config.backend.stdio});
  }

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

// Check if backendProcess exists, if so kill it
function stopBackend() {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
    console.log('Backend process stopped');
  }
}

// Getter for backendProcess
function getBackendProcess() {
  return backendProcess;
}

module.exports = {
  startBackend,
  stopBackend,
  getBackendProcess
};