# Fusion Command-Line Arguments and Switches

Command-line switches that Fusion accepts, taken from the `client-delivery` source tree on branch `develop`, 2026-11-23, and grouped by **who would use them**. For environment variables, see [Fusion-Environment-Variables.md](Fusion-Environment-Variables.md).

## How the parser works

Fusion's command line is handled by `Ns::CommandLineMgr` (`Core/Neutron/Server/BaseCore/CommandLine/`), which is built on Boost.Program_options. Switches are registered with these macros:

- `NS_COMMANDLINE_OPTION` / `NS_COMMANDLINE_OPTION_INTERNAL`: on/off flags that take no value.
- `NS_COMMANDLINE_ACTION` / `NS_COMMANDLINE_ACTION_INTERNAL`: switches that take a value, which can be required, optional or not allowed.

Syntax rules (`Impl/implCommandLineMgr.cpp`):

- Long form is `--name` or `--name=value` / `--name value`. The single-dash form `-name` also works.
- Short form is `-x`, and `/x` also works. Short flags can be stacked, for example `-sk`.
- Names are **case-insensitive**, and unambiguous prefixes are accepted.
- **After add-ins** means the switch runs after add-ins have loaded. All other switches run during startup, before add-ins load.
- **Hidden** switches are left out of `--help` unless you also pass `--showInternal`.

> **Caution:** only categories 1–3 are intended for people outside the Fusion development team. Later categories are for QA, Autodesk infrastructure or Fusion's own launchers. Some of them turn off dialogs, sign in automatically or change authentication.

## Summary by category

| # | Category | Who uses it | Switches |
|---|---|---|---|
| 1 | [General startup](#1-general-startup) | End users | 3 |
| 2 | [Troubleshooting and recovery](#2-troubleshooting-and-recovery) | End users and support | 6 |
| 3 | [Scripting and add-in automation](#3-scripting-and-add-in-automation) | Power users and add-in developers | 4 |
| 4 | [Product integration](#4-product-integration) | Other Autodesk products (AutoCAD, Inventor) | 2 |
| 5 | [Testing, QA and CI](#5-testing-qa-and-ci) | QA, test automation and build servers | 10 |
| 6 | [Hosted and automation service contexts](#6-hosted-and-automation-service-contexts) | Autodesk infrastructure | 6 |
| 7 | [Developer and internal](#7-developer-and-internal) | Fusion developers | 3 |
| | **Total (main executable)** | | **34** |
| 8 | [Performance Feedback Agent](#8-performance-feedback-agent-helper-executable) (separate helper) | Set by Fusion itself | 17 |

The **Set automatically by** notes say when Fusion or its launcher passes a switch itself. For example, NLauncher adds `--nologo`, and a restart adds `-ClearUserCache`.

## 1. General startup

**Who:** end users. These are safe, everyday options for starting Fusion.

| Switch / Argument | Short | Value | Hidden | After add-ins | Function | Notes | Source |
|---|---|---|---|---|---|---|---|
| `--help` | `-?` | – | No | No | Prints every registered option and action, with help text, to the console. | Add `--showInternal` to include hidden switches. | `Core/Neutron/UI/Base/Application/CommandLineActionsAndOptions/CommandLineOptions.cpp:15` |
| `--nologo` | – | – | No | No | Turns off the splash screen. | Set automatically by NLauncher unless a `fusion360://…&flag=--showLogo` URL is passed (`Core/Neutron/Suites/NLauncher/AppLauncherUtility.cpp:242`). | `…/CommandLineOptions.cpp:95` |
| `--offlineStart` | – | – | No | No | Starts Fusion in offline mode. | Similar to the `NEUTRON_FORCE_OFFLINE=YES` environment variable. | `Core/Fusion/Applications/Fusion360Application/CommandLineActionsAndOptions/CommandLineOptions.cpp:132` |

## 2. Troubleshooting and recovery

**Who:** end users and support. Use these to recover from a startup problem or gather information for a support case.

| Switch / Argument | Short | Value | Hidden | After add-ins | Function | Notes | Source |
|---|---|---|---|---|---|---|---|
| `--safeMode` | – | – | No | No | Runs in safe mode: no scripts or add-ins load automatically at startup, and some optimizations are turned off. | Use it when a startup script or add-in stops Fusion from launching. | `Core/Neutron/UI/Base/Application/CommandLineActionsAndOptions/CommandLineOptions.cpp:115` |
| `--serviceUtil` | – | – | No | No | Starts the Fusion Service Utility (repair/reset/uninstall) instead of the normal UI. | Set automatically by the Service Utility command (`Core/Neutron/UI/Commands/Commands/Application/ServiceUtilityCmd.cpp:78`). The `FUSION_SERVICE_UTILITY=DISABLE` environment variable turns this path off. | `…/CommandLineOptions.cpp:122` |
| `--ClearUserCache` | – | – | No | Yes | Deletes the user's cloud cache folders once online. | Set automatically as `-ClearUserCache` when Fusion restarts itself to clear the cache (`Core/Neutron/UI/Commands/Commands/Application/ExitApplicationCmd.cpp:1041`). | `Core/Fusion/Applications/Fusion360Application/CommandLineActionsAndOptions/CommandLineOptions.cpp:125` |
| `--Diagnostic` | `-d` | none | No | Yes | Dumps the user's diagnostics data to a zip file (`PostLoadDiagnosticsTask`). | Useful for support cases. | `Core/Neutron/Client/Base/Application/CommandLineActionsAndOptions/CommandLineActions.cpp:130` |
| `--log <file>` | – | required | No | No | Writes command-line output to the given log file. | Combine with `--help`, `--execute` and similar switches to capture their output. | `…/Client/Base/Application/CommandLineActionsAndOptions/CommandLineActions.cpp:107` |
| `--disable "<AddIn1 AddIn2 …>"` | – | required | No | No | Turns off the listed add-ins, given by AppName in double quotes. | A more targeted alternative to `--safeMode` when one add-in is the problem. | `…/CommandLineActions.cpp:57` |

## 3. Scripting and add-in automation

**Who:** power users and add-in developers. These run scripts or text commands, turn add-ins on, and control when Fusion exits.

| Switch / Argument | Short | Value | Hidden | After add-ins | Function | Notes | Source |
|---|---|---|---|---|---|---|---|
| `--script <path>` | `-s` | required | No | Yes | Runs a Python (`.py`), C++ or TypeScript script once add-ins have loaded and sign-in is initialized. | Logs an error for any other file extension. | `Core/Neutron/Server/XLayer/Infrastructure/ScriptManager.cpp:3757` |
| `--execute <TextCommand>` | `-e` | required | No | Yes | Runs the given text command (for example `"Diagnostics.Foo /x"`) once add-ins have loaded. | Some text commands only exist in internal builds. | `Core/Neutron/Client/Base/Application/CommandLineActionsAndOptions/CommandLineActions.cpp:22` |
| `--enable "<AddIn1 AddIn2 …>"` | – | required | No | No | Turns on the listed add-ins, given by AppName in double quotes. | | `…/CommandLineActions.cpp:36` |
| `--exitAfterAddIn` | – | – | No | Yes | Shuts Fusion down after add-ins load. | Use with `--script` or `--execute` for one-shot runs. | `Core/Neutron/UI/Base/Application/CommandLineActionsAndOptions/CommandLineOptions.cpp:107` |

## 4. Product integration

**Who:** other Autodesk products. AutoCAD and Inventor pass these when they hand a model to Fusion. Do not use them by hand: they expect a temp file to already exist.

| Switch / Argument | Short | Value | Hidden | After add-ins | Function | Notes | Source |
|---|---|---|---|---|---|---|---|
| `--AutoCAD` | – | – | No | Yes | Opens the DWG that AutoCAD handed over through the temp folder, shows a "Return to AutoCAD" button, and blocks the New, Save and Open commands. | Asserts and fails if the temp file is missing. | `Core/Fusion/Applications/Fusion360Application/CommandLineActionsAndOptions/CommandLineOptions.cpp:79` |
| `--Inventor` | – | – | No | Yes | Opens `Fusion_Edit_Temp.sat` from the temp folder, shows a "Return to Inventor" button, and blocks the New, Save and Open commands. | Asserts and fails if the temp file is missing. | `…/Fusion360Application/CommandLineActionsAndOptions/CommandLineOptions.cpp:109` |

## 5. Testing, QA and CI

**Who:** QA, test automation and build servers. These run test suites, start the NTest test server, sign in automatically, or turn off dialogs and prompts.

| Switch / Argument | Short | Value | Hidden | After add-ins | Function | Notes | Source |
|---|---|---|---|---|---|---|---|
| `--fullTest [result file]` | – | optional | No | Yes | Runs the full regression suite once the UI has loaded, then exits. | Uses `Diagnostics.RunTests /F`, which is deprecated. | `Core/Neutron/UI/Base/Application/CommandLineActionsAndOptions/RegressionTestActions.cpp:17` |
| `--perfTest "<Baseline> [TestCase\|TranscriptFileOrDir] [/log <result>]"` | – | optional | No | Yes | Runs performance tests once the UI has loaded (`Diagnostics.RunPerfTests`), then exits. | Paths can be relative to the `Performance` folder or absolute. | `…/RegressionTestActions.cpp:26` |
| `--ntestwsserver` | – | – | No | Yes | Starts the NTest automation WebSocket server (`NTestAutomationServer.ActivateWebSocket`). | | `Core/Neutron/NTest/Server/NTest/CommandLine/NTestCommandLine.cpp:8` |
| `--activateTestingContext` | – | – | No | Yes | Turns on the testing context. | | `Core/Neutron/UI/Base/Application/CommandLineActionsAndOptions/CommandLineOptions.cpp:135` |
| `--standaloneNTestStartFusion` | – | – | No | Yes | Marks this Fusion instance as started by the standalone NTest test runner. | Set automatically by the NTest runner. | `…/CommandLineOptions.cpp:147` |
| `--TestingDashboard` | – | – | No | Yes | Creates a new document and sets the "running tests" flag so that dialogs are suppressed, for dashboard JS test automation. | | `Core/Fusion/Applications/Fusion360Application/CommandLineActionsAndOptions/CommandLineOptions.cpp:114` |
| `--autoSendCER` | – | – | No | Yes | Sends crash reports (CER) automatically, without asking the user. | Meant for unattended runs. | `Core/Neutron/UI/Base/Application/CommandLineActionsAndOptions/CommandLineOptions.cpp:141` |
| `--noInteractiveUser` | – | – | **Yes** | Yes | Runs with no user interaction (headless or automation). | | `…/CommandLineOptions.cpp:154` |
| `--autologin <user,password>` | – | required | No | No | Signs in automatically with the given credentials. | The credentials are visible in the process list, so use test accounts only. | `Core/Neutron/Client/Base/Application/CommandLineActionsAndOptions/CommandLineActions.cpp:143` |
| `--autoregister <first,last,email,password>` | – | required | No | No | Registers a new account and signs in automatically. | Test accounts only. | `…/CommandLineActions.cpp:167` |

## 6. Hosted and automation service contexts

**Who:** Autodesk infrastructure. The Fusion Automation Service (FAS), the embedded canvas host, and bearer-token hosts pass these. All are hidden.

| Switch / Argument | Short | Value | Hidden | After add-ins | Function | Notes | Source |
|---|---|---|---|---|---|---|---|
| `--fas` | – | – | **Yes** | Yes | Runs in the Fusion Automation Service context. | Works together with the `FAS_*` environment variables. | `Core/Neutron/Server/Base/Utility/FusionAutomationService.cpp:195` |
| `--2legged` | – | – | **Yes** | Yes | Expects 2-legged (app-only, no user) authentication. | | `…/FusionAutomationService.cpp:200` |
| `--fasregion <region>` | – | required | **Yes** | Yes | Sets the region used to pick a hub in the FAS context. | | `…/FusionAutomationService.cpp:205` |
| `--bearer` | – | – | **Yes** | Yes | Uses bearer-token authentication. | The token comes from the `FUSION_BEARER_TOKEN` environment variable. | `Core/Neutron/UI/Base/Cloud/BearerAuth.cpp:794` |
| `--canvasOnly` | – | – | **Yes** | No | Shows only the canvas area, with no surrounding UI (embedded/asset shell). | | `Core/Neutron/UI/Commands/Shells/AssetShell.cpp:151` |
| `--delayed-host-url <url>` | – | value (next arg) | Not registered | – | Adds the URL to the data registry once the UI is ready. | Read straight from `qApp->arguments()`, and only when `--canvasOnly` is set. | `Core/Neutron/UI/Base/Application/Impl/implApplication.cpp:1610` |

## 7. Developer and internal

**Who:** Fusion developers. Also includes switches Fusion's own updater passes, and one placeholder.

| Switch / Argument | Short | Value | Hidden | After add-ins | Function | Notes | Source |
|---|---|---|---|---|---|---|---|
| `--showInternal` | – | – | No | No | Includes hidden switches in the `--help` output. | | `Core/Neutron/UI/Base/Application/CommandLineActionsAndOptions/CommandLineOptions.cpp:89` |
| `--exit` | – | – | No | No | Shuts Fusion down before add-ins load. | Useful for timing startup or checking that the app initializes. | `…/CommandLineOptions.cpp:101` |
| `--disableupdatecheck` | – | – | **Yes** | No | Turns off the Live Update check. | Set automatically by the ODIS update host when it relaunches Fusion (`Core/Services/Platform/LiveUpdate/ODISHost.cpp:889`). | `Core/Services/Platform/LiveUpdate/LiveUpdateBase.cpp:72` |
| `--print <arg>` | – | required | No | Yes | **Not implemented.** It is registered but does nothing. | Not counted in the totals above. | `Core/Neutron/Client/Base/Application/CommandLineActionsAndOptions/CommandLineActions.cpp:100` |

## 8. Performance Feedback Agent (helper executable)

**Who:** set by Fusion itself. Fusion's Performance Feedback Recorder launches this separate helper with these Windows-style `/Name:value` switches. Users never pass them directly.

| Switch / Argument | Function | Source |
|---|---|---|
| `/ProductName:"name"` | Name of the host product. | `Core/Fusion/Applications/PerformanceFeedbackRecorder/PerfFeedbackAgent/CommandLineParser.cpp:12` |
| `/PID:nnnnn` | Process ID of the host product. | `…/CommandLineParser.cpp:14` |
| `/HostHwnd:nnnnn` | Window handle of the host product. | `…/CommandLineParser.cpp:16` |
| `/MaxRecMinutes:nnnnn` | Maximum recording time in minutes (optional, default 10). | `…/CommandLineParser.cpp:19` |
| `/ProductKey:"key"` | Product identity key. | `…/CommandLineParser.cpp:23` |
| `/Lang:ENU` | Product language. | `…/CommandLineParser.cpp:25` |
| `/Theme:Light` | Product UI theme. | `…/CommandLineParser.cpp:26` |
| `/CPRServer:Production\|staging` | Which CPR server to upload to. | `…/CommandLineParser.cpp:29` |
| `/Profiles:"CPU GPU DiskIO FileIO"` | Space-separated list of profilers to run. `NONE` skips profiling and goes straight to the questionnaire and upload. | `…/CommandLineParser.cpp:34` |
| `/Position:(x,y)` | Screen position of the agent window. | `…/CommandLineParser.cpp:39` |
| `/SRN:<notifier>` | Stop-Recording notifier (optional). | `…/CommandLineParser.cpp:41` |
| `/DRN:<notifier>` | Data-Ready notifier (optional). | `…/CommandLineParser.cpp:43` |
| `/Start` | Starts recording right away (optional). Added automatically by the Fusion-side launcher. | `…/CommandLineParser.cpp:44` |
| `/Master:<id>` | Product Master ID (UPI). | `…/CommandLineParser.cpp:45` |
| `/Product_line:<line>` | Product line from ForgeApplicationEditionService. | `…/CommandLineParser.cpp:47` |
| `/Build:<version>` | Build version (`NEUTRON_VERSION_STRING`). | `…/CommandLineParser.cpp:48` |
| `/Release:<id>` | Product release ID (`Ns::SoftwareVersion::productReleaseId`). | `…/CommandLineParser.cpp:49` |

## Scope

- **Searched:** everything under `Core/`, plus the submodules (`Electron/`, `Make/`, `Mesh/`, `Publish/`, `Simulation/`, `CloudTranslation/`, `VolumetricField/`) for the `NS_COMMANDLINE_*` macros, and for raw `argv` / `qApp->arguments()` checks. The submodules register no switches of their own.
- **Other arguments:** anything that is neither an option nor an action (for example file paths) is collected in `CommandLineMgr::nonActionAndNonOptionArguments()`.
- **Not included:**
  - Registrations used only by unit tests (`commandLineOptionTest` `-x`, `commandLineActionTest` `-y`, `CLATest*` `-z`).
  - Switches that Fusion passes to *child* processes, such as `--inspect` / `--use-system-ca` to Node and `--silent` / `--ppid` to the uninstaller.
- **Categories are a judgment call** based on what each switch does in the code. Nothing in the source marks them this way.
