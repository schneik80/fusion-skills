# Dashboard.ShowInLocation — folder / project support and `openDataPanel` flag

**Repo:** `client-delivery` (Fusion) · **Branch:** `Schneik` (from `develop`)
**Commit:** `8702ace40e84e48e171c2c991523eb863eea1ca7` — 2026-08-24
**Title:** `Dashboard.ShowInLocation: accept folder/project ids and optional openDataPanel flag`
**Files:** 4 changed, +166 / −62

| File | Change |
| --- | --- |
| `Core/Neutron/UI/Commands/Dashboard/MainDashboardController.cpp` | Core logic: id classification, folder/project resolution, helpers |
| `Core/Neutron/UI/Commands/Dashboard/MainDashboardController.h` | New `bOpenDataPanel` parameter, private error helper, doc comment |
| `Core/Neutron/UI/Commands/Dashboard/TextCommands/DashboardTextCommands.cpp` | Text command parsing of the new optional flag; help text |
| `Core/Neutron/UI/OfflineJS/Dashboard/src/app/panes/designs.js` | Data Panel JS: honour `isFolder` marker; null‑safe error path |

> Status: **not yet built or tested**. Authored on a Linux machine that cannot build Fusion. No pre‑commit hook was installed in the clone, so `rfmt` did not run — format the two C++ files before opening a PR.

---

## 1. Motivation

`Dashboard.ShowInLocation` is a text command (transcript/automation entry point) that makes the Data Panel navigate to a file and highlight it. It had two limitations:

1. It **always forced the Data Panel open** (`DashboardModeOpenCommand`) — there was no way to update the panel's location silently.
2. It only accepted a **file lineage URN** (`urn:adsk.wipprod:dm.lineage:…`). Folders and projects could not be targeted.

This commit adds:

- An optional second parameter, `openDataPanel` (`true|false|1|0`, default `true`).
- Support for **folder URNs** (`urn:adsk.<env>:fs.folder:co.<id>`) → the Data Panel opens *inside* the folder with nothing selected.
- Support for **DM project ids** (`a.<base64>`, decoding to `<hub>#<groupId>`) → the Data Panel opens the project's root folder.

File behaviour is unchanged: navigate to the parent folder and highlight the file.

New usage:

```
Dashboard.ShowInLocation <id> [openDataPanel]

Dashboard.ShowInLocation "urn:adsk.wipprod:dm.lineage:1HD7MrtmRLiS2umonmmPQQ"
Dashboard.ShowInLocation "urn:adsk.wipprod:fs.folder:co.ZX4Hk0ZPTpWklqU7gGPg0A" false
Dashboard.ShowInLocation "a.YnVzaW5lc3M6d2lwMWZxYWF1dG9kZXNrMTYwMg"
```

---

## 2. Architecture / how the pieces fit

```
Text command window / transcript
        │  Dashboard.ShowInLocation <id> [openDataPanel]
        ▼
DashboardTextCommands.cpp  (NS_TEXTCOMMAND_SUBCLASS Dashboard::ShowInLocation)
        │  validates params, parses flag
        ▼
MainDashboardController::showInLocation(id, documentName, bOpenDataPanel)
        │  1. optionally execute DashboardModeOpenCommand
        │  2. classify id  ──► file / folder / project
        │  3. resolve via CloudFileStore / CloudBrowser::Browser
        │  4. build JSON path array, root‑first
        ▼
jsObject()->sendJavascriptEvent("showInLocation", <json array>)
        │
        ▼
designs.js  _onNeutronEvent  (cmdId == "showInLocation")
        │  last element tagged isFolder?  ──► fileDatum = null, whole array = path
        │  else                            ──► last = fileDatum, rest = path
        ▼
_onGetFolderInfoForGoTo → GoToPaneAndChangePath → DataView._goToFolder
        → ProjectDetail.goTo (switches active project if needed)
        → Designs.goToFolder(pathData, fileDatum)   // fileDatum null ⇒ no highlight, no spinner
```

### The JS payload contract (pre‑existing, now extended)

`showInLocation` sends a JSON **array** of `{ "id": …, "name": … }` objects:

- Elements `[0 .. n‑2]` are the folder chain from the **project root folder** downward. `folderPath[0].id` **must** be the project's root‑folder URN because `Projects.getProjectObj()` matches `project.rootFolder.id === folderPath[0].id`.
- Element `[n‑1]` is the item to **highlight** after navigation.

Extension introduced here: if the last element carries `"isFolder": true`, JS treats the **entire** array as the path and passes `fileDatum = null` — which `Designs.goToFolder` already supports (it is the shape used by the existing `GoToSelectedFolder` flow).

---

## 3. C++ changes — `MainDashboardController`

### 3.1 Header (`MainDashboardController.h`)

```cpp
/// Navigate the Data Panel to an item. `id` may be a file lineage urn (parent folder opened, file
/// highlighted), a folder urn (folder opened) or a DM project id "a.<base64>" (project root opened).
void showInLocation(const Ns::IString& id, bool bOpenDataPanel = true);
void showInLocation(const Ns::IString& id, const Ns::IString documentName, bool bOpenDataPanel = true);
...
private:
    void sendShowInLocationError(const Ns::IString& id, const Ns::IString& name);
```

- `bOpenDataPanel` is **defaulted to `true`** on both overloads so every existing caller (`ShowInLocationCmd.cpp`, `NotificationCenterController.cpp`, the text command) compiles and behaves exactly as before.
- `sendShowInLocationError` is a private helper replacing an inline block that previously existed only for the file case.

### 3.2 New include

```cpp
#include <Services/Data/CloudFileStore/QontextUtilities.h>
```
Provides `Ns::QontextUtilities::isLineageURI / isFolderURI` (`QontextUtilities.h:68‑70`), the canonical URN classifiers already used elsewhere in the codebase. `Base64Utilities.h` and the CloudBrowser headers were already included.

### 3.3 Helper: `buildFolderPathNode` (extracted, behaviour‑preserving)

The original function contained an inline loop that walked from a folder id to the project root using a `std::stack` and then emitted the entries root‑first. That loop is now a file‑static helper so all three id kinds share it:

```cpp
// Walks from startFolderId up to the project root and appends {id, name} entries to pathNode, root first.
static void buildFolderPathNode(const IString& startFolderId, JSONNode& pathNode)
{
    CloudBrowser::Browser* pBrowser = CloudBrowser::Browser::get();
    NEUTRON_ASSERT(pBrowser);
    if (!pBrowser)
        return;

    std::stack<std::pair<IString, IString>> foldersInPath;
    IString folderId = startFolderId;

    while (true)
    {
        std::shared_ptr<CloudBrowser::Folder> folder;
        Ns::Status status = pBrowser->getFolderById(ToHString(folderId), folder);
        // We get the parent folder as nullptr when we ask the project's root folder for the parent
        if (folder.get() == nullptr)
            break;

        foldersInPath.push(std::make_pair(folderId, ToIString(folder->name())));

        folderId = ToIString(folder->parentFolderId());
    }

    while (!foldersInPath.empty())
    {
        auto folder = foldersInPath.top();

        JSONNode folderNode;
        folderNode["id"] = folder.first;
        folderNode["name"] = folder.second;

        foldersInPath.pop();

        pathNode.push_back(folderNode);
    }
}
```

Logic: `getFolderById` is called repeatedly with `parentFolderId()`; the root folder's parent lookup returns `nullptr`, terminating the loop. Because the stack reverses insertion order, the output array is root‑first, which is what the JS expects.

Incidental cleanup: the old loop also fetched `getCachedFileById(fileUrn)` into a local that was never used; that call has been dropped.

### 3.4 Helper: `groupIdFromDmProjectId`

```cpp
// Decodes a DM project id of the form "a.<base64 of hub#groupId>" into the group id. Returns empty on failure.
static HString groupIdFromDmProjectId(const IString& projectId)
{
    if (!projectId.starts_with(L"a."))
        return HString();

    const HString base64 = ToHString(projectId).substr(2);
    const HString decoded = Ns::Base64::decodeBase64(base64.data(), base64.size());
    const size_t pos = decoded.find("#");
    if (pos == HString::npos || pos >= decoded.size() - 1)
        return HString();

    return decoded.substr(pos + 1);
}
```

This mirrors the decoding already done in `Core/Neutron/UI/Commands/Commands/Documents/DocumentUtilsUI.cpp:504‑515` for the insert command. `a.` ids base64‑encode a string like `business:wip1fqaautodesk1602#20140708309098`; the part after `#` is the CloudBrowser **group id**, which is what `Browser::getGroupById` accepts (it explicitly rejects `urn:`‑prefixed ids — `Browser.cpp:1024‑1030`).

### 3.5 Helper: `sendShowInLocationError`

```cpp
void MainDashboardController::sendShowInLocationError(const IString& id, const IString& name)
{
    Ns::JSONNode node;
    node["lineageUrn"] = id;
    node["name"] = name;
    node["error_reason"] = "FILE_NOT_FOUND";
    JavaScriptObject* dashboardJsObj = jsObject();
    if (dashboardJsObj)
        dashboardJsObj->sendJavascriptEvent(L"showGoToLocationError", node.toIString(), true);
}
```

The payload keys are unchanged from the previous inline code so the JS `showGoToLocationError` handler (`designs.js` → `_displayGoToError`) shows the existing toast: *"Cannot access **<name>**. It may have been moved or deleted."* (`FILE_NOT_FOUND` is one of the two reasons that produce that message). The key is still named `lineageUrn` for backward compatibility even though it may now hold a folder URN or project id.

### 3.6 Main function: `showInLocation`

```cpp
void MainDashboardController::showInLocation(const IString& id, const IString documentName, bool bOpenDataPanel)
{
    bool dataPanelOpened = Nu::UIBaseOptionGroup::get()->wantToShowDataPanel();
    if (bOpenDataPanel && !dataPanelOpened)
    {
        Nu::CommandContext ctx(Nu::CommandContext::eApSystem);
        Nu::CommandMgr::get()->executeCommand(L"DashboardModeOpenCommand", ctx);
    }

    const HString hId = ToHString(id);
    JSONNode pathNode;
```

**Step 1 — Data Panel open.** Unchanged except for the `bOpenDataPanel &&` guard. When `false`, the event is still sent; if the panel is closed the web view simply updates its state without becoming visible.

**Step 2 — File lineage URN** (`isLineageURI` ⇒ contains `dm.lineage:`):

```cpp
    if (Ns::QontextUtilities::isLineageURI(hId))
    {
        IString fileUrn = id;
        IString fileName = documentName;

        Ns::CloudService::CloudFileStore* pCFS = Ns::CloudService::CloudFileStore::get();
        if (pCFS == nullptr)
            return;

        auto cloudfile = pCFS->cloudFileFromUri(hId);

        // validate if we are able to get file data
        if (cloudfile == nullptr)
        {
            sendShowInLocationError(fileUrn, fileName);
            return;
        }

        // validate if asset file is a configuration
        if (cloudfile->isConfigMember())
        {
            const IString factoryLineageUrn = cloudfile->factoryLineageUrl();
            cloudfile = pCFS->cloudFileFromUri(ToHString(factoryLineageUrn));
            if (cloudfile != nullptr)
            {
                fileUrn = cloudfile->lineageUri();
                fileName = cloudfile->documentName();
            }
        }

        // create file hierarchy information, then the file itself as the item to highlight
        buildFolderPathNode(cloudfile->parentFolderUrn(), pathNode);

        JSONNode fileDatum;
        fileDatum["id"] = fileUrn;
        fileDatum["name"] = fileName;
        pathNode.push_back(fileDatum);
    }
```

Identical semantics to the original: resolve the `CloudFile`, redirect configuration members to their factory design, build the path from the file's **parent** folder, append the file as the highlight target. Payload example:

```json
[ {"id":"urn:…:fs.folder:co.ROOT","name":"Project"},
  {"id":"urn:…:fs.folder:co.SUB","name":"Sub"},
  {"id":"urn:…:dm.lineage:FILE","name":"Bracket v3"} ]
```

**Step 3 — Folder URN** (`isFolderURI` ⇒ contains `fs.folder:co.`):

```cpp
    else if (Ns::QontextUtilities::isFolderURI(hId))
    {
        // Folder: open the folder itself (path includes the folder, nothing selected)
        CloudBrowser::Browser* pBrowser = CloudBrowser::Browser::get();
        std::shared_ptr<CloudBrowser::Folder> folder;
        if (pBrowser)
            pBrowser->getFolderById(hId, folder);

        if (!folder)
        {
            sendShowInLocationError(id, documentName);
            return;
        }

        buildFolderPathNode(id, pathNode);
        if (pathNode.empty())
        {
            sendShowInLocationError(id, ToIString(folder->name()));
            return;
        }
        pathNode[pathNode.size() - 1]["isFolder"] = true;
    }
```

- The folder is looked up first purely to fail fast with a proper error toast if it doesn't exist / isn't accessible.
- The path is built **starting at the folder itself** (not its parent), so the last array element *is* the target folder.
- That last element is tagged `"isFolder": true`. `JSONNode` has no `back()`, hence `pathNode[size‑1]`; `JSONRef` supports chained `[]` and `operator=(bool)`.
- A project's "wip id" is itself a root‑folder URN, so passing a root‑folder URN naturally lands on the project root through this branch.

Payload example:

```json
[ {"id":"urn:…:fs.folder:co.ROOT","name":"Project"},
  {"id":"urn:…:fs.folder:co.SUB","name":"Sub","isFolder":true} ]
```

**Step 4 — DM project id** (anything else; only `a.<base64>` is actually resolvable):

```cpp
    else
    {
        // Project: "a.<base64>" DM project id -> group -> root folder
        const HString groupId = groupIdFromDmProjectId(id);
        CloudBrowser::Browser* pBrowser = CloudBrowser::Browser::get();
        std::shared_ptr<CloudBrowser::Group> group;
        if (!groupId.empty() && pBrowser)
            pBrowser->getGroupById(groupId, group);

        std::shared_ptr<CloudBrowser::Folder> rootFolder = group ? group->rootFolder() : nullptr;
        if (!rootFolder)
        {
            sendShowInLocationError(id, group ? ToIString(group->name()) : documentName);
            return;
        }

        JSONNode rootNode;
        rootNode["id"] = ToIString(rootFolder->getId());
        rootNode["name"] = ToIString(rootFolder->name());
        rootNode["isFolder"] = true;
        pathNode.push_back(rootNode);
    }
```

- Decode → `Browser::getGroupById` → `Group::rootFolder()` (`Group.h:77`). Any failure (bad prefix, bad base64, unknown group, no root folder) falls into the error toast.
- The payload is a single tagged element. JS then has a one‑element path whose `[0].id` is the root‑folder URN — exactly what `getProjectObj` needs to switch projects — and no highlight target.

**Step 5 — send:**

```cpp
    // fire location change event to data-panel
    Nu::JavaScriptObject* dashboardJsObj = jsObject();
    if (dashboardJsObj)
        dashboardJsObj->sendJavascriptEvent("showInLocation", pathNode.stringify(), true);
}
```

---

## 4. Text command — `DashboardTextCommands.cpp`

```cpp
NS_TEXTCOMMAND_SUBCLASS(
    Dashboard,
    ShowInLocation,
    L"<id> [openDataPanel] Navigate to an item in the Data Panel. <id> is a file lineage urn (parent folder opened, "
    L"file highlighted), a folder urn (folder opened) or a DM project id \"a.<base64>\" (project root opened). "
    L"Optional openDataPanel (true|false, default true): when false, the Data Panel is not forced open",
    "",
    parameters)
{
    if (parameters.parameters() == 0)
        return TextCommandResult(NS_ERROR, L"Missing id parameter");

    IString lineageUrn = parameters.parameter(0);
    if (lineageUrn.empty())
        return TextCommandResult(NS_ERROR, L"Empty id parameter");

    bool bOpenDataPanel = true;
    if (parameters.parameters() > 1)
    {
        const IString openParam = parameters.parameter(1);
        if (openParam == L"false" || openParam == L"0")
            bOpenDataPanel = false;
        else if (openParam != L"true" && openParam != L"1")
            return TextCommandResult(NS_ERROR, L"Invalid openDataPanel parameter, expected true or false");
    }

    MainDashboardController::get()->showInLocation(lineageUrn, bOpenDataPanel);
    return TextCommandResult(NS_SUCCESS, L"Navigating to file location");
}
```

- The second parameter is optional; omitted ⇒ `true` (legacy behaviour).
- Strict validation: any value other than `true/false/1/0` returns an error rather than silently defaulting.
- No id classification happens here — that is deliberately centralised in the controller so C++ callers get the same behaviour.

---

## 5. JavaScript — `designs.js`

### 5.1 `showInLocation` event handler (`_onNeutronEvent`)

```js
else if (e.cmdId == "showInLocation") {

    var jsonObject = goog.json.parse(e.cmdArgs);

    if(!jsonObject.length)
        return;

    const last = jsonObject[jsonObject.length - 1];
    if (last && last.isFolder) {
        // Target is a folder (or project root): open it, nothing selected
        this._onGetFolderInfoForGoTo(null, {
            sequence: jsonObject.slice().reverse()
        }, "done");
    }
    else {
        // Target is a file: open its parent folder and highlight it
        this._onGetFolderInfoForGoTo(last, {
            sequence: jsonObject.slice(0, jsonObject.length - 1).reverse()
        }, "done");
    }

    // Hide the Details Popup as the showInLocation command refreshes the view
    this._hideDetail();
}
```

Why `.reverse()`: `_onGetFolderInfoForGoTo` expects the `sequence` in the leaf‑first order that the native `invoker.getFolderInfo()` callback produces, then reverses it back to root‑first before dispatching `GoToPaneAndChangePath`. The C++ side emits root‑first, so the handler reverses once here. `slice()` is used so the parsed array is not mutated in place.

Downstream, `fileDatum === null` means:
- `Designs.goToFolder` sets `_goToSelectedFile = null` → `_highlightFile` listener is never armed;
- `_showFullPageSpinner(!!fileDatum)` → no spinner.

### 5.2 Null‑safety in `_onGetFolderInfoForGoTo`

```js
-        this._displayGoToError(fileDatum.name, e);
+        this._displayGoToError(fileDatum?.name, e);
```

This branch only runs when the event object carries `error_reason`, which the C++ `showInLocation` payload never does; the guard is defensive so a null `fileDatum` can never throw. Optional chaining is already used elsewhere in this file (`opt_err?.['error_reason']`).

---

## 6. Backward compatibility

| Concern | Result |
| --- | --- |
| Existing C++ callers of `showInLocation(urn)` / `(urn, name)` | Unchanged — new parameter is defaulted. |
| Existing transcripts using `Dashboard.ShowInLocation "<lineage urn>"` | Unchanged — one‑param form defaults `openDataPanel = true`. |
| JS payload for files | Byte‑identical to before; `isFolder` is only added for folder/project targets. |
| `showGoToLocationError` payload | Same keys; `lineageUrn` may now contain a folder/project id. |
| `SingleBrowserHomeTabController::showInLocation` (UDA/home tab twin) | **Not modified.** It has its own JS and does not go through this text command. |

---

## 7. Known limitations / follow‑ups

- Only `a.<base64>` DM project ids are accepted as *project* inputs. Numeric group ids (e.g. `20140708309098`) are **not** accepted (they fall into the project branch, fail decoding, and produce the "Cannot access" toast). Root‑folder URNs work implicitly through the folder branch.
- `getFolderById` / `getGroupById` / `rootFolder()` are synchronous and may hit the network on a cache miss; this matches the pre‑existing file path's behaviour.
- The DM‑project resolution requires the group to already be in the user's cached group list (`getGroupById` does a cache lookup; unlike `getGroupByWipId` it does not refetch the tenant's groups).
- The error toast for a bad project id shows the raw id (truncated to 10 chars by JS) unless `documentName` was supplied.

---

## 8. Verification checklist (to run on Windows/macOS build)

1. Build `Nu::Commands` + FusionUI and the Dashboard JS bundle.
2. `Dashboard.ShowInLocation "<file lineage urn>"` → parent folder opens, file highlighted and scrolled into view (regression).
3. `Dashboard.ShowInLocation "<folder urn>"` → panel shows the folder's contents, breadcrumb correct, nothing selected, no spinner left running.
4. `Dashboard.ShowInLocation "a.<base64>"` → active project switches, root folder shown.
5. Each of 2–4 with trailing `false` and the Data Panel closed → panel stays closed, no JS console errors; open the panel afterwards and confirm it is on the right location.
6. `Dashboard.ShowInLocation "<urn>" maybe` → command error "Invalid openDataPanel parameter".
7. Deleted folder / unknown project / garbage id → "Cannot access …" toast, no exception.
8. Run `Core/Neutron/UI/Commands/Dashboard/UnitTests/`.
9. Run `rfmt` on the two C++ files (pre‑commit hook was not installed in this clone).
