"use client"

import { useState, useEffect } from 'react';
import { AppHeaderLayout } from '@/components/layouts/app-header-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  User, 
  Shield, 
  CreditCard, 
  Save,
  Key,
  Crown,
  Check,
  AlertCircle
} from 'lucide-react';
import { authService, User as UserType } from '@/lib/auth';
import { toast } from 'sonner';

export default function SettingsPage() {
  const [user, setUser] = useState<UserType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Profile form state
  const [profileForm, setProfileForm] = useState({
    name: '',
    email: '',
  });
  const [isProfileLoading, setIsProfileLoading] = useState(false);

  // Password form state
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [isPasswordLoading, setIsPasswordLoading] = useState(false);

  useEffect(() => {
    const loadUser = async () => {
      try {
        const currentUser = await authService.getCurrentUser();
        if (currentUser) {
          setUser(currentUser);
          setProfileForm({
            name: currentUser.name || '',
            email: currentUser.email,
          });
        }
      } catch (error) {
        toast.error('Error al cargar la información del usuario');
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
  }, []);

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsProfileLoading(true);

    try {
      const response = await fetch('/api/user/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...authService.getAuthHeader(),
        },
        body: JSON.stringify({
          name: profileForm.name,
        }),
      });

      if (!response.ok) {
        throw new Error('Error al actualizar el perfil');
      }

      const updatedUser = await response.json();
      setUser(updatedUser);
      toast.success('Perfil actualizado correctamente');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Error al actualizar el perfil');
    } finally {
      setIsProfileLoading(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      toast.error('Las contraseñas no coinciden');
      return;
    }

    if (passwordForm.newPassword.length < 6) {
      toast.error('La nueva contraseña debe tener al menos 6 caracteres');
      return;
    }

    setIsPasswordLoading(true);

    try {
      const response = await fetch('/api/user/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authService.getAuthHeader(),
        },
        body: JSON.stringify({
          currentPassword: passwordForm.currentPassword,
          newPassword: passwordForm.newPassword,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Error al cambiar la contraseña');
      }

      setPasswordForm({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
      toast.success('Contraseña cambiada correctamente');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Error al cambiar la contraseña');
    } finally {
      setIsPasswordLoading(false);
    }
  };

  if (isLoading) {
    return (
      <AppHeaderLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse text-muted-foreground">Cargando configuración...</div>
        </div>
      </AppHeaderLayout>
    );
  }

  return (
    <AppHeaderLayout>
      <div className="p-6">
        <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
          {/* Page Header */}
          <div className="space-y-2">
            <h1 className="text-3xl font-bold tracking-tight">Configuración de Cuenta</h1>
            <p className="text-muted-foreground">
              Gestiona tu perfil, seguridad y configuración de facturación
            </p>
          </div>

          <Tabs defaultValue="profile" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
            <TabsTrigger value="profile" className="flex items-center space-x-2">
              <User className="h-4 w-4" />
              <span>Perfil</span>
            </TabsTrigger>
            <TabsTrigger value="security" className="flex items-center space-x-2">
              <Shield className="h-4 w-4" />
              <span>Seguridad</span>
            </TabsTrigger>
            <TabsTrigger value="billing" className="flex items-center space-x-2">
              <CreditCard className="h-4 w-4" />
              <span>Plan y Facturación</span>
            </TabsTrigger>
          </TabsList>

          {/* Profile Tab */}
          <TabsContent value="profile" className="space-y-6">
            <Card className="animate-slide-up">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <User className="h-5 w-5" />
                  <span>Información del Perfil</span>
                </CardTitle>
                <CardDescription>
                  Actualiza tu información personal y de contacto
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleProfileSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">Correo Electrónico</Label>
                    <Input
                      id="email"
                      type="email"
                      value={profileForm.email}
                      disabled
                      className="bg-muted"
                    />
                    <p className="text-xs text-muted-foreground">
                      El correo electrónico no se puede cambiar por razones de seguridad
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="name">Nombre Completo</Label>
                    <Input
                      id="name"
                      type="text"
                      placeholder="Tu nombre completo"
                      value={profileForm.name}
                      onChange={(e) => setProfileForm(prev => ({ ...prev, name: e.target.value }))}
                      disabled={isProfileLoading}
                    />
                  </div>

                  <div className="pt-4">
                    <Button 
                      type="submit" 
                      disabled={isProfileLoading}
                      className="w-full sm:w-auto"
                    >
                      {isProfileLoading ? (
                        <>
                          <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                          Guardando...
                        </>
                      ) : (
                        <>
                          <Save className="mr-2 h-4 w-4" />
                          Guardar Cambios
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security" className="space-y-6">
            <Card className="animate-slide-up" style={{ animationDelay: '100ms' }}>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="h-5 w-5" />
                  <span>Cambiar Contraseña</span>
                </CardTitle>
                <CardDescription>
                  Actualiza tu contraseña para mantener tu cuenta segura
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handlePasswordSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="currentPassword">Contraseña Actual</Label>
                    <Input
                      id="currentPassword"
                      type="password"
                      value={passwordForm.currentPassword}
                      onChange={(e) => setPasswordForm(prev => ({ ...prev, currentPassword: e.target.value }))}
                      disabled={isPasswordLoading}
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="newPassword">Nueva Contraseña</Label>
                    <Input
                      id="newPassword"
                      type="password"
                      placeholder="Mínimo 6 caracteres"
                      value={passwordForm.newPassword}
                      onChange={(e) => setPasswordForm(prev => ({ ...prev, newPassword: e.target.value }))}
                      disabled={isPasswordLoading}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword">Confirmar Nueva Contraseña</Label>
                    <Input
                      id="confirmPassword"
                      type="password"
                      placeholder="Repite la nueva contraseña"
                      value={passwordForm.confirmPassword}
                      onChange={(e) => setPasswordForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
                      disabled={isPasswordLoading}
                      required
                    />
                  </div>

                  <div className="pt-4">
                    <Button 
                      type="submit" 
                      disabled={isPasswordLoading || !passwordForm.currentPassword || !passwordForm.newPassword || !passwordForm.confirmPassword}
                      className="w-full sm:w-auto"
                    >
                      {isPasswordLoading ? (
                        <>
                          <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                          Cambiando...
                        </>
                      ) : (
                        <>
                          <Key className="mr-2 h-4 w-4" />
                          Cambiar Contraseña
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>

            {/* Security Info */}
            <Card className="animate-slide-up" style={{ animationDelay: '200ms' }}>
              <CardHeader>
                <CardTitle className="text-lg">Recomendaciones de Seguridad</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-start space-x-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 shrink-0" />
                  <div>
                    <p className="font-medium">Contraseña segura</p>
                    <p className="text-sm text-muted-foreground">
                      Usa al menos 8 caracteres con mayúsculas, minúsculas y números
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 shrink-0" />
                  <div>
                    <p className="font-medium">Sesión segura</p>
                    <p className="text-sm text-muted-foreground">
                      Tu sesión se cierra automáticamente después de inactividad
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <AlertCircle className="h-5 w-5 text-amber-500 mt-0.5 shrink-0" />
                  <div>
                    <p className="font-medium">Cambios regulares</p>
                    <p className="text-sm text-muted-foreground">
                      Recomendamos cambiar tu contraseña cada 90 días
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Billing Tab */}
          <TabsContent value="billing" className="space-y-6">
            {/* Current Plan */}
            <Card className="animate-slide-up" style={{ animationDelay: '100ms' }}>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Crown className="h-5 w-5" />
                  <span>Plan Actual</span>
                </CardTitle>
                <CardDescription>
                  Información sobre tu suscripción y uso
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <h3 className="font-semibold">Plan Gratuito</h3>
                        <Badge variant="secondary">Activo</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Perfecto para empezar con Aterges AI
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold">$0</div>
                      <div className="text-sm text-muted-foreground">por mes</div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <h4 className="font-medium">Características incluidas:</h4>
                    <div className="grid gap-2">
                      <div className="flex items-center space-x-2">
                        <Check className="h-4 w-4 text-green-500" />
                        <span className="text-sm">100 consultas de IA por mes</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Check className="h-4 w-4 text-green-500" />
                        <span className="text-sm">1 agente de IA</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Check className="h-4 w-4 text-green-500" />
                        <span className="text-sm">Soporte por email</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Check className="h-4 w-4 text-green-500" />
                        <span className="text-sm">Historial de 30 días</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Usage Stats */}
            <Card className="animate-slide-up" style={{ animationDelay: '200ms' }}>
              <CardHeader>
                <CardTitle>Uso del Mes Actual</CardTitle>
                <CardDescription>
                  Seguimiento de tu consumo mensual
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Consultas de IA</span>
                      <span>23 / 100</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div className="bg-primary h-2 rounded-full" style={{ width: '23%' }}></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Agentes activos</span>
                      <span>1 / 1</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div className="bg-primary h-2 rounded-full" style={{ width: '100%' }}></div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Upgrade Options */}
            <Card className="animate-slide-up" style={{ animationDelay: '300ms' }}>
              <CardHeader>
                <CardTitle>Actualizar Plan</CardTitle>
                <CardDescription>
                  Desbloquea más funcionalidades con nuestros planes premium
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="border rounded-lg p-4 space-y-3">
                    <div className="space-y-1">
                      <h3 className="font-semibold">Plan Pro</h3>
                      <div className="text-2xl font-bold">$29<span className="text-sm font-normal text-muted-foreground">/mes</span></div>
                    </div>
                    <ul className="space-y-1 text-sm">
                      <li className="flex items-center space-x-2">
                        <Check className="h-3 w-3 text-green-500" />
                        <span>1,000 consultas por mes</span>
                      </li>
                      <li className="flex items-center space-x-2">
                        <Check className="h-3 w-3 text-green-500" />
                        <span>5 agentes de IA</span>
                      </li>
                      <li className="flex items-center space-x-2">
                        <Check className="h-3 w-3 text-green-500" />
                        <span>Integraciones BYOK</span>
                      </li>
                    </ul>
                    <Button variant="outline" className="w-full" disabled>
                      Próximamente
                    </Button>
                  </div>

                  <div className="border rounded-lg p-4 space-y-3 relative">
                    <Badge className="absolute -top-2 left-4">Más Popular</Badge>
                    <div className="space-y-1">
                      <h3 className="font-semibold">Plan Enterprise</h3>
                      <div className="text-2xl font-bold">$99<span className="text-sm font-normal text-muted-foreground">/mes</span></div>
                    </div>
                    <ul className="space-y-1 text-sm">
                      <li className="flex items-center space-x-2">
                        <Check className="h-3 w-3 text-green-500" />
                        <span>Consultas ilimitadas</span>
                      </li>
                      <li className="flex items-center space-x-2">
                        <Check className="h-3 w-3 text-green-500" />
                        <span>Agentes ilimitados</span>
                      </li>
                      <li className="flex items-center space-x-2">
                        <Check className="h-3 w-3 text-green-500" />
                        <span>Soporte prioritario</span>
                      </li>
                    </ul>
                    <Button variant="outline" className="w-full" disabled>
                      Próximamente
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Billing Management */}
            <Card className="animate-slide-up" style={{ animationDelay: '400ms' }}>
              <CardHeader>
                <CardTitle>Gestión de Facturación</CardTitle>
                <CardDescription>
                  Administra tus métodos de pago y facturas
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg bg-muted/50">
                    <div className="flex items-center space-x-3">
                      <CreditCard className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="font-medium">Método de Pago</p>
                        <p className="text-sm text-muted-foreground">No configurado</p>
                      </div>
                    </div>
                    <Button variant="outline" disabled>
                      Gestionar Facturación
                    </Button>
                  </div>

                  <Separator />

                  <div className="text-center py-4">
                    <p className="text-sm text-muted-foreground mb-4">
                      La integración con Stripe estará disponible próximamente para gestionar 
                      tus suscripciones y métodos de pago de forma segura.
                    </p>
                    <div className="flex items-center justify-center space-x-2 text-xs text-muted-foreground">
                      <Shield className="h-3 w-3" />
                      <span>Pagos seguros con encriptación SSL</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          </Tabs>
        </div>
      </div>
    </AppHeaderLayout>
  );
}