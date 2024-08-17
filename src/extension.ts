import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

interface LogEntry {
    timestamp: number;
    event: 'suggestion' | 'acceptance';
    code: string;
}

let log: LogEntry[] = [];
let lastTypingTime: number = 0;
let suggestionBuffer: string = '';

export function activate(context: vscode.ExtensionContext) {
    console.log('Activating extension...');

    const logDirPath = path.join(context.globalStoragePath, 'copilot_usage_log');
    const logFilePath = path.join(logDirPath, 'copilot_usage_log.json');
    
    console.log('Log directory path:', logDirPath);
    console.log('Log file path:', logFilePath);

    // Ensure the log directory exists
    if (!fs.existsSync(logDirPath)) {
        fs.mkdirSync(logDirPath, { recursive: true });
        console.log('Created log directory.');
    }

    // Load existing log entries
    if (fs.existsSync(logFilePath)) {
        const logData = fs.readFileSync(logFilePath, 'utf8');
        log = JSON.parse(logData);
        console.log('Loaded existing log data.');
    } else {
        fs.writeFileSync(logFilePath, JSON.stringify([]));
        console.log('Created log file.');
    }

    const disposable = vscode.commands.registerCommand('extension.startLogging', () => {
        console.log('Command executed: Start Copilot Usage Logging');
        vscode.window.showInformationMessage('Copilot usage logging started.');

        vscode.workspace.onDidChangeTextDocument(event => {
            event.contentChanges.forEach(change => {
                lastTypingTime = Date.now();
                suggestionBuffer += change.text;

                // If there's a pause in typing, log it as a suggestion event
                setTimeout(() => {
                    if (Date.now() - lastTypingTime >= 1000 && suggestionBuffer.trim().length > 0) {  // 1 second pause
                        logSuggestion(suggestionBuffer);
                        suggestionBuffer = '';  // Reset buffer after logging
                    }
                }, 1000);  // 1 second wait to detect pause
            });
        });

        vscode.workspace.onDidSaveTextDocument(document => {
            const acceptedCode = document.getText();
            logAcceptance(acceptedCode);
        });

        // Detect when the user accepts a suggestion (typically by pressing Tab or Enter)
        vscode.commands.registerCommand('type', (args) => {
            if (args.text === '\t' || args.text === '\n') {
                const activeEditor = vscode.window.activeTextEditor;
                if (activeEditor) {
                    const acceptedText = activeEditor.document.getText(activeEditor.selection);
                    logAcceptance(acceptedText);
                }
            }
            return vscode.commands.executeCommand('default:type', args);
        });

        function logSuggestion(suggestion: string) {
            console.log('Logging suggestion:', suggestion);
            log.push({ timestamp: Date.now(), event: 'suggestion', code: suggestion });
            saveLog();
        }

        function logAcceptance(acceptedCode: string) {
            console.log('Logging acceptance:', acceptedCode);
            log.push({ timestamp: Date.now(), event: 'acceptance', code: acceptedCode });
            saveLog();
        }

        function saveLog() {
            console.log('Saving log...');
            fs.writeFileSync(logFilePath, JSON.stringify(log, null, 2));
        }
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {
    console.log('Deactivating extension...');
}
