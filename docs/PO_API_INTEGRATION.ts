/**
 * =====================================================
 * COMPREHENSIVE PO OPERATIONS INTEGRATION FILE
 * =====================================================
 * 
 * This file contains all request/response models and API endpoints
 * for Purchase Order (PO) operations across the system.
 * 
 * Categories:
 * 1. Client PO Operations
 * 2. Bajaj PO Upload & Parsing
 * 3. PO Management (Line Items, Multiple POs, Verbal Agreements)
 * 4. Billing PO Operations
 * 5. Vendor Orders
 * 
 * Usage: Import these types in your frontend and use them for API calls.
 * =====================================================
 */

// =====================================================
// BASE RESPONSE TYPES
// =====================================================

export interface ApiResponse<T> {
  status: "SUCCESS" | "FAILED" | "ERROR";
  message?: string;
  data?: T;
  error?: string;
  [key: string]: any;
}

export interface ErrorResponse {
  status: "FAILED" | "ERROR";
  detail: string;
}

// =====================================================
// 1. CLIENT PO MODELS & ENDPOINTS
// =====================================================

export namespace ClientPO {
  // Request Models
  export interface CreateClientPORequest {
    po_number: string;
    po_date: string; // ISO date format: YYYY-MM-DD
    po_value?: number;
    po_type?: string;
    parent_po_id?: number;
    notes?: string;
  }

  // Response Models
  export interface ClientPOItem {
    id?: number;
    client_po_id?: number;
    item_name: string;
    quantity: number;
    rate: number;
    total?: number;
  }

  export interface ClientPOData {
    status: "SUCCESS";
    po?: {
      po_id: number;
      po_number: string;
      po_date: string;
      po_value: number;
      po_type: string;
      notes?: string;
      status?: string;
      store_id?: string;
      location?: string;
    };
    line_items?: ClientPOItem[];
    client_po_id?: number;
    client_name?: string;
    vendor_name?: string;
    location?: string;
    [key: string]: any;
  }

  export interface GetClientPOResponse {
    status: "SUCCESS";
    po: {
      po_id: number;
      po_number: string;
      po_date: string;
      po_value: number;
      po_type?: string;
      notes?: string;
      location?: string;
      store_id?: string;
    };
    line_items?: ClientPOItem[];
    client_po_id?: number;
    location?: string;
    [key: string]: any;
  }

  // API Endpoint: GET /api/client-po/{client_po_id}
  export async function getClientPO(clientPoId: number): Promise<GetClientPOResponse> {
    const response = await fetch(`/api/client-po/${clientPoId}`);
    return response.json();
  }
}

// =====================================================
// 2. BAJAJ PO UPLOAD & PARSING
// =====================================================

export namespace BajajPO {
  // Request Models (multipart form)
  export interface BajajPOUploadRequest {
    file: File; // Excel file (.xlsx or .xls)
    client_id: number;
    project_id?: number;
  }

  export interface BajajPOBulkUploadRequest {
    files: File[]; // Multiple Excel files
    client_id: number;
    project_id?: number;
  }

  // Response Models
  export interface PODetails {
    po_number: string;
    po_date: string;
    po_value: number;
    store_id?: string;
    location?: string;
    quantity?: number;
    rate?: number;
    [key: string]: any;
  }

  export interface Summary {
    total_items?: number;
    total_quantity?: number;
    total_value?: number;
    [key: string]: any;
  }

  export interface LineItem {
    item_name: string;
    quantity: number;
    rate: number;
    total: number;
    [key: string]: any;
  }

  export interface BajajPOParseResponse {
    status: "SUCCESS";
    client_po_id: number;
    po: PODetails;
    summary: Summary;
    line_items: LineItem[];
    line_item_count: number;
  }

  export interface UploadedPO {
    client_po_id: number;
    filename: string;
    po_number: string;
    po_value: number;
    store_id?: string;
    line_item_count: number;
  }

  export interface BajajPOBulkUploadResponse {
    status: "SUCCESS";
    total_files: number;
    successful: number;
    failed: number;
    uploaded_pos: UploadedPO[];
    errors: Array<{
      filename: string;
      error: string;
    }>;
  }

  // API Endpoints
  // POST /api/bajaj-po - Single file upload
  export async function uploadBajajPO(
    file: File,
    clientId: number,
    projectId?: number
  ): Promise<BajajPOParseResponse> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("client_id", clientId.toString());
    if (projectId) formData.append("project_id", projectId.toString());

    const response = await fetch("/api/bajaj-po", {
      method: "POST",
      body: formData,
    });
    return response.json();
  }

  // POST /api/bajaj-po/bulk - Multiple file upload
  export async function bulkUploadBajajPO(
    files: File[],
    clientId: number,
    projectId?: number
  ): Promise<BajajPOBulkUploadResponse> {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    formData.append("client_id", clientId.toString());
    if (projectId) formData.append("project_id", projectId.toString());

    const response = await fetch("/api/bajaj-po/bulk", {
      method: "POST",
      body: formData,
    });
    return response.json();
  }
}

// =====================================================
// 2B. DAVA INDIA PO UPLOAD & PARSING
// =====================================================

export namespace DavaIndiaPO {
  // Request Models (multipart form)
  export interface DavaIndiaPOUploadRequest {
    file: File; // Excel file (.xlsx or .xls)
    client_id: number;
    project_id?: number;
  }

  export interface DavaIndiaPOBulkUploadRequest {
    files: File[]; // Multiple Excel files
    client_id: number;
    project_id?: number;
  }

  // Response Models
  export interface PODetails {
    po_number: string;
    po_date: string;
    po_value: number;
    location?: string;
    warehouse?: string;
    reference_no?: string;
    [key: string]: any;
  }

  export interface Summary {
    total_items?: number;
    total_quantity?: number;
    total_value?: number;
    [key: string]: any;
  }

  export interface LineItem {
    item_name: string;
    quantity: number;
    rate: number;
    total: number;
    [key: string]: any;
  }

  export interface DavaIndiaPOParseResponse {
    status: "SUCCESS";
    client_po_id: number;
    po: PODetails;
    summary: Summary;
    line_items: LineItem[];
    line_item_count: number;
  }

  export interface UploadedPO {
    client_po_id: number;
    filename: string;
    po_number: string;
    po_value: number;
    location?: string;
    line_item_count: number;
  }

  export interface DavaIndiaPOBulkUploadResponse {
    status: "SUCCESS";
    total_files: number;
    successful: number;
    failed: number;
    uploaded_pos: UploadedPO[];
    errors: Array<{
      filename: string;
      error: string;
    }>;
  }

  // API Endpoints
  // POST /api/dava-india-po - Single file upload
  export async function uploadDavaIndiaPO(
    file: File,
    clientId: number,
    projectId?: number
  ): Promise<DavaIndiaPOParseResponse> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("client_id", clientId.toString());
    if (projectId) formData.append("project_id", projectId.toString());

    const response = await fetch("/api/dava-india-po", {
      method: "POST",
      body: formData,
    });
    return response.json();
  }

  // POST /api/dava-india-po/bulk - Multiple file upload
  export async function bulkUploadDavaIndiaPO(
    files: File[],
    clientId: number,
    projectId?: number
  ): Promise<DavaIndiaPOBulkUploadResponse> {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    formData.append("client_id", clientId.toString());
    if (projectId) formData.append("project_id", projectId.toString());

    const response = await fetch("/api/dava-india-po/bulk", {
      method: "POST",
      body: formData,
    });
    return response.json();
  }
}

// =====================================================
// 3. PO MANAGEMENT - LINE ITEMS
// =====================================================

export namespace POManagement {
  namespace LineItems {
    // Request Models
    export interface LineItemRequest {
      item_name: string;
      quantity: number;
      unit_price: number;
    }

    export interface LineItemUpdateRequest {
      item_name?: string;
      quantity?: number;
      unit_price?: number;
    }

    // Response Models
    export interface LineItem {
      id?: number;
      line_item_id?: number;
      item_name: string;
      quantity: number;
      unit_price: number;
      total_price?: number;
    }

    export interface AddLineItemResponse {
      status: "SUCCESS";
      message: string;
      line_item: LineItem;
    }

    export interface GetLineItemsResponse {
      status: "SUCCESS";
      client_po_id: number;
      line_items: LineItem[];
      line_item_count: number;
      total_value: number;
    }

    export interface UpdateLineItemResponse {
      status: "SUCCESS";
      message: string;
      line_item: LineItem;
    }

    export interface DeleteLineItemResponse {
      status: "SUCCESS";
      message: string;
    }

    // API Endpoints
    // POST /api/po/{client_po_id}/line-items
    export async function addLineItem(
      clientPoId: number,
      item: LineItemRequest
    ): Promise<AddLineItemResponse> {
      const response = await fetch(`/api/po/${clientPoId}/line-items`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(item),
      });
      return response.json();
    }

    // GET /api/po/{client_po_id}/line-items
    export async function getLineItems(clientPoId: number): Promise<GetLineItemsResponse> {
      const response = await fetch(`/api/po/${clientPoId}/line-items`);
      return response.json();
    }

    // PUT /api/line-items/{line_item_id}
    export async function updateLineItem(
      lineItemId: number,
      item: LineItemUpdateRequest
    ): Promise<UpdateLineItemResponse> {
      const response = await fetch(`/api/line-items/${lineItemId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(item),
      });
      return response.json();
    }

    // DELETE /api/line-items/{line_item_id}
    export async function deleteLineItem(lineItemId: number): Promise<DeleteLineItemResponse> {
      const response = await fetch(`/api/line-items/${lineItemId}`, {
        method: "DELETE",
      });
      return response.json();
    }
  }

  // =====================================================
  // PO MANAGEMENT - GET ALL POs
  // =====================================================

  namespace AllPOs {
    export interface GetAllPOsResponse {
      status: "SUCCESS";
      pos: PODetails[];
      total_count: number;
      total_value: number;
    }

    export interface PODetails {
      po_id?: number;
      client_po_id: number;
      po_number: string;
      po_date: string;
      po_value: number;
      po_type?: string;
      status?: string;
      notes?: string;
      client_name?: string;
      vendor_name?: string;
      location?: string;
      is_primary?: boolean;
    }

    // API Endpoint: GET /api/po?client_id={client_id}
    export async function getAllPOs(clientId?: number): Promise<GetAllPOsResponse> {
      const params = new URLSearchParams();
      if (clientId) params.append("client_id", clientId.toString());

      const response = await fetch(`/api/po?${params}`);
      return response.json();
    }
  }

  // =====================================================
  // PO MANAGEMENT - MULTIPLE POs PER PROJECT
  // =====================================================

  namespace ProjectPOs {
    // Request Models
    export interface CreatePORequest {
      po_number: string;
      po_date: string; // ISO date format
      po_value?: number;
      po_type?: string;
      parent_po_id?: number;
      notes?: string;
    }

    export interface AttachPORequest {
      sequence_order?: number;
    }

    // Response Models
    export interface PODetails {
      po_id?: number;
      client_po_id: number;
      po_number: string;
      po_date: string;
      po_value: number;
      po_type?: string;
      is_primary?: boolean;
      status?: string;
      location?: string;
    }

    export interface CreatePOResponse {
      status: "SUCCESS";
      message: string;
      client_po_id: number;
      po_number: string;
      po_type: string;
    }

    export interface GetProjectPOsResponse {
      status: "SUCCESS";
      project_id: number;
      pos: PODetails[];
      total_po_count: number;
      total_project_value: number;
      primary_po?: PODetails;
    }

    export interface AttachPOResponse {
      status: "SUCCESS";
      message: string;
      sequence_order: number;
    }

    export interface SetPrimaryPOResponse {
      status: "SUCCESS";
      message: string;
      primary_po_id: number;
    }

    // API Endpoints
    // POST /api/projects/{project_id}/po
    export async function createPOForProject(
      projectId: number,
      clientId: number,
      po: CreatePORequest
    ): Promise<CreatePOResponse> {
      const response = await fetch(`/api/projects/${projectId}/po?client_id=${clientId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(po),
      });
      return response.json();
    }

    // GET /api/projects/{project_id}/po
    export async function getProjectPOs(projectId: number): Promise<GetProjectPOsResponse> {
      const response = await fetch(`/api/projects/${projectId}/po`);
      return response.json();
    }

    // POST /api/projects/{project_id}/po/{client_po_id}/attach
    export async function attachPOToProject(
      projectId: number,
      clientPoId: number,
      sequenceOrder?: number
    ): Promise<AttachPOResponse> {
      const params = new URLSearchParams();
      if (sequenceOrder) params.append("sequence_order", sequenceOrder.toString());

      const response = await fetch(
        `/api/projects/${projectId}/po/${clientPoId}/attach?${params}`,
        {
          method: "POST",
        }
      );
      return response.json();
    }

    // PUT /api/projects/{project_id}/po/{client_po_id}/set-primary
    export async function setPrimaryPO(
      projectId: number,
      clientPoId: number
    ): Promise<SetPrimaryPOResponse> {
      const response = await fetch(
        `/api/projects/${projectId}/po/${clientPoId}/set-primary`,
        {
          method: "PUT",
        }
      );
      return response.json();
    }
  }

  // =====================================================
  // PO MANAGEMENT - UPDATE PO
  // =====================================================

  namespace UpdatePO {
    // Request Model
    export interface UpdatePORequest {
      po_number?: string;
      po_date?: string;
      po_value?: number;
      pi_number?: string;
      pi_date?: string;
      notes?: string;
      status?: string;
    }

    // Response Model
    export interface UpdatePOResponse {
      status: "SUCCESS";
      message: string;
      po: {
        po_id: number;
        po_number: string;
        po_date: string;
        po_value: number;
        status?: string;
      };
    }

    // API Endpoint: PUT /api/po/{client_po_id}
    export async function updatePO(
      clientPoId: number,
      po: UpdatePORequest
    ): Promise<UpdatePOResponse> {
      const response = await fetch(`/api/po/${clientPoId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(po),
      });
      return response.json();
    }
  }

  // =====================================================
  // PO MANAGEMENT - VERBAL AGREEMENTS
  // =====================================================

  namespace VerbalAgreements {
    // Request Models
    export interface VerbalAgreementRequest {
      pi_number: string;
      pi_date: string; // ISO date format
      value?: number;
      notes?: string;
    }

    export interface AddPOToVerbalAgreementRequest {
      po_number: string;
      po_date: string;
    }

    // Response Models
    export interface VerbalAgreement {
      agreement_id: number;
      pi_number: string;
      pi_date: string;
      po_number?: string;
      po_date?: string;
      value: number;
      notes?: string;
      vendor_name?: string;
      client_name?: string;
    }

    export interface CreateVerbalAgreementResponse {
      status: "SUCCESS";
      message: string;
      agreement_id: number;
      pi_number: string;
      pi_date: string;
    }

    export interface AddPOToVerbalAgreementResponse {
      status: "SUCCESS";
      message: string;
      agreement_id: number;
      pi_number: string;
      po_number: string;
      po_date: string;
    }

    export interface GetVerbalAgreementsResponse {
      status: "SUCCESS";
      project_id: number;
      agreements: VerbalAgreement[];
      total_agreement_count: number;
      total_agreement_value: number;
    }

    // API Endpoints
    // POST /api/projects/{project_id}/verbal-agreement
    export async function createVerbalAgreement(
      projectId: number,
      clientId: number,
      agreement: VerbalAgreementRequest
    ): Promise<CreateVerbalAgreementResponse> {
      const response = await fetch(`/api/projects/${projectId}/verbal-agreement?client_id=${clientId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(agreement),
      });
      return response.json();
    }

    // PUT /api/verbal-agreement/{agreement_id}/add-po
    export async function addPOToVerbalAgreement(
      agreementId: number,
      poData: AddPOToVerbalAgreementRequest
    ): Promise<AddPOToVerbalAgreementResponse> {
      const response = await fetch(`/api/verbal-agreement/${agreementId}/add-po`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(poData),
      });
      return response.json();
    }

    // GET /api/projects/{project_id}/verbal-agreements
    export async function getVerbalAgreements(
      projectId: number
    ): Promise<GetVerbalAgreementsResponse> {
      const response = await fetch(`/api/projects/${projectId}/verbal-agreements`);
      return response.json();
    }
  }

  // =====================================================
  // PO MANAGEMENT - DELETE PO
  // =====================================================

  namespace DeletePO {
    export interface DeletePOResponse {
      status: "SUCCESS";
      message: string;
      client_po_id: number;
    }

    // API Endpoint: DELETE /api/po/{client_po_id}
    export async function deletePO(clientPoId: number): Promise<DeletePOResponse> {
      const response = await fetch(`/api/po/${clientPoId}`, {
        method: "DELETE",
      });
      return response.json();
    }
  }

  // =====================================================
  // PO MANAGEMENT - PROJECTS
  // =====================================================

  namespace Projects {
    // Request Models
    export interface CreateProjectRequest {
      name: string;
      location?: string;
      city?: string;
      state?: string;
      country?: string;
      latitude?: number;
      longitude?: number;
    }

    export interface DeleteProjectRequest {
      name: string; // Project name to delete
    }

    // Response Models
    export interface CreateProjectResponse {
      status: "SUCCESS";
      message: string;
      project_id: number;
      name: string;
    }

    export interface DeleteProjectResponse {
      status: "SUCCESS";
      message: string;
      project_id: number;
      pos_deleted: number;
    }

    // API Endpoints
    // POST /api/projects
    export async function createProject(
      project: CreateProjectRequest
    ): Promise<CreateProjectResponse> {
      const response = await fetch("/api/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(project),
      });
      return response.json();
    }

    // DELETE /api/projects?name={name}
    export async function deleteProject(name: string): Promise<DeleteProjectResponse> {
      const response = await fetch(`/api/projects?name=${encodeURIComponent(name)}`, {
        method: "DELETE",
      });
      return response.json();
    }
  }

  // =====================================================
  // PO MANAGEMENT - FINANCIAL SUMMARY
  // =====================================================

  namespace FinancialSummary {
    export interface FinancialData {
      total_po_value: number;
      total_agreement_value: number;
      total_project_value: number;
      documents: number;
      verbal_agreements: number;
      total_collected: number;
      outstanding_amount: number;
      net_profit: number;
      profit_margin_percentage: number;
      active_orders: number;
      vendor_count: number;
      client_count: number;
    }

    export interface POData {
      po_id?: number;
      client_po_id: number;
      po_number: string;
      po_value: number;
      po_date: string;
      status?: string;
      location?: string;
    }

    export interface AgreementData {
      agreement_id: number;
      pi_number: string;
      pi_date: string;
      value: number;
    }

    export interface FinancialSummaryResponse {
      status: "SUCCESS";
      project_id: number;
      financial_summary: FinancialData;
      purchase_orders: {
        count: number;
        total_value: number;
        orders: POData[];
      };
      verbal_agreements: {
        count: number;
        total_value: number;
        agreements: AgreementData[];
      };
    }

    // API Endpoint: GET /api/projects/{project_id}/financial-summary
    export async function getFinancialSummary(
      projectId: number
    ): Promise<FinancialSummaryResponse> {
      const response = await fetch(`/api/projects/${projectId}/financial-summary`);
      return response.json();
    }
  }

  // =====================================================
  // PO MANAGEMENT - ENRICHED POs (WITH PAYMENT DATA)
  // =====================================================

  namespace EnrichedPOs {
    export interface PaymentDetail {
      payment_id: number;
      amount: number;
      date: string;
      method: string;
      tds?: number;
    }

    export interface EnrichedPO {
      po_id?: number;
      client_po_id: number;
      po_number: string;
      po_date: string;
      po_value: number;
      total_paid: number;
      receivable_amount: number;
      payment_status: "paid" | "partial" | "pending";
      total_tds: number;
      payment_details: PaymentDetail[];
      payment_count: number;
      location?: string;
    }

    export interface EnrichedPOsResponse {
      status: "SUCCESS";
      project_id: number;
      pos: EnrichedPO[];
      total_po_count: number;
      total_project_value: number;
      total_paid: number;
      total_receivable: number;
      summary: {
        paid_count: number;
        partial_count: number;
        pending_count: number;
      };
    }

    // API Endpoint: GET /api/projects/{project_id}/po/enriched
    export async function getEnrichedPOs(projectId: number): Promise<EnrichedPOsResponse> {
      const response = await fetch(`/api/projects/${projectId}/po/enriched`);
      return response.json();
    }
  }
}

// =====================================================
// 4. BILLING PO OPERATIONS
// =====================================================

export namespace BillingPO {
  // Request Models
  export interface CreateBillingPORequest {
    client_po_id: number;
    billed_value: number;
    billed_gst?: number;
    billing_notes?: string;
  }

  export interface BillingLineItemRequest {
    description: string;
    qty: number;
    rate: number;
  }

  export interface UpdateBillingPORequest {
    billed_value?: number;
    billed_gst?: number;
    billing_notes?: string;
  }

  // Response Models
  export interface BillingLineItem {
    id?: number;
    line_item_id?: string;
    description: string;
    qty: number;
    rate: number;
    total: number;
  }

  export interface BillingPODetails {
    billing_po_id: string;
    po_number: string;
    client_po_id: number;
    project_id: number;
    billed_value: number;
    billed_gst: number;
    billing_notes?: string;
    line_items?: BillingLineItem[];
    created_at?: string;
  }

  export interface CreateBillingPOResponse {
    status: "SUCCESS";
    message: string;
    billing_po: BillingPODetails;
  }

  export interface GetBillingPOResponse {
    status: "SUCCESS";
    billing_po?: BillingPODetails;
    [key: string]: any;
  }

  export interface GetBillingLineItemsResponse {
    status: "SUCCESS";
    billing_po_id: string;
    line_item_count: number;
    total_value: number;
    line_items: BillingLineItem[];
  }

  export interface AddBillingLineItemResponse {
    status: "SUCCESS";
    message: string;
    line_item: BillingLineItem;
  }

  export interface UpdateBillingPOResponse {
    status: "SUCCESS";
    message: string;
    billing_po: BillingPODetails;
  }

  export interface DeleteBillingLineItemResponse {
    status: "SUCCESS";
    message: string;
  }

  export interface BillingPOFinancial {
    total?: number;
    gst?: number;
    net?: number;
  }

  export interface BillingSummary {
    original_po: BillingPOFinancial;
    billing_po: BillingPOFinancial;
    financial_summary: {
      delta_value: number;
      delta_percent: number;
      vendor_costs: number;
      profit: number;
      profit_margin_percent: number;
      final_revenue: number;
    };
  }

  export interface GetProjectBillingSummaryResponse {
    status: "SUCCESS";
    project_id: number;
    data: BillingSummary;
  }

  export interface ProfitLossAnalysis {
    baseline: { po_value: number };
    billing: { billed_value: number };
    variance: {
      delta: number;
      delta_percent: number;
      direction: "up" | "down";
    };
    costs: { vendor_costs: number };
    profit_loss: {
      amount: number;
      margin_percent: number;
      status: "profit" | "loss";
    };
    totals: {
      revenue: number;
      costs: number;
      profit: number;
    };
  }

  export interface GetProjectProfitLossResponse {
    status: "SUCCESS";
    project_id: number;
    analysis: ProfitLossAnalysis;
  }

  // API Endpoints
  // POST /api/projects/{project_id}/billing-po
  export async function createBillingPO(
    projectId: number,
    request: CreateBillingPORequest
  ): Promise<CreateBillingPOResponse> {
    const response = await fetch(`/api/projects/${projectId}/billing-po`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
    return response.json();
  }

  // GET /api/billing-po/{billing_po_id}
  export async function getBillingPO(billingPoId: string): Promise<GetBillingPOResponse> {
    const response = await fetch(`/api/billing-po/${billingPoId}`);
    return response.json();
  }

  // GET /api/projects/{project_id}/billing-summary
  export async function getProjectBillingSummary(
    projectId: number
  ): Promise<GetProjectBillingSummaryResponse> {
    const response = await fetch(`/api/projects/${projectId}/billing-summary`);
    return response.json();
  }

  // POST /api/billing-po/{billing_po_id}/line-items
  export async function addBillingLineItem(
    billingPoId: string,
    item: BillingLineItemRequest
  ): Promise<AddBillingLineItemResponse> {
    const response = await fetch(`/api/billing-po/${billingPoId}/line-items`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(item),
    });
    return response.json();
  }

  // GET /api/billing-po/{billing_po_id}/line-items
  export async function getBillingLineItems(
    billingPoId: string
  ): Promise<GetBillingLineItemsResponse> {
    const response = await fetch(`/api/billing-po/${billingPoId}/line-items`);
    return response.json();
  }

  // PUT /api/billing-po/{billing_po_id}
  export async function updateBillingPO(
    billingPoId: string,
    request: UpdateBillingPORequest
  ): Promise<UpdateBillingPOResponse> {
    const response = await fetch(`/api/billing-po/${billingPoId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
    return response.json();
  }

  // DELETE /api/billing-po/{billing_po_id}/line-items/{line_item_id}
  export async function deleteBillingLineItem(
    billingPoId: string,
    lineItemId: string
  ): Promise<DeleteBillingLineItemResponse> {
    const response = await fetch(
      `/api/billing-po/${billingPoId}/line-items/${lineItemId}`,
      {
        method: "DELETE",
      }
    );
    return response.json();
  }

  // GET /api/projects/{project_id}/billing-pl-analysis
  export async function getProjectProfitLoss(
    projectId: number
  ): Promise<GetProjectProfitLossResponse> {
    const response = await fetch(`/api/projects/${projectId}/billing-pl-analysis`);
    return response.json();
  }
}

// =====================================================
// 5. VENDOR ORDERS (RELATED TO PO)
// =====================================================

export namespace VendorOrders {
  // Request Models
  export interface VendorOrderRequest {
    vendor_id: number;
    po_number: string;
    po_date: string; // ISO date format
    po_value?: number;
    due_date?: string;
    description?: string;
  }

  export interface BulkCreateVendorOrdersRequest {
    orders: VendorOrderRequest[];
  }

  export interface VendorOrderUpdateRequest {
    po_value?: number;
    due_date?: string;
    description?: string;
    work_status?: string;
    payment_status?: string;
  }

  export interface VendorOrderStatusRequest {
    work_status?: string;
    payment_status?: string;
  }

  export interface VendorOrderLineItemRequest {
    item_name: string;
    quantity: number;
    unit_price: number;
  }

  export interface VendorOrderLineItemUpdateRequest {
    item_name?: string;
    quantity?: number;
    unit_price?: number;
  }

  // Response Models
  export interface VendorOrderDetails {
    vendor_order_id?: number;
    vendor_id: number;
    project_id: number;
    po_number: string;
    po_date: string;
    po_value: number;
    due_date?: string;
    description?: string;
    work_status?: string;
    payment_status?: string;
    vendor_name?: string;
  }

  export interface VendorOrderLineItem {
    line_item_id?: number;
    item_name: string;
    quantity: number;
    unit_price: number;
    total?: number;
  }

  export interface CreateVendorOrderResponse {
    status: "SUCCESS";
    message: string;
    vendor_order: VendorOrderDetails;
  }

  export interface BulkCreateVendorOrdersResponse {
    status: "SUCCESS";
    message: string;
    vendor_orders: VendorOrderDetails[];
    count: number;
  }

  export interface GetVendorOrdersResponse {
    status: "SUCCESS";
    project_id: number;
    vendor_orders: VendorOrderDetails[];
    total_orders: number;
    total_value: number;
  }

  export interface GetVendorOrderDetailsResponse {
    status: "SUCCESS";
    vendor_order: VendorOrderDetails;
  }

  export interface UpdateVendorOrderResponse {
    status: "SUCCESS";
    message: string;
    vendor_order: VendorOrderDetails;
  }

  export interface VendorOrderLineItemsResponse {
    status: "SUCCESS";
    vendor_order_id: number;
    line_items: VendorOrderLineItem[];
    line_item_count: number;
    total_value: number;
  }

  export interface VendorOrderPaymentSummary {
    total_po_value: number;
    total_paid: number;
    outstanding: number;
    payment_status: "paid" | "partial" | "pending";
  }

  // API Endpoints
  // POST /api/projects/{project_id}/vendor-orders
  export async function createVendorOrder(
    projectId: number,
    order: VendorOrderRequest
  ): Promise<CreateVendorOrderResponse> {
    const response = await fetch(`/api/projects/${projectId}/vendor-orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(order),
    });
    return response.json();
  }

  // POST /api/projects/{project_id}/vendor-orders/bulk
  export async function bulkCreateVendorOrders(
    projectId: number,
    request: BulkCreateVendorOrdersRequest
  ): Promise<BulkCreateVendorOrdersResponse> {
    const response = await fetch(`/api/projects/${projectId}/vendor-orders/bulk`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
    return response.json();
  }

  // GET /api/projects/{project_id}/vendor-orders
  export async function getProjectVendorOrders(
    projectId: number
  ): Promise<GetVendorOrdersResponse> {
    const response = await fetch(`/api/projects/${projectId}/vendor-orders`);
    return response.json();
  }

  // GET /api/vendor-orders/{vendor_order_id}
  export async function getVendorOrderDetails(
    vendorOrderId: number
  ): Promise<GetVendorOrderDetailsResponse> {
    const response = await fetch(`/api/vendor-orders/${vendorOrderId}`);
    return response.json();
  }

  // PUT /api/vendor-orders/{vendor_order_id}
  export async function updateVendorOrder(
    vendorOrderId: number,
    request: VendorOrderUpdateRequest
  ): Promise<UpdateVendorOrderResponse> {
    const response = await fetch(`/api/vendor-orders/${vendorOrderId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
    return response.json();
  }

  // PUT /api/vendor-orders/{vendor_order_id}/status
  export async function updateVendorOrderStatus(
    vendorOrderId: number,
    status: VendorOrderStatusRequest
  ): Promise<UpdateVendorOrderResponse> {
    const response = await fetch(`/api/vendor-orders/${vendorOrderId}/status`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(status),
    });
    return response.json();
  }

  // DELETE /api/vendor-orders/{vendor_order_id}
  export async function deleteVendorOrder(vendorOrderId: number): Promise<{
    status: "SUCCESS" | "FAILED";
    message: string;
  }> {
    const response = await fetch(`/api/vendor-orders/${vendorOrderId}`, {
      method: "DELETE",
    });
    return response.json();
  }

  // POST /api/vendor-orders/{vendor_order_id}/line-items
  export async function addVendorOrderLineItem(
    vendorOrderId: number,
    item: VendorOrderLineItemRequest
  ): Promise<{
    status: "SUCCESS";
    message: string;
    line_item: VendorOrderLineItem;
  }> {
    const response = await fetch(
      `/api/vendor-orders/${vendorOrderId}/line-items`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(item),
      }
    );
    return response.json();
  }

  // GET /api/vendor-orders/{vendor_order_id}/line-items
  export async function getVendorOrderLineItems(
    vendorOrderId: number
  ): Promise<VendorOrderLineItemsResponse> {
    const response = await fetch(
      `/api/vendor-orders/${vendorOrderId}/line-items`
    );
    return response.json();
  }

  // PUT /api/vendor-orders/{vendor_order_id}/line-items/{line_item_id}
  export async function updateVendorOrderLineItem(
    vendorOrderId: number,
    lineItemId: number,
    item: VendorOrderLineItemUpdateRequest
  ): Promise<{
    status: "SUCCESS";
    message: string;
    line_item: VendorOrderLineItem;
  }> {
    const response = await fetch(
      `/api/vendor-orders/${vendorOrderId}/line-items/${lineItemId}`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(item),
      }
    );
    return response.json();
  }

  // DELETE /api/vendor-orders/{vendor_order_id}/line-items/{line_item_id}
  export async function deleteVendorOrderLineItem(
    vendorOrderId: number,
    lineItemId: number
  ): Promise<{
    status: "SUCCESS";
    message: string;
  }> {
    const response = await fetch(
      `/api/vendor-orders/${vendorOrderId}/line-items/${lineItemId}`,
      {
        method: "DELETE",
      }
    );
    return response.json();
  }

  // GET /api/vendor-orders/{vendor_order_id}/payment-summary
  export async function getVendorOrderPaymentSummary(
    vendorOrderId: number
  ): Promise<{
    status: "SUCCESS";
    summary: VendorOrderPaymentSummary;
  }> {
    const response = await fetch(
      `/api/vendor-orders/${vendorOrderId}/payment-summary`
    );
    return response.json();
  }
}

// =====================================================
// HELPER UTILITIES & API CONFIGURATION
// =====================================================

export class POAPIClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;

  constructor(baseURL: string = process.env.REACT_APP_API_URL || "http://localhost:8000") {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      "Content-Type": "application/json",
    };
  }

  /**
   * Set authentication token for requests
   */
  setAuthToken(token: string) {
    this.defaultHeaders["Authorization"] = `Bearer ${token}`;
  }

  /**
   * Generic fetch wrapper with error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.defaultHeaders,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || error.message || "API Error");
    }

    return response.json();
  }

  // ==========================================
  // CLIENT PO OPERATIONS
  // ==========================================

  async getClientPO(clientPoId: number) {
    return this.request(`/api/client-po/${clientPoId}`);
  }

  // ==========================================
  // BAJAJ PO OPERATIONS
  // ==========================================

  async uploadBajajPO(
    file: File,
    clientId: number,
    projectId?: number
  ): Promise<BajajPO.BajajPOParseResponse> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("client_id", clientId.toString());
    if (projectId) formData.append("project_id", projectId.toString());

    const url = `${this.baseURL}/api/bajaj-po`;
    const response = await fetch(url, {
      method: "POST",
      body: formData,
      headers: {
        Authorization: this.defaultHeaders["Authorization"] || "",
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Upload failed");
    }

    return response.json();
  }

  async bulkUploadBajajPO(
    files: File[],
    clientId: number,
    projectId?: number
  ): Promise<BajajPO.BajajPOBulkUploadResponse> {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    formData.append("client_id", clientId.toString());
    if (projectId) formData.append("project_id", projectId.toString());

    const url = `${this.baseURL}/api/bajaj-po/bulk`;
    const response = await fetch(url, {
      method: "POST",
      body: formData,
      headers: {
        Authorization: this.defaultHeaders["Authorization"] || "",
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Bulk upload failed");
    }

    return response.json();
  }

  // ==========================================
  // DAVA INDIA PO OPERATIONS
  // ==========================================

  async uploadDavaIndiaPO(
    file: File,
    clientId: number,
    projectId?: number
  ): Promise<DavaIndiaPO.DavaIndiaPOParseResponse> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("client_id", clientId.toString());
    if (projectId) formData.append("project_id", projectId.toString());

    const url = `${this.baseURL}/api/dava-india-po`;
    const response = await fetch(url, {
      method: "POST",
      body: formData,
      headers: {
        Authorization: this.defaultHeaders["Authorization"] || "",
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Upload failed");
    }

    return response.json();
  }

  async bulkUploadDavaIndiaPO(
    files: File[],
    clientId: number,
    projectId?: number
  ): Promise<DavaIndiaPO.DavaIndiaPOBulkUploadResponse> {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    formData.append("client_id", clientId.toString());
    if (projectId) formData.append("project_id", projectId.toString());

    const url = `${this.baseURL}/api/dava-india-po/bulk`;
    const response = await fetch(url, {
      method: "POST",
      body: formData,
      headers: {
        Authorization: this.defaultHeaders["Authorization"] || "",
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Bulk upload failed");
    }

    return response.json();
  }

  // ==========================================
  // PO MANAGEMENT - LINE ITEMS
  // ==========================================

  async addLineItem(clientPoId: number, item: POManagement.LineItems.LineItemRequest) {
    return this.request(`/api/po/${clientPoId}/line-items`, {
      method: "POST",
      body: JSON.stringify(item),
    });
  }

  async getLineItems(clientPoId: number) {
    return this.request(`/api/po/${clientPoId}/line-items`);
  }

  async updateLineItem(
    lineItemId: number,
    item: POManagement.LineItems.LineItemUpdateRequest
  ) {
    return this.request(`/api/line-items/${lineItemId}`, {
      method: "PUT",
      body: JSON.stringify(item),
    });
  }

  async deleteLineItem(lineItemId: number) {
    return this.request(`/api/line-items/${lineItemId}`, {
      method: "DELETE",
    });
  }

  // ==========================================
  // PO MANAGEMENT - MULTIPLE POs PER PROJECT
  // ==========================================

  async getAllPOs(clientId?: number) {
    const params = new URLSearchParams();
    if (clientId) params.append("client_id", clientId.toString());
    return this.request(`/api/po?${params}`);
  }

  async createPOForProject(
    projectId: number,
    clientId: number,
    po: POManagement.ProjectPOs.CreatePORequest
  ) {
    return this.request(`/api/projects/${projectId}/po?client_id=${clientId}`, {
      method: "POST",
      body: JSON.stringify(po),
    });
  }

  async getProjectPOs(projectId: number) {
    return this.request(`/api/projects/${projectId}/po`);
  }

  async attachPOToProject(
    projectId: number,
    clientPoId: number,
    sequenceOrder?: number
  ) {
    const params = new URLSearchParams();
    if (sequenceOrder) params.append("sequence_order", sequenceOrder.toString());
    return this.request(`/api/projects/${projectId}/po/${clientPoId}/attach?${params}`, {
      method: "POST",
    });
  }

  async setPrimaryPO(projectId: number, clientPoId: number) {
    return this.request(`/api/projects/${projectId}/po/${clientPoId}/set-primary`, {
      method: "PUT",
    });
  }

  async updatePO(clientPoId: number, po: POManagement.UpdatePO.UpdatePORequest) {
    return this.request(`/api/po/${clientPoId}`, {
      method: "PUT",
      body: JSON.stringify(po),
    });
  }

  async deletePO(clientPoId: number) {
    return this.request(`/api/po/${clientPoId}`, {
      method: "DELETE",
    });
  }

  // ==========================================
  // PO MANAGEMENT - VERBAL AGREEMENTS
  // ==========================================

  async createVerbalAgreement(
    projectId: number,
    clientId: number,
    agreement: POManagement.VerbalAgreements.VerbalAgreementRequest
  ) {
    return this.request(`/api/projects/${projectId}/verbal-agreement?client_id=${clientId}`, {
      method: "POST",
      body: JSON.stringify(agreement),
    });
  }

  async addPOToVerbalAgreement(
    agreementId: number,
    poData: POManagement.VerbalAgreements.AddPOToVerbalAgreementRequest
  ) {
    return this.request(`/api/verbal-agreement/${agreementId}/add-po`, {
      method: "PUT",
      body: JSON.stringify(poData),
    });
  }

  async getVerbalAgreements(projectId: number) {
    return this.request(`/api/projects/${projectId}/verbal-agreements`);
  }

  // ==========================================
  // PO MANAGEMENT - PROJECTS
  // ==========================================

  async createProject(project: POManagement.Projects.CreateProjectRequest) {
    return this.request("/api/projects", {
      method: "POST",
      body: JSON.stringify(project),
    });
  }

  async deleteProject(name: string) {
    return this.request(`/api/projects?name=${encodeURIComponent(name)}`, {
      method: "DELETE",
    });
  }

  // ==========================================
  // PO MANAGEMENT - FINANCIAL SUMMARY
  // ==========================================

  async getFinancialSummary(projectId: number) {
    return this.request(`/api/projects/${projectId}/financial-summary`);
  }

  async getEnrichedPOs(projectId: number) {
    return this.request(`/api/projects/${projectId}/po/enriched`);
  }

  // ==========================================
  // BILLING PO OPERATIONS
  // ==========================================

  async createBillingPO(projectId: number, request: BillingPO.CreateBillingPORequest) {
    return this.request(`/api/projects/${projectId}/billing-po`, {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async getBillingPO(billingPoId: string) {
    return this.request(`/api/billing-po/${billingPoId}`);
  }

  async getProjectBillingSummary(projectId: number) {
    return this.request(`/api/projects/${projectId}/billing-summary`);
  }

  async addBillingLineItem(
    billingPoId: string,
    item: BillingPO.BillingLineItemRequest
  ) {
    return this.request(`/api/billing-po/${billingPoId}/line-items`, {
      method: "POST",
      body: JSON.stringify(item),
    });
  }

  async getBillingLineItems(billingPoId: string) {
    return this.request(`/api/billing-po/${billingPoId}/line-items`);
  }

  async updateBillingPO(
    billingPoId: string,
    request: BillingPO.UpdateBillingPORequest
  ) {
    return this.request(`/api/billing-po/${billingPoId}`, {
      method: "PUT",
      body: JSON.stringify(request),
    });
  }

  async deleteBillingLineItem(billingPoId: string, lineItemId: string) {
    return this.request(
      `/api/billing-po/${billingPoId}/line-items/${lineItemId}`,
      {
        method: "DELETE",
      }
    );
  }

  async getProjectProfitLoss(projectId: number) {
    return this.request(`/api/projects/${projectId}/billing-pl-analysis`);
  }

  // ==========================================
  // VENDOR ORDERS OPERATIONS
  // ==========================================

  async createVendorOrder(
    projectId: number,
    order: VendorOrders.VendorOrderRequest
  ) {
    return this.request(`/api/projects/${projectId}/vendor-orders`, {
      method: "POST",
      body: JSON.stringify(order),
    });
  }

  async bulkCreateVendorOrders(
    projectId: number,
    request: VendorOrders.BulkCreateVendorOrdersRequest
  ) {
    return this.request(`/api/projects/${projectId}/vendor-orders/bulk`, {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async getProjectVendorOrders(projectId: number) {
    return this.request(`/api/projects/${projectId}/vendor-orders`);
  }

  async getVendorOrderDetails(vendorOrderId: number) {
    return this.request(`/api/vendor-orders/${vendorOrderId}`);
  }

  async updateVendorOrder(
    vendorOrderId: number,
    request: VendorOrders.VendorOrderUpdateRequest
  ) {
    return this.request(`/api/vendor-orders/${vendorOrderId}`, {
      method: "PUT",
      body: JSON.stringify(request),
    });
  }

  async updateVendorOrderStatus(
    vendorOrderId: number,
    status: VendorOrders.VendorOrderStatusRequest
  ) {
    return this.request(`/api/vendor-orders/${vendorOrderId}/status`, {
      method: "PUT",
      body: JSON.stringify(status),
    });
  }

  async deleteVendorOrder(vendorOrderId: number) {
    return this.request(`/api/vendor-orders/${vendorOrderId}`, {
      method: "DELETE",
    });
  }

  async addVendorOrderLineItem(
    vendorOrderId: number,
    item: VendorOrders.VendorOrderLineItemRequest
  ) {
    return this.request(`/api/vendor-orders/${vendorOrderId}/line-items`, {
      method: "POST",
      body: JSON.stringify(item),
    });
  }

  async getVendorOrderLineItems(vendorOrderId: number) {
    return this.request(`/api/vendor-orders/${vendorOrderId}/line-items`);
  }

  async updateVendorOrderLineItem(
    vendorOrderId: number,
    lineItemId: number,
    item: VendorOrders.VendorOrderLineItemUpdateRequest
  ) {
    return this.request(
      `/api/vendor-orders/${vendorOrderId}/line-items/${lineItemId}`,
      {
        method: "PUT",
        body: JSON.stringify(item),
      }
    );
  }

  async deleteVendorOrderLineItem(vendorOrderId: number, lineItemId: number) {
    return this.request(
      `/api/vendor-orders/${vendorOrderId}/line-items/${lineItemId}`,
      {
        method: "DELETE",
      }
    );
  }

  async getVendorOrderPaymentSummary(vendorOrderId: number) {
    return this.request(`/api/vendor-orders/${vendorOrderId}/payment-summary`);
  }
}

// =====================================================
// EXPORT ALL NAMESPACES & UTILITIES
// =====================================================

export default {
  ClientPO,
  BajajPO,
  DavaIndiaPO,
  POManagement,
  BillingPO,
  VendorOrders,
  POAPIClient,
};
