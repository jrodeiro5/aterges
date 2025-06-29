import { PublicLayout } from '@/components/layouts/public-layout';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { 
  ArrowRight, 
  Zap, 
  Shield, 
  TrendingUp, 
  Users,
  CheckCircle 
} from 'lucide-react';

const features = [
  {
    icon: Zap,
    title: 'Automatización Inteligente',
    description: 'Automatiza procesos complejos con IA avanzada que aprende y se adapta a tu negocio.'
  },
  {
    icon: Shield,
    title: 'Seguridad Empresarial',
    description: 'Protección de datos de nivel empresarial con encriptación y cumplimiento normativo.'
  },
  {
    icon: TrendingUp,
    title: 'Crecimiento Escalable',
    description: 'Soluciones que crecen contigo, desde startups hasta grandes corporaciones.'
  },
  {
    icon: Users,
    title: 'Colaboración en Equipo',
    description: 'Herramientas diseñadas para equipos modernos con flujos de trabajo integrados.'
  }
];

const benefits = [
  'Reducción del 70% en tareas repetitivas',
  'Aumento del 45% en productividad del equipo',
  'ROI positivo en los primeros 3 meses',
  'Integración sin interrupciones',
  'Soporte 24/7 en español'
];

export default function Home() {
  return (
    <PublicLayout>
      <div className="animate-fade-in">
        {/* Hero Section */}
        <section className="relative overflow-hidden bg-gradient-to-b from-background to-muted/20">
          <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-32 lg:px-8">
            <div className="mx-auto max-w-4xl text-center">
              <div className="animate-slide-up">
                <h1 className="text-4xl font-bold tracking-tight sm:text-6xl bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                  Revoluciona tu Negocio con{' '}
                  <span className="text-primary">Inteligencia Artificial</span>
                </h1>
                <p className="mt-6 text-lg leading-8 text-muted-foreground max-w-2xl mx-auto">
                  Aterges AI transforma la manera en que las empresas operan. 
                  Automatiza procesos, potencia tu marketing digital y optimiza 
                  tu e-commerce con nuestra plataforma SaaS impulsada por IA.
                </p>
                <div className="mt-10 flex items-center justify-center gap-x-6">
                  <Button asChild size="lg" className="text-base h-12 px-8">
                    <Link href="/signup">
                      Empezar Gratis
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                  <Button variant="outline" asChild size="lg" className="text-base h-12 px-8">
                    <Link href="/login">
                      Iniciar Sesión
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-24 bg-muted/30">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center mb-16">
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                Potencia tu Empresa con IA
              </h2>
              <p className="mt-4 text-lg text-muted-foreground">
                Descubre las características que hacen de Aterges AI la elección 
                perfecta para empresas modernas.
              </p>
            </div>

            <div className="mx-auto max-w-5xl">
              <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
                {features.map((feature, index) => {
                  const Icon = feature.icon;
                  return (
                    <div 
                      key={feature.title}
                      className="group relative rounded-2xl border border-border bg-card p-6 shadow-sm transition-all hover:shadow-md hover:scale-105"
                      style={{ animationDelay: `${index * 100}ms` }}
                    >
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                        <Icon className="h-6 w-6 text-primary" />
                      </div>
                      <h3 className="mt-4 text-lg font-semibold text-card-foreground">
                        {feature.title}
                      </h3>
                      <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                        {feature.description}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </section>

        {/* Benefits Section */}
        <section className="py-24">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-4xl">
              <div className="grid grid-cols-1 gap-16 lg:grid-cols-2 items-center">
                <div>
                  <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                    Resultados que Hablan por Sí Mismos
                  </h2>
                  <p className="mt-4 text-lg text-muted-foreground">
                    Miles de empresas ya confían en Aterges AI para transformar 
                    sus operaciones y acelerar su crecimiento.
                  </p>
                  
                  <ul className="mt-8 space-y-4">
                    {benefits.map((benefit, index) => (
                      <li key={index} className="flex items-center space-x-3">
                        <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                        <span className="text-foreground font-medium">{benefit}</span>
                      </li>
                    ))}
                  </ul>

                  <div className="mt-8">
                    <Button asChild size="lg">
                      <Link href="/signup">
                        Prueba Gratuita - 14 Días
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Link>
                    </Button>
                  </div>
                </div>

                <div className="relative">
                  <div className="aspect-square rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 border border-border flex items-center justify-center">
                    <div className="text-center space-y-4">
                      <div className="text-4xl font-bold text-primary">99.9%</div>
                      <div className="text-muted-foreground">Uptime garantizado</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-24 bg-primary/5">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                ¿Listo para Transformar tu Negocio?
              </h2>
              <p className="mt-4 text-lg text-muted-foreground">
                Únete a miles de empresas que ya están revolucionando sus 
                operaciones con Aterges AI.
              </p>
              <div className="mt-8">
                <Button asChild size="lg" className="text-base h-12 px-8">
                  <Link href="/signup">
                    Comenzar Ahora - Es Gratis
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
              <p className="mt-4 text-sm text-muted-foreground">
                Sin tarjeta de crédito requerida • Configuración en 5 minutos
              </p>
            </div>
          </div>
        </section>
      </div>
    </PublicLayout>
  );
}