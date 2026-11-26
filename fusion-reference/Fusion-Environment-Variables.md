# Fusion Environment Variables

Environment variables that Fusion reads at runtime, taken from the `client-delivery` source tree on branch `develop`, 2026-11-23, and grouped by **who would set them**. For command-line switches, see [Fusion-Command-Line-Arguments.md](Fusion-Command-Line-Arguments.md).

## Setting variables

- **Shell or OS:** set the variable before Fusion starts. Most variables are read once, at startup or on first use, and many are cached in a `static`.
- **Override file:** at startup Fusion loads `<Documents>/Fusion 360/environment-variables.txt`, which has one `NAME=value` per line, and adds each entry to its own process environment (FUS-126165). Each loaded variable is written to the app log as `ENV: Initialized environment variables from …`. This is the easiest way to set variables for the macOS app bundle or the Windows launcher.
- **Windows:** variable names are case-insensitive.

> **Caution:** only categories 1–5 are intended for people outside the Fusion development team. Everything from category 6 on is for development, QA or Autodesk infrastructure. Some of those variables bypass licensing, security (TLS) or expiry checks, and several are compiled out of release builds anyway (marked "Internal builds only").

## How to read the tables

- **Area:**
  - `Core` is the platform layer (`Core/Neutron`).
  - `Core (Fusion/Services)` is `Core/Fusion` and `Core/Services`.
  - Any other area is the submodule that reads the variable.
- **Expected value:** what the code checks for. "Any non-empty" or "presence" means only whether the variable is set matters. `YES` comparisons are usually case-insensitive.
- **Notes:** "Internal builds only" means the code is compiled out when `END_USER_BUILD` is defined. "Debug only" means it sits inside `#ifdef _DEBUG`.
- **Variables read in more than one area** appear as one row per category. The extra areas' details are separated by line breaks.
- **Categories are a judgment call** based on what each variable does in the code. Nothing in the source marks them this way.

## Summary by category

| # | Category | Who sets it | Variables |
|---|---|---|---|
| 1 | [Graphics and display troubleshooting](#1-graphics-and-display-troubleshooting) | End users and support | 24 |
| 2 | [Diagnostics and logging](#2-diagnostics-and-logging) | Support (and users asked to gather logs) | 14 |
| 3 | [Network, proxy and transfer tuning](#3-network-proxy-and-transfer-tuning) | IT admins and support | 23 |
| 4 | [Deployment, updates and crash reporting](#4-deployment-updates-and-crash-reporting) | IT admins | 10 |
| 5 | [User paths and preferences](#5-user-paths-and-preferences) | End users | 6 |
| 6 | [Feature toggles and behaviour overrides](#6-feature-toggles-and-behaviour-overrides) | Developers and QA | 29 |
| 7 | [Server and environment overrides](#7-server-and-environment-overrides) | Developers and QA (internal) | 11 |
| 8 | [Hosted, automation and cloud worker contexts](#8-hosted-automation-and-cloud-worker-contexts) | Autodesk infrastructure | 38 |
| 9 | [Testing, QA and CI](#9-testing-qa-and-ci) | QA, test automation and build servers | 50 |
| 10 | [Developer only](#10-developer-only) | Fusion developers | 97 |
| 11 | [Set by Fusion itself](#11-set-by-fusion-itself) | Nobody (internal handshake) | 5 |
| 12 | [Standard OS and toolkit variables](#12-standard-os-and-toolkit-variables) | Read only (OS/installer-defined) | 32 |
| 13 | [Not active (code present but never runs)](#13-not-active-code-present-but-never-runs) | Nobody | 10 |
| | **Total** | | **349** |

## 1. Graphics and display troubleshooting

**Who:** End users and support. Workarounds for GPU, driver, remote-desktop and embedded-browser (Chromium) rendering problems. Change one at a time and remove it once the problem is understood.

| Variable | Area | Expected value | Function | Notes | Source |
|---|---|---|---|---|---|
| `DisableSoftwareRendererWarning` | Core | any non-empty | Suppresses the "using software renderer" toast. |  | `Core/Neutron/UI/Base/Application/Impl/NotifySoftwareRendererTask.cpp:23` |
| `EAGLE_GRAPHICS_BACKEND` | Electron | `qt`, `skia`, `skia_gpu` (case-insensitive) | Forces graphics backend; disables GPU-rendering checkbox when set; reported to analytics; standalone mode defaults it to `Qt` |  | Electron/EAGLE/src/display.cpp:965, Electron/EAGLE/src/d_set.cpp:1871, Electron/EAGLE/src/application/eagleapp_private.cpp:242, Electron/Electron/UI/ElectronUI.cpp:1033 |
| `EAGLE_GRAPHICS_SKIA_MULTITHREAD` | Electron | `0` disables | Disables multithreaded Skia paint recording |  | Electron/EAGLE/SkiaBridge/SkiaPaintRecorder.cpp:1230 |
| `EAGLE_HDPI_FULL_RESOLUTION` | Electron | `1` | HiDPI: render backing store at full device pixel ratio | Only with PassThrough DPI rounding policy | Electron/EAGLE/src/u_draw.cpp:969 |
| `EAGLE_HDPI_LOGICAL_RESOLUTION` | Electron | `1` | HiDPI: render backing store at logical resolution | Only with PassThrough DPI rounding policy | Electron/EAGLE/src/u_draw.cpp:970 |
| `EAGLE_METAL_USE_INTEL` | Electron | `1` allow / `0` disallow | Whether Intel low-power GPU may be used for Metal | macOS only | Electron/EAGLE/SkiaBridge/SkiaWindowContextMtl.mm:72 |
| `EAGLE_NO_MPO` | Electron | `1` force DX11 / `0` force DX12 | Selects D3D window context (multi-plane overlay workaround) | Windows only | Electron/EAGLE/SkiaBridge/SkiaWindowContextDx12.cpp:1568 |
| `FUSION360_RDPO_ENABLE` | Core | bool (`1`/`on`/`yes`/`true`, else false) | Overrides the RDP optimization enable option. |  | `Core/Neutron/Server/Scene/Options/RDPOptimizationOptions.cpp:94` (names at :160) |
| `FUSION360_RDPO_THROTTLE_EFFECT` | Core | bool | Overrides RDP throttle-effects. |  | `Core/Neutron/Server/Scene/Options/RDPOptimizationOptions.cpp:164` |
| `FUSION360_RDPO_THROTTLE_FRAMERATE_DURING_NAV` | Core | double (fps, default 10) | Overrides the frame-rate cap during navigation in RDP. |  | `Core/Neutron/Server/Scene/Options/RDPOptimizationOptions.cpp:161` |
| `FUSION360_RDPO_THROTTLE_MATERIAL` | Core | bool | Overrides RDP throttle-material. |  | `Core/Neutron/Server/Scene/Options/RDPOptimizationOptions.cpp:163` |
| `FUSION360_RDPO_THROTTLE_SHADED_DURING_NAV` | Core | bool | Overrides RDP throttle-shaded-during-nav. |  | `Core/Neutron/Server/Scene/Options/RDPOptimizationOptions.cpp:162` |
| `FUSION_CHROME_PREFS` | Core | `1` | Shows the hidden Chromium preferences (graphics backend, disable HTTPS-only) in Compatibility options. |  | `Core/Neutron/Server/BaseCore/Options/CompatibilityGroup.cpp:319` |
| `FUSION_GRAPHICS_PREFS` | Core | `1` | Applies the Chromium graphics backend preference to WebEngine flags (not on AppStream). |  | `Core/Neutron/UI/Base/Adaptations/QT/WebBrowser/QTWebBrowser.cpp:598` |
| `NEUTRON_CHROME_DISABLE_ACCELERATED_2D_CANVAS` | Core | `1` | Adds `--disable-accelerated-2d-canvas` to Chromium flags. |  | `Core/Neutron/UI/Base/Adaptations/QT/WebBrowser/QTWebBrowser.cpp:569` |
| `NEUTRON_CHROME_DISABLE_ACCELERATED_COMPOSITING` | Core | `1` | Adds `--disable-accelerated-compositing`. |  | `Core/Neutron/UI/Base/Adaptations/QT/WebBrowser/QTWebBrowser.cpp:575` |
| `NEUTRON_CHROME_DISABLE_GPU` | Core | `1` | Adds `--disable-gpu`. |  | `Core/Neutron/UI/Base/Adaptations/QT/WebBrowser/QTWebBrowser.cpp:563` |
| `NEUTRON_CHROME_DISABLE_GPU_RASTERIZATION` | Core | `1` | Adds `--disable-gpu-rasterization`. |  | `Core/Neutron/UI/Base/Adaptations/QT/WebBrowser/QTWebBrowser.cpp:581` |
| `NEUTRON_DISABLE_GL_METAL_LAYER` | Core | `1`/`on`/`yes`/`true` | Turns off the Metal device for the GL Metal layer. | Mac only | `Core/Neutron/Server/Scene/Platform/OS/Mac/GLMetalLayer.mm:68` |
| `NEUTRON_GRAPHICS_API` | Core | `AUTO`, `DX11` (Win), `OPENGLCORE`, `METAL` (Apple Silicon) | Overrides the graphics driver and virtual device choice. | Values are platform-specific | `Core/Neutron/Server/Scene/Options/GraphicsOptions.cpp:374`, `Core/Neutron/Server/Scene/Utility/SceneUtil.cpp:924` |
| `NEUTRON_GRAPHICS_CARD_VENDORID_OVERRIDE` | Core | integer vendor enum | Overrides the detected GPU vendor (for example when VMWare hides the GPU) so driver workarounds apply. | Win/Mac/Linux impls | `Core/Neutron/Server/Scene/Platform/OS/Windows/GraphicsDriverInfo.cpp:370` |
| `NEUTRON_WEBBROWSER_ALLOW_GPU_BLACKLIST` | Core | `1` | Stops adding `--ignore-gpu-blocklist`, so Chromium honors the GPU blocklist. |  | `Core/Neutron/UI/Base/Adaptations/QT/WebBrowser/QTWebBrowser.cpp:590` |
| `QT_D3D_NO_FLIP` | Core | any (presence) | If the user has not set it, Fusion decides itself (it leaves it off when a DisplayLink device is present). Its state is logged with the RHI info. | Windows (decision), all (logging) | `Core/Neutron/UI/Base/Application/Impl/implApplication.cpp:1799`, `Core/Neutron/UI/Base/Adaptations/QT/Application/QTApplication.cpp:2001` |
| `QTWEBENGINE_CHROMIUM_FLAGS` | Electron | Chromium flags | Appends `--supports-dual-gpus=true` unless already specified |  | Electron/EAGLE/src/application/eagleapp_private.cpp:574 |

## 2. Diagnostics and logging

**Who:** Support (and users asked to gather logs). Extra logging, crash-dump detail and log retention. These are safe to set temporarily while gathering information for a support case.

| Variable | Area | Expected value | Function | Notes | Source |
|---|---|---|---|---|---|
| `APPLOG_FOR_PERFORMANCE` | Core<br>Core (Fusion/Services) | `YES` (case-insens.)<br>`YES` (case-insensitive) | Turns on performance applog and startup clocks, plus timing logs for home tab, open, copy and move workflows.<br>*Core (Fusion/Services):* Logs start/end timestamps for Data Panel / CloudBrowser workflows (move, copy, delete, recents). Same effect as the `logApphomePerfomance` general option. | All builds. Read in MoveItems, CopyItems, DeleteItems (x3), GetRecentItems. | `Core/Neutron/Server/BaseCore/AppLog/AppPerfLog.cpp:33`, `Core/Neutron/Server/BaseCore/clocks/ClockMgr.cpp:428`<br>`Core/Services/Data/CloudBrowser/Workflows/GetRecentItems.cpp:38` |
| `EAGLE_ENABLE_DRED_REPORT` | Electron | `1` | Enables D3D12 DRED (device-removed breadcrumbs) reporting | Windows (DX12) only | Electron/EAGLE/SkiaBridge/SkiaWindowContextDx12.cpp:229, :245 |
| `EAGLE_SHOW_DIAGNOSTIC` | Electron | `1` | Enables draw-window diagnostic overlay (fps) | Debug aid | Electron/EAGLE/src/u_draw.cpp:1662 |
| `ENABLE_LOG_APPEARANCE_DIALOG` | Core (Fusion/Services) | `yes` (exact, lowercase) | Writes material/appearance download log lines to `<temp>/AppearanceDialog.txt`. | All builds. Read once (static). | `Core/Fusion/Server/Fusion/Materials/MaterialDownloadHelper.cpp:43` |
| `FORCE_STOP_ADEXMTSV` | Core | `true`/`YES`/`1` (case-insens.) | Force-kills the adexmtsv process. | Mac only | `Core/Neutron/UI/Base/Application/Impl/implApplication.cpp:940` |
| `LOG_ENTITLEMENT` | Core | `YES` | Logs the entitlement JSON to applog. |  | `Core/Neutron/Client/Base/Client/Cloud/EntitlementHelper.cpp:2259` |
| `NEUTRON_CER_LEVEL` | Core | `1` or `2` | Minidump detail: `1` adds indirect memory, `2` adds full memory info, handles, threads and more. | Windows only | `Core/Neutron/Server/Base/OS/Windows/DumpMiniDump.cpp:49` |
| `NEUTRON_LIVE_UPDATE_DISPLAYERRORS` | Core (Fusion/Services) | `DISPLAY` (exact) | Shows live-update Python errors as text-command output. They are hidden otherwise. | All builds. | `Core/Services/Platform/LiveUpdate/LiveUpdateBase.cpp:98` |
| `NEUTRON_LOG_FILE_SAVE_DURATION` | Core | integer days (default 15) | How long log files are kept. |  | `Core/Neutron/Server/BaseCore/AppLog/AppLogMgr.cpp:208` |
| `NEUTRON_LOG_GRAPHICS` | Core | `1` | Forces graphics logging on (including during init). |  | `Core/Neutron/Server/Scene/Options/GraphicsOptions.cpp:1118` |
| `nwreqinfo-log` | Core | any (presence) | Logs network request headers to the log file. |  | `Core/Neutron/Server/Base/Utility/NetworkRequestInfo.cpp:599` |
| `OS3_VERBOSE` | Core (Fusion/Services) | `1` | Turns on verbose OSS logging and analytics. | All builds. | `Core/Services/Data/WIPDataModel/OSSService/OSSService.cpp:84` |
| `PIM_LOGLEVEL` | Core (Fusion/Services) | `DEBUG` (case-insensitive) | Sets the PIM log manager default level to Debug. | All builds. | `Core/Services/Data/PIM/PIMLogMgr.cpp:129` |
| `RECENTS_DIAGNOSTICS` | Core (Fusion/Services) | `YES` (case-insensitive) | Writes Recents diagnostics (JSON payloads) to the app log. | All builds. | `Core/Services/Data/CloudBrowser/API/Impl/Recents.cpp:68` |

## 3. Network, proxy and transfer tuning

**Who:** IT admins and support. TLS/certificate handling, proxy behaviour, feature-flag and push-notification transport, offline mode, MCP server allowlists, and cloud transfer tuning (OSS/S3 thread counts, chunk sizes, timeouts).

| Variable | Area | Expected value | Function | Notes | Source |
|---|---|---|---|---|---|
| `ADEXMTSV_TIMEOUT_MS` | Core | integer ms (default 60000) | Overrides the network timeout of Protein's adexmtsv restart policy. |  | `Core/Neutron/UI/Base/Application/Impl/implApplication.cpp:1442` |
| `CLOSE_SERVER_VERIFY_DLG` | Core | `YES` | Suppresses the SSL "Server Verification Warning" dialog. |  | `Core/Neutron/UI/Base/Cloud/CloudController.cpp:150` |
| `CURLOPT_CAINFO` | Core | `0` or other | `0` = use the OS CA store. Any other value = use the bundled CA bundle. When unset: custom CA on Linux, OS store elsewhere. | Default differs on Linux | `Core/Neutron/Server/Base/Utility/HTTPClient.cpp:432`, `Core/Neutron/Server/Base/Utility/HTTPClient.cpp:438` |
| `CURLSSLOPT_NO_REVOKE` | Core | `1` | Adds `CURLSSLOPT_NO_REVOKE` (turns off certificate revocation checks). |  | `Core/Neutron/Server/Base/Utility/HTTPClient.cpp:484` |
| `CURLSSLOPT_REVOKE_BEST_EFFORT` | Core | `0` | Turns off the default `CURLSSLOPT_REVOKE_BEST_EFFORT` (strict revocation checks). |  | `Core/Neutron/Server/Base/Utility/HTTPClient.cpp:488` |
| `DISABLE_PUSH_NOTIFICATIONS` | Core (Fusion/Services) | `TRUE` (case-insensitive) | Turns off push notifications (PubNub) and logs it once. | Windows only. | `Core/Services/Platform/PushNotifications/PushNotificationManager.cpp:296` |
| `FUSION_FLAGS_ALLOW_PEER_VERIFY` | Core (Fusion/Services) | Any non-empty | Lets the LaunchDarkly (feature flag) client use SSL peer verification, following the SSL verify-peer preference. Peer verification is off otherwise. | All builds. Read at init and when the option changes. | `Core/Services/Platform/LDCSDKWrapper/LDCSDKWrapper.cpp:278` |
| `FUSION_MCP_HOST_ALLOWLIST` | Core (Fusion/Services) | Comma/semicolon-separated host list | Extra allowed `Host` headers for the local MCP HTTP server (127.0.0.1:27182/mcp). | All builds. Read through `readAllowlistEnv(name)`. | `Core/Services/Platform/MCP/MCPManager.cpp:123` |
| `FUSION_MCP_ORIGIN_ALLOWLIST` | Core (Fusion/Services) | Comma/semicolon-separated origin list | Allowed `Origin` headers for the local MCP HTTP server. Empty means every Origin is rejected. | All builds. Read through `readAllowlistEnv(name)`. | `Core/Services/Platform/MCP/MCPManager.cpp:124` |
| `FUSION_POLL_FOR_FLAGS` | Core (Fusion/Services) | Non-empty and not `0`/`false`/`off` | Switches the LaunchDarkly feature-flag client from streaming (SSE) to polling mode (FUS-104668). | All builds. | `Core/Services/Platform/LDCSDKWrapper/LDCSDKWrapper.cpp:310` |
| `FUSION_USE_LEGACY_PROXY_BEHAVIOR` | Core | any (presence) | Uses the legacy proxy behaviour. |  | `Core/Neutron/Server/Base/Utility/ProxyManager.cpp:350` |
| `FUSION_USE_NEW_PROXY_BEHAVIOR` | Core | any (presence) | Uses the new proxy behaviour. Wins if both proxy-behaviour vars are set. |  | `Core/Neutron/Server/Base/Utility/ProxyManager.cpp:352` |
| `NEUTRON_CLOUD_DISABLE` | Core (Fusion/Services) | Any non-empty | Turns off cloud access (`BaseAuth` reports cloud disabled). | All builds. Cached on first read. | `Core/Services/Platform/Ad360/Base/BaseAuth.cpp:57` |
| `NEUTRON_FORCE_OFFLINE` | Core | `YES` (case-insens.) | Forces startup in offline mode. |  | `Core/Neutron/Server/Base/Options/Network/NetworkOptionGroup.cpp:35` |
| `OS3_ENABLE` | Core (Fusion/Services) | `1` or `0` | Forces S3 (direct OSS) transfer on (`1`) or off (`0`). Unset means feature flags decide. | All builds. | `Core/Services/Data/WIPDataModel/OSSService/OSSService.cpp:67` |
| `OS3_USEACCEL` | Core<br>Core (Fusion/Services) | `0` / `1`<br>`1` or other | If set, the "Disable transfer acceleration" preference checkbox shows partially-checked (env override in effect). Purpose beyond the UI is unclear from this code.<br>*Core (Fusion/Services):* Overrides transfer acceleration (`1` on, any other non-empty value off). Default comes from the compatibility option. | All builds. | `Core/Neutron/UI/Base/Adaptations/QT/Dialogs/QTPreferencesDialog.cpp:3535`<br>`Core/Services/Data/WIPDataModel/OSSService/OSSService.cpp:99` |
| `OS3_USECDN` | Core<br>Core (Fusion/Services) | `0` / `1`<br>`1` or other | Same as `OS3_USEACCEL`, for CDN use.<br>*Core (Fusion/Services):* Overrides CDN use for OSS transfers (`1` on, any other non-empty value off). | All builds. | `Core/Neutron/UI/Base/Adaptations/QT/Dialogs/QTPreferencesDialog.cpp:3534`<br>`Core/Services/Data/WIPDataModel/OSSService/OSSService.cpp:92` |
| `OSS_CHUNK_SIZE` | Core (Fusion/Services) | Integer MB, 1-15 | Overrides the OSS upload chunk size. | All builds. | `Core/Services/Data/WIPDataModel/OSSService/OSSServiceSDK.cpp:617` |
| `OSS_DOWNLOAD_THREADS` | Core (Fusion/Services) | Integer 1-16 | Overrides the OSS download thread-pool size. | All builds. | `Core/Services/Data/WIPDataModel/OSSService/OSSServiceSDK.cpp:592` |
| `OSS_UPLOAD_THREADS` | Core (Fusion/Services) | Integer 1-16 | Overrides the OSS upload thread-pool size. | All builds. | `Core/Services/Data/WIPDataModel/OSSService/OSSServiceSDK.cpp:609` |
| `pubNubExpiredChannelTimeout` | Core (Fusion/Services) | Channel-expiration value (string) | Sent as the `x-ads-channel-expiration` header when a WIP PubNub channel is requested. | All builds. | `Core/Services/Platform/PushNotifications/PubNubSubscriber.cpp:331` |
| `pubNubSubscribeTimeout` | Core (Fusion/Services) | Integer (PubNub transaction timeout) | Overrides the PubNub subscribe transaction timeout (default 5 min). Normally set by the `pubnub.timeout` text command. | All builds. | `Core/Services/Platform/PubNub/api/pubNubAPI.cpp:133` |
| `uploadTimeout` | Core (Fusion/Services) | Integer minutes (default 60) | Timeout before a WIP push-notification / translation-for-open job is given up. | All builds. Also read in WIPPushNotifyTranslationForOpenStep.cpp:55. | `Core/Services/Data/WIPDataModel/Jobs/WIPPushNotificationStep.cpp:66` |

## 4. Deployment, updates and crash reporting

**Who:** IT admins. Controls live update, update snooze, the Service Utility and crash reporting (CER) in managed deployments.

| Variable | Area | Expected value | Function | Notes | Source |
|---|---|---|---|---|---|
| `FUSION_SERVICE_UTILITY` | Core (Fusion/Services) | `DISABLE` | Turns off the Safe Mode / Service Utility launch path. | Fusion360Application. | `Core/Fusion/Applications/Fusion360Application/SafeMode/ServiceUtility.cpp:21` |
| `FUSION_SERVICE_UTILITY_STREAM` | Core (Fusion/Services) | Stream name string | Overrides the release stream the Service Utility uninstall uses. | Uninstall flow (wscript) is Windows. | `Core/Fusion/Applications/Fusion360Application/SafeMode/ServiceUtility.cpp:27` |
| `FUSION_UPDATE_SNOOZE` | Core (Fusion/Services) | `DISABLE` | Turns off the live-update snooze feature (enabled by default). | Read once at static init. | `Core/Services/Platform/LiveUpdate/LiveUpdateMgr.cpp:60` |
| `FUSION_UPDATE_SNOOZE_CHECK_INTERVAL` | Core (Fusion/Services) | Integer minutes | Overrides the snooze update-check interval (used by CheckUpdatesCmd). | Read once at static init. | `Core/Services/Platform/LiveUpdate/LiveUpdateMgr.cpp:62` |
| `FUSION_UPDATE_SNOOZE_COMMANDS` | Core (Fusion/Services) | `ENABLE` | Turns on snooze text commands (disabled by default). | Read once at static init. | `Core/Services/Platform/LiveUpdate/LiveUpdateMgr.cpp:69` |
| `FUSION_UPDATE_SNOOZE_CONFIG_ENCRYPTION` | Core (Fusion/Services) | `DISABLE` | Turns off encryption of the snooze/update config file (enabled by default). | Read once at static init. | `Core/Services/Platform/LiveUpdate/LiveUpdateMgr.cpp:68` |
| `FUSION_UPDATE_SNOOZE_DURATION_COMMERCIAL` | Core (Fusion/Services) | Integer (`stoi`) | Overrides the maximum snooze duration for commercial users. | Read once at static init. | `Core/Services/Platform/LiveUpdate/LiveUpdateMgr.cpp:64` |
| `FUSION_UPDATE_SNOOZE_DURATION_OTHERS` | Core (Fusion/Services) | Integer (`stoi`) | Overrides the maximum snooze duration for non-commercial users. | Read once at static init. | `Core/Services/Platform/LiveUpdate/LiveUpdateMgr.cpp:66` |
| `NEUTRON_DISABLE_CER` | Core<br>Core (Fusion/Services) | any non-empty<br>Any non-empty | Skips CER (crash error reporting) initialization.<br>*Core (Fusion/Services):* Skips CER (crash error reporting) component init. On Windows it also skips turning off WER at exit. | Init is in the console app. The WER step (Fusion360.cpp:191) is Windows only. The read at ConsoleAppImpl.cpp:832 is commented out. | `Core/Neutron/UI/Base/Application/Impl/implApplication.cpp:3685`<br>`Core/Fusion/Applications/Fusion360ConsoleApplication/ConsoleAppImpl.cpp:1020` |
| `NEUTRON_LIVE_UPDATE` | Core (Fusion/Services) | `DISABLE` | Turns off live-update checks and the snooze feature. | The LiveUpdateBase check is skipped in `_DEBUG` when simulating an update test, and has no effect when `LIVEUPATE_DEBUG != 0`. | `Core/Services/Platform/LiveUpdate/LiveUpdateBase.cpp:1234` |

## 5. User paths and preferences

**Who:** End users. Personal overrides such as home and template folders, locale, and default EAGLE options.

| Variable | Area | Expected value | Function | Notes | Source |
|---|---|---|---|---|---|
| `ADSK_UIA_SUPPORT` | Core | any non-empty | Installs the Marking Menu UI Automation (accessibility) factory. | Windows reads via `getenv_s`; other OSes via `getenv` | `Core/Neutron/UI/Base/Adaptations/QT/MarkingMenus/src/UIA/UIAController.cpp:51` |
| `EAGLE` | Electron | Command-line option string | Default EAGLE command-line options (response env) prepended to args |  | Electron/EAGLE/src/options.cpp:399 (name passed from Electron/EAGLE/src/application/eagleapp_private.cpp:459) |
| `EAGLE_HOME` | Electron | Directory | Overrides EAGLE home directory (else Documents on Windows, `HOME` elsewhere) |  | Electron/EAGLE/src/csio.cpp:257 |
| `FORCE_DECIMAL_GERBER_OUTPUT` | Electron | `true` (case-insensitive) | Forces `C` numeric locale during Gerber X2 export |  | Electron/EAGLE/src/cam_ui/processor/gerberx2export.cpp:72 |
| `MAG_FORCED_LOCALE` | Make | Qt locale name (e.g. `de_DE`) | Overrides Fabrication add-in locale (else from Fusion UI language) |  | Make/Fabrication/Server/MSFFusionAbstraction/src/MSFFsnAddin.cpp:32 |
| `MYTEMPLATEDIR` | Publish | Directory | Overrides drawing template directory | Dev use only; `_wdupenv_s` | Publish/AcFusionDoc/AcFusionService/AcFusionTemplateManager.cpp:204 |

## 6. Feature toggles and behaviour overrides

**Who:** Developers and QA. Forces a feature, algorithm or UI variant on or off, overriding feature flags. Not supported for production use.

| Variable | Area | Expected value | Function | Notes | Source |
|---|---|---|---|---|---|
| `BrowserSegmentationEnabled` | Core | `YES` | Turns on browser segmentation regardless of the `design-performance-segmentation` flag. |  | `Core/Neutron/Server/DataModel/Segment/Segment.cpp:342` |
| `CONVERTARRANGETOCREATENEWCOMPONENTS` | Core (Fusion/Services) | `1` | Arrange creates new components (`ArrangeUtil::isConvertToCreateNewComponents`). | All builds. | `Core/Fusion/Server/Fusion/DesignCapture/Arrange/ArrangeUtil.cpp:1297` |
| `CORE_ENABLE_DOUBLE_BUFFER` | Publish | Presence | Use 2 IOSurface buffers instead of 1 | macOS only | Publish/AcFusionDoc/AcCoreConsole/osx/IOSurface/AcIOSurface.mm:28 |
| `DISABLE_DASHBOARD` | Publish | `YES` (case-insensitive) | Disables Qontext dashboard (`CloudOptionGroup::dashboardDisabled`) in Animation/Publisher UI |  | Publish/Animation/UI/AnimationUI/PublisherUI.cpp:306 |
| `EAGLE_USE_NEW_CYCLE_FINDER` | Electron | Integer; `1` (default) on | Toggles new cycle-finder algorithm |  | Electron/EAGLE/src/eaglerc.cpp:268 |
| `ENABLE2DARRANGEMESHBODY` | Core (Fusion/Services) | `1` | Allows mesh bodies in 2D Arrange. | All builds. | `Core/Fusion/Server/Fusion/DesignCapture/Arrange/ArrangeUtil.cpp:845` |
| `ENABLE_ANIMATION` | Publish | `YES` (case-insensitive) | Enables the Animation environment |  | Publish/Animation/UI/AnimationUI/Utils/CommonUtils.cpp:1042 |
| `EnableOnDemandLoad` | Core | `YES` (other non-empty = off) | Overrides the on-demand segment load option. |  | `Core/Neutron/Server/BaseCore/Options/GeneralOptionGroup.cpp:2134` |
| `ENV_EXTENSION_MANAGER_FCDR` | Core | `true` | Forces Extension Manager V2 on. |  | `Core/Neutron/Server/BaseCore/Utility/CheckFeatureFlags.cpp:1435` |
| `ENV_MY_FUSION_V2` | Core | `true` | Forces My Fusion V2 on. |  | `Core/Neutron/Server/BaseCore/Utility/CheckFeatureFlags.cpp:1386` |
| `ENV_MY_FUSION_VARIANT` | Core | variant string | Overrides the My Fusion variant flag value. |  | `Core/Neutron/Server/BaseCore/Utility/CheckFeatureFlags.cpp:1392` |
| `ENV_SUPPORT_ZERO_DOCUMENT` | Core | `yes` | Overrides the `SupportZeroDocument` feature flag (zero-document mode). In testing/build-machine context, only `yes` turns it on. |  | `Core/Neutron/Server/BaseCore/Options/GeneralOptionGroup.cpp:936`, `Core/Neutron/Server/BaseCore/Options/GeneralOptionGroup.cpp:2269` |
| `FORGE_REPLACE_SEL` | Core (Fusion/Services) | `FALSE` (exact) to disable | Turns off "replace selection" support in the T-Spline/Form SubD modeling command. Enabled by default. | All builds. Checked once. | `Core/Fusion/UI/TSplineUI/Commands/Form/SubDModelingCmd.cpp:68` |
| `_FUSION_DRAWING_ENABLE_BACKGROUND_PROCESS_` | Publish | JSON, e.g. `{"how_many_sheets_per_process":N,"debugging":"..."}` | Enables background drawing-sheet refresh via AcCoreConsole when valid JSON; sets sheets per process; non-empty `debugging` adds `/pause` arg |  | Publish/FusionDoc/UI/FusionDocUI/SheetSet/DrawingSheetRefresher.cpp:167, :589 |
| `FUSION_REGIONALIZATION_FLAG_ENABLED` | Core | `1` | Forces regionalization on (OR with the `fusion-regionalization` flag). |  | `Core/Neutron/Server/BaseCore/Utility/CheckFeatureFlags.cpp:733` |
| `FUSION_THO_REGIONALIZATION_FLAG_ENABLED` | Core | `1` | Forces THO regionalization on (needs regionalization on too). |  | `Core/Neutron/Server/BaseCore/Utility/CheckFeatureFlags.cpp:745` |
| `_INV_SUPPRESSINTERIORCUTLINE_ALIGNED` | Publish | Integer; >0 suppress, 0 show (default: suppress) | Suppress interior cut lines in aligned section views (DrawingViewCompute) | Uses `_wdupenv_s` (MSVC CRT); read once | Publish/AcFusionDoc/DrawingViewCompute/View/DrawingView.cpp:1461 |
| `_INV_SUPPRESSINTERIORCUTLINE_OFFSET` | Publish | Integer; >0 suppress (default: not suppressed) | Suppress interior cut lines in offset section views | Uses `_wdupenv_s`; read once | Publish/AcFusionDoc/DrawingViewCompute/View/DrawingView.cpp:1478 |
| `IRON_BETA_MODE` | Make | `1` | Enables beta-testing feature flags |  | Make/IronLib/core/IronApplication.cpp:1485 |
| `IRON_USE_INTERNAL_EDITOR` | Make | `1` | Forces use of internal (NC) editor in normal builds |  | Make/NeuCAM/UI/NeuCAMUI/NeutronUIHost.cpp:1413 |
| `MAGEnableHig` | Make | Non-empty | Applies HIG stylesheet to Fabrication UI |  | Make/Fabrication/UI/MSFCommonUI/src/MSFCmnUIManager.cpp:285 |
| `MAGFusionUseSmartran` | Make | `1` | Use Smartran translation mode instead of in-memory (nesting) |  | Make/Fabrication/Server/MSFNesting/src/MSFNestTranslationSelector.cpp:53, :124 |
| `MFG_EXT_TRIALAVAIL` | Core | `yes` | Forces the extension trial availability override to "yes". |  | `Core/Neutron/Server/BaseCore/Utility/CheckFeatureFlags.cpp:628` |
| `_NEUTRON_DATAPANEL_PROJECT_PUNCHOUT_` | Core (Fusion/Services) | `1` | Turns on the "punch out" (open in browser) flow for joining a project from the Data Panel project list. | Non-`END_USER_BUILD` only. | `Core/Services/Data/CloudBrowser/Workflows/GetProjectList.cpp:597` |
| `NEUTRON_SHOW_INTERNAL_PREVIEW_FEATURES` | Core | any non-empty | The Feature Packs option filter defaults to show everything, including internal previews. |  | `Core/Neutron/UI/Base/Adaptations/QT/FeaturePacks/UIFeaturePackOptionGroup.cpp:202` |
| `NotCalculateMassProperty` | Core (Fusion/Services) | `1` | Midsurface/shell thickness estimation does not use mass properties. | All builds. Read in SurfaceMidsurfaceShellCmd (x3), SurfaceMidsurfaceShellRequest (x2), MidSurfaceComputeUtil. | `Core/Fusion/Server/Fusion/Features/ComputeUtil/MidSurfaceComputeUtil.cpp:198` |
| `SIMULUS_BEARING_LOAD_REFINEMENT_DIVISOR` | Simulation | Positive number (default 32) | Bearing-load mesh refinement divisor | Env only on mac/Linux (Windows reads HKCU\Software\Autodesk\SimStudio registry); env path only checks presence, value is not returned | Simulation/Simulation/Server/Common/Utility/SimRegistryUtils.cpp:88 via Simulation/Simulation/Server/StructuralAttributes/Objects/SimBearingLoad.cpp:284, Simulation/Simulation/Controllers/LinearAnalysis/Controller/Objects/SimController.cpp:4760 |
| `SIMULUS_MESH_LIMIT_SCALING_FACTOR` | Simulation | Unsigned int (default 8) | Mesh-size job limit scaling factor | Env only on mac/Linux (Windows: registry); env path only checks presence, value not returned | Simulation/Simulation/Server/Common/Utility/SimRegistryUtils.cpp:88 via Simulation/Simulation/Controllers/LinearAnalysis/Controller/Utility/JobSizeLimiter.cpp:61 |
| `SKETCH_FORCE_FCA` | Core (Fusion/Services) | Any non-empty | Forces global fully-constrained checking on for sketches. | All builds. | `Core/Fusion/Sketch/Server/Sketch/Objects/MSketch.cpp:1326` |

## 7. Server and environment overrides

**Who:** Developers and QA (internal). Points Fusion at staging/dev back ends (Oxygen auth, PLM, Qontext, CDE, FCDR, EAGLE web services). Several only work in internal builds.

| Variable | Area | Expected value | Function | Notes | Source |
|---|---|---|---|---|---|
| `EAGLE_FEWS_URL` | Electron | URL | Overrides FEWS server base URL |  | Electron/EAGLE/src/webapi/content.cpp:1951 |
| `EAGLEDEVENVIRONMENT` | Electron | `ALPHA`, `ALPHA_WITH_LOCAL_EDITORS`, `BETA`, `BETA_WITH_LOCAL_EDITORS`, `STAGING`, `LOCAL`, `OFFLINE`, `PRODBACKEND`; empty = production | Selects web-service environment/URLs; standalone mode defaults it to `BETA` |  | Electron/EAGLE/src/webapi/webapi.cpp:220, Electron/EAGLE/src/webapi/frrwebapiurls.cpp:163, Electron/EAGLE/src/webapi/content.cpp:1910, Electron/EAGLE/src/application/eagleapp_private.cpp:239 |
| `EAGLEDEVLICENSE` | Electron | Edition name (`free`, `premium`, ...) | Developer license edition override for `@autodesk.com` accounts | Only when compiled with `DEBUG_WEBAPIINTERFACE == 1` | Electron/EAGLE/src/webapi/webapiinterface.cpp:129 |
| `ENV_MY_FUSION_URL` | Core | URL | Overrides the My Fusion home-tab URL. | Internal builds only | `Core/Neutron/UI/Commands/UDA/HomeTabDef.cpp:131` |
| `NEUTRON_CDE_URL_<CDEID>` | Core | URL | Overrides the URL of the CDE component. `<CDEID>` = cdeId upper-cased with `-` replaced by `_`. | Internal builds only | `Core/Neutron/UI/Commands/CDE/CDEMgr.cpp:78` |
| `NEUTRON_FCDR_FRR_TESTING` | Core (Fusion/Services) | `1` | FRR component loads `testing/ApplicationOptions.json` instead of `ApplicationOptions.json`. | All builds. | `Core/Services/Platform/FCDR/FCDRComponent.cpp:118` |
| `NEUTRON_FCDR_FRR_USAGE` | Core (Fusion/Services) | `0` or `1` | `0` force-disables FRR (Fusion region registry) content, `1` force-enables it. Also shown by a region diagnostic text command. | All builds. Name comes from the constant `NEUTRON_FCDR_FRR_USAGE_ENV` (FCDRComponentDefinition.cpp). | `Core/Services/Platform/FCDR/FCDRComponentDefinition.cpp:29` |
| `NEUTRON_FCDR_VERSION_OVERRIDE` | Core (Fusion/Services) | `MAJOR.MINOR.BUILD` version | Overrides the software version FCDR (Fremont) content requests use. An invalid value is ignored with a warning. Also shown by a region text command. | All builds. Name comes from `NEUTRON_FCDR_VERSION_OVERRIDE_ENV` (FCDRMgrImpl.cpp:42). | `Core/Services/Platform/FCDR/FCDRMgrImpl.cpp:51` |
| `NEUTRON_OXYGEN_OVERRIDE` | Core (Fusion/Services) | `DEV` \| `PRODUCTION` \| anything else (Staging) | Picks the Oxygen (auth) server target: Development, Production or Staging. Replaces the built-in default. | All builds. Static init. Name comes from the constant `OXYGEN_OVERRIDE` (OxygenOptionGroup.cpp:23). | `Core/Services/Platform/Ad360/Base/OxygenOptionGroup.cpp:31` |
| `NEUTRON_PLM_OVERRIDE` | Core (Fusion/Services) | URL | Overrides the PLM REST services URL. | All builds. Static init. Name comes from `PLM_OVERRIDE` (OxygenOptionGroup.cpp:24). | `Core/Services/Platform/Ad360/Base/OxygenOptionGroup.cpp:56` |
| `NEUTRON_QONTEXT_OVERRIDE` | Core (Fusion/Services) | URL | Overrides the Qontext webpage URL. | All builds. Static init. Name comes from `QONTEXT_OVERRIDE` (OxygenOptionGroup.cpp:25). | `Core/Services/Platform/Ad360/Base/OxygenOptionGroup.cpp:60` |

## 8. Hosted, automation and cloud worker contexts

**Who:** Autodesk infrastructure. Set by Fusion Automation Service (FAS) workers, AppStream/Fusion Online (Chotay), containers, headless Linux and cloud translators. Includes client-credential variables, of which only the names are listed here.

| Variable | Area | Expected value | Function | Notes | Source |
|---|---|---|---|---|---|
| `ACP_RUNTIME_OVERRIDES_LAMBDAS_EMAG_ANSYS_MOM` | Electron | String (override value) | Forwarded as `x-adsk-environment-variables` header on EMag cloud simulation requests | Non-public builds only (`#ifndef EAGLE_PUBLIC_BUILD`) | Electron/EAGLE/src/Emag/CloudJobs/SimulationJob.cpp:138 |
| `CHOTAY_APP` | Core | `1` | Marks the session as an AppStream/Fusion Online (Chotay) session. On Windows it also enables the `NEUTRON_DEVICE_THEME` override. |  | `Core/Neutron/Server/Base/Utility/AppStream.cpp:71`, `Core/Neutron/Server/Platform/OS/Windows/WindowsPlatform.cpp:1138` |
| `CHOTAY_BASE_URL` | Core | URL | AppStream base URL (`getAppStreamURL`). |  | `Core/Neutron/Server/Base/Utility/AppStream.cpp:101` |
| `CHOTAY_SESSION_ID` | Core | string | AppStream session ID. |  | `Core/Neutron/Server/Base/Utility/AppStream.cpp:96` |
| `CHOTAY_USER_ID` | Core | string | AppStream user ID. |  | `Core/Neutron/Server/Base/Utility/AppStream.cpp:91` |
| `CONTAINER_FILE_PATH` | Core | relative path | Appended to `DOCKER_WORKING_DIRECTORY` to give the TypeScript API working-files path. |  | `Core/Neutron/API/TypeScript/Build/ObjectWrapper.cpp:418` |
| `COPY_FOLDER_BEFORE` | Core (Fusion/Services) | Comma-separated folder list | Automation API (FAS worker) setting: folders to copy before a job. Overrides XML `fusionworker/copy/before`. | All builds. Read through the `Configuration` settings table (`pSetting->regestryKey`). | `Core/Fusion/Server/AutomationAPI/AutomationAPI/Configuration.cpp:100` |
| `COS_ADSK_LEGACY_REGION` | Core (Fusion/Services) | Region ID string (lowercased by the code) | Sets the region for CloudTranslation and other headless cloud apps instead of the default region lookup. | All builds. | `Core/Services/Data/CloudTranslatorBrowser/CloudTranslatorBrowser.cpp:28` |
| `DOCKER_WORKING_DIRECTORY` | Core | path | Base of the TypeScript API working-files path in containers. If unset, `typeScriptFilesPath()` is used. |  | `Core/Neutron/API/TypeScript/Build/ObjectWrapper.cpp:417` |
| `env` | Publish | `prd` / `stg` (case-insensitive) | FusionDocToLMV translator: detect production/staging build environment (falls back to client-ID check) | Lowercase name (constant `EXTRACTOR_BUILD_ENV_VAR`); cloud worker | Publish/FusionDoc/Translator/FusionDocToLMV/FusionDocToLMV.cpp:105, :129 (const in Publish/FusionDoc/Translator/FusionDocToLMV/Utils/TranslationConstants.h:89) |
| `f2d_extractor_key` | Publish | OAuth client ID | Client ID for access-token creation; also used to infer prod/staging environment | Constant `EXTRACTOR_KEY`; cloud worker | Publish/FusionDoc/Translator/FusionDocToLMV/FusionDocToLMV.cpp:117, :141, Publish/FusionDoc/Translator/FusionDocToLMV/Utils/ApiClient.cpp:78 (via Translator/DrawingQSTranslator.cpp:651) |
| `f2d_extractor_secret` | Publish | OAuth client secret | Client secret for access-token creation | Constant `EXTRACTOR_SECRET`; cloud worker | Publish/FusionDoc/Translator/FusionDocToLMV/Utils/ApiClient.cpp:79 (via Translator/DrawingQSTranslator.cpp:651) |
| `f3d_extractor_key` | Core (Fusion/Services) | Client ID string | Client ID FusionProducer uses to create an API access token. Token creation fails if this is empty. | All builds. Name comes from `EXTRACTOR_KEY` in `FusionProducerConstants.h:58`. | `Core/Fusion/Translators/FusionProducer/FusionProducer/ApiClient.cpp:68` |
| `f3d_extractor_secret` | Core (Fusion/Services) | Client secret string | Client secret paired with `f3d_extractor_key` for the FusionProducer access token. | All builds. Name comes from `EXTRACTOR_SECRET` in `FusionProducerConstants.h:59`. Secret. | `Core/Fusion/Translators/FusionProducer/FusionProducer/ApiClient.cpp:70` |
| `FAS_ACP_HTTP_TIMEOUT` | Core (Fusion/Services) | Integer seconds (default 20) | Automation API HTTP timeout. Overrides XML `fusionworker/acp/timeout`. | Read through the Configuration settings table. | `Core/Fusion/Server/AutomationAPI/AutomationAPI/Configuration.cpp:100` |
| `FAS_CONFIG_PATH` | Core (Fusion/Services) | Path to XML file | Automation API config XML. Read only when the working directory (`FASCONTROLPATH`) is not set. | All builds. | `Core/Fusion/Server/AutomationAPI/AutomationAPI/AutomationAddin.cpp:29` |
| `FAS_CONTAINER_ENDPOINT` | Core<br>Core (Fusion/Services) | URL prefix<br>URL/endpoint string | Requests starting with this URL are allow-listed (add-in to runner communication) in FAS.<br>*Core (Fusion/Services):* Automation API container runner endpoint. Overrides XML `fusionworker/container/endpoint`. | Read through the Configuration settings table. | `Core/Neutron/Server/Base/Utility/FusionAutomationService.cpp:87`<br>`Core/Fusion/Server/AutomationAPI/AutomationAPI/Configuration.cpp:100` |
| `FAS_EXECUTION` | Core (Fusion/Services) | `sandbox` \| `internal` \| `runner` (or 0/1/2); default sandbox | Automation API execution mode. | Read through the Configuration settings table. An invalid value throws. | `Core/Fusion/Server/AutomationAPI/AutomationAPI/Configuration.cpp:100` |
| `FAS_EXIT_MODE` | Core (Fusion/Services) | `graceful` \| `forcekill` (or 0/1); default graceful | Automation API exit mode. | Read through the Configuration settings table. An invalid value throws. | `Core/Fusion/Server/AutomationAPI/AutomationAPI/Configuration.cpp:100` |
| `FAS_FEATURE_<name>` | Core | any non-empty | Turns on FAS feature `<name>` (for example `FAS_FEATURE_MACHINE_WORKS`) when no text-command setting exists. | FAS context only | `Core/Neutron/Server/Base/Utility/FusionAutomationService.cpp:235` |
| `FAS_GAIA_ALLOW_CER_SEND` | Core | `true` | Allows CER sending in 2-legged FAS (GAIA) context. |  | `Core/Neutron/Server/Base/OS/CERWrapper.cpp:1886` |
| `FAS_GRACEFUL_EXIT_WAIT_SEC` | Core (Fusion/Services) | Integer seconds (default 5) | Automation API wait time during graceful exit. | Read through the Configuration settings table. | `Core/Fusion/Server/AutomationAPI/AutomationAPI/Configuration.cpp:100` |
| `FAS_HUB` | Core | hub/tenant ID | FAS login: if set, the tenant is fetched from the cloud asynchronously. | Non-2-legged FAS | `Core/Neutron/UI/Base/Cloud/BearerAuth.cpp:823` |
| `FAS_JOB_TIMEOUT_SEC` | Core (Fusion/Services) | Integer seconds (default 1000) | Automation API job timeout. | Read through the Configuration settings table. | `Core/Fusion/Server/AutomationAPI/AutomationAPI/Configuration.cpp:100` |
| `FAS_LOG_POST_INTERVAL_MS` | Core (Fusion/Services) | Integer ms (default 2000) | Automation API log-post interval. | Read through the Configuration settings table. | `Core/Fusion/Server/AutomationAPI/AutomationAPI/Configuration.cpp:100` |
| `FAS_LOGGING_PATH` | Core | existing dir | Log directory when run with `--fas`. |  | `Core/Neutron/Server/BaseCore/AppLog/AppLogMgr.cpp:110` |
| `FAS_PID_FILE_WRITING_INTERVAL_MS` | Core (Fusion/Services) | Integer ms (default 1000) | Automation API PID-file write interval. | Read through the Configuration settings table. | `Core/Fusion/Server/AutomationAPI/AutomationAPI/Configuration.cpp:100` |
| `FAS_POLLING_SLEEP_MS` | Core (Fusion/Services) | Integer ms (default 50) | Automation API polling sleep. | Read through the Configuration settings table. | `Core/Fusion/Server/AutomationAPI/AutomationAPI/Configuration.cpp:100` |
| `FAS_TEST_ENVIRONMENT` | Core (Fusion/Services) | e.g. `production` / `prd` | If `production` or `prd` in a build without `END_USER_BUILD`, Automation add-in startup throws ("Production-Fusion not build with _END_USER_BUILD"). | Behaviour depends on `END_USER_BUILD`. | `Core/Fusion/Server/AutomationAPI/AutomationAPI/AutomationAddin.cpp:42` |
| `FAS_TEXTCMD_GUARD_APP_BUNDLE_ID` | Core (Fusion/Services) | Bundle ID string (default `Fusion.TextGuardApp`) | Automation API text-command guard app bundle ID. | Read through the Configuration settings table. | `Core/Fusion/Server/AutomationAPI/AutomationAPI/Configuration.cpp:100` |
| `FASCONTROLPATH` | Core (Fusion/Services) | Directory path | Automation API working/control directory (`WorkingDirectory`). Overrides XML `fusionworker/directory/basepath`. | Read through the Configuration settings table. | `Core/Fusion/Server/AutomationAPI/AutomationAPI/Configuration.cpp:100` |
| `FUSION_BEARER_TOKEN` | Core | OAuth2 token | Supplies the bearer token directly. If empty on AppStream, the token is refreshed another way. |  | `Core/Neutron/UI/Base/Cloud/BearerAuth.cpp:710` |
| `FUSION_CER_HEADLESS` | Core | `YES` | Auto-sends CERs without UI. | Linux only | `Core/Neutron/Server/Base/OS/CERWrapper.cpp:1175` |
| `FUSION_CER_MOCK_USER_ID` | Core | email | Auto-send email for headless CER (default `fusion-linux-noreply@autodesk.com`). | Linux only | `Core/Neutron/Server/Base/OS/CERWrapper.cpp:1180` |
| `FUSION_ENVIRONMENT` | Core (Fusion/Services) | e.g. `production` | Same check as `FAS_TEST_ENVIRONMENT`: `production` without `END_USER_BUILD` makes Automation add-in startup throw. | Behaviour depends on `END_USER_BUILD`. | `Core/Fusion/Server/AutomationAPI/AutomationAPI/AutomationAddin.cpp:40` |
| `NEUTRON_DEVICE_THEME` | Core | `dark` (case-insens.) or other | Overrides OS dark/light theme detection. Only honored when `CHOTAY_APP=1`. | Windows only | `Core/Neutron/Server/Platform/OS/Windows/WindowsPlatform.cpp:1140` |
| `NEUTRON_OFFSCREEN_MODE` | Core | `OSMESA` | Offscreen (OSMesa) mode: skips the UDA home tab and FusionGuide web browser, and changes window/splash init. |  | `Core/Neutron/UI/Base/Application/Impl/implApplication.cpp:2029`, `Core/Neutron/UI/Commands/HomeTabBase/HomeTabSelectionUtility.cpp:38` |
| `WORKER.ENV` | CloudTranslation | `stg`, `sfrue2`, `prod`, `pfrue2` | Cloud translation worker environment (staging/QA/production, incl. FedRAMP) | Constant `Constants::EXTRACTOR_BUILD_ENV_VAR` (ATFTranslationEnvironmentConfig.h:18); cloud worker | CloudTranslation/TranslationCommon/Utils/ATFTranslationEnvironmentConfig.cpp:11 |

## 9. Testing, QA and CI

**Who:** QA, test automation and build servers. NTest, contract and regression tests, build-machine mode, entitlement and licence mocking, gold-file generation, and suppressing dialogs and analytics in pipelines.

| Variable | Area | Expected value | Function | Notes | Source |
|---|---|---|---|---|---|
| `ACAD_FD_TEST` | Publish | Presence (any value) | Test/regression (FDRegress) mode: e.g. keeps properties JSON, alters view-compute/Inventor-subent behaviour, registers test commands | Test mode; forwarded to Wine child on Linux | Publish/AcFusionDoc/AcFusionService/AcFusionServiceUtils.cpp:980, Publish/AcFusionDoc/AcModelDoc/ViewCompute/AcDvViewComputeImpl.cpp:519, Publish/AcFusionDoc/AcFusionFields/AcFusionFieldsLookup.cpp:556, Publish/AcFusionDoc/AcModelDocObj/AcDbAssocInventorPersSubentIdManager.cpp:59, Publish/AcFusionDoc/AcFusionServiceTest/AcFusionServiceTest.cpp:687, Publish/AcFusionDoc/AcCoreViewProxy/linux/windowless.cpp:195 |
| `AggregateNO_CONTENT` | Core (Fusion/Services) | Any value (presence) | Skips the `SET_CONTENT_AVAILABLE` operation in the WIP aggregate request. Testing only, per the code comment. | All builds. | `Core/Services/Data/WIPDataModel/WIPService/WIPService.cpp:1074` |
| `ALLOW_DUPLICATE_MPC_NOTIFICATIONS` | Core | `true` | Allows duplicate MPC dashboard notifications (for testing). |  | `Core/Neutron/UI/Commands/Dashboard/MpcNotificationController.cpp:127` |
| `APPLOG_FOR_BUILDSERVER` | Core | `YES` (case-insens.) | Turns on build-server applog mode (`isAppLogForBuildServer`). |  | `Core/Neutron/Server/BaseCore/AppLog/AppLogMgr.cpp:41` |
| `AUTODESK_HSM_AUTOMATION` | Make | `1` (default `0`) | Enables saving document XML for automation (`SaveAutomationXML`) |  | Make/IronLib/core/IronDocument.cpp:6899 |
| `AUTODESK_HSM_OUTPUT` | Make | Existing directory (default app-data folder) | Output folder for automation XML; source folder for saved post-processing properties |  | Make/IronLib/core/IronDocument.cpp:6907, Make/IronLib/core/post/PostProcessingTask.cpp:872 |
| `AUTOSEND_CER_INPIPELINE` | Core<br>Make | `YES`<br>Presence | Forces CER crash reports to auto-send (`getForceSend`).<br>*Make:* With CER force-send, auto-sends CAM kernel crash report without dialog (pipeline/tests) |  | `Core/Neutron/Server/Base/OS/CERWrapper.cpp:741`<br>Make/NeuCAM/UI/NeuCAMUI/NeutronUIHost.cpp:1169 |
| `BANNER_TESTING` | Core | `1` | Message banners skip the "already shown" and start/end time filters. Platform warnings always show. |  | `Core/Neutron/UI/Base/UI/Controls/MessageBannerController.cpp:689`, `Core/Neutron/UI/Base/Commands/QAT/PlatformWarningCmd.cpp:606` |
| `BUILD_MACHINE` | Core | `YES` (case-insens.) | Marks the process as a build machine (`Utility::isBuildMachine`). Any non-empty value plus `SKIP_ENTITLEMENT` clears the user email in automation CERs. |  | `Core/Neutron/Server/BaseCore/Utility/BuildMachine.cpp:11`, `Core/Neutron/Server/Base/OS/CERWrapper.cpp:1108` |
| `BUILDSERVER_DISABLE_GA` | Core<br>Make | any non-empty<br>Non-empty | Suppresses ADP analytics (env eligibility returns false) on CI/automation.<br>*Make:* Disables all CAM analytics tracking (GA, Marketo, CIP) on build servers | `IRON_NEU` builds; ignored for test analytics host | `Core/Neutron/Server/Base/ADP/ADPWrapper.cpp:682`<br>Make/IronLib/core/analytics/AnalyticsMgr.cpp:63 |
| `EmagOnlyGenerateGolds` | Electron | `1` | Test runner only regenerates gold files | Test code only | Electron/EAGLE/src/Emag/Tests/GeometryAnalyzer.Tests.cpp:30 |
| `ENABLE_CODECOVERAGE` | Core | `YES` | Suppresses assert pop-ups and skips NTest local logging during code-coverage runs. |  | `Core/Neutron/Server/BaseCore/Assert/Handlers/DefaultAssertHandler.cpp:53`, `Core/Neutron/NTest/Server/NTest/Adaptations/QT/ServerThread.cpp:173` |
| `ENABLE_VCS_JOURNALING` | Core (Fusion/Services) | Any non-empty | Turns on VCS journaling for NTest test runs (on test-start event). | All builds. Test tooling. | `Core/Fusion/UI/FusionUI/TextCommands/VCSJournalingManager.cpp:42` |
| `F360SESS_CONCUR` | Core | `1` / `0` | Concurrent session licensing. Internal builds: off unless `1`. User builds: `0` turns it off on staging, or on production for internal users. | Behaviour differs by `END_USER_BUILD` | `Core/Neutron/UI/Base/Cloud/SessionLicensingMgr.cpp:532` |
| `F360SESS_CONCUR_DEVICE` | Core | string | Overrides the concurrent-session device ID. |  | `Core/Neutron/UI/Base/Cloud/SessionLicensingMgr.cpp:609` |
| `F360SESS_CONCUR_FREQ` | Core | integer | Overrides the concurrent-session heartbeat frequency. |  | `Core/Neutron/UI/Base/Cloud/SessionLicensingMgr.cpp:625` |
| `F360SESS_CONCUR_HOST` | Core | hostname | Overrides the concurrent-session host name. |  | `Core/Neutron/UI/Base/Cloud/SessionLicensingMgr.cpp:618` |
| `FEEDBACK_TESTING` | Core | any non-empty | Performance feedback test mode: the notification shows whenever FPS drops below the threshold. |  | `Core/Neutron/UI/Base/Common/PerformanceFeedbackController.cpp:40` |
| `FUSION_NTESTGEN_MCP` | Core<br>Core (Fusion/Services) | `1` | Turns on text command history recording (NTest generation via MCP).<br>*Core (Fusion/Services):* Turns on the NTestGen MCP tools (internal and external surfaces). | All builds. | `Core/Neutron/Server/BaseCore/TextCommands/TextCommandHistory.cpp:26`<br>`Core/Fusion/Server/Fusion/MCP/NTestGen/NTestGenTextCommand.h:26` |
| `FUSION_SUPPRESS_CAMKERNEL_CER_DIALOG` | Make | Presence | Suppresses CAM kernel crash-report dialog |  | Make/NeuCAM/UI/NeuCAMUI/NeutronUIHost.cpp:1182 |
| `FUSION_TEST_BUILD_EXPIRY_DATE` | Core | date `YYYY-MM-DD` | Overrides the build expiry date (BuildExpiryManager). |  | `Core/Neutron/UI/Base/UI/Controls/BuildExpiryManager.cpp:96` |
| `FUSION_TEST_NEEDS_UPDATE` | Core | integer (`0` = no update needed) | Overrides the forced-update "needs update" status. In release (`NDEBUG`) builds any value just returns false. Only debug builds parse it. | Effective in non-NDEBUG builds | `Core/Neutron/UI/Base/UI/Controls/BuildExpiryManager.cpp:278` |
| `FUSIONMAKE_WORKSPACE` | Make | Path to FusionMake repo root (UTF-8) | Locates NeuCAM unit-test data/dataset folders | Test code only | Make/NeuCAM/Server/NeuCAMUnitTest/utilities/Utilities.cpp:18, :32 |
| `ICON_SCRAPE` | Core | file path | While a transcript replays, writes command icon info to this file when a command ends. |  | `Core/Neutron/UI/Base/CommandsUI/InteractiveCommandBaseUI.cpp:605` |
| `LICENSE_JSON` | Core | file path | Reads the entitlement JWT/JSON from a local file instead of the server. | Ignored when `Oxygen::isRestricted()` | `Core/Neutron/Client/Base/Client/Cloud/EntitlementHelper.cpp:195` |
| `MAGAtmPlatformMode` | Make | Integer `MAGAtmEnums::PlatformMode` | Automation mode; Recording/Batch/UiBatch registers automation platform | Constant `SYS_ENV_AUTOMATION_ENUM_KEY` (MSFNestUIAddin.cpp:139) | Make/Fabrication/UI/MSFNestingUI/src/MSFNestUIAddin.cpp:787 |
| `MAS_SIMULATE_DRACONIAN_UPDATE` | Core | version string | Simulates a forced Mac App Store update by comparing this "latest version" with the bundle version. | Mac only | `Core/Neutron/UI/Base/Adaptations/OSX/MacAppVersion.mm:105` |
| `NEUTRON_ADD_UNICODE_TO_USERPATHS` | Core | any non-empty | Adds Unicode characters to user data paths to expose Unicode path bugs. | Windows only | `Core/Neutron/Server/Platform/OS/Windows/PathInfo.cpp:9` |
| `_NEUTRON_MOCK_SERVER` | Core | path to exe | Overrides the mock-server executable path used by tests. | Test infrastructure (`Server/Base/Tests`) | `Core/Neutron/Server/Base/Tests/MockServer/MockServer.cpp:214` |
| `_NEUTRON_MOCK_SERVER_PORT` | Core | integer port | Overrides the mock-server port. | Test infrastructure | `Core/Neutron/Server/Base/Tests/MockServer/MockServer.cpp:218` |
| `NEUTRON_NO_GRAPHICS` | Core | `1` | Uses the null virtual device (no graphics). |  | `Core/Neutron/Server/Scene/Options/GraphicsOptions.cpp:452` |
| `NEUTRON_PACT_PROVIDER_VERIFY` | Core | any (presence) | Runs Pact provider verification (skipped if unset). | Contract test code | `Core/Neutron/Server/PactCppPocContractTests/tests/tst_HdsPact.cpp:107` |
| `NEUTRON_REDUCEDLIB_IN_TRANSLATORS` | Core<br>Simulation | `ON` | Uses the reduced (Protein) material library in translators.<br>*Simulation:* NTest/ReducedLib env: don't count other-module load failures as errors | NTest | `Core/Neutron/Server/Types/Appearance/ProteinManager.cpp:83`<br>Simulation/Simulation/Application/FusionToFEACS/FusionToFEACS.cpp:1142 |
| `NEUTRON_SHOW_CLOUD_DIALOGS` | Core | non-empty, not `NO` | Shows cloud session dialogs even in test/automation contexts. |  | `Core/Neutron/UI/Commands/Cloud/CloudSessionManager.cpp:469` |
| `NEUTRON_TESTING_IMAGE` | Core | existing dir | Logs derived image-set resources to this dir. |  | `Core/Neutron/UI/Base/Adaptations/QT/Utilities/QTImageSetResourceTypeGenerator.cpp:37` |
| `NEUTRON_TESTING_RETINA` | Core | dir, or `1` (= default icon test dir) | Icon/retina testing output dir. Writes toolbar icon info logs. |  | `Core/Neutron/UI/Base/Utility/UIUtil.cpp:198`, `Core/Neutron/UI/Base/UI/Toolbar/Impl/TextCommands/ToolbarTextCommands.cpp:872` |
| `NEUTRON_UPDATE_CHECK_ETAG` | Core (Fusion/Services) | `DISABLE` (exact) | Skips the ETag-based live-update check and assumes an update is available. | All builds. | `Core/Services/Platform/LiveUpdate/LiveUpdateBase.cpp:150` |
| `OFC_FEATURES_JSON` | Core | file path | Offline file cache reads the feature list from this file. | Ignored when restricted (Oxygen) | `Core/Neutron/Server/DataModel/Offline/OfflineFileCache.cpp:787` |
| `OFC_LICENSE_JSON` | Core | file path | Offline file cache reads the entitlement JSON from this file. Also counts as a local-license source in EntitlementHelper. | Ignored when restricted | `Core/Neutron/Server/DataModel/Offline/OfflineFileCache.cpp:744`, `Core/Neutron/Client/Base/Client/Cloud/EntitlementHelper.cpp:176` |
| `PACT_PLUGIN_DIR` | Make | Directory | Pact plugin dir; set to build default if missing | Test code only; Windows | Make/NeuCAM/Server/NeuCAMUnitTest/main.cpp:151 |
| `RUNCLOUDBROWSERTESTS` | Core | `YES` | "Go online" runs synchronously, not async (cloud browser tests). |  | `Core/Neutron/UI/Commands/Cloud/OnlineStatusControllerImpl.cpp:408` |
| `SHEET_METAL_RULES_LIBRARY_CUSTOM_UI_REMOTE_ENTRY_FILE_PATH` | Core (Fusion/Services) | Path/URL to `remoteEntry.js` | Overrides the Sheet Metal Rules library custom UI location (for testing). | Non-`END_USER_BUILD` only. | `Core/Fusion/UI/FusionSheetMetalUI/FusionSheetMetalUI.cpp:251` |
| `_SIM_TEST_N1_NEW_RESULTS` | Simulation | Presence (non-empty) | Switches stress XX result field/type layout to the "new results" variant | Only honored when `inDevelopmentCode()` is true | Simulation/Simulation/Extensions/LinearStaticStress/Server/Overrules/SimMeshDBLSSOverrule.cpp:73, :199 |
| `SKIP_ENTITLEMENT` | Core<br>Core (Fusion/Services) | `YES` (case-insens.)<br>`YES` (case-insensitive) | Skips entitlement and expiry checks (automation runs without login) in open/save/save-as. Any non-empty value plus `BUILD_MACHINE` clears the CER user email.<br>*Core (Fusion/Services):* Only tags an analytics report with `SKIP_ENTITLEMENT` here. No entitlement bypass at this site. | All builds. | `Core/Neutron/Client/Base/Client/Cloud/EntitlementHelper.cpp:130`, `Core/Neutron/Server/Base/OS/CERWrapper.cpp:1107`<br>`Core/Fusion/UI/FusionUI/FusionUI.cpp:3977` |
| `SKIP_FIRST_LAUNCH` | Core | `YES` | Skips the first-launch experience. |  | `Core/Neutron/UI/Commands/FirstLaunch/FirstLaunchMgr.cpp:231` |
| `TEST_ACCORECONSOLE_VISIBLE` | Publish | `y`/`Y`/`1` | Show AcCoreConsole during FusionDoc tests | Test code only | Publish/AcFusionDoc/FusionDocTest/ConnectedConsoleSession.cpp:34, :36 |
| `TEST_FORCE_USE_SECONDARY` | Core | `true` or `1` | ADP SDK treats the primary storage path as unwritable and uses the secondary. | Debug only | `Core/Neutron/Server/Base/ADP/ADPDesktopSDK/ADPDesktopSDK.cpp:5898` |
| `TEST_XML_OUTPUT` | Publish | gtest output spec (default `xml`) | Sets gtest XML output | Test code only | Publish/AcFusionDoc/FusionDocTest/CommonApp.cpp:196, :199 |
| `testShutdownMenu` | Core | any (presence) | Test hook: fakes a decrementing pending-simulation-job count in the shutdown status menu. |  | `Core/Neutron/UI/Base/Adaptations/QT/Controls/ActionMenu/Items/QTSimStatusItem.cpp:46` |
| `WRITE_LICENSE_JSON` | Core | dir path | Writes decoded entitlement JSONs to this folder. | Ignored when restricted | `Core/Neutron/Client/Base/Client/Cloud/EntitlementHelper.cpp:217` |

## 10. Developer only

**Who:** Fusion developers. Developer builds and source trees, local solver/third-party paths, debuggers (RenderDoc, DX11 debug, Qt event tracing), internal text commands, and dev tool windows.

| Variable | Area | Expected value | Function | Notes | Source |
|---|---|---|---|---|---|
| `ACAD_FD_IDLE` | Publish | Positive integer | Overrides AcCoreConsole idle-count threshold | macOS only | Publish/AcFusionDoc/AcCoreConsole/osx/Connected.mm:44 |
| `ACAD_FD_NOIPE` | Publish | Presence (any value) | Run without activating the in-place editor (IPE) | Marked temporary in code | Publish/AcFusionDoc/AcFusionService/AcFusionCommand.cpp:176 |
| `ACAD_FD_VIEWCOMPUTE_ASMJOURNAL` | Publish | `Y`/`y`/`1` | Enables ASM journaling during drawing view compute |  | Publish/AcFusionDoc/AcFusionService/AcFusionDocInteropStub.cpp:2312 |
| `ACAD_FUSDOC_JOURNAL_DIR_DELETE` | Publish | `Y` | Deletes ASM journal directory in temp folder | Debug builds only; set by DrawingDebugCmd.cpp:301 | Publish/FusionDoc/Server/FusionDoc/Objects/FusionDocAssetAdapter.cpp:281 |
| `ACCORECONSOLE_VISIBLE` | Publish | Presence | ExpressTools: report AcCoreConsole as visible | Win (`_dupenv_s`) / macOS (`getenv`) | Publish/FusionDoc/AddIns/ExpressTools/ExpressTools.cpp:414, :417 |
| `ACCORECONSOLEDEBUG` | Publish | Presence | Shows message box at AcCoreConsole start so a debugger can be attached | Debug + Windows only | Publish/AcFusionDoc/AcCoreConsole/AcCoreConsole.cpp:947 |
| `ArroDiagnostics` | Core (Fusion/Services) | Any non-empty | Remove Details command shows an alert with the execution time and the delete-portion time. | All builds. The reads in RemoveFeaturesCmd.cpp:1099 and RemoveFacesCmd.cpp:606 are commented out. | `Core/Fusion/UI/FusionUI/Commands/Modeling/RemoveDetailsCmd.cpp:447` |
| `AUTOCAD_ADP_UTILITY` | Publish | `1` | Load the ACCIP ARX module in AcCoreConsole | Read via AutoCAD `acGetEnvString` (AutoCAD env, may come from profile not OS env); Windows block | Publish/AcFusionDoc/AcCoreConsole/AcCoreConsole.cpp:773 |
| `_CAMKERNEL` | Make | Path to CAM kernel third-party area | If no installation folder found, use `<value>/bin` as CAM kernel location | Debug builds only (`_DEBUG`) | Make/IronLib/core/generation/CamkernelRunner.cpp:77 |
| `csm-shadow` | Core | any (presence) | Debug aid: the cloud status dialog's drop shadow turns red. |  | `Core/Neutron/UI/Base/Adaptations/QT/Controls/ActionMenu/QTCloudStatusDialog.cpp:36` |
| `CURL_DIRECTORY_PATH` | Core | path | Overrides where libcurl is loaded from (`<path>/LIBCURL/lib/libcurl.4.dylib`). | Mac only | `Core/Neutron/Server/Base/Utility/HTTPClient.cpp:109` |
| `DEBUG_ACC_PATH` | Publish | Path to AcCoreConsole executable | Custom AcCoreConsole path when `USE_DEBUG_ACC=YES` (not in FAS context) | Dev override | Publish/FusionDoc/Server/FusionDoc/Utilities/FusionDocUtils.cpp:690 |
| `DEBUG_DUMP_COMPLETE_JSON` | Electron | `TRUE` (default `TRUE`) | Synchronizer: dump complete JSON | Debug aid | Electron/EAGLE/src/synchronizer/data/Common.h:75 |
| `DEBUG_DUMP_RESOURCES` | Core | `TRUE` | Dumps all Qt resource (`:/`) entries in the Weave QSS theme window. | Dev tool window | `Core/Neutron/UI/Base/Adaptations/QT/StyleSheet/Internal/ThemeWindow.cpp:66` |
| `_DEBUG_FEACSCOMMANDLINE_ARGS` | Simulation | Presence (any value) | Logs FEACS command-line args to `C:/temp/test.log` | Windows only | Simulation/Simulation/Controllers/LinearAnalysis/Controller/Objects/FEACSJobWriter.cpp:1734 |
| `DEBUG_INCLUDE_HASHES_IN_DUMPS` | Electron | `TRUE` (default `TRUE`) | Synchronizer: include hashes in JSON dumps | Debug aid | Electron/EAGLE/src/synchronizer/data/Common.h:74 |
| `DEBUG_SYNCHRONIZER` | Electron | Presence | Allows synchronizer on designs with modules; adds "Export *.SCR instead" debug button | Debug aid | Electron/EAGLE/src/d_synchronize.cpp:74, Electron/EAGLE/src/synchronizer/ui/SynchronizerDialog.cpp:244 |
| `DebugIntermediateResult` | Simulation | Presence | Enables intermediate-result debugging in frequency-response mesh DB overrule; details unclear from code | Debug builds only | Simulation/Simulation/Extensions/LinearStaticStress/Server/Overrules/SimMeshDBFreqResponseOverrule.cpp:60 |
| `DISABLE_NEUTRON_ASSERTS` | Core | `1` | Turns off `NEUTRON_ASSERT` handling (returns early). |  | `Core/Neutron/Server/BaseCore/Assert/Assert.cpp:94` |
| `DVCBUGALERT` | Publish | Integer; `0` disables | Disables DrawingViewCompute bug-alert dialogs when 0 | Uses `_wdupenv_s` | Publish/AcFusionDoc/DrawingViewCompute/assert/BugAlert.cpp:147 |
| `EAGLE_ASSET_DEBUG_CACHE_EXPIRE_SECOND` | Electron | Integer seconds | Overrides asset cache expiry time | Debug aid | Electron/EAGLE/src/assetcacheutil.cpp:50 |
| `EAGLE_ASSET_DEBUG_UPLOAD` | Electron | `TRUE` (case-insensitive) | Adds "Add or update" asset upload button to asset select dialog | Debug aid | Electron/EAGLE/src/UI/AssetSelectDialog/AssetSelectDialog.cpp:151 |
| `EAGLE_NEWS_SERVER_PULL_PERIOD_MS` | Electron | Integer ms (default 3600000) | Start-page news pull period |  | Electron/EAGLE/src/webapi/startpage.cpp:33 |
| `EAGLE_OUTLINE_*` / `EAGLE_OVERLAY_*` (15 vars) | Electron | Color `0xAARRGGBB` or Qt color name | Overrides hover/selection outline/overlay color | Only applied when `EAGLE_UX_TWEAKING=1`. Names: `EAGLE_OUTLINE_HOVER_DARK`, `EAGLE_OUTLINE_HOVER_LIGHT_BRD`, `EAGLE_OUTLINE_HOVER_LIGHT_SCH`, `EAGLE_OUTLINE_OVER_SELECTED_DARK`, `EAGLE_OUTLINE_OVER_SELECTED_LIGHT_BRD`, `EAGLE_OUTLINE_OVER_SELECTED_LIGHT_SCH`, `EAGLE_OUTLINE_SELECTED_DARK`, `EAGLE_OUTLINE_SELECTED_LIGHT_BRD`, `EAGLE_OUTLINE_SELECTED_LIGHT_SCH`, `EAGLE_OVERLAY_HOVER_DARK`, `EAGLE_OVERLAY_HOVER_LIGHT_BRD`, `EAGLE_OVERLAY_HOVER_LIGHT_SCH`, `EAGLE_OVERLAY_SELECTED_DARK`, `EAGLE_OVERLAY_SELECTED_LIGHT_BRD`, `EAGLE_OVERLAY_SELECTED_LIGHT_SCH`. Internal UX tweaking; only when `EAGLE_UX_TWEAKING=1` | Electron/EAGLE/src/PaletteAndColors.cpp:578 (read at Electron/EAGLE/src/PaletteAndColors.cpp:534) |
| `EAGLE_STYLESHEET_DEBUG` | Electron | `TRUE` | Hosted mode: init private stylesheet-debug routines | Debug aid | Electron/EAGLE/src/application/eagleapp_private.cpp:375 |
| `EAGLE_TF_ALLOWANCE_S` | Electron | Integer seconds (default 20) | TokenFlex free allowance time |  | Electron/EAGLE/src/services/TokenFlex/TokenFlexManager.cpp:35 |
| `EAGLE_TF_OFFLINE_HB_S` | Electron | Integer seconds (default 86400) | TokenFlex offline heartbeat period |  | Electron/EAGLE/src/services/TokenFlex/TokenFlexManager.cpp:37 |
| `EAGLE_TF_ONLINE_HB_S` | Electron | Integer seconds (default 3600) | TokenFlex online heartbeat period |  | Electron/EAGLE/src/services/TokenFlex/TokenFlexManager.cpp:36 |
| `EAGLE_UI_MODE` | Electron | `STANDALONE` / `HOSTED` (case-insensitive) | Overrides application UI mode | Non-public builds only | Electron/EAGLE/src/application/eagleapp_private.cpp:631 |
| `EAGLE_UX_TWEAKING` | Electron | `1` | Enables `EAGLE_OUTLINE_*`/`EAGLE_OVERLAY_*` color overrides | Internal use only | Electron/EAGLE/src/PaletteAndColors.cpp:531 |
| `EMAG_DEBUG_OUTPUT_PATH` | Electron | Directory | Writes EMag simulation job debug files under `<dir>/<jobId>` | Debug aid | Electron/EAGLE/src/Emag/CloudJobs/SimulationJob.cpp:30 |
| `ENABLE_OSS_DEBUG_MESSAGES` | Core<br>Core (Fusion/Services) | `1` | Turns on OSS service debug messages at init.<br>*Core (Fusion/Services):* Turns on OSS (object storage) SDK debug messages at `OSSService_global_init`. | Console application. | `Core/Neutron/UI/Base/Application/Impl/implApplication.cpp:2347`<br>`Core/Fusion/Applications/Fusion360ConsoleApplication/ConsoleAppImpl.cpp:569` |
| `EXEDIR` | Publish | Directory | Folder containing `accoreconsole.exe` (else derived from module path); test data folder in FusionDocTest | Windows (`_wgetenv_s`); FusionDocTest is test code | Publish/AcFusionDoc/AcCoreViewProxy/CoreViewProxyWindow.cpp:31, Publish/AcFusionDoc/FusionDocTest/FusionDocTestUtils.cpp:82 |
| `_FEACS` | Simulation | Path to FEACS third-party folder | Locates `feacscommandline.exe` (under lib64/debug or release) instead of bundled copy | Windows only (mac/Linux always use bundle) | Simulation/Simulation/Controllers/LinearAnalysis/Controller/Objects/FEACSJobWriter.cpp:1461 |
| `_FIMSolver` | Simulation | Path to solver folder | Root folder of Injection Molding (FIM) solver executable |  | Simulation/Simulation/Extensions/InjectionMolding/Server/Overrules/SimCaseOverrule.cpp:1219 |
| `FULL_INVALIDATE_LOGGING` | Core | any non-empty, or `ALL` | Logs command invalidation in full. `ALL` adds all details. |  | `Core/Neutron/Client/Base/Client/CommandFramework/CommandDefinitionMgr.cpp:51` |
| `FUSION_BEARER_TOKEN` | Electron | Bearer token | Overrides auth token (default read from EAGLE debug config file) |  | Electron/EAGLE/src/webapi/webapi.cpp:128 |
| `FUSION_DEBUG_QML_IMPORTS` | Core | non-zero integer | Logs QML import paths for the Scripts Manager dialog. |  | `Core/Neutron/UI/Base/Adaptations/QT/Dialogs/QTQmlScriptsManagerDialog.cpp:662` |
| `FUSION_DOC_BUILD` | Publish | Presence | Forces Fusion-doc mode in AcCoreConsole without CLI flag | Dev aid | Publish/AcFusionDoc/AcCoreConsole/AcCoreConsole.cpp:2064 |
| `FUSION_DUMP_CMD_SHORTCUT` | Core | any (presence) | Registers a shortcut-enabled variant of the "Dump Entity Info" command. |  | `Core/Neutron/UI/Components/Commands/DumpEntityCmd.cpp:47` |
| `FUSIONMAKE_POST_EXE` | Make | Path to post.exe (UTF-8) | Developer override of post-processor executable | Dev aid | Make/IronLib/core/post/Config.cpp:844 |
| `GBIN` | Publish | Directory | Locates `AcCoreConsole.app/Contents/PlugIns/` bundles | Test code; macOS | Publish/AcFusionDoc/AcFusionServiceTest/AcFusionServiceTest.cpp:406 |
| `INSIGHTS_UUP_API_KEY_PRD` | Core | API key | Default production Insights UUP API key for a FusionGuide text command (overridden by the command argument). |  | `Core/Neutron/UI/Commands/Commands/FusionGuide/FusionGuide.cpp:2741` |
| `INSIGHTS_UUP_API_KEY_STG` | Core | API key | Same, for staging. |  | `Core/Neutron/UI/Commands/Commands/FusionGuide/FusionGuide.cpp:2741` |
| `_INVSERVER` | CloudTranslation | Path to Inventor Server root | Uses `<value>/runtimeroots/Release/InventorServerClient_x64.manifest` if it exists for Inventor import |  | CloudTranslation/Translators/InventorTranslator/Requests/InventorImportRequest.cpp:89 |
| `IRON_BENCHMARK` | Make | Directory | Non-empty enables automatic benchmark with output to that folder |  | Make/IronLib/core/Benchmark.cpp:313 |
| `IRONPROFILE_OUTPUTDIR` | Make | Existing directory | Output folder for task profiler results | Profiling aid | Make/IronLib/util/utility/task/TaskProfiler.cpp:867 |
| `JOB_MANAGER_POLLING_FREQUENCY` | Core (Fusion/Services) | Integer (retry interval; default 15) | Job Manager step processor retry/poll interval. A parse failure resets it to 15. | All builds. | `Core/Services/Platform/JobManager/Objects/JobManagerObjects.cpp:283` |
| `LI_DIR` | Make | Directory | MachineWorks: locate diagnostic messages file |  | Make/IronLib/core/machineworks/mi_conf.cpp:311 |
| `MAGFusionSaveMSIFileDir` | Make | Directory | Output directory for saved MSI translation files (nesting) |  | Make/Fabrication/Server/MSFNesting/src/MSFNestTranslationSelector.cpp:54, :125 |
| `MAGRESOURCES_LOCAL_PATH` | Make | Existing directory | Overrides Fabrication resources path |  | Make/Fabrication/Server/MSFCommon/src/MSFCmnInitialization.cpp:34 |
| `MSFNestDebugOutputSvg` | Make | Directory | Copies generated nest-compare SVGs there | Debug aid | Make/Fabrication/UI/MSFNestingUI/src/MSFNestCompareNewVM.cpp:170 |
| `MSFNestNoSvg` | Make | `1` | Disables SVG generation/preview in nest compare |  | Make/Fabrication/UI/MSFNestingUI/src/MSFNestCompareNewVM.cpp:153, Make/Fabrication/UI/MSFNestingUI/src/MSFNestComparePreviewWidget.cpp:352 |
| `MULGA_SOLVER_PATH` | Simulation | Path to Mulga solver | Locates Mulga (Fluid Dynamics) solver; asserts if missing |  | Simulation/Simulation/Extensions/FluidDynamics/Server/Overrules/SimCaseOverrule.cpp:844 |
| `NEUCAM_UI_RESOURCES_FROM_SOURCE` | Make | `1` | Load NeuCAM UI resources from source tree | Dev aid | Make/NeuCAM/UI/NeuCAMUI/Resources/Resources.cpp:20 |
| `_NEUTRON_3P` | Core (Fusion/Services) | Directory path | Third-party root. The dependency-graph text command runs `<dir>\graphviz\2.44.1\WIN64\bin\dot.exe` to render an SVG. | Windows only. Dev/diagnostic text command. | `Core/Fusion/UI/FusionUI/TextCommands/TextCommandUtils.cpp:59` |
| `NEUTRON_ANALYTICS_MEMORY_STORAGE` | Core | `1` | Also stores ADP analytics events in memory. |  | `Core/Neutron/Server/Base/ADP/ADPWrapper.cpp:996` |
| `NEUTRON_BUILD` | Core<br>Core (Fusion/Services) | `DEBUG` (case-insens.)<br>`DEBUG` (case-insensitive) | Always shows the debug environment and skips offline-expiry exit handling. Any value makes AppMgr try to load the NTest app.<br>*Core (Fusion/Services):* Console app loads the NTest add-in automatically. FusionUI analytics reports the debug environment as enabled via env var. | All builds. | `Core/Neutron/Client/Base/Client/Common/UIBaseOptionGroupDI.cpp:103`, `Core/Neutron/Server/AddInMgr/App/AppMgr.cpp:172`<br>`Core/Fusion/Applications/Fusion360ConsoleApplication/ConsoleAppImpl.cpp:653` |
| `NEUTRON_CHECK_REFCOUNTED_ON_TERMINATE` | Core | any non-empty | On exit, writes leaked RefCounted toolbar objects to `LogInfoOnTerminate.xml`. | Debug only | `Core/Neutron/UI/Base/Application/Impl/implApplication.cpp:3766` |
| `NEUTRON_CHROME_DEVTOOLS` | Core | `0`/`false` to disable | Release builds: `0` or `false` turns off the WebEngine remote debugging port (on by default). | Non-debug builds only | `Core/Neutron/UI/Base/Adaptations/QT/WebBrowser/QTWebBrowser.cpp:548` |
| `NEUTRON_DELAY_AUTH` | Core | any non-empty | Makes the session ineligible for ADP analytics. |  | `Core/Neutron/Server/Base/ADP/ADPWrapper.cpp:680` |
| `_NEUTRON_DISABLE_API_CIP` | Core | any non-empty | Turns off API analytics (CIP) recording in `APIAnalyticsMgr`. |  | `Core/Neutron/Server/XLayer/Infrastructure/ClientCallScopedLock.cpp:451` |
| `NEUTRON_DISABLE_ATTACH_CONSOLE` | Core | any non-empty | Skips attaching to the parent console at command-line init. |  | `Core/Neutron/Server/BaseCore/CommandLine/CommandLine.cpp:47` |
| `NEUTRON_DISABLE_GESTURA` | Core | any non-empty | Turns off Gestura (gesture input) and makes the option read-only. | Internal builds only | `Core/Neutron/UI/Base/Options/UIBaseOptionGroup.cpp:830` |
| `NEUTRON_DISABLE_TIMEBOMB` | Core<br>Core (Fusion/Services) | any non-empty<br>Any non-empty | Turns off the product-expiration (timebomb) check.<br>*Core (Fusion/Services):* Bypasses the product-expiration (timebomb) check. | Console app. | `Core/Neutron/UI/Base/Application/Impl/implApplication.cpp:3417`<br>`Core/Fusion/Applications/Fusion360ConsoleApplication/ConsoleAppImpl.cpp:991` |
| `NEUTRON_ENABLE_ANALYTICS` | Core | `1` / `0` | Forces debug analytics on or off. If set, the `Analytics.Enable` text command does nothing. | Internal builds only | `Core/Neutron/Server/BaseCore/Options/BootstrapOptionGroup.cpp:418`, `Core/Neutron/Client/Base/Client/Analytics/AnalyticsMgr.cpp:1144` |
| `NEUTRON_ENABLE_THEME_QUERY_LOGGING` | Core | `1` | Turns on ToolbarFramework theme query logging. |  | `Core/Neutron/UI/Base/Adaptations/QT/ToolbarFramework/src/Core/TBFUtility.cpp:1174` |
| `NEUTRON_IGNORE_CERTIFICATE_ERRORS` | Core | `1` | Adds Chromium `--ignore-certificate-errors` (debug aid, unsafe). | Internal builds only | `Core/Neutron/UI/Base/Adaptations/QT/WebBrowser/QTWebBrowser.cpp:647` |
| `NEUTRON_LOG_THEME_QUERY_MISMATCHES` | Core | `0` to disable | Logs theme query mismatches (on unless `0`). |  | `Core/Neutron/UI/Base/Adaptations/QT/ToolbarFramework/src/Core/TBFUtility.cpp:1176` |
| `NEUTRON_MEMORY_PROFILER_OGS_ALL_DOCUMENTS` | Core | any non-empty | The memory profiler walks OGS for all open documents, not just the active one. |  | `Core/Neutron/SharedExtensions/Diagnostics/MemoryProfiler/MemoryProfilerCollector.cpp:630` |
| `NEUTRON_OGS_USE_CRT_ALLOCATION` | Core | `1`/`on`/`yes`/`true` | Forces OGS to use CRT memory allocation. |  | `Core/Neutron/Server/Scene/Pipeline/Provider.cpp:159` |
| `NEUTRON_OSX_PLATFORM_EXECUTABLE_PATH` | Core | path | Overrides the platform executable path (for Node Extensions / Fusion Server, set by `deploy.py`). | Mac only | `Core/Neutron/Server/Platform/OS/Mac/MacPlatform.mm:679` |
| `NEUTRON_RENDERDOC_ENABLE` | Core | `1`/`on`/`yes`/`true` | Loads the RenderDoc integration. | Windows, debug only (`RenderDoc::Init` called under `_DEBUG`) | `Core/Neutron/Server/Scene/Platform/OS/Windows/RenderDoc.cpp:22` |
| `NEUTRON_RENDERDOC_PATH` | Core | dir | RenderDoc install dir (overrides the default). | Windows, debug only | `Core/Neutron/Server/Scene/Platform/OS/Windows/RenderDoc.cpp:23` |
| `_NEUTRON_ROOT` | Core | path (dev tree root) | If set, `PathInfo::isInstalledBuild()` returns false, so the build is treated as a dev/source build. | Windows and Linux impls | `Core/Neutron/Server/Base/OS/Windows/PathInfo.cpp:34`, `Core/Neutron/Server/Base/OS/Linux/PathInfo.cpp:32` |
| `_NEUTRON_SRC` | Core | path to source tree | Launcher uses it to find the developer start script, so the app launches in the dev environment. | NLauncher | `Core/Neutron/Suites/NLauncher/AppLauncherUtility.cpp:70` |
| `NEUTRON_TEXT_COMMAND_ENABLE` | Core | `1` | Turns on text commands in all environments, including production. |  | `Core/Neutron/Server/BaseCore/TextCommands/TextCmdUtilities.cpp:17` |
| `NEUTRON_USE_RESOURCES_FROM_SOURCES` | Core | `1` | ResourceMgr loads resources from the source tree. |  | `Core/Neutron/Server/BaseCore/Resources/Impl/implResourceMgr.cpp:262` |
| `NEUTRON_USE_THEME_SOURCES` | Core<br>Make, Simulation | `1` | Loads theme and theme-map files from the source tree for live editing.<br>*Make, Simulation:* Load themeMap.json from source tree for live editing | Dev aid | `Core/Neutron/UI/Base/Adaptations/QT/ToolbarFramework/src/Core/TBFUtility.cpp:1159`<br>Make/NeuCAM/UI/NeuCAMUI/NeuCAMUI.cpp:1185, Simulation/Simulation/UI/CommonUI/CommonUI.cpp:792 |
| `NEUTRON_WEAVE_QSS_PATH` | Core | path | Overrides the Weave QSS stylesheet path. |  | `Core/Neutron/UI/Base/Adaptations/QT/StyleSheet/WeaveQssThemeMgr.cpp:141` |
| `NEUTRON_WEAVE_QSS_SHOW_DENSITY_IN_GALLERY` | Core | `TRUE` | Shows the density combo in the Weave QSS theme gallery window. | Dev tool window | `Core/Neutron/UI/Base/Adaptations/QT/StyleSheet/Internal/ThemeWindow.cpp:216` |
| `NEUTRON_WEB_DEVELOPER_EXTRAS` | Core | `yes` (case-insens.) or `1` | Defaults the "Developer Tools" (web developer extras) option to on. | Non-debug builds only (`#else` of `_DEBUG`) | `Core/Neutron/UI/Base/Options/UIBaseOptionGroup.cpp:3079` |
| `OGS_DX11_DEVELOPER_MODE_ENABLE` | Core | `1`/`true`/`TRUE` | Creates the OGS DX11 device with the debug flag. | Windows, debug only | `Core/Neutron/Server/Scene/Platform/OS/Windows/PlatformSceneUtil.cpp:90` |
| `OS3_TEST` | Core (Fusion/Services) | Integer | Sets the internal OSS test flag, which a text command can read. Purpose unclear from code. | All builds. | `Core/Services/Data/WIPDataModel/OSSService/OSSService.cpp:77` |
| `PIM_COMMANDS` | Core (Fusion/Services) | Any non-empty | Allows PIM text commands. | All builds. Static. | `Core/Fusion/UI/FusionUI/TextCommands/TextCommandUtils.cpp:36` |
| `PrintQObjectName` | Core | any non-empty | Computes and records QObject names in event notifications (debug). |  | `Core/Neutron/UI/Base/Adaptations/QT/Application/QTApplication.cpp:569` |
| `PROFILENEWDWG` | Publish | `1` | Enables profiling (`FusDocUtilities::DoProfiling`) for new DWG | Win `_dupenv_s` / mac+Linux `getenv` | Publish/FusionDoc/UI/FusionDocUI/Utilities/FusDocUtilities.cpp:365, :367 |
| `_PYTHON` | Core | path | Python root folder for dev builds. If empty, the installed Python location is used. | Windows only | `Core/Neutron/Server/Base/Python/PythonManager.cpp:448` |
| `QTApplication` | Core | any non-empty | Calls `debugNotify` for every Qt event (debug breakpoint hook). |  | `Core/Neutron/UI/Base/Adaptations/QT/Application/QTApplication.cpp:598` |
| `QTConsoleApplication` | Core (Fusion/Services) | Any non-empty | Turns on debug tracing of Qt event notifications in the console application. | Console app. Static. | `Core/Fusion/Applications/Fusion360ConsoleApplication/QTConsoleApplication.cpp:208` |
| `_REDUCEDLIB` | Core | path | Base dir for the Material Library fallback (`<path>/MaterialLibrary/Material Library`) in dev builds. | Windows and Mac impls | `Core/Neutron/Server/Types/Platform/OS/Windows/PlatformTypesUtil.cpp:353`, `Core/Neutron/Server/Types/Platform/OS/Mac/PlatformTypesUtil.mm:130` |
| `RENDER_PROCESS_EXECUTABLE` | Core | path | Overrides the RenderProcess executable used by batch render. |  | `Core/Neutron/Server/BatchRender/BatchRenderManager.cpp:60` |
| `SHOW_CORE_WINDOW` | Publish | Presence | Shows AcCoreConsole window (hidden by default) | macOS only | Publish/AcFusionDoc/AcCoreConsole/osx/Connected.mm:25 |
| `SHOW_INVALIDATE_DIALOG` | Core | any non-empty | Shows a dialog for slow command invalidation. |  | `Core/Neutron/Client/Base/Client/CommandFramework/CommandDefinitionMgr.cpp:54` |
| `TSPLINE_CONSOLE` | Core (Fusion/Services) | Any value (presence) | Opens a console window for T-Spline stdout output. | Debug (`_DEBUG`) and Windows only. | `Core/Fusion/UI/TSplineUI/Environments/TSplineEnvironment.cpp:100` |
| `USE_DEBUG_ACC` | Publish | `YES` | Use AcCoreConsole from `DEBUG_ACC_PATH` | Dev override | Publish/FusionDoc/Server/FusionDoc/Utilities/FusionDocUtils.cpp:686 |
| `_ZGRViewer` | Core (Fusion/Services) | Directory path | Folder holding `zgrviewer.bat`, used by a parametric-compute graph text command to view dot output. | Windows only. Dev text command. | `Core/Fusion/UI/FusionUI/TextCommands/ParametricComputeTextCommands.cpp:1775` |

## 11. Set by Fusion itself

**Who:** Nobody (internal handshake). Fusion or its launcher/updater sets these to pass state to a child or restarted process. Do not set them by hand.

| Variable | Area | Expected value | Function | Notes | Source |
|---|---|---|---|---|---|
| `ACAD_FD_ENABLED_FEATURES` | Publish | `Name=1;Name=0;...` list (uppercased on read) | Feature-toggle states passed from Fusion to AcCoreConsole/AcFusionService | Set by Fusion at `Publish/FusionDoc/Server/FusionDoc/AcCoreIPC/FusionDocIpcServer.cpp:310` | Publish/AcFusionDoc/AcFusionService/AcFusionFeatureToggle.cpp:69 |
| `ACAD_FD_TEST_BUILD` | Publish | Presence (Fusion sets `T`) | Marks a test build (uses test white-list of commands; enables test service init) | Set by `Publish/FusionDoc/UI/FusionDocUI/FusionDocUI.cpp:733`; forwarded to Wine child on Linux | Publish/AcFusionDoc/AcFusionService/AcFusionServiceUtils.cpp:992, Publish/AcFusionDoc/AcFusionServiceTest/AcFusionServiceTest.cpp:690, Publish/AcFusionDoc/AcCoreViewProxy/linux/windowless.cpp:198 |
| `FUSION_DX9_MIGRATED_TO_AUTOSELECT` | Core | `1` | Fusion sets this itself (SceneUtil) when DX9 was migrated to Auto. The notify task reads it, shows the "Graphics driver support" EOL notice, then clears it. | Windows only | `Core/Neutron/UI/Base/Application/Impl/WindowsGraphicsDriverNotifyTask.cpp:30` |
| `_FUSION_PARENT_PID_INTERNAL_` | Core (Fusion/Services) | Integer PID | At startup, Fusion waits up to 30 s for this parent process to exit before launching. Live Update / ODIS sets it when relaunching Fusion. | Windows and macOS only. Internal (set by Fusion itself). Name comes from `Ns::FUSION_PARENT_PID_ENV_VAR` in `Core/Services/Platform/LiveUpdate/LiveUpdateBase.h:34`. | `Core/Fusion/Applications/Fusion360Application/Fusion360.cpp:82` |
| `RESTART_FUSION` | Core (Fusion/Services) | `1` | Suppresses the "multiple Fusion instances" dialog when Fusion restarts itself. The variable is cleared after it is read. | Windows only. | `Core/Fusion/Applications/Fusion360Application/WindowsUtilities.cpp:215` |

## 12. Standard OS and toolkit variables

**Who:** Read only (OS/installer-defined). Ordinary OS, Qt, Python, Wine and Ansys variables that Fusion reads. Normally you would not change them for Fusion.

| Variable | Area | Expected value | Function | Notes | Source |
|---|---|---|---|---|---|
| `ACAD` | Publish | AutoCAD support path (`;`-separated) | Read via AutoCAD `getEnv`, template folder appended, written back | AutoCAD host env (profile), not necessarily OS env | Publish/AcFusionDoc/AcFusionService/AcFusionLayoutCommand.cpp:1042 |
| `all_proxy` | Core | proxy URL | Logged to applog (proxy diagnostics only).<br>*Core:* Logged to applog. |  | `Core/Neutron/Server/Base/Utility/ProxyManager.cpp:359` |
| `ALLUSERSPROFILE` | Core<br>Core (Fusion/Services) | path<br>Path (ProgramData) | ProgramData root for the admin-install Material Library and adexmtsv config.<br>*Core (Fusion/Services):* Base folder for the ODIS live-update config file `<ALLUSERSPROFILE>\Autodesk\Fusion\<config>`. | Windows only<br>Windows only. ODIS installs only. | `Core/Neutron/Server/Types/Platform/OS/Windows/PlatformTypesUtil.cpp:81`<br>`Core/Services/Platform/LiveUpdate/LiveUpdateMgr.cpp:86` |
| `APIH_BIN` | Publish | Directory | AutoCAD API harness bin dir used to build dump paths | Test code; non-mac `_wgetenv`, mac via `acedGetEnv` | Publish/AcFusionDoc/AcFusionServiceTest/DbDumpObject.cpp:4237 |
| `AppData` | Core | path | Location of the `Autodesk\Autodesk Fusion 360\SafeModeSession` marker file (check/clear safe mode). | Windows (PinnableLauncher) | `Core/Neutron/Installer/Windows/PinnableLauncher/Launcher.cpp:214` |
| `AWP_ROOT201, AWP_ROOT202, AWP_ROOT203, AWP_ROOT204, AWP_ROOT211, AWP_ROOT212, AWP_ROOT213, AWP_ROOT214, AWP_ROOT215, AWP_ROOT216, AWP_ROOT217, AWP_ROOT218, AWP_ROOT219, AWP_ROOT220, AWP_ROOT221, AWP_ROOT222, AWP_ROOT223, AWP_ROOT224, AWP_ROOT225, AWP_ROOT226, AWP_ROOT227, AWP_ROOT228, AWP_ROOT229, AWP_ROOT230, AWP_ROOT231, AWP_ROOT232, AWP_ROOT233, AWP_ROOT234, AWP_ROOT235, AWP_ROOT236, AWP_ROOT237, AWP_ROOT238, AWP_ROOT239, AWP_ROOT240, AWP_ROOT241, AWP_ROOT242, AWP_ROOT243, AWP_ROOT244, AWP_ROOT245, AWP_ROOT246, AWP_ROOT247, AWP_ROOT248, AWP_ROOT249, AWP_ROOT250, AWP_ROOT251, AWP_ROOT252, AWP_ROOT253, AWP_ROOT254, AWP_ROOT255, AWP_ROOT256, AWP_ROOT257, AWP_ROOT258, AWP_ROOT259, AWP_ROOT260, AWP_ROOT261, AWP_ROOT262, AWP_ROOT263, AWP_ROOT264, AWP_ROOT265, AWP_ROOT266, AWP_ROOT267, AWP_ROOT268, AWP_ROOT269, AWP_ROOT270, AWP_ROOT271, AWP_ROOT272, AWP_ROOT273, AWP_ROOT274, AWP_ROOT275` | Simulation | Ansys install root path | Finds installed Ansys Mechanical/Discovery releases (201-204, 211-275) for export |  | Simulation/Simulation/UI/CommonUI/Commands/Export/SimExportToAnsysCmd.cpp:176 (range in SimExportToAnsysCmd.h:10, :12) |
| `DISPLAY` | Publish | X display | Forwarded to Wine-launched AcCoreConsole | Linux only | Publish/AcFusionDoc/AcCoreViewProxy/linux/windowless.cpp:184 |
| `DYLD_IMAGE_SUFFIX` | Publish | dyld suffix | Cleared before launching AcCoreConsole | macOS, debug only | Publish/FusionDoc/Server/FusionDoc/AcCoreIPC/FusionDocIpcServer.cpp:149 |
| `DYLD_LIBRARY_PATH` | Publish | Library path | Cleared before launching AcCoreConsole so it doesn't load Fusion's dylibs | macOS | Publish/FusionDoc/Server/FusionDoc/AcCoreIPC/FusionDocIpcServer.cpp:136 |
| `HOME` | Core<br>Core (Fusion/Services)<br>Electron, Make, Publish | path<br>Directory path<br>Home directory | User home: Linux user data, Documents and Downloads dirs. Also the Mac `~/Applications` NTest lookup, the Clocks.Trace output dir (non-Windows), the ADP SDK fallback (Linux), and ODIS uninstall logging.<br>*Core (Fusion/Services):* macOS: finds `~/Applications` to locate the AppLogToolkit app bundle. SketchConstrainerCmd: dumps sketch JSON to `$HOME/SketchExtraction/` (test code in execute).<br>*Electron, Make, Publish:* User folders (App Support/Documents/Desktop; `.local/share`); EAGLE home and legacy eaglerc location; forwarded to Wine child / default `WINEPREFIX` | Linux/Mac<br>AppLogToolkit read is macOS only. The read at SketchConstrainerCmd.cpp:191 is commented out.<br>Make: macOS/Linux; Publish: Linux; Electron csio non-Windows, eaglerc Windows | `Core/Neutron/Server/Platform/OS/Linux/LinuxPlatform.cpp:471`, `Core/Neutron/UI/Commands/Commands/NTest/NTestExcCmd.cpp:172`<br>`Core/Fusion/UI/FusionUI/TextCommands/AppLogToolkitTextCommands.cpp:60`<br>Make/IronLib/util/utility/FileSystem.cpp:3395, :3415, Electron/EAGLE/src/csio.cpp:262, Electron/EAGLE/src/eaglerc.cpp:246, Publish/AcFusionDoc/AcCoreViewProxy/linux/windowless.cpp:174, :190, :330 |
| `http_proxy` | Core | proxy URL | Logged to applog. |  | `Core/Neutron/Server/Base/Utility/ProxyManager.cpp:359` |
| `https_proxy` | Core | proxy URL | Logged to applog. |  | `Core/Neutron/Server/Base/Utility/ProxyManager.cpp:359` |
| `LOCALAPPDATA` (read as `localappdata` / `LocalAppData`) | Core<br>Core (Fusion/Services) | path<br>Directory path | Per-user Material Library location. Also the user-install root for the PinnableLauncher purge.<br>*Core (Fusion/Services):* Safe Mode: finds `Autodesk\Autodesk Fusion 360\FusionDiagnosticsData` for log gathering, and `Autodesk\webdeploy\meta\uninstall.wsf` for uninstall. | Windows only<br>Windows only. Also read in SafeModeUninstall.cpp:154. | `Core/Neutron/Server/Types/Platform/OS/Windows/PlatformTypesUtil.cpp:82`, `Core/Neutron/Installer/Windows/PinnableLauncher/Launcher.cpp:67`<br>`Core/Fusion/Applications/Fusion360Application/SafeMode/SafeModeGather.cpp:331` |
| `no_proxy` | Core | host list | Logged to applog. |  | `Core/Neutron/Server/Base/Utility/ProxyManager.cpp:359` |
| `_NT_ALTERNATE_SYMBOL_PATH` | Core | path list | Added to the StackWalker symbol search path. | Windows only | `Core/Neutron/Server/Platform/OS/Windows/StackWalker.cpp:656` |
| `_NT_SYMBOL_PATH` | Core | path list | Added to the StackWalker symbol search path. | Windows only | `Core/Neutron/Server/Platform/OS/Windows/StackWalker.cpp:650` |
| `PATH` (read as `Path` on Windows) | Core<br>Core (Fusion/Services)<br>Electron, Publish, Simulation | path list<br>Path list<br>Search path | Mac: read and extended at startup. Windows: CAM, Fusion and DirectModeling folders are prepended before running ironlib tests.<br>*Core (Fusion/Services):* The console app appends `/usr/bin` to PATH.<br>*Electron, Publish, Simulation:* Prepended with solver/translator/add-in dirs for spawned processes; forwarded to Wine child | Mac (implApplication), Windows (Transcripting text cmd)<br>macOS only.<br>Publish: Linux; DXF translator: Windows; QtInitHelpers: test, Windows | `Core/Neutron/UI/Base/Application/Impl/implApplication.cpp:2187`, `Core/Neutron/UI/Commands/Commands/Transcripting/TextCommands/TranscriptingTextCommands.cpp:48`<br>`Core/Fusion/Applications/Fusion360ConsoleApplication/ConsoleAppImpl.cpp:465`<br>Simulation/Simulation/Extensions/InjectionMolding/Server/Overrules/SimCaseOverrule.cpp:1276, Simulation/Simulation/Controllers/LinearAnalysis/Controller/Objects/FEACSJobWriter.cpp:1666, Electron/Electron/Server/Eagle/Dxf/FusionDxfTranslator.cpp:112, Publish/AcFusionDoc/AcCoreViewProxy/linux/windowless.cpp:187, Electron/EAGLE/src/tests/TestRunner/QtInitHelpers.cpp:31 |
| `ProgramFiles` | Core | path | Finds `dbghelp.dll` under "Debugging Tools for Windows" (StackWalker). Also the global-install root for the PinnableLauncher purge. | Windows only | `Core/Neutron/Server/Platform/OS/Windows/StackWalker.cpp:78`, `Core/Neutron/Installer/Windows/PinnableLauncher/Launcher.cpp:67` |
| `PYTHONHOME` | Core (Fusion/Services)<br>Publish | Path<br>Python home | Saved and unset while an external Python script runs, then restored.<br>*Publish:* Unset before launching AcCoreConsole (avoids crash FDWG-6128) | macOS only. Name comes from `m_pythonHomeName`. | `Core/Fusion/UI/FusionUI/TextCommands/DataTextCommands.cpp:271`<br>Publish/FusionDoc/Server/FusionDoc/AcCoreIPC/FusionDocIpcServer.cpp:143 |
| `SYSTEMDRIVE` | Core | drive | Builds the `SRV*<drive>\websymbols` symbol server path. | Windows only | `Core/Neutron/Server/Platform/OS/Windows/StackWalker.cpp:675` |
| `SYSTEMROOT` | Core | path | Added (plus `system32`) to the symbol search path. | Windows only | `Core/Neutron/Server/Platform/OS/Windows/StackWalker.cpp:662` |
| `TCL_LIBRARY` | Core | path | Checked with `TK_LIBRARY`: if both are set, the Tkinter environment counts as configured. |  | `Core/Neutron/Server/Base/Python/PythonManager.cpp:1815` |
| `TEMP` | Core<br>Electron, Make | path<br>Temp directory | Launcher copies it to `TMP` if `TMP` is unset. Also the VCS debug dump output dir.<br>*Electron, Make:* CAM kernel: saved, overridden with intermediate folder, restored; EAGLE temp file fallback after `TMP` | Windows only<br>Make: Windows only | `Core/Neutron/Suites/NLauncher/NeutronAppLauncher.cpp:34`, `Core/Neutron/Server/Component/Assembly/VCSDebugDump.cpp:34`<br>Make/IronLib/core/generation/CamkernelRunner.cpp:337, Electron/EAGLE/src/files.cpp:709 |
| `TERM` | Publish | Terminal type | Forwarded to Wine-launched AcCoreConsole | Linux only | Publish/AcFusionDoc/AcCoreViewProxy/linux/windowless.cpp:181 |
| `TK_LIBRARY` | Core | path | See `TCL_LIBRARY`. |  | `Core/Neutron/Server/Base/Python/PythonManager.cpp:1816` |
| `TMP` | Core<br>Electron | path<br>Temp directory | Checked by the launcher (set from `TEMP` if missing). Fallback VCS debug dump dir.<br>*Electron:* EAGLE temp file location (then `TEMP`, then `/tmp`) | Windows only | `Core/Neutron/Suites/NLauncher/NeutronAppLauncher.cpp:31`, `Core/Neutron/Server/Component/Assembly/VCSDebugDump.cpp:36`<br>Electron/EAGLE/src/files.cpp:707 |
| `USER` | Core<br>Electron, Simulation | user name<br>User name | Used in the session-licensing device/user hash.<br>*Electron, Simulation:* Default report author; lock-file owner; machine-ID salt | Mac only<br>Non-Windows (csio: Linux/macOS) | `Core/Neutron/UI/Base/Cloud/SessionLicensingMgr.cpp:164`<br>Simulation/Simulation/Server/Common/Options/SimReportOptions.cpp:18, Simulation/Simulation/Server/Common/Report/SimReportPropertiesSummary.cpp:63, Electron/EAGLE/src/files.cpp:1176, Electron/EAGLE/src/csio.cpp:62, :131 |
| `USERNAME` | Core<br>Electron, Make, Simulation | user name<br>User name | Fallback for `USER`.<br>*Electron, Make, Simulation:* Default report author; lock-file owner; salt for Process Simulation file encoding; machine-ID salt fallback | Mac only<br>Simulation/files: Windows; csio: Linux/macOS fallback | `Core/Neutron/UI/Base/Cloud/SessionLicensingMgr.cpp:166`<br>Make/IronLib/core/additive/processSimulation/ProcessSimTask.cpp:63, Simulation/Simulation/Server/Common/Options/SimReportOptions.cpp:16, Simulation/Simulation/Server/Common/Report/SimReportPropertiesSummary.cpp:61, Electron/EAGLE/src/files.cpp:1176, Electron/EAGLE/src/csio.cpp:64, :133 |
| `USERPROFILE` | Core | path | Output dir for the `Clocks.Trace` text command. | Windows only | `Core/Neutron/Server/Base/clocks/TextCommands/ClocksTextCommands.cpp:136` |
| `WINDIR` | Electron, Make | Windows directory | Locate system `d3dcompiler_47.dll` (via `ExpandEnvironmentStringsW`); test locates `whoami.exe` | Windows only; Make site is unit test | Electron/EAGLE/SkiaBridge/SkiaWindowContextDx12.cpp:216, Make/IronLib/util/unittests/testcases/tst_Process.cpp:32 |
| `WINEPREFIX` | Publish | Wine prefix dir (default `$HOME/.wine`) | Forwarded to Wine-launched AcCoreConsole | Linux only | Publish/AcFusionDoc/AcCoreViewProxy/linux/windowless.cpp:171, :325 |
| `XDG_DATA_HOME` | Make | Directory | App-data folder (else `$HOME/.local/share`) | Linux/POSIX only | Make/IronLib/util/utility/FileSystem.cpp:3417 |

## 13. Not active (code present but never runs)

**Who:** Nobody. Reads that are commented out, in `#if 0`, in disabled code paths, or never reached on the platform that reads them. Listed only so the inventory is complete.

| Variable | Area | Expected value | Function | Notes | Source |
|---|---|---|---|---|---|
| `ASMJOURNALDIR` | Core (Fusion/Services) | Directory path | ACIS (ASM) journal output directory for offset-sketch journaling. Falls back to TMPDIR, then TEMP, then TMP. | Compiled out: `JOURNALING` is 0 in OffsetSketchRequest.cpp, and `OFFSET_DUMP_ASM_SCRIPT` is commented out in OffsetSketchCmdNew.cpp:46. ACIS toolkit variable. | `Core/Fusion/Server/Fusion/Requests/OffsetSketchRequest.cpp:291` |
| `FUSION_DWG_LOG` | Publish | Presence | Would gate FusionDwg CER event log | Dead code (`#if 0`) | Publish/FDocsCommon/Includes/FusionDwgLog.h:96 |
| `_HSM_AVOID_EXTENSION_FEATURE_CHECK` | VolumetricField | Presence | Would skip extension feature check | Dead code: guarded by `#if defined(END_USER_BUILD) \|\| 1`, never compiled | VolumetricField/UI/VolFieldUI/FeatureFlag/FeatureFlag.cpp:396 |
| `LI_JOURNAL` | Make | File path (default `log.lwc`) | MachineWorks journaling file | Dead code (`#if 0 && _DEBUG`) | Make/IronLib/core/machineworks/MachineworksInit.h:47 |
| `SIMULUS_UJM_DISABLE_ASYNC_MODE` | Simulation | `1` | Disables async job-manager mode | Caller is Windows-only, so read from registry, never env in practice | Simulation/Simulation/Server/Common/Utility/SimRegistryUtils.cpp:88 via Simulation/Simulation/Server/Common/JobOrganizer/SimJobOrganizer.cpp:64 |
| `SYNERGY_IRONMAN_MIGRATION` | Publish | Integer | Would toggle Ironman DWG view migration | Dead code (commented out; function returns true) | Publish/AcFusionDoc/AcModelDoc/AcSyViewRepUtil.cpp:1131 |
| `TEMP` | Core (Fusion/Services) | Directory path | Fallback journal directory for offset-sketch ASM journaling. | Compiled out (see ASMJOURNALDIR). | `Core/Fusion/Server/Fusion/Requests/OffsetSketchRequest.cpp:298` |
| `TMP` | Core (Fusion/Services) | Directory path | Last-resort journal directory for offset-sketch ASM journaling. | Compiled out (see ASMJOURNALDIR). | `Core/Fusion/Server/Fusion/Requests/OffsetSketchRequest.cpp:302` |
| `TMPDIR` | Core (Fusion/Services) | Directory path | First fallback journal directory for offset-sketch ASM journaling. | Compiled out (see ASMJOURNALDIR). | `Core/Fusion/Server/Fusion/Requests/OffsetSketchRequest.cpp:294` |
| `USE_MARCHING_PROJECTION` | Core (Fusion/Services) | Any value (presence) | Would force marching projection instead of LoftMappingUtil for loft edge mapping. | Compiled out: inside `#if 0` (BRepUtils.cpp:1005-1058). | `Core/Fusion/Server/Fusion/Util/Convert/BRepUtils.cpp:1020` |

## Appendix: reads not tabulated

- `Core/Neutron/UI/Base/Cloud/TextCommands/EntitlementTextCommands.cpp:107`: a text command reads any variable name the user supplies.
- `Core/Neutron/Server/BaseCore/OS/EnvironmentVars.cpp:89` and `Core/Neutron/UI/Base/Cloud/TextCommands/EntitlementTextCommands.cpp:150`: re-read every variable loaded from the environment override file, to report mismatches.
- `Core/Neutron/Server/Base/OS/Windows/WindowsPlatform.cpp:739`: `EnvionmentVariableModifier` reads whatever variable it is constructed with (no in-repo callers found).
- Commented-out reads ignored: `useRecycleBin` (`CheckFeatureFlags.cpp:48`), `QSG_RHI_PREFER_SOFTWARE_RENDERER` (`implApplication.cpp:1753`), `ADSKSIMPKG_LOCAL` (`ExportCmd.cpp:317`), `NEUTRON_ENABLE_RETINA_SUPPORT` (`MacPlatform.mm:245`).
- Whole-environment copies (no specific name read): `Publish/AcFusionDoc/AcCoreViewProxy/osx/windowless.mm:69` (NSProcessInfo env passed to AcCoreConsole), `Make/IronLib/core/additive/processSimulation/ProcessSimTask.cpp:104`, `Simulation/.../Posix.cpp` `getEnvironmentVector` (used by FEACSJobWriter / InjectionMolding SimCaseOverrule).
- Wrappers with no remaining name-literal callers: `cEnvironmentUrls` (Electron/EAGLE/src/webapi/EnvironmentUrls.cpp:12, no instantiations found), `getEnvironmentVariable` helper in Publish/AcFusionDoc/DrawingViewCompute/imp/DrawingViewComputeImpl.cpp:57 (unused), Simulation `Posix.h` `getenv` wrapper (no callers).
- Commented-out reads ignored: `TRAIL_ENABLE` (Publish/Animation/Server/Animation/Annotation/TrailManager.cpp:87), `APIH_SRC` (DbDumpObject.cpp:4654), `USERPROFILE` (FluidDynamics SimCaseOverrule.cpp:838).
- Third-party reads skipped: `Electron/EAGLE/libs/whereami` (PATH), `Electron/EAGLE/libs/sqlite3` (SQLITE_TMPDIR, TMPDIR, TMP, TEMP, USERPROFILE, SQLITE_FORCE_PROXY_LOCKING).

## Scope and method

- **What was searched:** C, C++ and Objective-C sources in `Core/` and every submodule, for `getenv`, `_wgetenv(_s)`, `_dupenv_s`, `qgetenv`, `qEnvironmentVariable*`, `GetEnvironmentVariable*`, `QProcessEnvironment::value`, `Ns::OS::platformGetEnvironmentVariable`, and the project's own wrappers (`AcFusionServiceUtils`, IronLib `Process`/`System`, EAGLE `GetEnv`/`GetEnvInt`, `SimRegistryUtils`). Names passed through constants, loops or lookup tables were traced back to their actual strings.
- **Runtime Python:** the only Python code that reads a variable at runtime is the internal add-ins `parts4cad.py` and `traceparts.py`, which read `CHOTAY_APP`.
- **Excluded:** third-party code, unit tests (except a few test-only reads, which are in category 9), build-time-only variables (CMake, Conan, CI scripts), and code that only sets variables without reading them.
- **Secrets:** no secret values appear anywhere in this file, only variable names.
