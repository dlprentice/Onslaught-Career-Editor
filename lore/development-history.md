# Development History

### Timeline

| Period | Milestone |
|--------|-----------|
| **Pre-2000** | Glenn already working on terrain system during previous game |
| **Summer 2000** | Main development started with small team |
| **Mid-development** | In-house engine flexible enough for level designers to prototype |
| **2001** | GDC Europe presentation: "Procedural Landscapes" by Glenn Corpes |
| **Summer 2002** | Game finished |
| **GDC Europe 2002** | Cross-platform development presentation |
| **January 2003** | Released (publisher delayed from completion) |
| **April 2003** | Game Developer Magazine post-mortem published |
| **May 2003** | NVIDIA GeForce FX 5900 OEM deal signed; Stunt Car Racer Pro partnership announced |
| **August 2003** | Encore signs PC publishing deal |
| **October 2003** | PC version released; Lost Toys closes |
| **2020** | Steam release by Ziggurat Interactive |

---

## The GDM Post-Mortem (April 2003)

*The following is an extensive summary of the Game Developer Magazine post-mortem written by **Ben Carter**, Lead Programmer at Lost Toys. This article provides invaluable insight into the development process and is preserved here for the historical record.*

### About Ben Carter

> "Ben has been working in the games industry since 1995, both as a freelance journalist for magazines including Super Play, Edge, and G4, and was a lead programmer on two titles for the Acorn RISC OS platform (MERP and MIRROR IMAGE), and one on the PC (ABSOLUTE TERROR). He has also been involved in writing games coverage for many nonspecialist press publications such as Manga Max and The Irish Times. Having spent the last two years working on PS2 and Xbox engine code for BATTLE ENGINE AQUILA, he is now working on the graphics engine for Lost Toys' as-yet unannounced future projects and spending far too much time watching anime."

### The Original Vision

Battle Engine Aquila was built around the desire to create a "next-generation" shoot-'em-up combining the core playability of titles such as **1942** and **Radiant Silvergun** with cutting-edge technology and graphics.

> "The concept behind BATTLE ENGINE AQUILA's take on the genre was simple — instead of following the current trend of having a lone player battle against incredible odds, why not re-create those epic action scenes seen in films such as **Starship Troopers** and **Saving Private Ryan**? The player is not a lone soldier, but part of a vast fighting force — albeit one which is doomed to fail without the support of the players' vehicle, the Battle Engine Aquila."

### The Ambitious Design

From the outset, it was clear that Battle Engine Aquila would be an ambitious project:

> "The original design called for **massive battles between hundreds of individual units**, all controlled by their own AI and able to react to anything the player did (ruling out any extensive scripting). The player would have the freedom to roam throughout the battlefield and interact with everything that was happening. Effectively, we would be creating a **complex, large-scale RTS game engine**, and then attempting to provide FPS-style gameplay and graphics to match."

The team expanded from their relatively small first project (MoHo/Ball Breakers) to handle the project's scale — a process that continued right through to the later stages of development.

### Development Approach

> "Even though we were targeting consoles (specifically the Xbox and Playstation 2) for the final game, **all of our development work was done on the PC**. It wasn't until late in development that we moved the code base over to the two consoles, and even then it was only the programmers and testers working on those consoles that ran the game on them — all the artists and designers used the PC version of the game. This turned out to be both a blessing and a curse."

### Technical Stats

| Metric | Value |
|--------|-------|
| **Publisher** | Infogrames |
| **Full-time developers** | 12-18 |
| **Contractors** | 2 |
| **Development time** | 30 months |
| **Release date** | January 27, 2003 (NA); February 28, 2003 (EU) |
| **Target platforms** | PlayStation 2, Xbox (PC forthcoming) |
| **Dev hardware** | 400MHz-1.8GHz CPUs, 256-768MB RAM, GeForce 3 cards, PS2/Xbox devkits |
| **Dev software** | Visual Studio 6, Visual C++ 6, Source Safe, ProDG, 3DS Max, Photoshop |
| **Notable tech** | Bink, Multistream, in-house custom terrain generation and rendering |
| **C++ code** | 380,000 lines |
| **Script code** | 50,000 lines |
| **Game objects** | ~500 individual objects |

Additional workflow detail from preserved Discord archive extracts: the team also used PS2 DualShock USB adapter workflows during PC-centric controller testing.

---

## What Went Right

### 1. Flexible Core Technologies

From the project's beginning, everything was designed to be as modular and flexible as possible:

> "As much information as possible was read in from externally editable files, and several custom editors for different areas of the game were written to allow designers and artists to alter everything from level layouts and unit statistics to graphical effects, without needing code changes."

**Architecture Principles:**
- Engine and game code carefully segregated
- Defined interfaces between modules enabled implementation changes without affecting other code
- Custom **C-style scripting language** allowed special events, objectives, and mission design without mission-specific code

**The Scrolling World Example:**

A level requiring players to chase a retreating enemy battleship seemed to need complex code to make the normally static world map scroll:

> "While the programming team was attempting to figure out how to achieve this, **the level designers implemented the mission without it by misusing some of the scripting functionality in a clever way**. This was an unexpected side effect of the system's flexibility."

**Benefits:**
- Reduced knock-on effects of changes and potential bugs
- Enabled rapid prototyping — test versions could be implemented quickly
- Many of BEA's features and effects resulted directly from this approach

> "It was only near the end of the project that we were forced to scale back on this flexible approach... Even then, however, the engine's modular construction frequently allowed faster special-case code to be substituted for the generic routines without actually altering the interfaces."

### 2. Constant Play-Testing and Feedback

Since all development was done on PC, everyone on the team could play the game at any time on their own machine:

> "This made a huge difference to the development process, as team members not directly involved with the programming and design could see their work in the game almost instantly — a model could be exported from 3DS Max straight into the format and location needed. The artist responsible could then run the game and see changes immediately."

**Sound Effect Workflow:**

Sound creation was handled out-of-house, but the system made collaboration seamless:

> "By providing the audio contractor with a copy of the PC-development build and our custom sound-effect editing and placement tool, the contractors could experiment with different effects within the game, and then send us a complete set of sounds and the effects file (which mapped game events to specific sound files, and allowed alteration of relative volume, pitch-shifting, and the like). We could then drop these files straight into the game with no need for format conversion, file renaming, or other such annoyances."

**Bug Catching:**

> "It was not uncommon during development for changes to artwork or scene units to break certain levels (buildings being placed close together and then intersecting each other when the model changed, for example). But with many pairs of eyes constantly inspecting the whole game, these mishaps were generally found — and fixed — quickly."

### 3. Planning Localization and Porting in Advance

Knowing the game would be translated into multiple languages and run on multiple platforms, they planned ahead:

**The Localization Tag System:**

> "We developed a text management system that split all the text out from the code and scripts and instead allowed individual strings to be referenced by a special tag. For example, `FRONTEND_NOMEMCARD` would translate to a string informing the user that there was no memory card inserted. These tags could also be used to reference the appropriate speech sample for a spoken version of the text, if it was available."

The system was later extended to allow **platform-specific variations** where naming conventions differed between consoles.

**Benefits:**
- Single file containing all game text for translation teams
- Easy re-integration of localized versions
- Later text changes could be separated for retranslation
- Simple text viewer for localization QA teams to verify incorporation

**Cross-Platform Code Structure:**

> "The majority of the engine was structured in such a way that platform-specific code was collected into small modules, which were then called upon by the higher-level platform-independent code. By keeping code separated out like this, we were able to remove the PC implementation of these modules and insert Xbox and Playstation 2 replacement code with relative ease."

> "Until we deliberately split the code bases for final tweaking and testing, **the game could be built on all three supported platforms from one set of project files**."

### 4. Ambitious Goals

The team considered outlandish ideas as potential challenges rather than dismissing them:

**Wild Ideas Discussed:**
- "The islands should have **dense forests** on them that the walkers and tanks can flatten paths through as they go"
- "You should be able to **land on large enemy craft and destroy them from the inside**"
- "If you blow up buildings, there should still be **rubble when you return to that island later**"

> "This mindset caused us more than a few headaches later in development when we realized just how complex and resource-hungry the game had gotten, but the dedication of everyone working on the game ensured we could include a huge number of these ideas that were not originally planned. **If we hadn't aimed so high and constantly attempted to achieve the impossible, the game would not have been as fun or technically impressive.**"

### 5. Open Atmosphere and Good Communication

> "The entire Lost Toys team worked well together on the BATTLE ENGINE AQUILA project, and a lot of potential problems were averted by having relevant people talk them over beforehand."

> "With the entire company based in one open-plan office, it's always possible to walk over and ask questions. This way we are able to pool expertise from everyone involved. It's often the case that even if someone isn't working directly on a given aspect of the project, that person has some relevant knowledge that can be helpful."

---

## What Went Wrong

### 1. Late Console Development

The vast majority of development was on PCs, and it was only about **nine months before gold** that they started working on real development systems:

> "Although the PC-centric development environment was a great help in some areas, it wasn't long before we realized that working like this for so long had caused some serious bloating of code and resource."

**The Scale of the Problem:**

> "It only took us a day in both cases to get the core game engine running on each machine, but there was clearly an awful lot of work left to do."

> "Fundamentally, the game was too resource-hungry for the machines it was to run on; in terms of memory, the PCs we were using for development had **four to 16 times as much RAM** as the consoles. In the early days of the porting process, **even small levels were regularly using more than 100MB of RAM and running at below 20 frames per second**."

**The PS2 Challenge:**

> "Right until the game went gold there was a constant battle to get everything to fit into memory, especially on the Playstation 2 where **we only had about 28MB of RAM** after the game executable had been loaded."

> "The Xbox port of the game had the advantage of being based on DirectX, and hence the majority of the code was shared with the PC version. **The Playstation 2 port, however, required an entire graphics and sound engine to be coded from scratch** — a mammoth task for our two Playstation 2 programmers, one of whom had never actually written any code for the machine before this project."

**The Vicious Circle:**

> "A vicious circle developed mid-project, where **features were being added to the project faster than they could be ported**, and we were still struggling daily to get the code optimized enough to stand any hope of reaching acceptable speeds (or even running at all on retail hardware). It was only in a final burst — after the Xbox version of the game was finished and in final testing — that functionality stopped being added to the engine and we were able to get the port running acceptably."

**Desperate Measures:**

> "For the project's last couple of months, most of the programming team was thinking about just two things: **how to make the game run fast enough and how to use sufficiently little memory** on the two platforms. We used every trick we could think of — **structures were ruthlessly compacted, data was decompressed on the fly or streamed off-disk as needed**, and on the Playstation 2 we were even forced to **store additional game data in the I/O processor's memory** and move it into main RAM when it was required."

### 2. Too Much Story, Too Little Script

> "The storyline for BATTLE ENGINE AQUILA went through many revisions before arriving at the version in the final game. Unfortunately, **constant editing removed many of the interesting twists**, and cutting down on the volume of cutscenes and dialogue (both to keep from overstretching our limited art resources and to avoid bogging the game with irrelevant story) **resulted in a faint shadow of what the final plot could have been**."

**Mission Structure Problems:**

> "In making a conscious effort to keep the missions and story tied together, we ended up in a position where **we were tied to creating certain missions in a certain order**, with little room for maneuver if we felt part of the design wasn't working."

> "While I think we overcame this quite well, **one of the main criticisms leveled at BATTLE ENGINE AQUILA is that the missions often have similar objectives with little variation in the settings** — a direct consequence of sticking to the structure of the original story line."

### 3. Poor Resource Management

The game's 40+ levels comprised a bewildering array of files and data:

> "This system provided us with a lot of flexibility, but it wasn't until close to the project's end that we realized that we'd inadvertently **created an unmanageable process for building final output**."

**The Build Nightmare:**

> "The process of getting a complete build of the game from raw data involved using **about five different tools on different sets of data**, some of which were only understood by one or two of the team members. There were quirks in many of the tools (such as the level editor saving files with no scripting information unless you had the right set of script files on your hard drive), and **we had virtually no version-control system** to ensure that the right files were being used."

> "Amazingly, **the final game data was a huge directory on the server, which got files dumped into it by all team members.**"

**The Resource File Creation Disaster:**

> "By far the worst part of this system, however, was the process of creating the final resource files. The PC version of the game ran in a special mode where it would load each level and then dump the contents of its own resource pools into a file, performing operations like compressing textures and precalculating shadow data as it did so."

> "Unfortunately, this process relied on an incredibly risky system of **saving objects to disk by writing the entire contents of a C++ class structure** and then manually fixing up pointers and other information when it was reloaded."

**The Rebuild Problem:**

> "Any change to one of the stored structures would **render all the existing resource files useless and necessitate a full rebuild of the data** — a process that could take several hours for a full level set. It was not uncommon for people to waste hours simply trying to update both their code and resource file sets to be compatible with each other, only to find that in the interim someone else had made another change, rendering the new sets of files useless."

### 4. Lack of Communication Between Art and Programming Teams

**The Preview Problem:**

> "The similarity between the Xbox and PC versions of the game meant that the screen previews the art team was seeing of their work were almost pixel-perfect representations of what the Xbox version would look like. Unfortunately, **this approach to the preview process tended to hide two very important potential problems: performance and the Playstation 2 version.**"

**No Technical Sign-Off:**

> "The artists rarely paid much attention to the frame rate, as the game's speed varied a great deal depending on the specification of the machine it was running on at the time. **With no sign-off process for the technical aspects of artwork**, it wasn't uncommon for models with ridiculous numbers of textures or polygons to get put into the game."

**The 5x Polygon Disaster:**

> "Problems would only show up when the levels were played on the target hardware, and by that stage it was often hard to tell exactly what was causing the problem. In one case we had an innocuous building mesh that had texture mapping that generated **approximately five times as many polygons** as the original model contained when converted for rendering."

**Vague Guidelines:**

> "This problem was exacerbated by the fact that **until relatively late in development, the programming team was not sure what the eventual limits on polygon counts and texture usage would be**, so artists were often given vague or contradictory advice on what to aim for."

**PS2 Visual Differences:**

> "The Playstation 2 version of the game suffered from these problems and more — many of the features supported by the Xbox and PC engines (such as **anisotropic texture filtering**) were not available, and others had to be turned down or dropped entirely for speed or memory reasons."

> "Until very close to the gold master date, many of the models in the Playstation 2 version of the game did not look right or caused immense performance issues, and it was not until we made a concerted effort to produce and work through a list of problems that we really managed to bring the problem under control. **Even then, we found ourselves making modifications to artwork to fix odd problems mere days before the final build was sent off.**"

### 5. Too Much Flexibility

The engine's flexibility became a serious liability during optimization:

**The Exception Problem:**

> "A lot of our attempts to optimize systems went along the lines of 'Well, this functionality is only ever used in this way, so let's just hard-code that instead.' **We'd generally find out at that point (or sometimes only after actually making the code change) that there was one place in the game where this rule didn't hold.** There would be one particle effect that used a certain awkward blend mode, or one type of unit that had a nonstandard friction setting."

**The Tree Disaster:**

Trees were originally added as standard "things," handled like units and troops — they could be shot at, knocked over, or block line-of-sight:

> "While the programming team was attempting to figure out how to achieve this, the level designers implemented the mission without it by misusing some of the scripting functionality in a clever way... Unfortunately, **we realized a few weeks later that some levels now had in excess of 6,000 individual trees on them (which accounted for nearly 2MB of RAM at one stage)**, and re-engineering the code to handle this efficiently without breaking the now-established behavior took a great deal of thought and effort."

---

## Ben Carter's Closing Thoughts

> "Developing BATTLE ENGINE AQUILA was a tough struggle at times, and there are many things we'd undoubtedly do differently if we had a chance to do it all again. Our experiences should allow us to avoid making the same mistakes again in the future, freeing us to discover a host of new ones. But game development wouldn't be the vibrant, ever-evolving field it is without fresh pitfalls to uncover at every turn."

> "At the time of writing, the game has not yet been unleashed on the public. We're all understandably nervous about how the title we have slaved over for the last two years will be received, but **I don't think there's anyone here at Lost Toys who isn't immensely proud of what we have created**."

> "We've managed to produce a finished product without compromising the original concept and gameplay that we first aimed for, and **the finished BATTLE ENGINE AQUILA is a remarkably accurate reflection of that original vision**. That, above commercial success or critical acclaim, is surely the greatest thing a developer can hope for."

---

## Port Timeline (Summary)

```
PC Development Build (Stuart's code)
         │
         ├──→ Xbox Port ──→ FINISHED FIRST (shared DirectX code)
         │         │
         │         └──→ PC Retail Port (by Lost Toys in-house, Oct 2003; Encore = publisher only)
         │                    │
         │                    └──→ Steam/GOG Release (Ziggurat, 2020)
         │                              │
         │                              └──→ PS4/PS5 Port (Ziggurat, May 2025)
         │
         └──→ PS2 Port ──→ FINISHED LAST (complete graphics/sound rewrite)
```

### The PC Retail Port (Lost Toys In-House)

**CORRECTED (Dec 2025):** Stuart confirmed on Discord that Encore Software was only the **publisher**. The actual port work was done in-house at Lost Toys:

> *"The PC version was done inhouse at LT though. When the original console versions were complete the team moved onto other work and LT got a person or persons to convert our already 'inhouse' development version into something releasable. I remember someone called Jan worked on this. He was sat next to me in the office and did ask me questions about the code. I believe previously he worked at mucky foot, which makes sense."* — Stuart Gillam (Dec 2025)

**Jan** (surname unknown) was the primary PC port developer. He previously worked at **Mucky Foot** (UK studio known for Startopia, Urban Chaos, Blade II). Jan changed the cheat codes from the original Lost Toys codes (B4K42, !EVAH!, 105770Y2) to new ones (MALLOY, TURKEY, Maladim, etc.).

Source retention note (from preserved Discord archive extracts): ex-team recollection indicates no one retained the full finished retail PC source tree, which aligns with the current partial-source preservation reality.

The PC version was a **minimal-effort console port**, not a native PC build:

| Issue | Details |
|-------|---------|
| **Base version** | Xbox (explains split-screen multiplayer) |
| **Graphics** | Console textures ported directly without enhancement |
| **Multiplayer** | Only split-screen 2-player (no online/LAN) |
| **Config file** | Main configuration file is **encrypted** |
| **Data encoding** | Retail `.bes` values are raw little-endian dwords; many only *look* “shift-16” in 4-byte-aligned hex dumps because CCareer bytes are copied at `file + 2` |
| **Cheat codes** | Changed from original Lost Toys codes by Jan |

**Why Stuart's code doesn't match the retail game:**
- Stuart's source is from the **internal PC build** (native int/float)
- Jan and the LT team ported the **console version** (likely Xbox) to PC
- The retail `.bes` on-disk layout differs (CCareer blob begins at `file + 2`), which made many values appear “shift-16” in naive hex dumps
- This explains many of the encoding/offset discrepancies documented in `reverse-engineering/`

**First Public RE Documentation**: This project represents the first public documentation of the .bes save file format. No prior hex editing or modding discussions exist online.

---

## Development Tools

- Written entirely in **C++** using **DirectX 8**
- Custom in-house scripting language built with **Lex and Yacc** for level designers
- The scripting files were accidentally left on the retail CD (but modifying them does nothing — they're compiled)
- The team essentially built a "very cut down version of Unity" as their engine

Stuart described it:
> "Basically what we had was a simpler cut down version of unity and c# scripts."

**What the scripting language handled** (from Stuart, May 2024):
- Play radio messages when certain events occurred
- Make game units move to waypoints
- Check when win conditions have been met
- Level designers could use it without knowing C++

---

## Development Anecdotes (from Stuart, June 2022)

Additional recollection from preserved Discord archive extracts: early mission framing as a broad "equal forces stalemate" was progressively steered toward bigger boss/set-piece escalation as development priorities shifted.

**The Scale Problem**: Early on, the team struggled to nail down scale.
> "Are the islands 1 mile in length, 10 miles or 100 meters, who knows?"

The player mech started similar in size to troops, but by mid-development "game object sizes rapidly got bigger and bigger and bigger."

**Building Destruction System**: Started as an experiment. Neil (artist) said "Hey Stu, I've made this building model that can break up." Stuart coded the system, they tested it:
> "Letting rip with the cannon into the building and watching the amazing sequence of the building blowing up in small bits and us saying 'wow that's cool!'"

So they kept it.

**Boss Panic**:
> "Having cold sweat pouring down my face just thinking how on earth we were going to make the in-house game engine cope with" the massive bosses.

The Fenrir especially caused headaches with collision:
> "So you didn't get stuck inside it and pop through the model."

**Sentinel Appreciation**:
> "The Sentinel on the last level was the coolest to look at. I was amazed by what the team had achieved with that."

---

## Glenn Corpes on Design Philosophy (July 2025)

*Glenn Corpes (Technical Director of Lost Toys for all four years) left this comment on a YouTube video about Battle Engine Aquila. It provides invaluable insight into the original design philosophy and creative intent.*

**Source**: [YouTube comment](https://www.youtube.com/watch?v=QdazoYwUj8E) by Glenn Corpes (G7ennx), pinned by @nihilisticnerd, approximately July 2025.

> "Hi, I worked on this game. I was Technical Director of Lost Toys for the four years it existed. I also coded aspects of the Graphics Engine. It's great to see your appreciation of the game. The main idea was that the game played like an RTS with two computer opponents but the player's perspective is first person controlling the strongest unit in the game. The default objective is simply to swing the battle in favour of the blue team. We spent most of development getting that working how we wanted before adding the more scripted goals and events along with the plot. The plot was basically written by Alex Trowers (the main game designer) and was supposed to just justify the gameplay. As we put the story together we were kind of trying to make it a sort of parody. We tried to base it on movies cliches were a reluctant hero is forced to save the day. Sadly it wasn't funny enough for anyone to realise. Maybe we should have taken this idea further or got an actual writer involved. This probably would have been a waste of time though because the cutscenes were produced to an insanely short deadline by a single animator in his first industry job. I'd have loved to have had the chance to have taken this further"

### Key Insights from Glenn's Comment

**Design Philosophy - "RTS with First-Person Perspective":**
- The game was designed as an RTS with two AI-controlled armies battling
- The player controls the "strongest unit in the game" from first-person perspective
- Default objective: swing the battle in favor of the blue (Forseti) team
- This explains why the game feels unique - it's genuinely a hybrid genre

**Development Approach:**
- Core battle mechanics were developed FIRST
- Scripted goals, events, and plot were added LATER
- This validates what the GDM post-mortem described about their "flexible core technologies" approach

**Story Intent - The Parody That Wasn't:**
- Alex Trowers wrote the plot specifically to "justify the gameplay"
- The team intended the story as a **parody of movie cliches**
- Based on the "reluctant hero forced to save the day" trope
- Glenn admits: "Sadly it wasn't funny enough for anyone to realise"
- They considered getting "an actual writer involved" but didn't

**Cutscene Production:**
- Produced on an "insanely short deadline"
- Made by "a single animator in his first industry job"
- Glenn wished they could have taken the story/cutscenes further

**Glenn's Role Clarified:**
- **Technical Director** for all four years of Lost Toys' existence
- Coded "aspects of the Graphics Engine"
- Previously documented as working on terrain, shadows, impostor system, and battle map
