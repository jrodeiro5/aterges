'use client';

import { useEffect } from 'react';
import Script from 'next/script';

declare global {
  interface Window {
    dataLayer: any[];
  }
}

interface GTMProps {
  gtmId: string;
}

export function GoogleTagManager({ gtmId }: GTMProps) {
  useEffect(() => {
    // Initialize dataLayer
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      'gtm.start': new Date().getTime(),
      event: 'gtm.js'
    });
    
    console.log('🎯 GTM initialized:', gtmId);
  }, [gtmId]);

  if (!gtmId) {
    console.warn('⚠️ GTM Container ID not provided');
    return null;
  }

  return (
    <Script
      id="gtm-script"
      strategy="afterInteractive"
      dangerouslySetInnerHTML={{
        __html: `
          (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
          new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
          j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
          'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
          })(window,document,'script','dataLayer','${gtmId}');
        `,
      }}
    />
  );
}

export function GoogleTagManagerNoScript({ gtmId }: GTMProps) {
  if (!gtmId) return null;

  return (
    <noscript>
      <iframe
        src={`https://www.googletagmanager.com/ns.html?id=${gtmId}`}
        height="0"
        width="0"
        style={{ display: 'none', visibility: 'hidden' }}
      />
    </noscript>
  );
}

// Event tracking utilities
export const trackEvent = (event: string, data?: any) => {
  if (typeof window !== 'undefined' && window.dataLayer) {
    window.dataLayer.push({
      event: event,
      ...data,
      timestamp: new Date().toISOString(),
    });
    console.log('📊 GTM Event:', event, data);
  }
};

// Aterges-specific event tracking
export const atergesEvents = {
  // Authentication
  login: (method: string = 'email') => {
    trackEvent('aterges_login', {
      method: method,
      event_category: 'authentication',
    });
  },

  signup: (method: string = 'email') => {
    trackEvent('aterges_signup', {
      method: method,
      event_category: 'authentication',
    });
  },

  // AI interactions
  aiQuery: (queryType: string, success: boolean = true) => {
    trackEvent('aterges_ai_query', {
      query_type: queryType,
      success: success,
      event_category: 'ai_interaction',
    });
  },

  // Navigation
  pageView: (pagePath: string, pageTitle: string) => {
    trackEvent('aterges_page_view', {
      page_path: pagePath,
      page_title: pageTitle,
      event_category: 'navigation',
    });
  },

  // Features
  featureUsed: (featureName: string) => {
    trackEvent('aterges_feature_used', {
      feature_name: featureName,
      event_category: 'engagement',
    });
  },
};
