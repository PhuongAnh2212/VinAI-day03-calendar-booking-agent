# Calendar Invitation Bot Frontend

A beautiful, whimsical chatbot interface for sending calendar invitations. Built with Vite + React with a playful, colorful design inspired by modern UI aesthetics.

## Features

✨ **Beautiful UI Design**
- Whimsical blob shapes and gradients
- Smooth animations and transitions
- Responsive design for mobile and desktop
- Custom typography with Fredoka and Poppins fonts

🤖 **Chatbot Interface**
- Real-time message display
- User and bot message differentiation
- Typing indicators and loading states
- Natural conversation flow

📅 **Invitation Flow**
- Mock invitation system with realistic data
- User acceptance/rejection flow
- Processing animations
- Success/failure states

🔐 **Privacy-First**
- No calendar exposure
- Masked user identifiers (e.g., 0xaAFX...Tw1n)
- Safe invitation hashing

## Setup

### Prerequisites
- Node.js 16+ installed

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The app will be available at `http://localhost:5173`

## Project Structure

```
.
├── index.html                 # HTML entry point
├── package.json              # Dependencies
├── vite.config.js            # Vite configuration
├── src/
│   ├── main.jsx             # React entry point
│   ├── App.jsx              # Main app component
│   ├── App.css              # App styling
│   ├── index.css            # Global styles
│   └── components/
│       ├── ChatbotInterface.jsx      # Chat interface component
│       ├── ChatbotInterface.css      # Chat styling
│       ├── InvitationFlow.jsx        # Invitation card component
│       └── InvitationFlow.css        # Invitation styling
```

## How to Use

1. **Send a Message**: Type a message like "Invite Sarah to a 2pm meeting tomorrow" in the chat input
2. **Bot Processes**: The bot will detect the invitation intent and create a mock invitation
3. **Review Invitation**: The invitation card appears on the right showing:
   - Recipient details
   - Event title and time
   - Duration and invitation hash
4. **Respond**: Click Accept or Reject
5. **See Result**: The bot responds with the outcome

## Mock Data

The app uses completely mock data:
- **Recipients**: Sarah Chen, John Developer, Alex Morgan
- **Meeting Types**: Team Sync, Project Review, One-on-One, 1:1 Check-in, Strategy Meeting
- **Timing**: Randomized future dates and times

No actual calendar API is called.

## Design System

### Colors
- Primary Blue: `#4DD0E1`
- Primary Pink: `#FF4081`
- Primary Green: `#26C281`
- Accent Yellow: `#FFD54F`
- Accent Light Pink: `#F8BBD0`

### Typography
- Display: Fredoka (700 weight for headers)
- Body: Poppins (400-600 weights)

### Spacing & Radius
- Border Radius: 12px (sm), 20px (md), 32px (lg)
- Gap/Spacing: 0.5rem, 0.75rem, 1rem, 1.5rem, 2rem

### Animations
- Message appearance: 0.4s ease-out
- Button hover: transform + shadow
- Loading: Pulsing dots
- State transitions: Smooth scale and fade

## Future Integration

When you have an actual agent, you can:

1. Replace the mock data generation in `handleSendMessage()` 
2. Call your agent API with the user's message
3. Parse the agent response to extract:
   - Recipient information
   - Meeting details
   - Acceptance/rejection response

The component structure is designed to easily swap out the mock logic for real API calls.

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Vite provides instant Hot Module Replacement (HMR)
- CSS animations use GPU acceleration
- Optimized bundle size with tree-shaking
- Responsive images and lazy loading ready

## Customization

Edit CSS variables in `src/App.css` `:root` section to change:
- Colors
- Font families
- Border radius values
- Animation timings

Example:
```css
:root {
  --color-primary-blue: #4DD0E1;
  --color-primary-pink: #FF4081;
  /* ... more variables */
}
```

## License

MIT
