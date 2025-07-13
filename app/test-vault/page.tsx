"use client"

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Shield, Database, CheckCircle, AlertCircle, Loader2, Play, Zap } from 'lucide-react';
import { toast } from 'sonner';

interface TestResult {
  success: boolean;
  message: string;
  testResults?: Record<string, boolean>;
  details?: Record<string, any>;
  error?: string;
}

interface HealthCheck {
  ready: boolean;
  vault?: {
    available: boolean;
    version: string;
  };
  functions?: {
    required: string[];
    available: string[];
    missing: string[];
  };
  error?: string;
}

export default function TestVaultPage() {
  const [isRunningTest, setIsRunningTest] = useState(false);
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [healthCheck, setHealthCheck] = useState<HealthCheck | null>(null);
  const [isLoadingHealth, setIsLoadingHealth] = useState(false);

  const runHealthCheck = async () => {
    setIsLoadingHealth(true);
    try {
      const response = await fetch('/api/test-vault', {
        method: 'GET'
      });

      const data = await response.json();
      setHealthCheck(data);

      if (data.ready) {
        toast.success('System ready for testing!');
      } else {
        toast.error('System not ready: ' + (data.error || 'Unknown issue'));
      }
    } catch (error) {
      console.error('Health check failed:', error);
      toast.error('Health check failed: ' + (error as Error).message);
    } finally {
      setIsLoadingHealth(false);
    }
  };

  const runVaultTest = async () => {
    setIsRunningTest(true);
    setTestResult(null);
    
    try {
      const response = await fetch('/api/test-vault', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      setTestResult(data);

      if (data.success) {
        toast.success('All vault tests passed! 🎉');
      } else {
        toast.error('Some tests failed: ' + data.error);
      }
    } catch (error) {
      console.error('Test failed:', error);
      const errorResult: TestResult = {
        success: false,
        message: 'Test execution failed',
        error: (error as Error).message
      };
      setTestResult(errorResult);
      toast.error('Test execution failed: ' + (error as Error).message);
    } finally {
      setIsRunningTest(false);
    }
  };

  const getTestStatusIcon = (passed: boolean) => {
    return passed ? (
      <CheckCircle className="h-4 w-4 text-green-500" />
    ) : (
      <AlertCircle className="h-4 w-4 text-red-500" />
    );
  };

  const getTestStatusBadge = (passed: boolean) => {
    return (
      <Badge variant={passed ? "default" : "destructive"} className="text-xs">
        {passed ? "PASSED" : "FAILED"}
      </Badge>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-6">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center space-x-3">
            <Shield className="h-8 w-8 text-blue-600" />
            <h1 className="text-3xl font-bold">Supabase Vault Integration Test</h1>
            <Database className="h-8 w-8 text-green-600" />
          </div>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Test the complete BYOK (Bring Your Own Key) implementation with Supabase Vault.
            This will verify secure credential storage, retrieval, updates, and cleanup.
          </p>
        </div>

        {/* Health Check Section */}
        <Card className="border-blue-200 bg-blue-50/50 dark:border-blue-800 dark:bg-blue-950/20">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="h-5 w-5 text-blue-600" />
              <span>System Health Check</span>
            </CardTitle>
            <CardDescription>
              Verify that all required components are properly configured
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button 
              onClick={runHealthCheck} 
              disabled={isLoadingHealth}
              className="w-full"
              variant="outline"
            >
              {isLoadingHealth ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Checking System...
                </>
              ) : (
                <>
                  <Zap className="mr-2 h-4 w-4" />
                  Run Health Check
                </>
              )}
            </Button>

            {healthCheck && (
              <div className="space-y-3 p-4 bg-white dark:bg-gray-800 rounded-lg border">
                <div className="flex items-center justify-between">
                  <span className="font-medium">System Status:</span>
                  <Badge variant={healthCheck.ready ? "default" : "destructive"}>
                    {healthCheck.ready ? "READY" : "NOT READY"}
                  </Badge>
                </div>

                {healthCheck.vault && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Supabase Vault:</span>
                    <div className="flex items-center space-x-2">
                      {getTestStatusIcon(healthCheck.vault.available)}
                      <span className="text-xs text-muted-foreground">
                        v{healthCheck.vault.version}
                      </span>
                    </div>
                  </div>
                )}

                {healthCheck.functions && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Required Functions:</span>
                      <span className="text-xs text-muted-foreground">
                        {healthCheck.functions.available.length}/{healthCheck.functions.required.length}
                      </span>
                    </div>
                    
                    {healthCheck.functions.missing.length > 0 && (
                      <div className="text-xs text-red-600">
                        Missing: {healthCheck.functions.missing.join(', ')}
                      </div>
                    )}
                  </div>
                )}

                {healthCheck.error && (
                  <div className="text-sm text-red-600 bg-red-50 dark:bg-red-950/20 p-2 rounded">
                    {healthCheck.error}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Test Execution Section */}
        <Card className="border-green-200 bg-green-50/50 dark:border-green-800 dark:bg-green-950/20">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Play className="h-5 w-5 text-green-600" />
              <span>Vault Integration Test</span>
            </CardTitle>
            <CardDescription>
              Run comprehensive tests for the BYOK model implementation
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button 
              onClick={runVaultTest} 
              disabled={isRunningTest || (healthCheck && !healthCheck.ready)}
              className="w-full"
              size="lg"
            >
              {isRunningTest ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Running Tests...
                </>
              ) : (
                <>
                  <Play className="mr-2 h-4 w-4" />
                  Run Vault Integration Test
                </>
              )}
            </Button>

            {!healthCheck?.ready && healthCheck && (
              <div className="text-sm text-yellow-600 bg-yellow-50 dark:bg-yellow-950/20 p-3 rounded">
                ⚠️ Run health check first to ensure system is ready
              </div>
            )}
          </CardContent>
        </Card>

        {/* Test Results Section */}
        {testResult && (
          <Card className={`border-2 ${testResult.success 
            ? 'border-green-300 bg-green-50/50 dark:border-green-700 dark:bg-green-950/20' 
            : 'border-red-300 bg-red-50/50 dark:border-red-700 dark:bg-red-950/20'
          }`}>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                {testResult.success ? (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-red-600" />
                )}
                <span>Test Results</span>
              </CardTitle>
              <CardDescription>
                {testResult.message}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {testResult.testResults && (
                <div className="grid gap-3 md:grid-cols-2">
                  {Object.entries(testResult.testResults).map(([testName, passed]) => (
                    <div key={testName} className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg border">
                      <span className="text-sm font-medium capitalize">
                        {testName.replace(/([A-Z])/g, ' $1').trim()}
                      </span>
                      <div className="flex items-center space-x-2">
                        {getTestStatusIcon(passed)}
                        {getTestStatusBadge(passed)}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {testResult.details && (
                <div className="space-y-2">
                  <h4 className="font-medium text-sm">Test Details:</h4>
                  <div className="bg-white dark:bg-gray-800 p-3 rounded-lg border text-xs font-mono space-y-1">
                    {Object.entries(testResult.details).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="text-muted-foreground">{key}:</span>
                        <span className="font-medium">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {testResult.error && (
                <div className="text-sm text-red-600 bg-red-50 dark:bg-red-950/20 p-3 rounded border border-red-200 dark:border-red-800">
                  <strong>Error:</strong> {testResult.error}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Test Coverage Information */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Test Coverage</CardTitle>
            <CardDescription>
              This test suite covers the following aspects of the vault integration:
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <h4 className="font-medium text-sm">Security Tests:</h4>
                <ul className="text-xs text-muted-foreground space-y-1">
                  <li>• Vault secret creation and encryption</li>
                  <li>• Secure credential storage</li>
                  <li>• Access control validation</li>
                  <li>• Proper secret cleanup</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium text-sm">Functionality Tests:</h4>
                <ul className="text-xs text-muted-foreground space-y-1">
                  <li>• Integration CRUD operations</li>
                  <li>• Credential retrieval and updates</li>
                  <li>• Status management</li>
                  <li>• Database consistency</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
