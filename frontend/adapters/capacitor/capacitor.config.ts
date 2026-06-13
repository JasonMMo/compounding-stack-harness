import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'kr.co.n9n.csh',
  appName: 'Compounding Stack',
  webDir: 'www',
  server: {
    // Phase 1 — remote server mode: wraps the live PWA, no local bundle needed.
    // Phase 2 — switch to local bundle: remove server block, run `npm run build` first.
    url: 'https://edu-program.n9n.co.kr',
    cleartext: false,
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 1500,
      backgroundColor: '#1e3a5f',
      showSpinner: false,
    },
  },
};

export default config;
