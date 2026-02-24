# Frontend File Upload Configuration Guide

## Problem
Files are uploading but **orders are NOT being saved to the database**.

## Root Cause
The frontend is likely using one of these incorrectly:
1. ❌ Uploading without `client_id` in session metadata
2. ❌ Using `uploadFile()` without creating session first with `client_id`
3. ❌ Not enabling `auto_parse` parameter

## Solution: Two Upload Approaches

### ✅ Option 1: Simple One-Step Upload (RECOMMENDED)
**Best for:** File upload without session management  
**Endpoint:** `POST /api/uploads/po/upload`  
**Auto-saves to database:** YES ✅

```typescript
// Frontend: src/services/fileUploadService.ts

async uploadPO(file: File, clientId: number, projectId?: number): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);

  const params = new URLSearchParams({
    client_id: clientId.toString(),          // REQUIRED: 1=Bajaj, 2=Dava India
    auto_save: 'true',                       // REQUIRED: Save to DB
  });
  
  if (projectId) {
    params.append('project_id', projectId.toString());
  }

  const response = await fetch(`/api/uploads/po/upload?${params.toString()}`, {
    method: 'POST',
    body: formData,
  });

  const data = await response.json();
  
  // Response will include:
  // - client_po_id: Database ID of inserted PO (if parsing successful)
  // - po_details: Parsed PO data
  // - line_items: Line items from PO
  
  return data;
}
```

**Usage:**
```typescript
// In your component
const result = await uploadPO(file, 1, projectId); // 1 = Bajaj

if (result.status === 'SUCCESS') {
  console.log('PO saved to DB with ID:', result.client_po_id);
  
  // Now you can use this ID to:
  // - Get PO details: await getClientPO(result.client_po_id)
  // - Create billing: await createBillingPO(projectId, result.client_po_id)
  // - Add payments: await createPayment(result.client_po_id, amount)
}
```

---

### ✅ Option 2: Session-Based Upload (For Multiple Files)
**Best for:** Uploading multiple files in a session  
**Auto-saves to database:** YES ✅ (with fix)

```typescript
// Step 1: Create session WITH client_id
async createSession(clientId: number, projectId?: number): Promise<any> {
  const response = await fetch('/api/uploads/session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      metadata: {
        client_id: clientId,           // ⭐ CRITICAL: Include client_id
        project_id: projectId,
        upload_source: 'frontend'
      },
      ttl_hours: 24,
      client_id: clientId              // ⭐ Also pass as top-level param
    })
  });
  
  return response.json();
}

// Step 2: Upload file with auto_parse=true
async uploadFile(sessionId: string, file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('uploaded_by', 'frontend-user');
  formData.append('auto_parse', 'true');  // ⭐ CRITICAL: Enable auto-parse

  const response = await fetch(
    `/api/uploads/session/${sessionId}/files?auto_parse=true`,
    {
      method: 'POST',
      body: formData
    }
  );

  const data = await response.json();
  
  // Response will include:
  // - client_po_id: Database ID of inserted PO (if parsing successful)
  // - file_id: For reference
  
  return data;
}

// Step 3: Use the inserted PO
async handleMultipleFileUpload(files: File[], clientId: number, projectId: number) {
  // Create session once
  const session = await createSession(clientId, projectId);
  
  // Upload all files to same session
  for (const file of files) {
    const result = await uploadFile(session.session_id, file);
    
    if (result.client_po_id) {
      console.log(`✅ PO saved to DB: ${result.client_po_id}`);
      // Now use this ID for further operations
    }
  }
  
  // Clean up when done
  await deleteSession(session.session_id);
}
```

---

## Current Frontend Implementation Check

### Check Your fileUploadService.ts

**Look for these functions and verify they have the parameters:**

#### ❌ WRONG - Missing client_id
```typescript
async createSession(): Promise<any> {
  const response = await fetch('/api/uploads/session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      metadata: { project: "nexgen" },  // ❌ No client_id!
      ttl_hours: 24
    })
  });
  return response.json();
}
```

#### ✅ CORRECT - Includes client_id
```typescript
async createSession(clientId: number): Promise<any> {
  const response = await fetch('/api/uploads/session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      metadata: { client_id: clientId },  // ✅ Include client_id!
      ttl_hours: 24,
      client_id: clientId                 // ✅ Also here!
    })
  });
  return response.json();
}
```

#### ❌ WRONG - auto_parse not enabled
```typescript
async uploadFile(sessionId: string, file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  // ❌ Missing auto_parse parameter!
  
  const response = await fetch(
    `/api/uploads/session/${sessionId}/files`,  // ❌ No ?auto_parse=true
    { method: 'POST', body: formData }
  );
  return response.json();
}
```

#### ✅ CORRECT - auto_parse enabled
```typescript
async uploadFile(sessionId: string, file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('auto_parse', 'true');  // ✅ Enable auto-parse

  const response = await fetch(
    `/api/uploads/session/${sessionId}/files?auto_parse=true`,  // ✅ Parameter set
    { method: 'POST', body: formData }
  );
  return response.json();
}
```

---

## Quick Fix for Your Frontend

Add these to `src/services/fileUploadService.ts`:

### Fix 1: Update createSession to include client_id
```typescript
async createSession(clientId: number, projectId?: number): Promise<any> {
  const response = await fetch('/api/uploads/session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      metadata: {
        client_id: clientId,    // ← ADD THIS
        project_id: projectId
      },
      ttl_hours: 24,
      client_id: clientId       // ← ADD THIS
    })
  });
  return response.json();
}
```

### Fix 2: Update uploadFile to enable auto_parse
```typescript
async uploadFile(sessionId: string, file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('uploaded_by', 'frontend-user');
  formData.append('auto_parse', 'true');  // ← ADD THIS

  const response = await fetch(
    `/api/uploads/session/${sessionId}/files?auto_parse=true`,  // ← ADD ?auto_parse=true
    { method: 'POST', body: formData }
  );
  return response.json();
}
```

### Fix 3: Add simple uploadPO function
```typescript
async uploadPO(file: File, clientId: number, projectId?: number): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);

  let url = `/api/uploads/po/upload?client_id=${clientId}&auto_save=true`;
  if (projectId) {
    url += `&project_id=${projectId}`;
  }

  const response = await fetch(url, {
    method: 'POST',
    body: formData
  });
  return response.json();
}
```

---

## Use in Your Components

### Simple Upload (Recommended for most cases)
```typescript
// src/components/POUpload.tsx
import { uploadPO } from '@/services/fileUploadService';

function POUploadForm({ projectId }: { projectId: number }) {
  const handleUpload = async (file: File) => {
    try {
      const result = await uploadPO(file, 1, projectId);  // 1 = Bajaj client
      
      if (result.status === 'SUCCESS') {
        console.log('✅ PO saved to database!');
        console.log('PO ID:', result.client_po_id);
        console.log('PO Number:', result.po_details.po_number);
        console.log('Line Items:', result.line_items.length);
        
        // Now refresh your PO list or navigate to the PO
        // await refreshPOList();
      } else if (result.status === 'UPLOAD_SUCCESS_PARSE_FAILED') {
        console.log('⚠️ File uploaded but parsing failed');
      }
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  return (
    <input
      type="file"
      accept=".xlsx,.xls,.csv"
      onChange={(e) => e.target.files && handleUpload(e.target.files[0])}
    />
  );
}
```

### Session-Based Upload (For multiple files)
```typescript
// src/components/MultiFileUpload.tsx
import { createSession, uploadFile, deleteSession } from '@/services/fileUploadService';

function MultiFileUpload({ projectId }: { projectId: number }) {
  const handleBulkUpload = async (files: File[]) => {
    try {
      // Create session with client_id
      const session = await createSession(1, projectId);  // 1 = Bajaj
      console.log('Session created:', session.session_id);
      
      // Upload all files
      const poIds = [];
      for (const file of files) {
        const result = await uploadFile(session.session_id, file);
        
        if (result.client_po_id) {
          poIds.push(result.client_po_id);
          console.log(`✅ PO saved: ${result.client_po_id}`);
        }
      }
      
      // Clean up
      await deleteSession(session.session_id);
      
      console.log(`✅ Bulk upload complete. ${poIds.length} POs saved.`);
      // Refresh your PO list
      // await refreshPOList();
    } catch (error) {
      console.error('Bulk upload failed:', error);
    }
  };

  return (
    <div>
      <input
        type="file"
        multiple
        accept=".xlsx,.xls,.csv"
        onChange={(e) => e.target.files && handleBulkUpload(Array.from(e.target.files))}
      />
    </div>
  );
}
```

---

## Client ID Reference

When calling upload functions, use the correct client ID:

| Client | ID | Upload Type |
|--------|----|----|
| Bajaj | `1` | Bajaj PO (XLSX with specific columns) |
| Dava India | `2` | Proforma Invoice (XLSX/CSV) |

```typescript
// Example
await uploadPO(file, 1, projectId);     // Bajaj
await uploadPO(file, 2, projectId);     // Dava India
```

---

## Verification Checklist

- [ ] createSession includes `client_id` in metadata AND as top-level param
- [ ] uploadFile includes `auto_parse=true` query param
- [ ] uploadFile sends `auto_parse: 'true'` in formData
- [ ] Response is checked for `client_po_id` field
- [ ] Backend endpoint returns parsed data or error status
- [ ] Database query shows new `client_po` records after upload

---

## Testing

1. **Upload a test file:**
   ```typescript
   const result = await uploadPO(testFile, 1, 123);
   console.log(result);
   ```

2. **Check backend logs** for:
   - `✅ Successfully inserted PO into database with ID: XX`
   - Parse status messages

3. **Query database:**
   ```sql
   SELECT * FROM client_po ORDER BY created_at DESC LIMIT 5;
   ```

---

## Files to Update

**Location:** `src/services/fileUploadService.ts`

Changes needed:
1. ✅ createSession - add client_id
2. ✅ uploadFile - add auto_parse
3. ✅ uploadPO - add function if missing

---

## Summary

| Issue | Fix | Result |
|-------|-----|--------|
| Files upload but no POs in DB | Add `client_id` to session + `auto_parse=true` | POs auto-saved ✅ |
| Frontend doesn't know PO ID | Response includes `client_po_id` | Use ID for billing/payments |
| Parsing errors fail upload | Graceful degradation | Upload succeeds, note parse fail |

After making these changes, your file uploads **WILL** create orders in the database automatically.
