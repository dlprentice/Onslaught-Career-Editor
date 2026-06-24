# Lane 01 - WPF Shell UX Audit

Scope: `App.xaml`, `MainWindow.xaml`

Findings:

- HIGH | `App.xaml:57`, `App.xaml:63`, `App.xaml:72`, `App.xaml:86`, `App.xaml:92`, `App.xaml:109`, `App.xaml:117`, `App.xaml:175`, `App.xaml:211`, `App.xaml:218`, `App.xaml:227`, `App.xaml:236`, `App.xaml:242`, `App.xaml:257`, `App.xaml:452`, `App.xaml:461` | Duplicate resource/style keys (`HelperTextStyle`, `InfoCalloutBorderStyle`, `WarningCalloutBorderStyle`, `PrimaryActionButtonStyle`, `PrimaryButtonStyle`) are redefined multiple times. The last declaration silently wins, which makes the effective visual system hard to predict and easy to drift. | Collapse each keyed style to one canonical definition, keep variants `BasedOn` a single base style, and remove dead/overridden duplicates so shell styling is deterministic.

- HIGH | `App.xaml:360`-`App.xaml:400`, `MainWindow.xaml:92`-`MainWindow.xaml:139` | One global `TabItem` template is styling both the primary app navigation and the nested per-section tabs the same way. That flattens hierarchy, so top-level areas (`Saves`, `Media`, `Lore`) and second-level tools (`Save Editor`, `Save Analyzer`, `Configuration Editor`) visually compete instead of nesting clearly. | Split shell navigation into distinct keyed styles, e.g. `PrimaryTabItemStyle` for top-level navigation and a quieter `SecondaryTabItemStyle` for nested tabs, then apply them explicitly per `TabControl`.

- MEDIUM | `MainWindow.xaml:21`-`MainWindow.xaml:82` | The shell stacks a full menu card and a large hero card before any working content. On a dense desktop editor, that is too much non-working chrome, especially on shorter displays, and it pushes the first actionable controls further below the fold than necessary. | Compress the top chrome: either merge the menu into the header treatment or reduce hero padding/height and badge density so the content area gets more vertical space.

- MEDIUM | `MainWindow.xaml:8`-`MainWindow.xaml:10` | The window sets startup size but no `MinWidth` / `MinHeight`. With nested tab layouts and dense editors below, users can resize into states where navigation and forms become cramped or partially unusable. | Add tested desktop minimums (roughly the smallest layout that still keeps save/config editors readable) and rely on inner scrolling for overflow instead of allowing shell collapse.

- LOW | `MainWindow.xaml:143`-`MainWindow.xaml:175` | The footer’s right-side pill shows a raw path without an explicit label. It works once the user already knows what it is, but at a glance it reads like filesystem noise rather than a stable “current game directory” status element. | Add a visible label/prefix such as `Game:` or switch to a small caption-plus-value layout so the footer communicates meaning immediately.

Overall assessment:

- The shell direction is good for a desktop utility: clear branding, visible status, and strong top-level navigation.
- The main UX debt is not missing features; it is visual-system discipline. Cleaning `App.xaml` and separating primary vs secondary navigation styles would produce the biggest quality jump with low behavioral risk.
