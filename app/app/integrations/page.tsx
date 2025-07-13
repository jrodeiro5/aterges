"use client"

import { useState, useEffect } from 'react';
import { AppHeaderLayout } from '@/components/layouts/app-header-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { 
  Database, 
  Plus, 
  Settings, 
  Trash2,
  Key,
  CheckCircle,
  AlertCircle,
  ExternalLink,
  Cloud,
  Clock,
  XCircle,
  Shield,
  Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import { integrationsService, Integration, CreateIntegrationRequest } from '@/lib/integrations';

const integrationTypes = [
  {
    id: 'google-cloud' as const,
    name: 'Google Cloud',
    description: 'Conecta tu proyecto de Google Cloud para acceder a APIs de IA',
    icon: Cloud,
    color: 'bg-blue-500',
  },
  {
    id: 'openai' as const,
    name: 'OpenAI',
    description: 'Usa tu propia API key de OpenAI para modelos GPT',
    icon: Key,
    color: 'bg-green-500',
  },
  {
    id: 'aws' as const,
    name: 'Amazon Web Services',
    description: 'Integra servicios de AWS como Bedrock y SageMaker',
    icon: Database,
    color: 'bg-orange-500',
  },
  {
    id: 'azure' as const,
    name: 'Microsoft Azure',
    description: 'Conecta con Azure OpenAI Service y Cognitive Services',
    icon: Cloud,
    color: 'bg-blue-600',
  },
];

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [selectedType, setSelectedType] = useState<string>('');
  const [testingIntegrations, setTestingIntegrations] = useState<Set<string>>(new Set());
  const [formData, setFormData] = useState({
    name: '',
    credentials: '',
  });

  // Load integrations on component mount
  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      setIsLoading(true);
      const data = await integrationsService.getIntegrations();
      setIntegrations(data);
    } catch (error) {
      console.error('Error loading integrations:', error);
      toast.error('Error al cargar las integraciones');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddIntegration = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsCreating(true);

    try {
      const request: CreateIntegrationRequest = {
        name: formData.name,
        type: selectedType as Integration['type'],
        credentials: formData.credentials,
        config: {}
      };

      const result = await integrationsService.createIntegration(request);
      
      // Refresh integrations list
      await loadIntegrations();
      
      setIsDialogOpen(false);
      setFormData({ name: '', credentials: '' });
      setSelectedType('');
      
      toast.success('Integración creada exitosamente. Verificando credenciales...');
    } catch (error) {
      console.error('Error creating integration:', error);
      toast.error(error instanceof Error ? error.message : 'Error al crear la integración');
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteIntegration = async (id: string) => {
    try {
      await integrationsService.deleteIntegration(id);
      setIntegrations(prev => prev.filter(integration => integration.id !== id));
      toast.success('Integración eliminada correctamente');
    } catch (error) {
      console.error('Error deleting integration:', error);
      toast.error(error instanceof Error ? error.message : 'Error al eliminar la integración');
    }
  };

  const handleTestIntegration = async (id: string) => {
    try {
      setTestingIntegrations(prev => new Set(prev.add(id)));
      
      const result = await integrationsService.testIntegration(id);
      
      if (result.success) {
        toast.success(result.message);
      } else {
        toast.error(result.message);
      }

      // Refresh integrations to get updated status
      await loadIntegrations();
    } catch (error) {
      console.error('Error testing integration:', error);
      toast.error(error instanceof Error ? error.message : 'Error al probar la conexión');
    } finally {
      setTestingIntegrations(prev => {
        const newSet = new Set(prev);
        newSet.delete(id);
        return newSet;
      });
    }
  };

  const getStatusIcon = (status: Integration['status']) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'disabled':
        return <XCircle className="h-4 w-4 text-gray-500" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getStatusText = (status: Integration['status']) => {
    return integrationsService.getStatusText(status);
  };

  const getTypeInfo = (type: Integration['type']) => {
    return integrationTypes.find(t => t.id === type);
  };

  const getSelectedTypeInfo = () => {
    return integrationsService.getIntegrationTypeInfo(selectedType as Integration['type']);
  };

  if (isLoading) {
    return (
      <AppHeaderLayout>
        <div className="p-6">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin" />
              <span className="ml-2">Cargando integraciones...</span>
            </div>
          </div>
        </div>
      </AppHeaderLayout>
    );
  }

  return (
    <AppHeaderLayout>
      <div className="p-6">
        <div className="max-w-7xl mx-auto space-y-8 animate-fade-in">
          {/* Page Header */}
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <h1 className="text-3xl font-bold tracking-tight">Integraciones</h1>
              <p className="text-muted-foreground">
                Conecta tus propias APIs y servicios para usar el modelo BYOK (Bring Your Own Key)
              </p>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button className="animate-slide-up">
                  <Plus className="mr-2 h-4 w-4" />
                  Nueva Integración
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                  <DialogTitle className="flex items-center space-x-2">
                    <Shield className="h-5 w-5 text-green-500" />
                    <span>Agregar Nueva Integración</span>
                  </DialogTitle>
                  <DialogDescription>
                    Conecta tu propia API key o credenciales de servicio. Todas las credenciales se almacenan 
                    de forma segura y encriptada usando Supabase Vault.
                  </DialogDescription>
                </DialogHeader>
                
                <form onSubmit={handleAddIntegration} className="space-y-6">
                  {/* Integration Type Selection */}
                  <div className="space-y-3">
                    <Label>Tipo de Integración</Label>
                    <div className="grid grid-cols-2 gap-3">
                      {integrationTypes.map((type) => {
                        const Icon = type.icon;
                        return (
                          <button
                            key={type.id}
                            type="button"
                            onClick={() => setSelectedType(type.id)}
                            className={`p-3 border rounded-lg text-left transition-all hover:border-primary/50 ${
                              selectedType === type.id 
                                ? 'border-primary bg-primary/5' 
                                : 'border-border'
                            }`}
                          >
                            <div className="flex items-start space-x-3">
                              <div className={`p-2 rounded-lg ${type.color} text-white`}>
                                <Icon className="h-4 w-4" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="font-medium text-sm">{type.name}</p>
                                <p className="text-xs text-muted-foreground mt-1">
                                  {type.description}
                                </p>
                              </div>
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {selectedType && (
                    <>
                      <div className="space-y-2">
                        <Label htmlFor="name">Nombre de la Integración</Label>
                        <Input
                          id="name"
                          placeholder="Ej: Mi Proyecto de Google Cloud"
                          value={formData.name}
                          onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="credentials">
                          {getSelectedTypeInfo()?.credentialsLabel || 'Credenciales'}
                        </Label>
                        <Textarea
                          id="credentials"
                          placeholder={getSelectedTypeInfo()?.credentialsPlaceholder || 'Pega aquí tus credenciales...'}
                          value={formData.credentials}
                          onChange={(e) => setFormData(prev => ({ ...prev, credentials: e.target.value }))}
                          className="min-h-[120px] font-mono text-xs"
                          required
                        />
                        <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                          <Shield className="h-3 w-3 text-green-500" />
                          <span>Tus credenciales se almacenan de forma segura y encriptada en Supabase Vault</span>
                        </div>
                      </div>

                      <div className="flex justify-end space-x-3">
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => setIsDialogOpen(false)}
                          disabled={isCreating}
                        >
                          Cancelar
                        </Button>
                        <Button type="submit" disabled={isCreating}>
                          {isCreating ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Creando...
                            </>
                          ) : (
                            'Guardar y Verificar'
                          )}
                        </Button>
                      </div>
                    </>
                  )}
                </form>
              </DialogContent>
            </Dialog>
          </div>

          {/* Stats */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total de Integraciones
                </CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{integrations.length}</div>
                <p className="text-xs text-muted-foreground">
                  {integrations.filter(i => i.status === 'connected').length} activas
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Estado de Conexiones
                </CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {integrations.length > 0 
                    ? Math.round((integrations.filter(i => i.status === 'connected').length / integrations.length) * 100)
                    : 0}%
                </div>
                <p className="text-xs text-muted-foreground">
                  Conexiones exitosas
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Seguridad
                </CardTitle>
                <Shield className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">Vault</div>
                <p className="text-xs text-green-600">
                  Credenciales encriptadas
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Integrations List */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Integraciones Configuradas</h2>
            
            {integrations.length === 0 ? (
              <Card className="border-dashed border-2">
                <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted mb-4">
                    <Shield className="h-6 w-6 text-green-500" />
                  </div>
                  <CardTitle className="text-lg mb-2">No hay integraciones configuradas</CardTitle>
                  <CardDescription className="mb-4 max-w-sm">
                    Conecta tus propias APIs y servicios para empezar a usar el modelo BYOK. 
                    Todas las credenciales se almacenan de forma segura con Supabase Vault.
                  </CardDescription>
                  <Button onClick={() => setIsDialogOpen(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    Crear Primera Integración
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {integrations.map((integration, index) => {
                  const typeInfo = getTypeInfo(integration.type);
                  const Icon = typeInfo?.icon || Database;
                  const isTestingThis = testingIntegrations.has(integration.id);
                  
                  return (
                    <Card 
                      key={integration.id}
                      className="animate-slide-up hover:shadow-md transition-all"
                      style={{ animationDelay: `${index * 100}ms` }}
                    >
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className={`p-2 rounded-lg ${typeInfo?.color || 'bg-muted'} text-white`}>
                              <Icon className="h-4 w-4" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <CardTitle className="text-base truncate">{integration.name}</CardTitle>
                              <CardDescription className="text-sm">
                                {typeInfo?.name || integration.type}
                              </CardDescription>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Button variant="ghost" size="sm">
                              <Settings className="h-4 w-4" />
                            </Button>
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => handleDeleteIntegration(integration.id)}
                              className="text-red-500 hover:text-red-600"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardHeader>
                      
                      <CardContent className="space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            {getStatusIcon(integration.status)}
                            <span className="text-sm font-medium">
                              {getStatusText(integration.status)}
                            </span>
                          </div>
                          <Badge 
                            variant={integration.status === 'connected' ? 'default' : 'destructive'}
                            className="text-xs"
                          >
                            {integration.status === 'connected' ? 'Activa' : 'Inactiva'}
                          </Badge>
                        </div>

                        {integration.error_message && (
                          <div className="text-xs text-red-600 bg-red-50 dark:bg-red-950/20 p-2 rounded">
                            {integration.error_message}
                          </div>
                        )}

                        <div className="text-xs text-muted-foreground space-y-1">
                          <div className="flex justify-between">
                            <span>Creada:</span>
                            <span>{new Date(integration.created_at).toLocaleDateString()}</span>
                          </div>
                          {integration.last_used_at && (
                            <div className="flex justify-between">
                              <span>Último uso:</span>
                              <span>{new Date(integration.last_used_at).toLocaleDateString()}</span>
                            </div>
                          )}
                        </div>

                        <Button 
                          size="sm" 
                          variant="outline" 
                          className="w-full"
                          onClick={() => handleTestIntegration(integration.id)}
                          disabled={isTestingThis}
                        >
                          {isTestingThis ? (
                            <>
                              <Loader2 className="mr-2 h-3 w-3 animate-spin" />
                              Probando...
                            </>
                          ) : (
                            <>
                              <ExternalLink className="mr-2 h-3 w-3" />
                              Probar Conexión
                            </>
                          )}
                        </Button>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </div>

          {/* BYOK Information */}
          <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 border-blue-200 dark:border-blue-800">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-blue-700 dark:text-blue-300">
                <Key className="h-5 w-5" />
                <span>Modelo BYOK (Bring Your Own Key)</span>
              </CardTitle>
              <CardDescription className="text-blue-600 dark:text-blue-400">
                Usa tus propias credenciales para mayor control y privacidad
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-blue-700 dark:text-blue-300">
              <div className="grid gap-3 md:grid-cols-2">
                <div className="space-y-2">
                  <h4 className="font-medium flex items-center space-x-2">
                    <span>Beneficios:</span>
                  </h4>
                  <ul className="space-y-1 text-xs">
                    <li>• Control total sobre tus datos</li>
                    <li>• Facturación directa con el proveedor</li>
                    <li>• Configuración personalizada</li>
                    <li>• Mayor límites de uso</li>
                  </ul>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium flex items-center space-x-2">
                    <Shield className="h-4 w-4 text-green-500" />
                    <span>Seguridad:</span>
                  </h4>
                  <ul className="space-y-1 text-xs">
                    <li>• Credenciales encriptadas con Supabase Vault</li>
                    <li>• Acceso controlado por usuario</li>
                    <li>• Eliminación segura de secretos</li>
                    <li>• Auditoría y trazabilidad completa</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppHeaderLayout>
  );
}
