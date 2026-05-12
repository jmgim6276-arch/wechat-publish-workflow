# Draft Operations

This file covers how to create new drafts, update existing drafts, and preserve `media_id`.

## Create vs Update

### Create a new draft when

- trying a new cover direction
- trying a new正文 style direction
- keeping the old working version intact
- showing the user multiple options in parallel

### Update an existing draft when

- the user chose a working direction
- only refinements are needed
- the draft already has a stable `media_id`

## Always Record These

For every active draft, preserve:

1. markdown source path
2. cover image path
3. `thumb_media_id`
4. `media_id`

## Current Manifest Path

`/Users/tang/Library/Mobile Documents/iCloud~md~obsidian/Documents/Workshop/💼 工作时-工作台/零碳能源知识库/戴总的创业初心/公众号草稿/media_ids.json`

When a new draft is created successfully, update the manifest immediately.

## Practical Workflow

### New draft workflow

1. generate cover asset
2. convert markdown to the intended HTML style
3. upload cover
4. call `draft/add`
5. save returned `media_id`
6. write it into the manifest

### Update workflow

1. preserve current `media_id`
2. preserve or replace `thumb_media_id`
3. regenerate HTML after content or style changes
4. call `draft/update`
5. keep the same manifest entry

## Why This Matters

If you do not record `media_id`, the next revision usually becomes a new duplicate draft instead of a true update.

That breaks the iteration loop.

## Strong Recommendation

When exploring visual design:

- create a parallel draft first
- only overwrite the chosen draft after the user confirms the direction

This avoids destroying the last good version.
