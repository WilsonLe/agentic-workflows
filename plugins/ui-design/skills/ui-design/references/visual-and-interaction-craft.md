# Visual and interaction craft

Use these checks proportionately. Preserve the project's design language; the goal is coherent hierarchy and useful interaction, not a mandatory aesthetic recipe.

## Hierarchy and layout

Begin with the content order and the action the user should notice. Use alignment, whitespace, type size/weight, and readable contrast to express that order. A heading, status, and action can often share an open layout without a card around each one. Group content when the boundary communicates a relationship or interaction.

For a new visual system, choose a compact token set and reuse it: a legible body style, a few purposeful heading/label styles, spacing steps, neutral surfaces, clear state colors, and restrained emphasis. Use brand accents where they support recognition or priority. No typeface, palette, component library, border radius, or dark/light theme is universally required.

Keep line lengths comfortable for reading. Use tabular numerals and stable alignment when numbers are compared. Provide enough separation for distinct actions without stretching connected content so far apart that its relationship disappears. Differentiate the primary action locally, and avoid styling every control as primary.

## Working interfaces

Use tables for repeated records with shared attributes. Put decision-relevant columns first, allow useful sorting/filtering, and keep row actions predictable. Column controls help when people need different views; hiding all useful columns by default does not. On small screens, choose essential columns, row detail, or a deliberate scroll region according to the comparison task.

Forms need visible labels, clear requirements, actionable errors, and a clear completion state. Place advanced options behind labeled disclosure only when their defaults are safe for the task. Separate exploration from commitment: viewing a candidate's detail should not select, enroll, invite, archive, or publish it.

## State and accessibility

- Make loading, empty, unavailable, error, and completed states distinguishable and truthful.
- Use semantic links for navigation and buttons for actions. Use native controls where practical.
- Preserve keyboard access and visible focus. Use text or accessible names for icon actions; color alone cannot carry meaning.
- Match the disclosure semantics: expanded state for collapsible sections, labeled dialogs with appropriate focus handling, and accessible selected states.
- Keep essential explanations available without hover, and provide touch-friendly controls.
- Check actual rendered contrast and responsive wrapping. A sparse layout does not excuse faint text or clipped content.
- Keep scroll and focus continuity when content opens or updates. Return focus sensibly on dismissal and announce important async outcomes when needed.

## Motion

Use motion to explain a state change, preserve spatial continuity, or acknowledge input. Favor short, interruptible transitions for frequently used controls. Avoid large repeated entrance animations and ornamental movement that competes with the task.

Use easing and duration consistent with the component's movement and the existing system. Support reduced motion with an equivalent understandable state change. Verify interrupted transitions and repeated activation; do not assume a smooth screenshot means a working interaction. Animation values are implementation choices to test, not fixed taste laws.

## Finishing pass

Inspect a real rendered viewport, then the important revealed states. Check hierarchy first, then spacing/alignment, typography, states, and interaction details. Remove redundant headings, repeated helper text, ornamental stats, and unnecessary wrappers. Keep explanatory content that prevents a likely mistake or makes the next action understandable. If the surface is deliberately expressive, assess whether the expression helps its purpose rather than automatically flattening it.
