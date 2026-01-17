# GUI Tab Modules

This directory contains modular tab classes for the LoreForge GUI application. Each tab manages a specific entity type with full CRUD operations.

## Available Tabs

### 📄 PagesTab (`pages_tab.py`)
Manages lore pages with rich content, template support, and hierarchical organization.

**Features:**
- Create/edit/delete pages
- Template selection for consistent formatting
- Parent-child page relationships
- Tag management for categorization
- Image attachments
- Rich text content editor

**Dependencies:**
- Requires `Page` entity from `src.domain.entities.page`
- Uses `PageName`, `Content` value objects
- Integrates with templates and tags

---

### 📐 TemplatesTab (`templates_tab.py`)
Manages page templates and reusable runes (sub-templates).

**Features:**
- Create page templates and runes
- Template hierarchy (parent templates)
- Rune composition (embed runes in templates)
- Template type selection (Page/Rune)
- Content structure editor
- Usage validation (prevents deletion if in use)

**Dependencies:**
- Requires `Template` entity from `src.domain.entities.template`
- Uses `TemplateName`, `Content`, `TemplateType` value objects

---

### 📖 StoriesTab (`stories_tab.py`)
Manages narrative stories with support for linear and non-linear storytelling.

**Features:**
- Linear, non-linear, and interactive story types
- Player choice management for branching narratives
- World element connections (characters, items, events)
- Active/inactive status toggle
- Rich story content editor
- Dynamic UI based on story type

**Dependencies:**
- Requires `Story` entity from `src.domain.entities.story`
- Uses `StoryName`, `Content`, `StoryType` value objects
- Integrates with choice entities (if available)

---

### 🏷️ TagsTab (`tags_tab.py`)
Manages visual tags for content organization and categorization.

**Features:**
- Create/edit/delete tags
- Tag type selection (Category, Theme, Status, Custom)
- Color picker with hex color support
- Visual color preview in table
- Usage statistics (shows where tags are used)
- Safe deletion (warns if tag is in use)

**Dependencies:**
- Requires `Tag` entity from `src.domain.entities.tag`
- Uses `TagName`, `TagType` value objects
- Color validation for hex format

---

### 🖼️ ImagesTab (`images_tab.py`)
Manages image media library with preview and usage tracking.

**Features:**
- Image file upload and management
- File browser for image selection
- Image preview with automatic scaling
- Supported formats: PNG, JPG, JPEG, GIF, SVG
- Usage statistics (shows which pages use images)
- Safe deletion (warns if image is in use)

**Dependencies:**
- Requires `Image` entity from `src.domain.entities.image`
- Uses `ImagePath`, `ImageType` value objects
- Uses PyQt6 QPixmap for image rendering

---

## Usage

### Importing Tabs

```python
from src.presentation.gui.tabs import (
    PagesTab,
    TemplatesTab,
    StoriesTab,
    TagsTab,
    ImagesTab
)
```

### Integrating with Main Window

```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lore_data = LoreData(tenant_id=TenantId(1))

        # Create tabs
        self.pages_tab = PagesTab(self.lore_data)
        self.templates_tab = TemplatesTab(self.lore_data)
        self.stories_tab = StoriesTab(self.lore_data)
        self.tags_tab = TagsTab(self.lore_data)
        self.images_tab = ImagesTab(self.lore_data)

        # Add to tab widget
        self.tabs.addTab(self.pages_tab, "📄 Pages")
        self.tabs.addTab(self.templates_tab, "📐 Templates")
        self.tabs.addTab(self.stories_tab, "📖 Stories")
        self.tabs.addTab(self.tags_tab, "🏷️ Tags")
        self.tabs.addTab(self.images_tab, "🖼️ Images")
```

### Refreshing Tabs

```python
def refresh_all_tabs(self):
    """Refresh all tabs after data changes."""
    self.pages_tab.refresh()
    self.templates_tab.refresh()
    self.stories_tab.refresh()
    self.tags_tab.refresh()
    self.images_tab.refresh()
```

---

## Common Patterns

All tabs follow consistent design patterns:

### 1. **Constructor Pattern**
```python
def __init__(self, lore_data):
    super().__init__()
    self.lore_data = lore_data
    self.selected_entity = None
    self._setup_ui()
```

### 2. **UI Setup**
- Title with icon and large font
- Splitter for table/form layout
- Table with sortable columns
- Form with input fields
- Action buttons (Add/Update/Delete/Clear)

### 3. **CRUD Operations**
- `_add_entity()` - Create new entity
- `_update_entity()` - Update selected entity
- `_delete_entity()` - Delete with confirmation
- `_clear_form()` - Reset form fields

### 4. **Event Handlers**
- `_on_selection_changed()` - Handle table selection
- `refresh()` - Reload data from lore_data
- Signal emission on selection

### 5. **Data Validation**
- Input validation before creation
- Usage checking before deletion
- User confirmation for destructive actions

---

## Signals

Each tab emits selection signals:

```python
# Connect to selection signals
pages_tab.page_selected.connect(self.on_page_selected)
templates_tab.template_selected.connect(self.on_template_selected)
stories_tab.story_selected.connect(self.on_story_selected)
tags_tab.tag_selected.connect(self.on_tag_selected)
images_tab.image_selected.connect(self.on_image_selected)
```

---

## LoreData Integration

All tabs expect a `LoreData` object with:

### Required Attributes
- `tenant_id: TenantId` - Tenant identifier
- `worlds: List[World]` - List of worlds (required for all tabs)

### Tab-Specific Attributes
- `pages: List[Page]` - For PagesTab
- `templates: List[Template]` - For TemplatesTab
- `stories: List[Story]` - For StoriesTab
- `tags: List[Tag]` - For TagsTab
- `images: List[Image]` - For ImagesTab

### Cross-Entity References
- Pages reference templates, tags, and images
- Stories reference choices and world elements
- Templates can reference parent templates and runes

---

## Error Handling

All tabs include comprehensive error handling:

1. **Input Validation**
   - Empty field checking
   - Value object validation
   - File existence validation (images)

2. **User Feedback**
   - Success messages after operations
   - Error messages with details
   - Confirmation dialogs for destructive actions

3. **Safe Deletion**
   - Usage checking before deletion
   - Cascade warnings for related entities
   - Option to abort deletion

---

## Future Enhancements

Potential improvements for all tabs:

1. **Search and Filtering**
   - Global search across all entities
   - Filter by world, tags, type
   - Advanced query builder

2. **Bulk Operations**
   - Multi-select for batch operations
   - Bulk tag assignment
   - Bulk deletion with confirmation

3. **Import/Export**
   - Import from various formats
   - Export to PDF, Markdown, HTML
   - Backup and restore

4. **Version Control**
   - Entity version history
   - Diff viewing
   - Rollback capability

5. **Collaboration**
   - Real-time updates
   - Conflict resolution
   - User permissions

---

## Testing

To test the tabs:

```python
# Create test data
lore_data = LoreData(tenant_id=TenantId(1))
lore_data.worlds.append(World.create(...))

# Create and show tab
tab = PagesTab(lore_data)
tab.refresh()
tab.show()
```

---

## Architecture

```
tabs/
├── __init__.py          # Module exports
├── README.md            # This file
├── pages_tab.py         # Pages management
├── templates_tab.py     # Templates management
├── stories_tab.py       # Stories management
├── tags_tab.py          # Tags management
└── images_tab.py        # Images management
```

Each tab is self-contained and can be developed/tested independently.
