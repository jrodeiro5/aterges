"use client"

import { AppHeaderLayout } from '@/components/layouts/app-header-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Bot, 
  Plus, 
  Settings, 
  Activity,
  MessageSquare,
  Clock,
  Zap
} from 'lucide-react';

const agents = [
  {
    id: 1,
    name: 'Asistente de Ventas',
    description: 'Especializado en generar leads y cerrar ventas',
    status: 'active',
    conversations: 342,
    successRate: '92%',
    lastActive: 'Hace 5 min',
    type: 'Ventas'
  },
  {
    id: 2,
    name: 'Soporte Técnico',
    description: 'Resuelve problemas técnicos y consultas de productos',
    status: 'active',
    conversations: 128,
    successRate: '88%',
    lastActive: 'Hace 12 min',
    type: 'Soporte'
  },
  {
    id: 3,
    name: 'Marketing Digital',
    description: 'Optimiza campañas y analiza métricas de marketing',
    status: 'inactive',
    conversations: 67,
    successRate: '94%',
    lastActive: 'Hace 2 horas',
    type: 'Marketing'
  }
];

export default function AgentsPage() {
  return (
    <AppHeaderLayout>
      <div className="p-6">
        <div className="max-w-7xl mx-auto space-y-8 animate-fade-in">
          {/* Page Header */}
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <h1 className="text-3xl font-bold tracking-tight">Agentes</h1>
              <p className="text-muted-foreground">
                Gestiona y configura tus agentes de IA especializados
              </p>
            </div>
            <Button className="animate-slide-up">
              <Plus className="mr-2 h-4 w-4" />
              Crear Agente
            </Button>
          </div>

          {/* Stats Overview */}
          <div className="grid gap-4 md:grid-cols-3">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Total de Agentes
                  </CardTitle>
                  <Bot className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">3</div>
                  <p className="text-xs text-green-600">
                    +1 desde el mes pasado
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Agentes Activos
                  </CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">2</div>
                  <p className="text-xs text-muted-foreground">
                    67% del total
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Conversaciones Totales
                  </CardTitle>
                  <MessageSquare className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">537</div>
                  <p className="text-xs text-green-600">
                    +23% desde la semana pasada
                  </p>
                </CardContent>
              </Card>
          </div>

          {/* Agents Grid */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {agents.map((agent, index) => (
                <Card 
                  key={agent.id}
                  className="animate-slide-up hover:shadow-md transition-all hover:scale-105"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                          <Bot className="h-4 w-4 text-primary" />
                        </div>
                        <Badge 
                          variant={agent.status === 'active' ? 'default' : 'secondary'}
                          className="text-xs"
                        >
                          {agent.status === 'active' ? 'Activo' : 'Inactivo'}
                        </Badge>
                      </div>
                      <Button variant="ghost" size="sm">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </div>
                    <CardTitle className="text-lg">{agent.name}</CardTitle>
                    <CardDescription className="text-sm">
                      {agent.description}
                    </CardDescription>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Conversaciones</p>
                        <p className="font-semibold">{agent.conversations}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Tasa de Éxito</p>
                        <p className="font-semibold text-green-600">{agent.successRate}</p>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center text-muted-foreground">
                        <Clock className="mr-1 h-3 w-3" />
                        {agent.lastActive}
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {agent.type}
                      </Badge>
                    </div>

                    <div className="flex space-x-2">
                      <Button size="sm" className="flex-1">
                        <MessageSquare className="mr-1 h-3 w-3" />
                        Chat
                      </Button>
                      <Button size="sm" variant="outline" className="flex-1">
                        <Zap className="mr-1 h-3 w-3" />
                        Entrenar
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}

              {/* Add New Agent Card */}
              <Card className="border-dashed border-2 hover:border-primary/50 transition-colors animate-slide-up cursor-pointer" style={{ animationDelay: '300ms' }}>
                <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted mb-4">
                    <Plus className="h-6 w-6 text-muted-foreground" />
                  </div>
                  <CardTitle className="text-lg mb-2">Crear Nuevo Agente</CardTitle>
                  <CardDescription className="mb-4">
                    Configura un agente especializado para tus necesidades
                  </CardDescription>
                  <Button>
                    <Plus className="mr-2 h-4 w-4" />
                    Empezar
                  </Button>
                </CardContent>
              </Card>
          </div>

          {/* Coming Soon Notice */}
          <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 border-blue-200 dark:border-blue-800">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-blue-700 dark:text-blue-300">
                <Bot className="h-5 w-5" />
                <span>Funcionalidades Avanzadas - Próximamente</span>
              </CardTitle>
              <CardDescription className="text-blue-600 dark:text-blue-400">
                Estamos desarrollando capacidades avanzadas de entrenamiento y personalización de agentes.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </div>
    </AppHeaderLayout>
  );
}
