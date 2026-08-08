# Product Guide — NovaTrack

NovaTrack is an online project management tool designed for small teams (2 to 20 people). It combines a Kanban board, time tracking, and automatic progress reports.

## Core features

**Kanban boards.** Each project has a customizable board with free-form columns (by default: To Do, In Progress, In Review, Done). Cards can hold subtasks, attachments (up to 25 MB per file), and comments.

**Time tracking.** A built-in timer tracks time spent on each task. Data can be exported as CSV or synced directly with compatible billing tools (see the Integrations section).

**Automatic reports.** Every Monday morning, NovaTrack emails a summary of the previous week: completed tasks, delays, and workload per team member. This report is enabled by default but can be turned off in notification settings.

**Automations.** You can create simple rules such as "when a card moves to the Done column, notify the project lead" or "when a card sits without activity for more than 5 days, tag it as Overdue."

## Available integrations

NovaTrack connects with Slack, Google Calendar, GitHub, and Stripe (for billing). The GitHub integration automatically links a card to a pull request: the card moves to In Review as soon as the PR opens, and to Done as soon as it merges.

## Technical limits

- Number of projects per workspace: unlimited on the Team and Enterprise plans, 3 maximum on the Solo plan.
- Maximum attachment size: 25 MB.
- Activity history kept for a rolling 12 months, except on the Enterprise plan where it's unlimited.
- The mobile app (iOS and Android) supports viewing and updating tasks, but not creating new boards.
