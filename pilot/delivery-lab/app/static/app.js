"use strict";

const form = document.querySelector("#create-form");
const nameInput = document.querySelector("#item-name");
const nameError = document.querySelector("#name-error");
const createButton = document.querySelector("#create-button");
const refreshButton = document.querySelector("#refresh-button");
const statusRegion = document.querySelector("#status");
const list = document.querySelector("#items");
const count = document.querySelector("#item-count");
const empty = document.querySelector("#empty");
const itemsSection = document.querySelector("#items-section");

// Exactly the BASE-3 set; JS trim() has different U+0085/U+FEFF semantics.
const trimPattern = /^[\u0009-\u000d\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+|[\u0009-\u000d\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+$/gu;
const lengthMessage = "Enter 1–80 characters after trimming surrounding whitespace.";
let pending = false;
let refreshing = false;
let listReady = false;
let recovery = "normal"; // normal | created | uncertain

function announce(message, kind = "") {
  statusRegion.textContent = message;
  statusRegion.className = kind;
}

function controls() {
  createButton.disabled = pending || refreshing || !listReady;
  nameInput.readOnly = pending;
  createButton.textContent = pending ? "Creating…" : recovery === "uncertain" ? "Create another item" : "Create";
  refreshButton.disabled = pending || refreshing;
}

function fieldError(message) {
  nameError.textContent = message;
  nameError.hidden = !message;
  nameInput.setAttribute("aria-invalid", message ? "true" : "false");
  if (message) nameInput.focus();
}

async function request(url, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(url, { ...options, signal: controller.signal, cache: "no-store", credentials: "same-origin" });
    const body = await response.json();
    return { response, body };
  } finally {
    clearTimeout(timer);
  }
}

async function refreshItems() {
  if (refreshing) return;
  refreshing = true;
  listReady = false;
  itemsSection.setAttribute("aria-busy", "true");
  controls();
  try {
    const { response, body } = await request("/api/items");
    if (response.status !== 200 || !Array.isArray(body.items) || body.items.some(value =>
      typeof value.id !== "string" || typeof value.name !== "string")) throw new Error("List unavailable");
    const fragment = document.createDocumentFragment();
    for (const value of body.items) {
      const row = document.createElement("li");
      row.dataset.itemId = value.id;
      row.textContent = value.name;
      fragment.append(row);
    }
    list.replaceChildren(fragment);
    count.textContent = `${body.items.length} ${body.items.length === 1 ? "item" : "items"}`;
    empty.hidden = body.items.length !== 0;
    listReady = true;
    refreshButton.hidden = true;
    if (recovery === "uncertain") {
      announce("Check the list. A matching name may already exist. Create another item only if you intend to add one.");
    } else if (recovery === "created") {
      announce("Item created.", "success");
      recovery = "normal";
    } else {
      announce("Items loaded.");
    }
  } catch (_) {
    refreshButton.hidden = false;
    if (recovery === "uncertain") {
      announce("We still cannot check the list. Refresh the list before creating another item.", "error");
    } else if (recovery === "created") {
      announce("Item was created, but the list could not be refreshed. Refresh the list to see it.", "error");
    } else {
      announce("Items could not be loaded. Refresh the list to try again.", "error");
    }
  } finally {
    refreshing = false;
    itemsSection.setAttribute("aria-busy", "false");
    controls();
  }
}

async function reconcile() {
  recovery = "uncertain";
  listReady = false;
  announce("We could not confirm whether the item was created. Refreshing the list before you retry.", "error");
  // GET only. A matching name cannot identify a request: duplicates are valid.
  await refreshItems();
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  if (pending || refreshing || !listReady) return;
  const submitted = nameInput.value;
  const normalized = submitted.replace(trimPattern, "");
  const scalars = Array.from(normalized);
  if (scalars.some(c => c.codePointAt(0) >= 0xd800 && c.codePointAt(0) <= 0xdfff)) {
    fieldError("Use valid Unicode text.");
    return;
  }
  if (scalars.length < 1 || scalars.length > 80) {
    fieldError(lengthMessage);
    return;
  }
  fieldError("");
  pending = true;
  controls();
  announce("Creating item…");
  try {
    const { response, body } = await request("/api/items", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name: submitted })
    });
    if (response.status === 201 && typeof body.id === "string" && typeof body.name === "string") {
      recovery = "created";
      nameInput.value = "";
      announce("Item created. Updating the list…");
      await refreshItems();
    } else if (response.status === 422 && body.error?.code === "validation_error" &&
               body.error.fields?.length === 1 && typeof body.error.fields[0].message === "string") {
      fieldError(body.error.fields[0].message);
      announce("Check the item name.", "error");
    } else if ((response.status === 503 && body.error?.code === "storage_unavailable") ||
               (response.status === 403 && ["host_not_allowed", "origin_not_allowed"].includes(body.error?.code)) ||
               (response.status === 400 && body.error?.code === "invalid_json") ||
               (response.status === 413 && body.error?.code === "request_too_large") ||
               (response.status === 415 && body.error?.code === "unsupported_media_type")) {
      announce("Item was not created. Try again.", "error");
    } else {
      await reconcile();
    }
  } catch (_) {
    await reconcile();
  } finally {
    pending = false;
    controls();
  }
});

nameInput.addEventListener("input", () => fieldError(""));
refreshButton.addEventListener("click", () => { if (!pending && !refreshing) refreshItems(); });
refreshItems();
