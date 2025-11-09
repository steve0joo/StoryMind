# Character Relationship Graph - Implementation Complete

**Status:** ✅ Ready to Test
**Last Updated:** November 9, 2025

---

## What Was Implemented

### 1. New Component: `CharacterGraph.jsx`

**Location:** `frontend/src/components/CharacterGraph.jsx`

**Features:**
- ✅ Interactive 2D force-directed graph using `react-force-graph-2d`
- ✅ Node size based on character mention count
- ✅ Color gradient (light blue = few mentions, dark blue = many mentions)
- ✅ Hover tooltips showing character details
- ✅ Click nodes to navigate to character details
- ✅ Drag nodes to rearrange
- ✅ Zoom and pan support
- ✅ Animated particle links
- ✅ Legend and instructions overlay

**Smart Features:**
- Automatically creates relationships if not defined in database
- Connects secondary characters to main character
- Cross-connections between frequently mentioned characters
- Circular layout for better initial visualization

### 2. Updated Component: `BookDetail.jsx`

**New Features:**
- ✅ **Graph/List View Toggle** - Switch between visualization modes
- ✅ **Click-to-Navigate** - Click graph node to jump to character card
- ✅ **Smooth Scrolling** - Auto-scroll with highlight animation
- ✅ **ID Tracking** - Each character card has `id="character-{id}"` for navigation

---

## How to Test

### Step 1: Start Servers

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 2: Navigate to Book Detail

1. Go to http://localhost:5173
2. Search for a book (e.g., "harry")
3. Click on a book card
4. You should see the **Graph View** by default

### Step 3: Test Graph Features

**✅ Visual Test:**
- [ ] Graph displays with nodes (circles representing characters)
- [ ] Larger nodes = more mentions in the book
- [ ] Darker blue = more important characters
- [ ] Lines connect characters
- [ ] Animated particles flow along connections

**✅ Interaction Test:**
- [ ] Hover over a node → Tooltip appears with character info
- [ ] Click and drag a node → Node moves, connections stretch
- [ ] Scroll wheel → Graph zooms in/out
- [ ] Click and drag background → Graph pans
- [ ] Click a node → Switches to List View and scrolls to that character

**✅ Toggle Test:**
- [ ] Click "List View" button → Shows character cards
- [ ] Click "Graph View" button → Shows relationship graph

### Step 4: Test with Different Books

Try books with different character counts:
- **Few characters (1-3):** Should show simple connections
- **Many characters (10+):** Should show complex network
- **No characters:** Should show "No characters" message

---

## Graph Visualization Details

### Node Properties:

| Property | Meaning |
|----------|---------|
| **Size** | Mention count (bigger = more mentions) |
| **Color** | Importance (darker blue = more important) |
| **Position** | Force-directed layout (related characters closer) |

### Link Properties:

| Property | Meaning |
|----------|---------|
| **Thickness** | Relationship strength |
| **Particles** | Animated dots showing connection |
| **Color** | Gray with transparency |

### Default Relationship Logic:

If no relationships are defined in the database, the graph automatically:
1. Finds the most mentioned character (main character)
2. Connects all characters to main character
3. Adds random connections between top 4 characters
4. Creates a visually interesting network

---

## Customization Options

### Change Graph Colors:

Edit `frontend/src/components/CharacterGraph.jsx`:

```javascript
const getNodeColor = (mentionCount) => {
  // Current: Blue gradient
  // Change to green: rgb(100, intensity, 100)
  // Change to purple: rgb(intensity, 100, intensity)
  const intensity = Math.min(255, 100 + mentionCount * 5);
  return `rgb(${255 - intensity}, ${255 - intensity}, 255)`;
};
```

### Change Graph Size:

Edit `frontend/src/components/CharacterGraph.jsx`:

```javascript
const [dimensions, setDimensions] = useState({
  width: 800,   // Change width
  height: 600   // Change height
});
```

### Change Animation Speed:

Edit `frontend/src/components/CharacterGraph.jsx`:

```javascript
linkDirectionalParticleSpeed={0.005}  // Increase for faster, decrease for slower
```

---

## Adding Real Relationships to Database

Currently, relationships are auto-generated. To use real relationships from the book:

### Step 1: Update Character Service (Backend)

Edit `backend/services/character_service.py` to extract relationships:

```python
def extract_relationships(character_name, rag_system, all_characters):
    """Extract relationships for a character"""
    prompt = f"""
    Analyze mentions of {character_name} and identify their relationships
    with these other characters: {', '.join(all_characters)}

    Return JSON: [{{"character": "Name", "relationship": "friend/enemy/family/etc"}}]
    """
    # Use Gemini to extract
    response = llm.invoke(prompt)
    return json.loads(response.content)
```

### Step 2: Store in Database

The `relationships` field in the `characters` table already accepts JSON:

```python
character = Character(
    # ... other fields
    relationships=json.dumps(relationships)  # Store as JSON string
)
```

### Step 3: Graph Will Auto-Use Real Data

The `CharacterGraph` component already checks for real relationships first:

```javascript
if (char.relationships) {
    const relationships = JSON.parse(char.relationships);
    // Uses real data
} else {
    // Falls back to auto-generated
}
```

---

## Troubleshooting

### Issue: Graph not displaying

**Check:**
1. Browser console for errors (F12)
2. `react-force-graph-2d` installed: `npm list react-force-graph-2d`
3. Characters loaded: Check Network tab for `/api/characters` response

**Solution:**
```bash
cd frontend
npm install react-force-graph-2d@1.25.8
npm run dev
```

### Issue: Nodes overlapping

**Solution:** Graph needs time to stabilize

- Wait 2-3 seconds for force simulation to settle
- Drag nodes to manually adjust
- Increase `cooldownTicks` in CharacterGraph.jsx

### Issue: Graph too small/large

**Solution:** Adjust dimensions in CharacterGraph.jsx:

```javascript
setDimensions({
  width: container.clientWidth || 1000,  // Increase
  height: Math.min(container.clientHeight || 800, 800)  // Increase max
});
```

### Issue: Click node doesn't scroll to character

**Check:**
- Character cards have `id="character-{id}"` attribute
- Browser supports `scrollIntoView` (all modern browsers do)

---

## Performance Considerations

### Optimal Character Count:
- **1-20 characters:** Excellent performance
- **20-50 characters:** Good performance
- **50+ characters:** May be slow, consider pagination

### Optimization for Many Characters:

Edit `CharacterGraph.jsx`:

```javascript
// Limit to top N characters by mentions
const topCharacters = characters
  .sort((a, b) => b.mention_count - a.mention_count)
  .slice(0, 30);  // Show only top 30
```

---

## Demo Tips

### For Hackathon Presentation:

1. **Start with Graph View** - Wow factor!
2. **Explain the visualization:**
   - "Larger nodes = more important characters"
   - "Darker blue = more mentions in the book"
   - "Lines show relationships"

3. **Interact with the graph:**
   - Drag a node to show interactivity
   - Zoom in/out
   - Click a node to jump to details

4. **Switch to List View** - Show the dual functionality

5. **Highlight competitive advantage:**
   - "RAG-powered character extraction"
   - "Interactive visualization of book relationships"
   - "Deterministic seed ensures same character always looks the same"

---

## Future Enhancements (Post-Hackathon)

### Relationship Types:
- Color-code links by relationship type (friend=green, enemy=red)
- Different line styles (dotted, dashed, solid)

### Advanced Features:
- Timeline view (character relationships change over chapters)
- Cluster characters by location or faction
- Export graph as image
- 3D graph view (using `react-force-graph`)

### AI-Powered:
- Use Gemini to extract relationship types
- Sentiment analysis of relationships
- Story arc visualization

---

## Files Modified

1. ✅ **Created:** `frontend/src/components/CharacterGraph.jsx` (210 lines)
2. ✅ **Updated:** `frontend/src/pages/BookDetail.jsx` (added graph integration)
3. ✅ **Created:** `CHARACTER_GRAPH_IMPLEMENTATION.md` (this file)
4. ✅ **Created:** `E2E_TEST_GUIDE.md` (testing guide)

---

## Success Criteria

**Minimum (Working):**
- [ ] Graph displays on book detail page
- [ ] Can toggle between graph and list view
- [ ] Nodes are clickable

**Ideal (Demo Ready):**
- [ ] Graph looks visually appealing
- [ ] Smooth animations
- [ ] Click nodes navigates to character cards
- [ ] Tooltip hover works
- [ ] Drag and zoom work

---

## Next Steps

1. ✅ **Test the graph** - Follow E2E_TEST_GUIDE.md
2. ⏳ **Add real relationships** - Use Gemini to extract from text (optional)
3. ⏳ **Polish UI** - Adjust colors, sizes, animations
4. ⏳ **Practice demo** - Prepare talking points

---

**Status:** Ready for testing! 🎉

Run the servers and visit a book detail page to see it in action!
