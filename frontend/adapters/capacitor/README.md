# Capacitor Adapter — axis-4 Mobile Shell

Wraps the `vanilla-htmx` PWA with a native Capacitor shell for App Store (iOS) and Play Store (Android) submission.

**Status**: scaffold — Growth-49

## Strategy

Phase 1 (remote server mode): `capacitor.config.ts` points to the live deployment at `https://edu-program.n9n.co.kr`. No local bundle is needed. The app is essentially a thin native wrapper around the existing PWA.

Phase 2 (local bundle): When offline-first or native plugin access is required, remove the `server.url` block, place the vanilla-htmx static export in `www/`, and run `npx cap sync`.

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Node.js | 20+ | https://nodejs.org |
| Android Studio | Hedgehog+ | https://developer.android.com/studio |
| Xcode | 15+ (macOS only) | Mac App Store |
| JDK | 17+ | Bundled with Android Studio |

## Quick Start

```sh
cd frontend/adapters/capacitor
npm install

# First time — add platforms
npm run add:android     # generates android/
npm run add:ios         # generates ios/ (macOS only)

# Subsequent runs — sync after config changes
npm run sync

# Open in IDE to build / sign / publish
npm run open:android    # opens Android Studio
npm run open:ios        # opens Xcode
```

## Changing the Target URL

Edit `server.url` in `capacitor.config.ts`. Run `npm run sync` after any config change.

For customer-specific deployments (e.g. logistics tenant at `https://logistics.n9n.co.kr`), create a copy of this adapter directory with a patched config. Customer profile key: `stack.frontend: capacitor`.

## Native Plugin Roadmap

| Plugin | Use case | Phase |
|--------|----------|-------|
| `@capacitor/push-notifications` | 업무 알림 | Phase 2 |
| `@capacitor/camera` | 현장 사진 첨부 | Phase 2 |
| `@capacitor/filesystem` | 오프라인 데이터 캐시 | Phase 2 |
| `@capacitor/biometric-auth` | 지문/Face ID 로그인 | Phase 3 |

## App Store Submission Checklist

- [ ] `capacitor.config.ts`: `appId`, `appName` confirmed
- [ ] SplashScreen color matches customer theme token
- [ ] Android: `android/app/src/main/res/` icons replaced (use Android Studio Image Asset tool)
- [ ] iOS: `ios/App/App/Assets.xcassets/AppIcon.appiconset/` icons set
- [ ] Android: `android/app/build.gradle` — `versionCode` + `versionName` bumped
- [ ] iOS: Xcode → General → Version + Build bumped
- [ ] Release build signed with production keystore / provisioning profile
- [ ] `server.cleartext: false` enforced (HTTPS only)

## Relationship to Other Adapters

```
vanilla-htmx  (deployed as PWA → served over HTTPS)
     ↑
  capacitor   (Capacitor wraps same URL via WebView)
     ↓
 App Store / Play Store
```

React Native is deferred to M3-M4 as a separate adapter when paid customers report WebView performance issues.
