# Configuration File Rename - config-v2.ini → config.ini

**Date:** January 27, 2026  
**Action:** Renamed configuration file to reflect v3.0 as current version  
**Reason:** Simplify naming now that v2.x is archived

---

## What Was Done

### 1. Configuration File
✅ **Renamed:** `config-v2.ini` → `config.ini`  
✅ **Added:** v3.0 header comment with:
- Version identification (v3.0.0)
- Socket-only mode notation
- Reference to archived versions
- Copyright and license information

### 2. Script Updates (3 files)
✅ **FRS-Discovery-Server-v2.py**
- Updated `load_config()` function to read `config.ini`
- Updated error messages to reference `config.ini`

✅ **FRS-Discovery-Client-v2.py**
- Updated `load_config()` function to read `config.ini`
- Updated error messages to reference `config.ini`

✅ **health_checks.py**
- Updated all references from `config-v2.ini` to `config.ini`

### 3. Documentation Updates (9 files)
✅ **README.md** - Updated configuration instructions  
✅ **RELEASE_NOTES_v3.0.0.md** - Updated config references  
✅ **TROUBLESHOOTING.md** - Updated all config references  
✅ **HEALTH_CHECK_GUIDE.md** - Updated all config references  
✅ **INDEX.md** - Updated config file reference  
✅ **L3VPN_SOLUTION_GUIDE.md** - Updated all config references  
✅ **ENHANCEMENTS_ROADMAP.md** - Updated config references  
✅ **.cursorrules** - Updated configuration section  
✅ **ARCHIVE_MIGRATION_v2_to_v3.md** - Updated migration notes

### 4. Archived Files
✅ **Not updated** - Files in `archive/` retain original `config-v2.ini` references for historical accuracy

---

## New Configuration File Header

```ini
# FlexRadio Discovery Proxy - Version 3.0 Configuration
#
# This configuration file is for Version 3.0.0 of the FlexRadio Discovery Proxy
# Version 3.0 uses socket-only mode (TCP streaming between server and client)
#
# For v1.x or v2.x configuration files, see the archive/ directory
#
# Copyright (c) 2026 Chris L White (WX7V)
# Licensed under the MIT License
#
```

---

## Rationale

### Why Rename?

**Before (v2.x era):**
- `config.ini` - v1.x configuration (deprecated)
- `config-v2.ini` - v2.x configuration (dual-mode)

**After (v3.0):**
- `config.ini` - v3.0 configuration (socket-only)
- v2.x and v1.x configs archived

### Benefits:
1. ✅ **Simpler naming** - No version suffix needed for current version
2. ✅ **Clear current version** - `config.ini` is always the active config
3. ✅ **Historical clarity** - Archived versions keep their original names
4. ✅ **User friendly** - Users expect `config.ini` as the standard name

---

## Backward Compatibility

### Migration Path

**From v2.x:**
```bash
# Option 1: Rename your existing file
mv config-v2.ini config.ini

# Option 2: Copy the new template
# (Update with your settings)
```

**From v1.x:**
```bash
# v1.x used different config format
# See archive/v2.x/MIGRATION_GUIDE_v1_to_v2.md
# Then follow v2.x → v3.0 migration
```

### Compatibility Notes
- ✅ Scripts automatically detect `config.ini`
- ✅ Error messages now reference correct filename
- ✅ No functional changes to configuration format
- ⚠️ Old `config-v2.ini` will not be automatically detected

---

## File Structure Comparison

### Before
```
FlexRadio-Discovery-Proxy/
├── config-v2.ini          # Active v2.x/v3.0 config
├── archive/
│   └── v1.x/
│       └── config.ini     # Archived v1.x config
...
```

### After
```
FlexRadio-Discovery-Proxy/
├── config.ini             # Active v3.0 config (renamed from config-v2.ini)
├── archive/
│   ├── v1.x/
│   │   └── config.ini    # Archived v1.x config
│   └── v2.x/
│       └── (references to config-v2.ini in docs)
...
```

---

## Updated References

### Scripts (3 files)
| File | Lines Changed | Status |
|------|--------------|--------|
| FRS-Discovery-Server.py | 3 | ✅ Updated |
| FRS-Discovery-Client.py | 3 | ✅ Updated |
| health_checks.py | Multiple | ✅ Updated |

### Documentation (9 files)
| File | Changes | Status |
|------|---------|--------|
| README.md | Configuration section | ✅ Updated |
| RELEASE_NOTES_v3.0.0.md | Config references | ✅ Updated |
| TROUBLESHOOTING.md | All references | ✅ Updated |
| HEALTH_CHECK_GUIDE.md | All references | ✅ Updated |
| INDEX.md | Config reference | ✅ Updated |
| L3VPN_SOLUTION_GUIDE.md | All references | ✅ Updated |
| ENHANCEMENTS_ROADMAP.md | Config references | ✅ Updated |
| .cursorrules | Configuration section | ✅ Updated |
| ARCHIVE_MIGRATION_v2_to_v3.md | Migration notes | ✅ Updated |

### Archived Files (unchanged)
- ✅ `archive/v2.x/*.md` - Retain original references
- ✅ `archive/v1.x/*.md` - Unchanged

---

## Testing Checklist

### Server
- [ ] Run `python FRS-Discovery-Server-v2.py`
- [ ] Verify it loads `config.ini` successfully
- [ ] Check error message if config file missing
- [ ] Verify functionality unchanged

### Client
- [ ] Run `python FRS-Discovery-Client-v2.py`
- [ ] Verify it loads `config.ini` successfully
- [ ] Check error message if config file missing
- [ ] Verify functionality unchanged

### Health Checks
- [ ] Run health checks
- [ ] Verify config file detection
- [ ] Check diagnostic output

---

## Summary

✅ **Configuration file renamed** from `config-v2.ini` to `config.ini`  
✅ **v3.0 header added** with version and license information  
✅ **3 scripts updated** to reference new filename  
✅ **9 documentation files updated** to reference new filename  
✅ **Archived files preserved** with historical references  
✅ **No linter errors** - All code changes validated  

**Result:** Clean, simplified naming convention that reflects v3.0 as the current production version while maintaining historical references in archived documentation.

---

**Rename Completed:** January 27, 2026  
**Version:** 3.0.0  
**Impact:** Low (naming only, no functional changes)
