# The Campaign

- **Status:** live preservation record — the structure and framing are written
  from the game and from this project's measurements. **The mission list below is
  not shipped with this app.** It is read out of your own installed copy each
  time you open this page, so what you see is your game's text rather than
  someone's transcription of it.
- **Last updated:** 2026-08-02
- **Summary:** how the campaign is shaped, what the mission numbering means, and
  the mission list read live from your install.

## What you are playing

You are Hawk Winter, and for most of the campaign you are the only Battle Engine
the Forseti have. That is the premise the missions are built around: you arrive
where the line is failing, and the line is failing in more than one place at
once. The game is unusually willing to let you lose ground somewhere else while
you are busy — the artillery you did not silence keeps firing, the landing craft
you did not intercept keeps unloading.

It is a first-person war game that happens to be piloted from inside a mech,
rather than a mech game. The briefings talk about beachheads and supply, not
loadouts.

## How the missions are numbered

The game numbers levels `N.NN` — a chapter, then a mission inside it. The number
is not decoration: it is the level's real identity everywhere in the game's own
files, in the save format, and in this app. `1.00` is the training level.

Some numbers appear twice. Where the campaign returns to a map later in the war,
the game keeps the same code and gives it a different title — the same ground,
after things have gone worse. Those are marked in the list below.

Mission numbers are what the app uses when it talks to the game, which is why
Save Lab and the Media page show them beside the names.

## The missions

<!-- LIVE:CAMPAIGN-MISSIONS -->

## Why the list is read from your game rather than printed here

The names are the game's own text. They live in
`data/language/<language>.dat` in your installation, alongside about two and a
half thousand other strings — every line of dialogue, every menu label, every
briefing. This app can read that file, and does, so that the names you see are
the ones your copy actually uses.

What it does not do is copy them into itself. Shipping the game's text inside a
freely downloadable package is redistributing the game's content, which is not
this project's to redistribute — and it would also be worse: it would pin one
language's names into an app that can simply ask your copy which language it is.

The same decoding drives the real mission names on the Media page and the
transcripts on its voice lines. It is the same file, read the same way, every
time from your disk.
