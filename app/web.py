from __future__ import annotations

import json
from html import escape
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from app.core.config import settings

router = APIRouter(include_in_schema=False)

_UI_TEMPLATE = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>__PROJECT_NAME__ | Panel</title>
  <style>
    :root {
      color-scheme: light;
      --corp-navy: #0a1628;
      --corp-navy-mid: #132337;
      --corp-accent: #0c4a6e;
      --bg: #eef2f7;
      --bg-elevated: #f8fafc;
      --panel: var(--corp-navy);
      --panel-soft: var(--corp-navy-mid);
      --card: #ffffff;
      --line: #d1dae6;
      --line-strong: #b8c5d6;
      --text: #0f172a;
      --muted: #64748b;
      --brand: #0b6ead;
      --brand-soft: #e0f0fa;
      --brand-dark: #085a8f;
      --ok: #0d9488;
      --error: #b91c1c;
      --shadow: 0 1px 3px rgba(15, 23, 42, 0.06), 0 12px 32px rgba(15, 23, 42, 0.08);
      --radius-lg: 16px;
      --radius-md: 12px;
      --radius-sm: 10px;
      --font: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      --space-1: 6px;
      --space-2: 10px;
      --space-3: 14px;
      --space-4: 18px;
      --space-5: 22px;
      --space-6: 28px;
      --label-gap: 7px;
      --gap-form: var(--space-3);
      --gap-grid: var(--space-4);
      --gap-section: var(--space-4);
      --pad-card: 20px;
      --pad-card-block-end: 22px;
      --form-max-width: 920px;
    }

    * { box-sizing: border-box; }

    html { -webkit-font-smoothing: antialiased; }

    body {
      margin: 0;
      font-family: var(--font);
      font-size: 15px;
      line-height: 1.5;
      background-color: var(--bg);
      background-image:
        radial-gradient(ellipse 900px 420px at 12% -8%, rgba(11, 110, 173, 0.075), transparent 58%),
        radial-gradient(ellipse 800px 380px at 98% 5%, rgba(10, 22, 40, 0.055), transparent 52%);
      color: var(--text);
    }

    a {
      color: var(--brand);
      text-decoration: none;
    }

    a:hover { text-decoration: underline; }

    .app-shell {
      min-height: 100vh;
      display: grid;
      grid-template-columns: minmax(260px, 288px) minmax(0, 1fr);
    }

    .sidebar {
      background: linear-gradient(165deg, var(--panel) 0%, var(--panel-soft) 55%, #0d2137 100%);
      color: #fff;
      padding: 22px 16px;
      position: sticky;
      top: 0;
      height: 100vh;
      overflow: auto;
      border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    .brand {
      margin-bottom: 16px;
      padding-bottom: 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .brand h1 {
      margin: 0 0 6px;
      font-size: 1.35rem;
      font-weight: 800;
      letter-spacing: -0.02em;
    }

    .brand p {
      margin: 0;
      color: #94a3b8;
      line-height: 1.5;
      font-size: 13px;
    }

    .sidebar-url-hint {
      margin: 10px 0 0;
      font-size: 12px;
      color: #cbd5e1;
      line-height: 1.45;
    }

    .sidebar-url-hint strong {
      color: #e2e8f0;
    }

    .nav-group {
      margin-top: 18px;
    }

    .nav-title {
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: #64748b;
      margin-bottom: 8px;
      font-weight: 700;
    }

    .nav-button {
      width: 100%;
      text-align: left;
      border: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(255, 255, 255, 0.04);
      color: #f1f5f9;
      border-radius: var(--radius-md);
      padding: 11px 12px;
      margin-bottom: 6px;
      cursor: pointer;
      font-weight: 650;
      font-size: 14px;
      transition: background 0.15s ease, border-color 0.15s ease;
    }

    .nav-button small {
      display: block;
      margin-top: 3px;
      color: #94a3b8;
      font-weight: 400;
      font-size: 12px;
    }

    .nav-button:hover {
      background: rgba(255, 255, 255, 0.08);
      border-color: rgba(255, 255, 255, 0.15);
    }

    .nav-button.active {
      background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
      color: var(--corp-navy);
      border-color: rgba(11, 110, 173, 0.35);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
    }

    .nav-button.active small {
      color: #475569;
    }

    a.sidebar-manual-link {
      display: block;
      box-sizing: border-box;
      width: 100%;
      text-align: left;
      text-decoration: none;
      color: inherit;
      border: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(255, 255, 255, 0.04);
      color: #f1f5f9;
      border-radius: var(--radius-md);
      padding: 11px 12px;
      margin-bottom: 6px;
      cursor: pointer;
      font-weight: 650;
      font-size: 14px;
      transition: background 0.15s ease, border-color 0.15s ease;
    }

    a.sidebar-manual-link small {
      display: block;
      margin-top: 3px;
      color: #94a3b8;
      font-weight: 400;
      font-size: 12px;
    }

    a.sidebar-manual-link:hover {
      background: rgba(255, 255, 255, 0.08);
      border-color: rgba(255, 255, 255, 0.15);
    }

    .sidebar-note {
      margin-top: 18px;
      border-radius: var(--radius-md);
      padding: 12px 14px;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.08);
      color: #cbd5e1;
      font-size: 12px;
      line-height: 1.5;
    }

    .main {
      padding: var(--space-5) var(--space-6) 40px;
      min-width: 0;
      max-width: 1720px;
      margin: 0 auto;
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      gap: var(--space-4);
      align-items: flex-start;
      margin-bottom: var(--space-4);
      flex-wrap: wrap;
    }

    .topbar h2 {
      margin: 0;
      font-size: 1.65rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      color: var(--corp-navy);
      font-synthesis: weight;
    }

    .topbar p {
      margin: 6px 0 0;
      color: var(--muted);
      max-width: 52rem;
      line-height: 1.55;
      font-size: 14px;
    }

    .banner {
      margin-bottom: var(--space-4);
      padding: 14px 16px;
      border-radius: var(--radius-md);
      background: linear-gradient(135deg, var(--brand-soft) 0%, #f0f9ff 100%);
      border: 1px solid #bae6fd;
      color: var(--corp-accent);
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
      font-size: 14px;
      font-weight: 800;
      font-synthesis: weight;
    }

    .catalog-refresh-banner {
      margin-bottom: var(--space-4);
      padding: 12px 16px;
      border-radius: var(--radius-md);
      background: #fffbeb;
      border: 1px solid #fcd34d;
      color: #78350f;
      font-size: 14px;
      line-height: 1.5;
    }

    .catalog-refresh-banner strong {
      display: block;
      margin-bottom: 6px;
    }

    .catalog-refresh-banner ul {
      margin: 8px 0 0 1.1em;
      padding: 0;
    }

    .status-grid,
    .grid,
    .split {
      display: grid;
      gap: var(--gap-grid);
    }

    .status-grid {
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      margin-bottom: var(--gap-grid);
    }

    .grid {
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 340px), 1fr));
    }

    .grid > *,
    .split > * {
      min-width: 0;
    }

    .split {
      grid-template-columns: minmax(0, 1fr) minmax(0, 1.15fr);
      align-items: start;
    }

    .capture-grid {
      grid-template-columns: minmax(0, 1fr);
      max-width: var(--form-max-width);
    }

    .capture-card {
      background: linear-gradient(165deg, #ffffff 0%, #f8fafc 55%, #f1f5f9 100%);
      border: 1px solid var(--line-strong);
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06), 0 16px 40px rgba(15, 23, 42, 0.07);
    }

    .capture-card .hint {
      margin-bottom: 2px;
    }

    input.field-money {
      text-align: right;
      font-variant-numeric: tabular-nums;
    }

    .table-money {
      text-align: right;
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }

    .page {
      display: none;
    }

    .page.active {
      display: block;
    }

    .card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: var(--radius-lg);
      padding: var(--pad-card) var(--pad-card) var(--pad-card-block-end);
      box-shadow: var(--shadow);
      min-width: 0;
    }

    .card:has(.subpage-buttons) {
      background: linear-gradient(180deg, #ffffff 0%, var(--bg-elevated) 100%);
      border-color: var(--line-strong);
    }

    .card h3 {
      margin: 0 0 6px;
      font-size: 1.05rem;
      font-weight: 800;
      color: var(--corp-navy);
      letter-spacing: -0.02em;
      padding-left: 12px;
      border-left: 4px solid var(--brand);
      line-height: 1.35;
    }

    .card h4 {
      margin: 0 0 8px;
      font-size: 0.95rem;
      font-weight: 800;
      color: var(--text);
    }

    .hint,
    .meta {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
      font-weight: 700;
    }

    form > .form-callout {
      margin: 0 0 var(--space-3);
    }

    .stat {
      padding: 16px 18px;
      border-radius: var(--radius-md);
      background: var(--card);
      border: 1px solid var(--line);
      box-shadow: var(--shadow);
    }

    .stat strong {
      display: block;
      font-size: 26px;
      margin-bottom: 4px;
      font-weight: 800;
      color: var(--brand);
    }

    .stat div {
      font-weight: 800;
    }

    form,
    .contacto-capture {
      margin-top: var(--space-4);
      display: grid;
      gap: var(--gap-form);
    }

    .card form {
      max-width: var(--form-max-width);
    }

    .two-col {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: var(--gap-form);
      align-items: start;
    }

    .two-col > .span-2 {
      grid-column: 1 / -1;
    }

    .three-col {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: var(--gap-form);
      align-items: start;
    }

    .three-col .check-row {
      align-self: end;
      margin-bottom: 2px;
    }

    label {
      display: grid;
      gap: var(--label-gap);
      font-size: 13px;
      font-weight: 800;
      color: #334155;
      font-synthesis: weight;
    }

    label input:not([type="checkbox"]):not([type="radio"]),
    label textarea,
    label select {
      font-weight: 800;
      font-size: 15px;
      color: var(--text);
      font-synthesis: weight;
    }

    input, textarea, select, button {
      font: inherit;
    }

    input:not([type="checkbox"]):not([type="radio"]),
    textarea,
    select {
      font-weight: 800;
      font-synthesis: weight;
    }

    input, textarea, select {
      width: 100%;
      max-width: 100%;
      padding: 10px 12px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--line);
      background: #fff;
      color: var(--text);
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }

    input::placeholder,
    textarea::placeholder {
      font-weight: 800;
      opacity: 0.85;
    }

    input:hover,
    textarea:hover,
    select:hover {
      border-color: var(--line-strong);
    }

    input:focus,
    textarea:focus,
    select:focus {
      outline: none;
      border-color: var(--brand);
      box-shadow: 0 0 0 3px rgba(11, 110, 173, 0.2);
    }

    select[data-catalog] {
      border-left: 3px solid rgba(11, 110, 173, 0.4);
      padding-left: 11px;
      background: linear-gradient(90deg, rgba(11, 110, 173, 0.04) 0%, #fff 12px);
    }

    textarea {
      min-height: 88px;
      resize: vertical;
    }

    form > button[type="submit"] {
      justify-self: start;
      margin-top: var(--space-1);
      min-width: 200px;
      padding: 11px 22px;
      letter-spacing: 0.02em;
    }

    .toolbar form > button[type="submit"],
    .toolbar-actions button[type="submit"] {
      min-width: auto;
      margin-top: 0;
    }

    .check-row {
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--text);
      font-size: 14px;
      font-weight: 800;
      text-transform: none;
      letter-spacing: normal;
      font-synthesis: weight;
    }

    .check-row input {
      width: auto;
      padding: 0;
      accent-color: var(--brand);
    }

    button {
      border: none;
      border-radius: var(--radius-sm);
      padding: 10px 18px;
      background: var(--brand);
      color: #fff;
      cursor: pointer;
      font-weight: 800;
      font-size: 14px;
      transition: background 0.15s ease, transform 0.05s ease;
      font-synthesis: weight;
    }

    button:hover {
      background: var(--brand-dark);
    }

    button:active {
      transform: translateY(1px);
    }

    .message {
      margin-top: 12px;
      min-height: 22px;
      font-size: 14px;
      font-weight: 800;
    }

    .message.ok { color: var(--ok); }
    .message.error { color: var(--error); }

    .hidden {
      display: none;
    }

    .toolbar {
      margin-top: var(--gap-form);
      padding: var(--space-4);
      border-radius: var(--radius-md);
      border: 1px solid var(--line);
      background: var(--bg-elevated);
      display: grid;
      gap: var(--gap-form);
    }

    .toolbar h4 {
      margin: 0 0 4px;
      color: var(--corp-navy);
      font-weight: 800;
    }

    .filtro-busqueda-modo {
      margin-bottom: var(--gap-form);
      padding: var(--space-2) var(--space-3);
      border-radius: var(--radius-sm);
      background: rgba(11, 110, 173, 0.06);
      border: 1px solid rgba(11, 110, 173, 0.15);
    }

    .filtro-busqueda-modo label {
      max-width: min(100%, 40rem);
    }

    .filtro-busqueda-modo select {
      font-size: 14px;
    }

    .capture-section-title {
      margin: 0 0 8px;
      font-size: 15px;
      font-weight: 800;
      color: var(--corp-navy);
    }

    .contacto-table-wrap {
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid var(--line);
    }

    .toolbar-actions,
    .row-actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
    }

    .module-subpage-head {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px 16px;
    }

    .module-subpage-head > div:first-child {
      min-width: min(100%, 240px);
      flex: 1 1 auto;
    }

    .module-subpage-head .hint {
      margin-top: 6px;
    }

    .module-subpage-head .open-manual-btn {
      flex: 0 0 auto;
      align-self: center;
    }

    .subpage-buttons {
      display: flex;
      gap: var(--space-2);
      flex-wrap: wrap;
      margin-top: var(--gap-form);
    }

    .subpage-buttons .subpage-button {
      flex: 1 1 160px;
      min-width: min(140px, 100%);
      text-align: center;
      justify-content: center;
    }

    .subpage-button {
      background: #fff;
      color: var(--text);
      border: 1px solid var(--line-strong);
      font-weight: 800;
      font-synthesis: weight;
    }

    .subpage-button:hover {
      background: var(--bg-elevated);
      border-color: var(--brand);
      color: var(--corp-navy);
    }

    .subpage-button.active {
      background: var(--brand);
      color: #fff;
      border-color: var(--brand-dark);
    }

    .secondary-button {
      background: #fff;
      color: var(--text);
      border: 1px solid var(--line-strong);
      font-weight: 800;
      font-synthesis: weight;
    }

    .secondary-button:hover {
      background: var(--bg-elevated);
      border-color: var(--brand);
    }

    .small-button {
      padding: 7px 11px;
      font-size: 13px;
      font-weight: 800;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: var(--gap-form);
      font-size: 13px;
      background: #fff;
      border-radius: var(--radius-md);
      overflow: hidden;
      border: 1px solid var(--line);
    }

    th, td {
      text-align: left;
      padding: 11px 12px;
      border-bottom: 1px solid var(--line);
      vertical-align: middle;
      font-weight: 800;
      font-synthesis: weight;
    }

    tbody tr:nth-child(even) {
      background: #fafbfc;
    }

    tbody tr:hover {
      background: #f0f7fc;
    }

    th {
      color: var(--corp-navy);
      font-weight: 800;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
      border-bottom: 2px solid var(--line);
    }

    .pill {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      background: var(--brand-soft);
      color: var(--brand-dark);
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }

    .timeline-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: var(--gap-grid);
    }

    .summary-list {
      margin: 0;
      padding-left: 18px;
      color: var(--muted);
      line-height: 1.55;
    }

    .manual-doc {
      max-width: 52rem;
    }

    .manual-interface {
      max-width: none;
      grid-column: 1 / -1;
    }

    .manual-interface-head {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-start;
      justify-content: space-between;
      gap: 10px 16px;
      margin-bottom: 4px;
    }

    .manual-interface-head h3 {
      margin-bottom: 0;
    }

    .manual-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--brand-dark);
      background: var(--brand-soft);
      border: 1px solid rgba(11, 110, 173, 0.2);
      white-space: nowrap;
    }

    .manual-interface-body {
      display: grid;
      grid-template-columns: minmax(200px, 260px) minmax(0, 1fr);
      gap: var(--gap-grid);
      align-items: start;
      margin-top: 12px;
      min-height: 0;
    }

    .manual-toc {
      position: sticky;
      top: 12px;
      max-height: min(72vh, calc(100vh - 200px));
      overflow: auto;
      padding: 12px 14px;
      border-radius: var(--radius-md);
      border: 1px solid var(--line);
      background: linear-gradient(180deg, var(--bg-elevated) 0%, #ffffff 100%);
      box-shadow: 0 1px 0 rgba(15, 23, 42, 0.04);
    }

    .manual-toc-title {
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 10px;
    }

    .manual-toc a {
      display: block;
      padding: 7px 8px;
      margin: 2px 0;
      border-radius: var(--radius-sm);
      font-size: 13px;
      font-weight: 600;
      color: var(--text);
      line-height: 1.35;
      border: 1px solid transparent;
      transition: background 0.12s ease, border-color 0.12s ease;
    }

    .manual-toc a:hover {
      background: rgba(11, 110, 173, 0.08);
      border-color: rgba(11, 110, 173, 0.12);
      text-decoration: none;
    }

    .manual-scroll {
      max-height: min(72vh, calc(100vh - 200px));
      overflow: auto;
      overflow-x: hidden;
      padding: 4px 6px 20px 4px;
      border-radius: var(--radius-md);
      border: 1px solid var(--line-strong);
      background: var(--card);
      scroll-behavior: smooth;
    }

    .manual-scroll:focus {
      outline: 2px solid rgba(11, 110, 173, 0.35);
      outline-offset: 2px;
    }

    .manual-doc h4 {
      margin: 1.1rem 0 0.4rem;
      font-size: 0.98rem;
      color: var(--corp-navy);
      scroll-margin-top: 14px;
    }

    .manual-scroll > .manual-note:first-child {
      margin-top: 0;
    }

    .manual-scroll h4:first-of-type {
      margin-top: 0.15rem;
    }

    .manual-p {
      margin: 0.35rem 0 0.55rem;
      color: var(--muted);
      line-height: 1.55;
      font-size: 14px;
    }

    .manual-doc .summary-list {
      color: var(--text);
    }

    .manual-doc .summary-list strong {
      color: var(--corp-navy);
    }

    .manual-doc h5 {
      margin: 0.75rem 0 0.25rem;
      font-size: 0.88rem;
      font-weight: 600;
      color: var(--muted);
    }

    .manual-doc .manual-note {
      margin: 0.5rem 0 0.75rem;
      padding: 0.65rem 0.85rem;
      border-left: 3px solid var(--corp-teal, #0d9488);
      background: rgba(13, 148, 136, 0.06);
      border-radius: 0 6px 6px 0;
      font-size: 13px;
      line-height: 1.5;
      color: var(--text);
    }

    @media (max-width: 900px) {
      .manual-interface-body {
        grid-template-columns: 1fr;
      }

      .manual-toc {
        position: static;
        max-height: 220px;
      }

      .manual-scroll {
        max-height: min(58vh, 520px);
      }
    }

    @media (max-width: 1120px) {
      .app-shell {
        grid-template-columns: 1fr;
      }

      .sidebar {
        position: static;
        height: auto;
      }

      .split {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 860px) {
      .two-col,
      .three-col {
        grid-template-columns: 1fr;
      }

      .two-col > .span-2 {
        grid-column: 1;
      }

      .main {
        padding: var(--space-4) var(--space-3) 24px;
      }
    }
  </style>
</head>
<body>
  <noscript>
    <div style="margin:0;padding:14px 18px;background:#fef2f2;border-bottom:2px solid #fecaca;color:#991b1b;font-family:system-ui,sans-serif;">
      Este panel necesita <strong>JavaScript</strong> activado para cambiar de modulo. Activalo en el navegador y recarga.
      Puedes usar la API en <a href="/docs">/docs</a> mientras tanto.
    </div>
  </noscript>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <h1>__PROJECT_NAME__</h1>
        <p>Panel simple con menu lateral para trabajar un modulo a la vez.</p>
        <p class="sidebar-url-hint">Usa la URL <strong>/ui</strong> para este panel. El manual de cumplimiento es otra pagina.</p>
      </div>

      <div class="nav-group">
        <div class="nav-title">General</div>
        <button type="button" class="nav-button active" data-page="inicio">
          Inicio
          <small>Resumen rapido y accesos</small>
        </button>
      </div>

      <div class="nav-group">
        <div class="nav-title">Catalogos</div>
        <button type="button" class="nav-button" data-page="clientes">
          Clientes
          <small>Alta y listado</small>
        </button>
        <button type="button" class="nav-button" data-page="transportistas">
          Transportistas
          <small>Proveedores de transporte</small>
        </button>
        <button type="button" class="nav-button" data-page="viajes">
          Viajes
          <small>Planeacion</small>
        </button>
        <button type="button" class="nav-button" data-page="fletes">
          Fletes
          <small>Costo y vinculacion</small>
        </button>
        <button type="button" class="nav-button" data-page="facturas">
          Facturas
          <small>Simulacion administrativa de cobro</small>
        </button>
        <button type="button" class="nav-button" data-page="tarifas">
          Tarifas
          <small>Reglas de cotizacion</small>
        </button>
        <button type="button" class="nav-button" data-page="tarifas-compra">
          Tarifas compra
          <small>Compra negociada por transportista</small>
        </button>
        <button type="button" class="nav-button" data-page="operadores">
          Operadores
          <small>Choferes de transporte</small>
        </button>
        <button type="button" class="nav-button" data-page="unidades">
          Unidades
          <small>Vehiculos y economicos</small>
        </button>
      </div>

      <div class="nav-group">
        <div class="nav-title">Operacion</div>
        <button type="button" class="nav-button" data-page="asignaciones">
          Asignaciones
          <small>Operador + unidad + viaje</small>
        </button>
        <button type="button" class="nav-button" data-page="gastos">
          Gastos viaje
          <small>Costos reales por flete</small>
        </button>
        <button type="button" class="nav-button" data-page="despachos">
          Despachos
          <small>Programacion operativa</small>
        </button>
        <a
          class="sidebar-manual-link"
          href="/manual/cumplimiento"
          target="_blank"
          rel="noopener"
        >
          Manual cumplimiento
          <small>Legal MX (imprimir PDF)</small>
        </a>
        <button type="button" class="nav-button" data-page="seguimiento">
          Seguimiento
          <small>Salida, entrega, cierre</small>
        </button>
      </div>

      <div class="sidebar-note">
        Si algo avanzado no aparece aqui, puedes usar <a href="/docs" style="color:#fff;text-decoration:underline;">Swagger</a> como respaldo.
      </div>
    </aside>

    <main class="main">
      <div id="catalog-refresh-banner" class="catalog-refresh-banner" hidden></div>
      <div class="topbar">
        <div>
          <h2 id="page-title">Inicio</h2>
          <p id="page-description">Resumen del sistema y accesos a cada modulo sin mezclar pantallas.</p>
        </div>
        <div class="meta">La API key se usa en segundo plano desde <code>.env</code>.</div>
      </div>

      <section class="banner">
        <div><strong>Modo guiado</strong> ahora ves una sola seccion a la vez para evitar confusion.</div>
        <div class="meta">Abajo puedes cambiar de modulo cuando quieras.</div>
      </section>

      <section class="page active" id="page-inicio">
        <div class="status-grid" id="stats"></div>
        <div class="grid">
          <article class="card">
            <h3>Como usarlo</h3>
            <ol class="summary-list">
              <li><strong>Catalogos comerciales:</strong> clientes, transportistas, tarifas de venta y tarifas de compra (cuando apliquen).</li>
              <li><strong>Planeacion:</strong> viajes; luego <strong>fletes</strong> (cotizar venta/compra desde el formulario si hay tarifas).</li>
              <li><strong>Orden de servicio:</strong> en este panel suele ser <strong>consulta</strong> (Fletes → Ordenes de servicio); altas completas pueden hacerse por API (<a href="/docs">/docs</a>).</li>
              <li><strong>Operacion:</strong> operadores, unidades, <strong>asignacion</strong> (operador + unidad + viaje), <strong>despacho</strong>.</li>
              <li><strong>Seguimiento:</strong> salida, evento en ruta, entrega, cierre o cancelacion (registro hacia adelante).</li>
              <li><strong>Cierre economico:</strong> gastos de viaje por flete; <strong>facturas</strong> administrativas (no timbrado SAT en este modulo).</li>
            </ol>
            <p class="hint" style="margin:10px 0 0 0;">Lo que no se guarda con el boton correspondiente <strong>no queda en el servidor</strong> (no hay borradores automaticos en el navegador). Guarde por pasos antes de cambiar de modulo o recargar.</p>
          </article>
          <article class="card">
            <h3>Estado actual</h3>
            <div class="hint">Este panel consume la misma API que ya validaste. Si algo falla, el mensaje del formulario te dira la razon.</div>
            <div id="health-conn-info" class="hint" style="margin-top:12px;">Leyendo conexion de datos desde <a href="/health">/health</a>…</div>
            <div class="meta" style="margin-top:10px;">Si necesitas consultar raw endpoints, tienes disponible <a href="/docs">/docs</a>.</div>
          </article>
          <article class="card">
            <h3>Documentación</h3>
            <div class="hint">Los manuales integrados están en cada módulo del menú lateral: pestaña <strong>Manual</strong> o botón <strong>Abrir manual</strong> (índice y visor en pantalla).</div>
          </article>
        </div>
      </section>

      <section class="page" id="page-clientes">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de clientes</h3>
              <div class="hint">Trabaja una parte del cliente a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="cliente-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons" id="cliente-subpage-buttons">
            <button type="button" class="subpage-button active" data-cliente-tab="alta">Nuevo cliente</button>
            <button type="button" class="subpage-button" data-cliente-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-cliente-tab="contactos">Contactos</button>
            <button type="button" class="subpage-button" data-cliente-tab="domicilios">Domicilios</button>
            <button type="button" class="subpage-button" data-cliente-tab="condiciones">Condiciones</button>
            <button type="button" class="subpage-button" data-cliente-tab="manual">Manual</button>
          </div>
        </div>
        <div class="grid">
          <article class="card" data-cliente-tab-panel="alta">
            <h3>Nuevo cliente</h3>
            <div class="hint">Ficha general del cliente para venta, operacion y facturacion.</div>
            <form id="cliente-form">
              <label>Razon social
                <input name="razon_social" required />
              </label>
              <div class="two-col">
                <label>Nombre comercial
                  <input name="nombre_comercial" />
                </label>
                <label>Tipo cliente
                  <select name="tipo_cliente">
                    <option value="embarcador">embarcador</option>
                    <option value="consignatario">consignatario</option>
                    <option value="pagador">pagador</option>
                    <option value="corporativo">corporativo</option>
                    <option value="mixto" selected>mixto</option>
                  </select>
                </label>
              </div>
              <div class="three-col">
                <label>RFC
                  <input name="rfc" />
                </label>
                <label>Sector
                  <input name="sector" />
                </label>
                <label>Origen prospecto
                  <input name="origen_prospecto" placeholder="referido, web, directo..." />
                </label>
              </div>
              <div class="three-col">
                <label>Email general
                  <input name="email" type="email" />
                </label>
                <label>Telefono general
                  <input name="telefono" />
                </label>
                <label>Sitio web
                  <input name="sitio_web" />
                </label>
              </div>
              <label>Domicilio fiscal
                <textarea name="direccion"></textarea>
              </label>
              <div class="two-col">
                <label>Notas operativas
                  <textarea name="notas_operativas"></textarea>
                </label>
                <label>Notas comerciales
                  <textarea name="notas_comerciales"></textarea>
                </label>
              </div>
              <label class="check-row">
                <input name="activo" type="checkbox" checked />
                Cliente activo
              </label>
              <button type="submit">Guardar cliente</button>
            </form>
            <div id="cliente-message" class="message"></div>
          </article>
          <article class="card hidden" data-cliente-tab-panel="consulta">
            <h3>Listado de clientes</h3>
            <div class="toolbar">
              <h4>Consultar clientes</h4>
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <form id="cliente-filter-form">
                <div class="two-col">
                  <label>Buscar por razon social
                    <input id="cliente-filter-buscar" name="buscar" list="cliente-filter-buscar-dl" placeholder="Nombre, comercial o RFC" autocomplete="off" />
                  </label>
                  <label>Estatus
                    <select id="cliente-filter-activo" name="activo">
                      <option value="">Todos</option>
                      <option value="true">Activos</option>
                      <option value="false">Inactivos</option>
                    </select>
                  </label>
                </div>
                <datalist id="cliente-filter-buscar-dl"></datalist>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="cliente-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="clientes-table"></div>
            <div id="cliente-edit-panel" class="toolbar hidden">
              <h4>Editar cliente</h4>
              <p class="hint">
                Horario de carga, horario de descarga e instrucciones de acceso <strong>no</strong> van aquí: son datos de cada
                <strong>domicilio operativo</strong> (carga, descarga, fiscal, etc.). Captúralos en la subopción
                <strong>Domicilios</strong> (barra superior de este módulo), eligiendo el cliente y luego <strong>Editar</strong> en la fila del domicilio.
              </p>
              <div class="toolbar-actions">
                <button type="button" id="cliente-edit-open-contactos" class="secondary-button">Ir a Contactos de este cliente</button>
                <button type="button" id="cliente-edit-open-domicilios" class="secondary-button">Ir a Domicilios de este cliente</button>
              </div>
              <form id="cliente-edit-form">
                <input name="id" type="hidden" />
                <label>Razon social
                  <input name="razon_social" required />
                </label>
                <div class="two-col">
                  <label>Nombre comercial
                    <input name="nombre_comercial" />
                  </label>
                  <label>Tipo cliente
                    <select name="tipo_cliente">
                      <option value="embarcador">embarcador</option>
                      <option value="consignatario">consignatario</option>
                      <option value="pagador">pagador</option>
                      <option value="corporativo">corporativo</option>
                      <option value="mixto">mixto</option>
                    </select>
                  </label>
                </div>
                <div class="three-col">
                  <label>RFC
                    <input name="rfc" />
                  </label>
                  <label>Sector
                    <input name="sector" />
                  </label>
                  <label>Origen prospecto
                    <input name="origen_prospecto" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Email general
                    <input name="email" type="email" />
                  </label>
                  <label>Telefono general
                    <input name="telefono" />
                  </label>
                  <label>Sitio web
                    <input name="sitio_web" />
                  </label>
                </div>
                <label>Domicilio fiscal
                  <textarea name="direccion"></textarea>
                </label>
                <div class="two-col">
                  <label>Notas operativas
                    <textarea name="notas_operativas"></textarea>
                  </label>
                  <label>Notas comerciales
                    <textarea name="notas_comerciales"></textarea>
                  </label>
                </div>
                <label class="check-row">
                  <input name="activo" type="checkbox" />
                  Cliente activo
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="cliente-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="cliente-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden" data-cliente-tab-panel="contactos">
            <h3>Contactos del cliente</h3>
            <div class="hint">Registra contactos de trafico, facturacion, cobranza o almacen.</div>
            <div class="hint">Enter pasa al siguiente campo; al terminar, Enter con foco en Guardar contacto guarda.</div>
            <div class="hint">Los contactos ya guardados aparecen en la <strong>tabla de abajo</strong>. El bloque superior es solo para <strong>dar de alta</strong> un contacto nuevo (por eso los campos suelen ir vacíos).</div>
            <h4 class="capture-section-title">Nuevo contacto</h4>
            <div id="cliente-contacto-form" class="contacto-capture" role="group" aria-label="Nuevo contacto del cliente">
              <label>Cliente
                <select id="cliente-contacto-cliente" name="cliente_id" required></select>
              </label>
              <div id="cliente-contacto-summary" class="hint"></div>
              <div class="two-col">
                <label>Nombre
                  <input id="cliente-contacto-nombre" name="nombre" required autocomplete="off" />
                </label>
                <label>Area
                  <input id="cliente-contacto-area" name="area" placeholder="trafico, cobranza..." autocomplete="off" />
                </label>
              </div>
              <div class="two-col">
                <label>Puesto
                  <input id="cliente-contacto-puesto" name="puesto" autocomplete="off" />
                </label>
                <label>Email
                  <input id="cliente-contacto-email" name="email" type="email" autocomplete="off" />
                </label>
              </div>
              <div class="three-col">
                <label>Telefono
                  <input id="cliente-contacto-telefono" name="telefono" autocomplete="off" />
                </label>
                <label>Extension
                  <input id="cliente-contacto-extension" name="extension" autocomplete="off" />
                </label>
                <label>Celular
                  <input id="cliente-contacto-celular" name="celular" autocomplete="off" />
                </label>
              </div>
              <div class="two-col">
                <label class="check-row">
                  <input id="cliente-contacto-principal" name="principal" type="checkbox" />
                  Contacto principal
                </label>
                <label class="check-row">
                  <input id="cliente-contacto-activo" name="activo" type="checkbox" checked />
                  Contacto activo
                </label>
              </div>
            </div>
            <div class="toolbar-actions">
              <button type="button" id="cliente-contacto-guardar" data-primary-action="save">Guardar contacto</button>
              <button type="button" id="cliente-contacto-cancel-clear" class="secondary-button">Cancelar y limpiar</button>
            </div>
            <div id="cliente-contacto-message" class="message"></div>
            <div id="cliente-contactos-table" class="contacto-table-wrap"></div>
            <div id="cliente-contacto-edit-panel" class="toolbar hidden" aria-hidden="true">
              <h4>Editar contacto</h4>
              <p class="hint" style="margin:0 0 8px">Este bloque solo aparece al pulsar <strong>Editar</strong> en la tabla. No es un segundo alta: usa arriba <strong>Nuevo contacto</strong> para agregar.</p>
              <form id="cliente-contacto-edit-form" onsubmit="return false;">
                <input name="id" type="hidden" />
                <input type="hidden" id="cliente-contacto-path-cliente" />
                <label>Filtrar cliente (escribe para acortar la lista)
                  <input type="search" id="cliente-contacto-edit-buscar" placeholder="Razon social, nombre comercial o RFC" autocomplete="off" />
                </label>
                <label>Cliente
                  <select id="cliente-contacto-edit-cliente" name="cliente_id" required></select>
                </label>
                <div class="hint">Abre la lista o escribe arriba para filtrar. Si cambias de cliente y guardas, el contacto pasa a ese cliente.</div>
                <div class="two-col">
                  <label>Nombre
                    <input name="nombre" required />
                  </label>
                  <label>Area
                    <input name="area" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Puesto
                    <input name="puesto" />
                  </label>
                  <label>Email
                    <input name="email" type="email" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Telefono
                    <input name="telefono" />
                  </label>
                  <label>Extension
                    <input name="extension" />
                  </label>
                  <label>Celular
                    <input name="celular" />
                  </label>
                </div>
                <div class="two-col">
                  <label class="check-row">
                    <input name="principal" type="checkbox" />
                    Contacto principal
                  </label>
                  <label class="check-row">
                    <input name="activo" type="checkbox" />
                    Contacto activo
                  </label>
                </div>
              </form>
              <div class="toolbar-actions">
                <button type="button" id="cliente-contacto-edit-guardar" data-primary-action="save">Guardar cambios</button>
                <button type="button" id="cliente-contacto-edit-cancel" class="secondary-button">Cancelar</button>
              </div>
              <div id="cliente-contacto-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden" data-cliente-tab-panel="domicilios">
            <h3>Domicilios del cliente</h3>
            <div class="hint">Puntos de carga, descarga, fiscal o sedes del cliente. Aquí se capturan horarios de carga/descarga e instrucciones de acceso por cada domicilio. Para editarlos, elige el cliente y pulsa <strong>Editar</strong> en la tabla.</div>
            <form id="cliente-domicilio-form">
              <label>Filtrar cliente (escribe para acortar la lista)
                <input type="search" id="cliente-domicilio-buscar" placeholder="Razon social, nombre comercial o RFC" autocomplete="off" />
              </label>
              <label>Cliente
                <select id="cliente-domicilio-cliente" name="cliente_id" required></select>
              </label>
              <div class="hint">El buscador acorta la lista; si no ves al cliente, borra el texto o cambia la busqueda.</div>
              <div id="cliente-domicilio-summary" class="hint"></div>
              <div class="two-col">
                <label>Tipo domicilio
                  <input name="tipo_domicilio" placeholder="fiscal, carga, descarga..." required />
                </label>
                <label>Nombre sede
                  <input name="nombre_sede" required />
                </label>
              </div>
              <label>Direccion completa
                <textarea name="direccion_completa" required></textarea>
              </label>
              <div class="three-col">
                <label>Municipio
                  <input name="municipio" />
                </label>
                <label>Estado
                  <input name="estado" />
                </label>
                <label>Codigo postal
                  <input name="codigo_postal" />
                </label>
              </div>
              <div class="two-col">
                <label>Horario carga
                  <input name="horario_carga" />
                </label>
                <label>Horario descarga
                  <input name="horario_descarga" />
                </label>
              </div>
              <label>Instrucciones acceso
                <textarea name="instrucciones_acceso"></textarea>
              </label>
              <label class="check-row">
                <input name="activo" type="checkbox" checked />
                Domicilio activo
              </label>
              <button type="submit">Guardar domicilio</button>
            </form>
            <div id="cliente-domicilio-message" class="message"></div>
            <div id="cliente-domicilios-table"></div>
            <div id="cliente-domicilio-edit-panel" class="toolbar hidden">
              <h4>Editar domicilio</h4>
              <form id="cliente-domicilio-edit-form">
                <input name="id" type="hidden" />
                <input name="cliente_id" type="hidden" />
                <label>Cliente
                  <input name="cliente_label" readonly />
                </label>
                <div class="two-col">
                  <label>Tipo domicilio
                    <input name="tipo_domicilio" required />
                  </label>
                  <label>Nombre sede
                    <input name="nombre_sede" required />
                  </label>
                </div>
                <label>Direccion completa
                  <textarea name="direccion_completa" required></textarea>
                </label>
                <div class="three-col">
                  <label>Municipio
                    <input name="municipio" />
                  </label>
                  <label>Estado
                    <input name="estado" />
                  </label>
                  <label>Codigo postal
                    <input name="codigo_postal" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Horario carga
                    <input name="horario_carga" />
                  </label>
                  <label>Horario descarga
                    <input name="horario_descarga" />
                  </label>
                </div>
                <label>Instrucciones acceso
                  <textarea name="instrucciones_acceso"></textarea>
                </label>
                <label class="check-row">
                  <input name="activo" type="checkbox" />
                  Domicilio activo
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="cliente-domicilio-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="cliente-domicilio-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden" data-cliente-tab-panel="condiciones">
            <h3>Condiciones comerciales</h3>
            <div class="hint">Credito, moneda y requisitos para facturacion u operacion.</div>
            <div class="hint">Enter en un campo pasa al siguiente; en observaciones Enter hace salto de linea. Guarde con el boton al final.</div>
            <form id="cliente-condicion-form">
              <label>Cliente
                <select id="cliente-condicion-cliente" name="cliente_id" required></select>
              </label>
              <div id="cliente-condicion-selected-summary" class="hint"></div>
              <div class="three-col">
                <label>Dias credito
                  <input name="dias_credito" type="number" min="0" step="1" inputmode="numeric" title="Solo numeros enteros (sin decimales)" />
                </label>
                <label>Limite credito
                  <input name="limite_credito" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                </label>
                <label>Moneda preferida
                  <input name="moneda_preferida" value="MXN" maxlength="3" />
                </label>
              </div>
              <div class="two-col">
                <label>Forma pago
                  <input name="forma_pago" placeholder="transferencia, PPD..." />
                </label>
                <label>Uso CFDI
                  <input name="uso_cfdi" placeholder="G03, S01..." />
                </label>
              </div>
              <div class="three-col">
                <label class="check-row">
                  <input name="requiere_oc" type="checkbox" />
                  Requiere OC
                </label>
                <label class="check-row">
                  <input name="requiere_cita" type="checkbox" />
                  Requiere cita
                </label>
                <label class="check-row">
                  <input name="bloqueado_credito" type="checkbox" />
                  Bloqueado por credito
                </label>
              </div>
              <label>Observaciones credito
                <textarea name="observaciones_credito"></textarea>
              </label>
              <button type="submit">Guardar condiciones</button>
            </form>
            <div id="cliente-condicion-message" class="message"></div>
            <div id="cliente-condicion-summary" class="hint"></div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-cliente-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Clientes</h3>
              <span class="manual-badge" title="Contenido completo en esta pantalla">Documentación en pantalla</span>
            </div>
            <div class="hint">Documento de apoyo integrado en la aplicación. La información se registra en el servidor a través de la API; el tono de esta guía es formal en el marco general y operativo en los procedimientos. Use el índice lateral para saltar entre secciones; el texto largo se desplaza dentro del panel derecho.</div>

            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-clientes-toc" aria-label="Índice del manual de clientes">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-clientes-1">1. Objetivo del módulo</a>
                <a href="#manual-clientes-2">2. Subopciones</a>
                <a href="#manual-clientes-3">3. Nuevo cliente</a>
                <a href="#manual-clientes-4">4. Consultar y editar</a>
                <a href="#manual-clientes-5">5. Contactos</a>
                <a href="#manual-clientes-6">6. Domicilios</a>
                <a href="#manual-clientes-7">7. Condiciones comerciales</a>
                <a href="#manual-clientes-8">8. Ejemplos de texto</a>
                <a href="#manual-clientes-9">9. Preguntas frecuentes</a>
                <a href="#manual-clientes-10">10. Mensajes y errores</a>
                <a href="#manual-clientes-11">11. Referencia técnica</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="clientes" tabindex="0" role="region" aria-label="Texto del manual de clientes">
            <div class="manual-note">
              <strong>Secuencia operativa recomendada:</strong> (1) Registrar la ficha en <strong>Nuevo cliente</strong>. (2) Capturar <strong>Contactos</strong> y <strong>Domicilios</strong> según corresponda al negocio. (3) Registrar <strong>Condiciones</strong> comerciales. (4) Utilizar <strong>Consultar y editar</strong> para auditoría o correcciones puntuales de la ficha.
            </div>

            <h4 id="manual-clientes-1">1. Objetivo del módulo</h4>
            <p class="manual-p">El módulo tiene por finalidad centralizar la información maestra del cliente (incluidos roles tales como embarcador o pagador), así como los contactos de trabajo, los domicilios operativos y las condiciones de crédito y facturación. La división en subopciones permite mantener la captura estructurada y reducir errores de mezcla de datos.</p>

            <h4 id="manual-clientes-2">2. Subopciones (barra superior)</h4>
            <ul class="summary-list">
              <li><strong>Nuevo cliente:</strong> registro de la ficha general: razón social, tipo, RFC, datos corporativos, domicilio fiscal en texto libre y notas.</li>
              <li><strong>Consultar y editar:</strong> búsqueda, visualización tabular y edición del registro seleccionado.</li>
              <li><strong>Contactos:</strong> personas de contacto para tráfico, facturación, cobranza, almacén u otras áreas.</li>
              <li><strong>Domicilios:</strong> ubicaciones operativas con dirección, horarios e instrucciones de acceso.</li>
              <li><strong>Condiciones:</strong> plazos y límites de crédito, moneda, forma de pago, uso CFDI e indicadores de orden de compra, cita y bloqueo.</li>
              <li><strong>Manual:</strong> la presente guía.</li>
            </ul>
            <p class="manual-p"><strong>Sincronización entre pestañas:</strong> al modificar el cliente seleccionado en <strong>Contactos</strong>, <strong>Domicilios</strong> o <strong>Condiciones</strong>, la aplicación replica la misma selección en los selectores de las otras dos subopciones, de modo que pueda continuar el trabajo sobre un mismo cliente sin volver a elegirlo manualmente.</p>

            <h4 id="manual-clientes-3">3. Nuevo cliente</h4>
            <p class="manual-p">El único campo obligatorio es <strong>Razón social</strong>. Se recomienda completar el resto de acuerdo con las políticas internas de ventas, operaciones y facturación.</p>
            <h5>Descripción de campos</h5>
            <ul class="summary-list">
              <li><strong>Nombre comercial:</strong> denominación habitual en operación o en documentos no fiscales.</li>
              <li><strong>Tipo cliente:</strong> clasificación operativa (embarcador, consignatario, pagador, corporativo, mixto). Valor predeterminado: mixto.</li>
              <li><strong>RFC, sector, origen prospecto:</strong> identificación fiscal y, en su caso, seguimiento del origen del prospecto.</li>
              <li><strong>Correo electrónico, teléfono y sitio web (generales):</strong> datos a nivel empresa; no sustituyen el detalle de personas de contacto en la subopción Contactos.</li>
              <li><strong>Domicilio fiscal:</strong> texto para fines de facturación; las ubicaciones operativas múltiples se registran en Domicilios.</li>
              <li><strong>Notas operativas y comerciales:</strong> información interna acordada para operación o fuerza de ventas.</li>
              <li><strong>Cliente activo:</strong> si se desactiva, el registro podrá excluirse por filtro de inactivos y dejará de considerarse en los flujos habituales.</li>
            </ul>
            <p class="manual-p"><strong>Procedimiento:</strong> capture la información y pulse <strong>Guardar cliente</strong>. Verifique el mensaje inmediatamente debajo del formulario: confirmará el resultado o mostrará la causa de rechazo devuelta por el servidor.</p>

            <h4 id="manual-clientes-4">4. Consultar y editar</h4>
            <p class="manual-p">El criterio de búsqueda aplica sobre <strong>razón social</strong>, <strong>nombre comercial</strong> y <strong>RFC</strong>, sin distinción de mayúsculas. El resultado se recalcula de forma automática al escribir en el campo de búsqueda y al cambiar <strong>Estatus</strong> (Todos, Activos, Inactivos). El control <strong>Aplicar filtro</strong> ejecuta la misma actualización para quien prefiera validar el criterio mediante un envío explícito.</p>
            <ul class="summary-list">
              <li><strong>Coincidencia única:</strong> si el filtro deja un solo registro, el panel <strong>Editar cliente</strong> se abre de forma automática con dicho cliente.</li>
              <li><strong>Tabla de resultados:</strong> columnas ID, razón social, nombre comercial, tipo, RFC, conteo de contactos y domicilios, estatus y acción <strong>Editar</strong>.</li>
              <li><strong>Limpiar:</strong> restablece filtros, muestra el universo completo y cierra el panel de edición si estaba visible.</li>
              <li><strong>Edición:</strong> los campos son análogos al alta; confirme con <strong>Guardar cambios</strong> o descarte con <strong>Cancelar</strong>.</li>
            </ul>

            <h4 id="manual-clientes-5">5. Contactos del cliente</h4>
            <p class="manual-p">Bajo el selector aparece un <strong>resumen</strong> del cliente (identificador, razón social, nombre comercial, RFC y conteos). Utilícelo como verificación previa antes de capturar o modificar contactos.</p>
            <ol class="summary-list">
              <li>Seleccione el <strong>Cliente</strong>. El campo <strong>Nombre</strong> del contacto es obligatorio; el resto de campos son opcionales pero se suelen completar para trazabilidad.</li>
              <li>Marque <strong>Contacto principal</strong> y <strong>Contacto activo</strong> conforme a la política de su organización.</li>
              <li>Teclado: la tecla <strong>Enter</strong> avanza al siguiente campo; con el foco en <strong>Guardar contacto</strong>, Enter envía la captura.</li>
              <li><strong>Cancelar y limpiar</strong> descarta la captura en curso sin persistir datos.</li>
              <li>En la grilla, <strong>Editar</strong> abre el panel inferior. Mediante <strong>Filtrar cliente</strong> puede acotar el listado; si modifica el cliente y guarda, el contacto queda <strong>reasignado</strong> al cliente indicado (corrección de error o cambio de cuenta).</li>
              <li><strong>Eliminar</strong> solicita confirmación antes de borrar el registro.</li>
            </ol>

            <h4 id="manual-clientes-6">6. Domicilios</h4>
            <p class="manual-p">Obligatorios: <strong>Cliente</strong>, <strong>Tipo domicilio</strong>, <strong>Nombre sede</strong> y <strong>Dirección completa</strong>. El tipo debe reflejar el uso operativo (por ejemplo fiscal, carga, descarga).</p>
            <ul class="summary-list">
              <li><strong>Municipio, estado, código postal:</strong> completar según requerimientos de reportes o de instructivos de ruta.</li>
              <li><strong>Horarios de carga y descarga:</strong> ventanas acordadas contractualmente o operativamente.</li>
              <li><strong>Instrucciones de acceso:</strong> requisitos de seguridad, citas en caseta, muelle asignado, contacto en planta, EPP, etc.</li>
              <li><strong>Domicilio activo:</strong> desmarcar cuando el punto deje de estar vigente.</li>
              <li><strong>Edición desde la tabla:</strong> el cliente se muestra en solo lectura; ajuste los demás campos y guarde o cancele.</li>
              <li><strong>Eliminar:</strong> requiere confirmación.</li>
            </ul>

            <h4 id="manual-clientes-7">7. Condiciones comerciales</h4>
            <ul class="summary-list">
              <li><strong>Días de crédito y límite de crédito:</strong> valores numéricos no negativos; el límite admite decimales.</li>
              <li><strong>Moneda preferida:</strong> convención habitual de tres caracteres (el formulario sugiere MXN).</li>
              <li><strong>Forma de pago y uso CFDI:</strong> texto libre alineado a catálogos internos y a criterio fiscal; véase la sección 8.</li>
              <li><strong>Requiere OC, Requiere cita, Bloqueado por crédito:</strong> indicadores para operación y cobranza; su efecto en otros módulos depende de las reglas que defina la empresa.</li>
              <li><strong>Observaciones de crédito:</strong> acuerdos especiales, garantías o seguimiento de incidencias.</li>
              <li>Pulse <strong>Guardar condiciones</strong> para persistir la configuración del cliente seleccionado.</li>
            </ul>

            <h4 id="manual-clientes-8">8. Ejemplos de texto (referencia operativa)</h4>
            <p class="manual-p">Los campos citados admiten texto libre. Para uniformar criterios, puede adoptar las convenciones corporativas y, en su defecto, tomar como referencia los ejemplos siguientes, habituales en el entorno fiscal mexicano.</p>
            <h5>Tipo de domicilio</h5>
            <ul class="summary-list">
              <li><strong>Fiscal:</strong> alineado a datos de facturación y RFC.</li>
              <li><strong>Carga o recolección:</strong> origen de mercancía o punto de retiro.</li>
              <li><strong>Descarga o entrega:</strong> destino o muelle de descarga.</li>
              <li><strong>Oficinas o corporativo:</strong> sede administrativa sin movimiento de carga.</li>
              <li><strong>Almacén o cross-dock:</strong> consolidación o transbordo.</li>
            </ul>
            <p class="manual-p">En <strong>Nombre sede</strong> se recomienda una etiqueta breve y única, por ejemplo: Planta Querétaro, CEDIS Guadalajara, Oficinas Ciudad de México.</p>
            <h5>Forma de pago</h5>
            <ul class="summary-list">
              <li>Referencias frecuentes: transferencia electrónica; <strong>PPD</strong> (pago en parcialidades o diferido); <strong>PUE</strong> (pago en una exhibición); cheque nominativo.</li>
              <li>Si aplica complemento de recepción de pagos, el texto debe ser coherente con contabilidad y con los requerimientos del SAT.</li>
            </ul>
            <h5>Uso CFDI</h5>
            <ul class="summary-list">
              <li>Ejemplos de claves de uso frecuentes: <strong>G03</strong> (gastos en general), <strong>G01</strong> (adquisición de mercancías), <strong>I04</strong> (equipo de transporte), <strong>P01</strong> (por definir, cuando aplique), <strong>S01</strong> (sin efectos fiscales, según normativa aplicable).</li>
              <li>La vigencia y el sentido exacto de cada clave deben validarse con el área fiscal y con los catálogos actualizados del SAT.</li>
            </ul>

            <h4 id="manual-clientes-9">9. Preguntas frecuentes</h4>
            <h5>No aparece el cliente en Contactos o Domicilios</h5>
            <p class="manual-p">Verifique que el alta se haya guardado correctamente en <strong>Nuevo cliente</strong> y que el estatus sea coherente con sus filtros (por ejemplo, activo). Si el registro es reciente, recargue la vista o vuelva a entrar al módulo para forzar la actualización del catálogo en pantalla.</p>
            <h5>Relación entre el domicilio fiscal del alta y los registros en Domicilios</h5>
            <p class="manual-p">No son equivalentes por definición. El domicilio fiscal en la ficha general es un campo de texto para facturación; la subopción <strong>Domicilios</strong> permite uno o varios puntos operativos con nombre de sede y detalle estructurado.</p>
            <h5>Uso del indicador «Bloqueado por crédito»</h5>
            <p class="manual-p">Registra una restricción de crédito visible para ventas y operación. La forma en que dicho bloqueo se traduzca en otros procesos (por ejemplo viajes o facturación) depende de las políticas internas de la organización.</p>
            <h5>Reasignación de un contacto a otro cliente</h5>
            <p class="manual-p">Procedimiento: abra <strong>Editar contacto</strong>, seleccione el cliente destino en el listado (use el filtro si el catálogo es extenso) y ejecute <strong>Guardar cambios</strong>. El contacto quedará asociado al nuevo cliente.</p>
            <h5>Apertura automática del panel de edición al filtrar</h5>
            <p class="manual-p">Cuando el criterio de búsqueda produce exactamente un resultado, el sistema abre <strong>Editar cliente</strong> de forma automática. Si existen varias coincidencias, deberá pulsar <strong>Editar</strong> en la fila correspondiente.</p>

            <h4 id="manual-clientes-10">10. Mensajes y errores</h4>
            <p class="manual-p">Los mensajes bajo cada formulario reproducen la respuesta del servidor (operación exitosa, validación de datos o reglas de negocio). Si las tablas permanecen vacías de forma inesperada, verifique la conectividad y el estado del servicio de API.</p>

            <h4 id="manual-clientes-11">11. Referencia técnica</h4>
            <p class="manual-p">Para consultar rutas, esquemas JSON y pruebas interactivas, utilice la documentación Swagger en <a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-transportistas">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de transportistas</h3>
              <div class="hint">Trabaja una parte del transportista a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="transportista-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons" id="transportista-subpage-buttons">
            <button type="button" class="subpage-button" data-transportista-tab="alta">Nuevo transportista</button>
            <button type="button" class="subpage-button active" data-transportista-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-transportista-tab="contactos">Contactos</button>
            <button type="button" class="subpage-button" data-transportista-tab="documentos">Documentos</button>
            <button type="button" class="subpage-button" data-transportista-tab="manual">Manual</button>
          </div>
        </div>
        <div class="grid">
          <article class="card hidden" data-transportista-tab-panel="alta">
            <h3>Nuevo transportista</h3>
            <div class="hint">Maestro del proveedor de transporte con datos fiscales, operativos y comerciales.</div>
            <form id="transportista-form">
              <div class="two-col">
                <label>Razon social
                  <input name="nombre" required />
                </label>
                <label>Nombre comercial
                  <input name="nombre_comercial" />
                </label>
              </div>
              <div class="three-col">
                <label>Tipo transportista
                  <select name="tipo_transportista">
                    <option value="propio">propio</option>
                    <option value="subcontratado" selected>subcontratado</option>
                    <option value="fletero">fletero</option>
                    <option value="aliado">aliado</option>
                  </select>
                </label>
                <label>Tipo persona
                  <select name="tipo_persona">
                    <option value="fisica">fisica</option>
                    <option value="moral" selected>moral</option>
                  </select>
                </label>
                <label>Estatus
                  <select name="estatus">
                    <option value="activo" selected>activo</option>
                    <option value="inactivo">inactivo</option>
                    <option value="bloqueado">bloqueado</option>
                  </select>
                </label>
              </div>
              <div class="three-col">
                <label>RFC
                  <input name="rfc" />
                </label>
                <label>CURP
                  <input name="curp" />
                </label>
                <label>Regimen fiscal
                  <input name="regimen_fiscal" />
                </label>
              </div>
              <div class="three-col">
                <label>Fecha alta
                  <input name="fecha_alta" type="date" />
                </label>
                <label>Nivel confianza
                  <select name="nivel_confianza">
                    <option value="alto">alto</option>
                    <option value="medio" selected>medio</option>
                    <option value="bajo">bajo</option>
                  </select>
                </label>
                <label>Prioridad asignacion
                  <input name="prioridad_asignacion" type="number" min="0" step="1" inputmode="numeric" value="0" title="Solo numeros enteros" />
                </label>
              </div>
              <div class="two-col">
                <label>Contacto principal
                  <input name="contacto" />
                </label>
                <label>Telefono general
                  <input name="telefono" />
                </label>
              </div>
              <div class="three-col">
                <label>Email general
                  <input name="email" type="email" />
                </label>
                <label>Sitio web
                  <input name="sitio_web" />
                </label>
                <label>Codigo postal
                  <input name="codigo_postal" />
                </label>
              </div>
              <div class="three-col">
                <label>Ciudad
                  <input name="ciudad" />
                </label>
                <label>Estado
                  <input name="estado" />
                </label>
                <label>Pais
                  <input name="pais" value="Mexico" />
                </label>
              </div>
              <label>Direccion fiscal
                <textarea name="direccion_fiscal"></textarea>
              </label>
              <label>Direccion operativa
                <textarea name="direccion_operativa"></textarea>
              </label>
              <div class="two-col">
                <label>Notas operativas
                  <textarea name="notas_operativas"></textarea>
                </label>
                <label>Notas comerciales
                  <textarea name="notas_comerciales"></textarea>
                </label>
              </div>
              <div class="two-col">
                <label class="check-row">
                  <input name="blacklist" type="checkbox" />
                  En blacklist
                </label>
                <label class="check-row">
                  <input name="activo" type="checkbox" checked />
                  Transportista activo
                </label>
              </div>
              <button type="submit">Guardar transportista</button>
            </form>
            <div id="transportista-message" class="message"></div>
          </article>
          <article class="card" data-transportista-tab-panel="consulta">
            <h3>Listado de transportistas</h3>
            <div class="toolbar">
              <h4>Consultar transportistas</h4>
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <form id="transportista-filter-form">
                <div class="two-col">
                  <label>Buscar por razon social
                    <input id="transportista-filter-buscar" name="buscar" list="transportista-filter-buscar-dl" placeholder="Nombre, comercial o RFC" autocomplete="off" />
                  </label>
                  <label>Estatus
                    <select id="transportista-filter-estatus" name="estatus">
                      <option value="">Todos</option>
                      <option value="activo">activo</option>
                      <option value="inactivo">inactivo</option>
                      <option value="bloqueado">bloqueado</option>
                    </select>
                  </label>
                </div>
                <div class="two-col">
                  <label>Tipo transportista
                    <select id="transportista-filter-tipo" name="tipo_transportista">
                      <option value="">Todos</option>
                      <option value="propio">propio</option>
                      <option value="subcontratado">subcontratado</option>
                      <option value="fletero">fletero</option>
                      <option value="aliado">aliado</option>
                    </select>
                  </label>
                </div>
                <datalist id="transportista-filter-buscar-dl"></datalist>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="transportista-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="transportistas-table"></div>
            <div id="transportista-edit-panel" class="toolbar hidden">
              <h4>Editar transportista</h4>
              <form id="transportista-edit-form">
                <input name="id" type="hidden" />
                <div class="two-col">
                  <label>Razon social
                    <input name="nombre" required />
                  </label>
                  <label>Nombre comercial
                    <input name="nombre_comercial" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Tipo transportista
                    <select name="tipo_transportista">
                      <option value="propio">propio</option>
                      <option value="subcontratado">subcontratado</option>
                      <option value="fletero">fletero</option>
                      <option value="aliado">aliado</option>
                    </select>
                  </label>
                  <label>Tipo persona
                    <select name="tipo_persona">
                      <option value="fisica">fisica</option>
                      <option value="moral">moral</option>
                    </select>
                  </label>
                  <label>Estatus
                    <select name="estatus">
                      <option value="activo">activo</option>
                      <option value="inactivo">inactivo</option>
                      <option value="bloqueado">bloqueado</option>
                    </select>
                  </label>
                </div>
                <div class="three-col">
                  <label>RFC
                    <input name="rfc" />
                  </label>
                  <label>CURP
                    <input name="curp" />
                  </label>
                  <label>Regimen fiscal
                    <input name="regimen_fiscal" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Fecha alta
                    <input name="fecha_alta" type="date" />
                  </label>
                  <label>Nivel confianza
                    <select name="nivel_confianza">
                      <option value="alto">alto</option>
                      <option value="medio">medio</option>
                      <option value="bajo">bajo</option>
                    </select>
                  </label>
                  <label>Prioridad asignacion
                    <input name="prioridad_asignacion" type="number" min="0" step="1" inputmode="numeric" title="Solo numeros enteros" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Contacto principal
                    <input name="contacto" />
                  </label>
                  <label>Telefono general
                    <input name="telefono" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Email general
                    <input name="email" type="email" />
                  </label>
                  <label>Sitio web
                    <input name="sitio_web" />
                  </label>
                  <label>Codigo postal
                    <input name="codigo_postal" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Ciudad
                    <input name="ciudad" />
                  </label>
                  <label>Estado
                    <input name="estado" />
                  </label>
                  <label>Pais
                    <input name="pais" />
                  </label>
                </div>
                <label>Direccion fiscal
                  <textarea name="direccion_fiscal"></textarea>
                </label>
                <label>Direccion operativa
                  <textarea name="direccion_operativa"></textarea>
                </label>
                <div class="two-col">
                  <label>Notas operativas
                    <textarea name="notas_operativas"></textarea>
                  </label>
                  <label>Notas comerciales
                    <textarea name="notas_comerciales"></textarea>
                  </label>
                </div>
                <div class="two-col">
                  <label class="check-row">
                    <input name="blacklist" type="checkbox" />
                    En blacklist
                  </label>
                  <label class="check-row">
                    <input name="activo" type="checkbox" />
                    Transportista activo
                  </label>
                </div>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="transportista-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="transportista-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden" data-transportista-tab-panel="contactos">
            <h3>Contactos del transportista</h3>
            <div class="hint">Captura trafico, administracion, cobranza o mantenimiento.</div>
            <h4 class="capture-section-title">Nuevo contacto</h4>
            <form id="transportista-contacto-form">
              <label>Transportista
                <select id="transportista-contacto-transportista" name="transportista_id" required></select>
              </label>
              <div class="two-col">
                <label>Nombre
                  <input name="nombre" required />
                </label>
                <label>Area
                  <input name="area" />
                </label>
              </div>
              <div class="two-col">
                <label>Puesto
                  <input name="puesto" />
                </label>
                <label>Email
                  <input name="email" type="email" />
                </label>
              </div>
              <div class="three-col">
                <label>Telefono
                  <input name="telefono" />
                </label>
                <label>Extension
                  <input name="extension" />
                </label>
                <label>Celular
                  <input name="celular" />
                </label>
              </div>
              <div class="two-col">
                <label class="check-row">
                  <input name="principal" type="checkbox" />
                  Contacto principal
                </label>
                <label class="check-row">
                  <input name="activo" type="checkbox" checked />
                  Contacto activo
                </label>
              </div>
              <button type="submit">Guardar contacto</button>
            </form>
            <div id="transportista-contacto-message" class="message"></div>
            <div id="transportista-contactos-table" class="contacto-table-wrap"></div>
            <div id="transportista-contacto-edit-panel" class="toolbar hidden" aria-hidden="true">
              <h4>Editar contacto</h4>
              <p class="hint" style="margin:0 0 8px">Solo aparece al pulsar <strong>Editar</strong> en la tabla. Para altas use <strong>Nuevo contacto</strong> arriba.</p>
              <form id="transportista-contacto-edit-form">
                <input name="id" type="hidden" />
                <input name="transportista_id" type="hidden" />
                <label>Transportista
                  <input name="transportista_label" readonly />
                </label>
                <div class="two-col">
                  <label>Nombre
                    <input name="nombre" required />
                  </label>
                  <label>Area
                    <input name="area" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Puesto
                    <input name="puesto" />
                  </label>
                  <label>Email
                    <input name="email" type="email" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Telefono
                    <input name="telefono" />
                  </label>
                  <label>Extension
                    <input name="extension" />
                  </label>
                  <label>Celular
                    <input name="celular" />
                  </label>
                </div>
                <div class="two-col">
                  <label class="check-row">
                    <input name="principal" type="checkbox" />
                    Contacto principal
                  </label>
                  <label class="check-row">
                    <input name="activo" type="checkbox" />
                    Contacto activo
                  </label>
                </div>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="transportista-contacto-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="transportista-contacto-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden" data-transportista-tab-panel="documentos">
            <h3>Documentos del transportista</h3>
            <div class="hint">Control de vigencias para operacion y cumplimiento.</div>
            <form id="transportista-documento-form">
              <label>Transportista
                <select id="transportista-documento-transportista" name="transportista_id" required></select>
              </label>
              <div class="three-col">
                <label>Tipo documento
                  <select name="tipo_documento">
                    <option value="permiso_sct">permiso_sct</option>
                    <option value="constancia_fiscal">constancia_fiscal</option>
                    <option value="seguro_rc">seguro_rc</option>
                    <option value="poliza_carga">poliza_carga</option>
                    <option value="tarjeta_circulacion">tarjeta_circulacion</option>
                    <option value="licencia_operador">licencia_operador</option>
                    <option value="ine">ine</option>
                    <option value="comprobante_domicilio">comprobante_domicilio</option>
                    <option value="contrato">contrato</option>
                    <option value="otro">otro</option>
                  </select>
                </label>
                <label>Numero documento
                  <input name="numero_documento" />
                </label>
                <label>Estatus
                  <select name="estatus">
                    <option value="vigente">vigente</option>
                    <option value="vencido">vencido</option>
                    <option value="pendiente" selected>pendiente</option>
                  </select>
                </label>
              </div>
              <div class="three-col">
                <label>Fecha emision
                  <input name="fecha_emision" type="date" />
                </label>
                <label>Fecha vencimiento
                  <input name="fecha_vencimiento" type="date" />
                </label>
                <label>Archivo URL
                  <input name="archivo_url" />
                </label>
              </div>
              <label>Observaciones
                <textarea name="observaciones"></textarea>
              </label>
              <button type="submit">Guardar documento</button>
            </form>
            <div id="transportista-documento-message" class="message"></div>
            <div id="transportista-documentos-table"></div>
            <div id="transportista-documento-edit-panel" class="toolbar hidden">
              <h4>Editar documento de transportista</h4>
              <form id="transportista-documento-edit-form">
                <input name="id" type="hidden" />
                <input name="transportista_id" type="hidden" />
                <label>Transportista
                  <input name="transportista_label" readonly />
                </label>
                <div class="three-col">
                  <label>Tipo documento
                    <select name="tipo_documento">
                      <option value="permiso_sct">permiso_sct</option>
                      <option value="constancia_fiscal">constancia_fiscal</option>
                      <option value="seguro_rc">seguro_rc</option>
                      <option value="poliza_carga">poliza_carga</option>
                      <option value="tarjeta_circulacion">tarjeta_circulacion</option>
                      <option value="licencia_operador">licencia_operador</option>
                      <option value="ine">ine</option>
                      <option value="comprobante_domicilio">comprobante_domicilio</option>
                      <option value="contrato">contrato</option>
                      <option value="otro">otro</option>
                    </select>
                  </label>
                  <label>Numero documento
                    <input name="numero_documento" />
                  </label>
                  <label>Estatus
                    <select name="estatus">
                      <option value="vigente">vigente</option>
                      <option value="vencido">vencido</option>
                      <option value="pendiente">pendiente</option>
                    </select>
                  </label>
                </div>
                <div class="three-col">
                  <label>Fecha emision
                    <input name="fecha_emision" type="date" />
                  </label>
                  <label>Fecha vencimiento
                    <input name="fecha_vencimiento" type="date" />
                  </label>
                  <label>Archivo URL
                    <input name="archivo_url" />
                  </label>
                </div>
                <label>Observaciones
                  <textarea name="observaciones"></textarea>
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="transportista-documento-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="transportista-documento-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-transportista-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Transportistas</h3>
              <span class="manual-badge" title="Contenido completo en esta pantalla">Documentación en pantalla</span>
            </div>
            <div class="hint">Guía integrada en la aplicación. El registro persiste en el servidor vía API. Enfoque formal en el marco del módulo y operativo en procedimientos e indicaciones de captura.</div>

            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-transportistas-toc" aria-label="Índice del manual de transportistas">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-transportistas-1">1. Objetivo del módulo</a>
                <a href="#manual-transportistas-2">2. Subopciones</a>
                <a href="#manual-transportistas-3">3. Nuevo transportista</a>
                <a href="#manual-transportistas-4">4. Consultar y editar</a>
                <a href="#manual-transportistas-5">5. Contactos</a>
                <a href="#manual-transportistas-6">6. Documentos</a>
                <a href="#manual-transportistas-7">7. Ejemplos de captura</a>
                <a href="#manual-transportistas-8">8. Preguntas frecuentes</a>
                <a href="#manual-transportistas-9">9. Mensajes y errores</a>
                <a href="#manual-transportistas-10">10. Referencia técnica</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="transportistas" tabindex="0" role="region" aria-label="Texto del manual de transportistas">
            <div class="manual-note">
              <strong>Secuencia operativa recomendada:</strong> (1) Registrar el maestro en <strong>Nuevo transportista</strong>. (2) Capturar <strong>Contactos</strong> operativos. (3) Registrar <strong>Documentos</strong> y vigencias. (4) Utilizar <strong>Consultar y editar</strong> para mantenimiento del catálogo.
            </div>

            <h4 id="manual-transportistas-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Centralizar el expediente de cada proveedor de transporte (flota propia, subcontratado, fletero o aliado), sus personas de contacto y el control documental para operación y cumplimiento. La separación en subopciones evita mezclar datos maestros, personas y expedientes.</p>

            <h4 id="manual-transportistas-2">2. Subopciones (barra superior)</h4>
            <ul class="summary-list">
              <li><strong>Nuevo transportista:</strong> alta del maestro con datos fiscales, tipo de figura, estatus, direcciones y notas.</li>
              <li><strong>Consultar y editar:</strong> filtros, tabla resumida y edición del registro seleccionado.</li>
              <li><strong>Contactos:</strong> personas de tráfico, administración, cobranza o mantenimiento asociadas al transportista.</li>
              <li><strong>Documentos:</strong> tipos de documento, números, fechas, estatus de vigencia y referencia a archivo (URL).</li>
              <li><strong>Manual:</strong> la presente guía.</li>
            </ul>
            <p class="manual-p"><strong>Sincronización entre pestañas:</strong> al cambiar el transportista en el selector de <strong>Contactos</strong> o <strong>Documentos</strong>, la aplicación replica la misma selección en el otro selector para continuar sobre el mismo proveedor.</p>

            <h4 id="manual-transportistas-3">3. Nuevo transportista</h4>
            <p class="manual-p">El campo obligatorio es <strong>Razón social</strong> (etiqueta &quot;Razon social&quot; en pantalla). El resto refuerza clasificación operativa, fiscal y de riesgo.</p>
            <h5>Descripción de campos relevantes</h5>
            <ul class="summary-list">
              <li><strong>Tipo transportista:</strong> propio, subcontratado, fletero o aliado (predeterminado: subcontratado).</li>
              <li><strong>Tipo persona y estatus:</strong> física o moral; estatus operativo activo, inactivo o bloqueado.</li>
              <li><strong>RFC, CURP, régimen fiscal:</strong> identificación fiscal conforme a políticas internas.</li>
              <li><strong>Fecha alta, nivel de confianza, prioridad de asignación:</strong> trazabilidad y orden sugerido en asignaciones.</li>
              <li><strong>Contacto principal y teléfono general, email, sitio web:</strong> datos corporativos; el detalle por persona va en Contactos.</li>
              <li><strong>Código postal, ciudad, estado, país:</strong> ubicación; el país puede venir precargado (por ejemplo México).</li>
              <li><strong>Dirección fiscal y dirección operativa:</strong> domicilio para facturación y, en su caso, base operativa.</li>
              <li><strong>Notas operativas y comerciales:</strong> acuerdos internos o restricciones.</li>
              <li><strong>En blacklist / Transportista activo:</strong> restricción de uso y vigencia en catálogo.</li>
            </ul>
            <p class="manual-p"><strong>Procedimiento:</strong> complete la información y pulse <strong>Guardar transportista</strong>. Verifique el mensaje bajo el formulario para confirmación o causa de error.</p>

            <h4 id="manual-transportistas-4">4. Consultar y editar</h4>
            <p class="manual-p">La búsqueda aplica sobre <strong>razón social</strong> (campo nombre), <strong>nombre comercial</strong> y <strong>RFC</strong>, sin distinguir mayúsculas. El listado se actualiza al escribir y al modificar <strong>Estatus</strong> o <strong>Tipo transportista</strong>. <strong>Aplicar filtro</strong> ejecuta la misma actualización de forma explícita.</p>
            <ul class="summary-list">
              <li><strong>Coincidencia única:</strong> si el filtro deja un solo registro, el panel <strong>Editar transportista</strong> se abre automáticamente.</li>
              <li><strong>Tabla:</strong> ID, razón social, nombre comercial, tipo, RFC, conteos de contactos y documentos, estatus y <strong>Editar</strong>.</li>
              <li><strong>Limpiar:</strong> restablece filtros, muestra el universo de registros y cierra el panel de edición si estaba abierto.</li>
              <li><strong>Edición:</strong> análoga al alta; confirme con <strong>Guardar cambios</strong> o cancele.</li>
            </ul>

            <h4 id="manual-transportistas-5">5. Contactos del transportista</h4>
            <p class="manual-p">Seleccione <strong>Transportista</strong> y capture el contacto. <strong>Nombre</strong> es obligatorio; área, puesto, medios de contacto y banderas de principal/activo son opcionales pero recomendables.</p>
            <ul class="summary-list">
              <li>El envío del formulario de alta sigue el flujo estándar del panel (botón <strong>Guardar contacto</strong>).</li>
              <li>En la tabla, <strong>Editar</strong> abre el panel inferior; el transportista se muestra en solo lectura.</li>
              <li><strong>Eliminar</strong> solicita confirmación antes de borrar el contacto.</li>
            </ul>

            <h4 id="manual-transportistas-6">6. Documentos del transportista</h4>
            <p class="manual-p">Permite llevar un inventario de permisos, pólizas, identificaciones y anexos con fechas y estatus de vigencia. <strong>Archivo URL</strong> almacena una referencia (ruta o enlace) al documento digitalizado según su política de archivos.</p>
            <ul class="summary-list">
              <li><strong>Tipo documento:</strong> valores predefinidos (por ejemplo permiso SCT, constancia fiscal, seguro RC, póliza de carga, tarjeta de circulación, contrato, otro).</li>
              <li><strong>Número, fechas de emisión y vencimiento, estatus</strong> (vigente, vencido, pendiente).</li>
              <li><strong>Observaciones:</strong> notas de auditoría o condiciones especiales.</li>
              <li>Edición y <strong>Eliminar</strong> desde la tabla, con confirmación en eliminación.</li>
            </ul>

            <h4 id="manual-transportistas-7">7. Ejemplos de captura (referencia operativa)</h4>
            <p class="manual-p">Use las convenciones corporativas; los ejemplos siguientes homogeneizan criterios habituales en transporte en México.</p>
            <h5>Tipo de documento</h5>
            <ul class="summary-list">
              <li><strong>permiso_sct:</strong> autorización federal de operación.</li>
              <li><strong>seguro_rc, poliza_carga:</strong> coberturas de responsabilidad civil y de mercancía.</li>
              <li><strong>constancia_fiscal:</strong> situación fiscal o constancia de situación.</li>
              <li><strong>tarjeta_circulacion, licencia_operador:</strong> unidad u operador según aplique.</li>
              <li><strong>contrato, otro:</strong> acuerdos marco o documentación miscelánea.</li>
            </ul>
            <h5>Estatus del documento</h5>
            <ul class="summary-list">
              <li><strong>vigente:</strong> dentro de periodo útil para operar.</li>
              <li><strong>vencido:</strong> requiere renovación antes de usar en operación.</li>
              <li><strong>pendiente:</strong> en trámite o sin validar.</li>
            </ul>

            <h4 id="manual-transportistas-8">8. Preguntas frecuentes</h4>
            <h5>No aparece el transportista en Contactos o Documentos</h5>
            <p class="manual-p">Verifique que el alta se haya guardado en <strong>Nuevo transportista</strong> y que los filtros de consulta no excluyan el estatus del registro. Recargue la vista si acaba de crear el maestro.</p>
            <h5>Diferencia entre dirección fiscal y operativa</h5>
            <p class="manual-p">La <strong>dirección fiscal</strong> se orienta a facturación y datos ante autoridad; la <strong>operativa</strong> describe la base o patio de operaciones si difiere del domicilio fiscal.</p>
            <h5>Uso de «En blacklist»</h5>
            <p class="manual-p">Marca al proveedor como no elegible para nuevas operaciones según la política interna; el efecto en asignaciones o compras depende de las reglas de su organización.</p>
            <h5>Apertura automática del panel al filtrar</h5>
            <p class="manual-p">Si el criterio produce exactamente un resultado, se abre <strong>Editar transportista</strong> automáticamente; con varias filas deberá pulsar <strong>Editar</strong> en la fila deseada.</p>
            <h5>Checklist al salir a ruta (cumplimiento)</h5>
            <p class="manual-p">La validación al registrar salida en <strong>Seguimiento</strong> puede exigir documentación del transportista (p. ej. <strong>seguro RC</strong> vigente en <strong>Documentos</strong>) y datos fiscales/CP completos según su configuración. Mantenga expediente y vigencias actualizados.</p>

            <h4 id="manual-transportistas-9">9. Mensajes y errores</h4>
            <p class="manual-p">Los mensajes bajo cada formulario reflejan la respuesta del servidor. Si las tablas no se poblan, compruebe conectividad y disponibilidad de la API.</p>

            <h4 id="manual-transportistas-10">10. Referencia técnica</h4>
            <p class="manual-p">Para rutas REST, esquemas y pruebas, utilice <a href="/docs">/docs</a> (Swagger).</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-viajes">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de viajes</h3>
              <div class="hint">Trabaja una parte a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="viaje-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-viaje-tab="alta">Nuevo viaje</button>
            <button type="button" class="subpage-button active" data-viaje-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-viaje-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-viaje-tab-panel="alta">
            <h3>Nuevo viaje</h3>
            <div class="hint">Planeacion del trayecto con origen, destino y estado.</div>
            <form id="viaje-form">
              <div class="two-col">
                <label>Codigo
                  <input name="codigo_viaje" required />
                </label>
                <label>Estado
                  <select name="estado">
                    <option value="planificado">planificado</option>
                    <option value="en_ruta">en_ruta</option>
                    <option value="completado">completado</option>
                    <option value="cancelado">cancelado</option>
                  </select>
                </label>
              </div>
              <label>Descripcion
                <input name="descripcion" />
              </label>
              <div class="two-col">
                <label>Origen
                  <input name="origen" required />
                </label>
                <label>Destino
                  <input name="destino" required />
                </label>
              </div>
              <div class="two-col">
                <label>Fecha salida
                  <input name="fecha_salida" type="datetime-local" required title="Use el selector; el valor debe ser fecha y hora validas" />
                </label>
                <label>Llegada estimada
                  <input name="fecha_llegada_estimada" type="datetime-local" title="Opcional. Formato fecha y hora local" />
                </label>
              </div>
              <p class="hint" style="margin:0;font-size:12px;">Si el navegador marca el campo como invalido, elija fecha y hora con el calendario o borre y vuelva a capturar.</p>
              <div class="two-col">
                <label>Kilometros estimados
                  <input
                    name="kilometros_estimados"
                    type="number"
                    step="0.01"
                    min="0"
                    inputmode="decimal"
                    autocomplete="off"
                    title="Numero en km (ej. 350 o 350.5). Punto como decimal; se usa en cotizacion de fletes."
                  />
                </label>
                <label>Notas
                  <input name="notas" />
                </label>
              </div>
              <button type="submit">Guardar viaje</button>
            </form>
            <div id="viaje-message" class="message"></div>
          </article>
          <article class="card" data-viaje-tab-panel="consulta">
            <h3>Listado de viajes</h3>
            <div class="toolbar">
              <h4>Consultar viajes</h4>
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <form id="viaje-filter-form">
                <div class="two-col">
                  <label>Buscar
                    <input id="viaje-filter-buscar" name="buscar" type="search" list="viaje-filter-buscar-dl" placeholder="Codigo, origen o destino" autocomplete="off" />
                  </label>
                  <label>Estado
                    <select name="estado">
                      <option value="">Todos</option>
                      <option value="planificado">planificado</option>
                      <option value="en_ruta">en_ruta</option>
                      <option value="completado">completado</option>
                      <option value="cancelado">cancelado</option>
                    </select>
                  </label>
                </div>
                <datalist id="viaje-filter-buscar-dl"></datalist>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="viaje-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="viajes-table"></div>
            <div id="viaje-edit-panel" class="toolbar hidden">
              <h4>Editar viaje</h4>
              <form id="viaje-edit-form">
                <input name="id" type="hidden" />
                <div class="two-col">
                  <label>Codigo
                    <input name="codigo_viaje" required />
                  </label>
                  <label>Estado
                    <select name="estado">
                      <option value="planificado">planificado</option>
                      <option value="en_ruta">en_ruta</option>
                      <option value="completado">completado</option>
                      <option value="cancelado">cancelado</option>
                    </select>
                  </label>
                </div>
                <label>Descripcion
                  <input name="descripcion" />
                </label>
                <div class="two-col">
                  <label>Origen
                    <input name="origen" required />
                  </label>
                  <label>Destino
                    <input name="destino" required />
                  </label>
                </div>
                <div class="two-col">
                  <label>Fecha salida
                    <input name="fecha_salida" type="datetime-local" required title="Use el selector; fecha y hora validas" />
                  </label>
                  <label>Llegada estimada
                    <input name="fecha_llegada_estimada" type="datetime-local" title="Opcional" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Llegada real
                    <input name="fecha_llegada_real" type="datetime-local" title="Opcional" />
                  </label>
                  <label>Kilometros estimados
                    <input
                      name="kilometros_estimados"
                      type="number"
                      step="0.01"
                      min="0"
                      inputmode="decimal"
                      autocomplete="off"
                      title="Numero en km; se usa en formulas de cotizacion"
                    />
                  </label>
                </div>
                <p class="hint" style="margin:0;font-size:12px;">Al editar, las fechas se cargan desde el servidor en formato compatible con este control. Si aparece error, borre el campo y elija de nuevo con el calendario.</p>
                <label>Notas
                  <input name="notas" />
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="viaje-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="viaje-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-viaje-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Viajes</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Guía del catálogo de viajes: planeación de trayecto, estados y consulta. Los datos se guardan vía API.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-viaje-toc" aria-label="Índice del manual de viajes">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-viaje-1">1. Objetivo</a>
                <a href="#manual-viaje-2">2. Subopciones</a>
                <a href="#manual-viaje-3">3. Nuevo viaje</a>
                <a href="#manual-viaje-4">4. Consultar y editar</a>
                <a href="#manual-viaje-5">5. Estados y seguimiento</a>
                <a href="#manual-viaje-6">6. Preguntas frecuentes</a>
                <a href="#manual-viaje-7">7. Mensajes y errores</a>
                <a href="#manual-viaje-8">8. Referencia técnica</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="viaje" tabindex="0" role="region" aria-label="Texto del manual de viajes">
            <div class="manual-note"><strong>Secuencia sugerida:</strong> registre el viaje en <strong>Nuevo viaje</strong> y utilice <strong>Consultar y editar</strong> para filtros y correcciones.</div>
            <h4 id="manual-viaje-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Definir cada trayecto (código, origen, destino, fechas, kilómetros estimados y estado) como base para fletes, asignaciones y despachos.</p>
            <h4 id="manual-viaje-2">2. Subopciones</h4>
            <ul class="summary-list">
              <li><strong>Nuevo viaje:</strong> alta del registro.</li>
              <li><strong>Consultar y editar:</strong> filtro, tabla y panel de edición.</li>
              <li><strong>Manual:</strong> esta guía.</li>
            </ul>
            <h4 id="manual-viaje-3">3. Nuevo viaje</h4>
            <p class="manual-p">Capture código, estado (planificado, en ruta, completado, cancelado), descripción, origen y destino, fechas de salida y llegada estimada, kilómetros estimados y notas. Pulse <strong>Guardar viaje</strong> y verifique el mensaje bajo el formulario.</p>
            <h4 id="manual-viaje-4">4. Consultar y editar</h4>
            <p class="manual-p">Filtre por texto (código, origen o destino) y por estado. <strong>Aplicar filtro</strong> y <strong>Limpiar</strong> ajustan la vista. En la tabla use <strong>Editar</strong> para abrir el panel; puede actualizar fechas reales de llegada y demás campos.</p>
            <h4 id="manual-viaje-5">5. Estados y seguimiento</h4>
            <p class="manual-p">El estado del viaje se actualiza aquí o en flujos posteriores (fletes, seguimiento). Mantenga coherencia con la operación real.</p>
            <h4 id="manual-viaje-6">6. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿No aparece en listados?</strong> Compruebe filtros y que el alta se haya guardado. <strong>¿No puedo elegir el viaje en otro módulo?</strong> Verifique que exista en catálogo y que el estado permita el vínculo.</p>
            <h4 id="manual-viaje-7">7. Mensajes y errores</h4>
            <p class="manual-p">Los avisos bajo el formulario provienen del servidor. Si la tabla no carga, revise conexión y API.</p>
            <h4 id="manual-viaje-8">8. Referencia técnica</h4>
            <p class="manual-p">Endpoints y esquemas en <a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-fletes">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de fletes</h3>
              <div class="hint">Trabaja una parte a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="flete-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-flete-tab="alta">Nuevo flete</button>
            <button type="button" class="subpage-button active" data-flete-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-flete-tab="ordenes-servicio">Ordenes de servicio</button>
            <button type="button" class="subpage-button" data-flete-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-flete-tab-panel="alta">
            <h3>Nuevo flete</h3>
            <div class="hint">Conecta cliente, transportista y viaje. Si no ves opciones, primero crea catalogos.</div>
            <form id="flete-form">
              <div class="two-col">
                <label>Codigo flete
                  <input name="codigo_flete" required />
                </label>
                <label>Estado
                  <select name="estado">
                    <option value="cotizado">cotizado</option>
                    <option value="confirmado">confirmado</option>
                    <option value="asignado">asignado</option>
                    <option value="en_transito">en_transito</option>
                    <option value="entregado">entregado</option>
                    <option value="cancelado">cancelado</option>
                  </select>
                </label>
              </div>
              <div class="three-col">
                <label>Tipo operacion
                  <select name="tipo_operacion">
                    <option value="propio">propio</option>
                    <option value="subcontratado" selected>subcontratado</option>
                    <option value="fletero">fletero</option>
                    <option value="aliado">aliado</option>
                  </select>
                </label>
                <label>Metodo calculo
                  <select name="metodo_calculo">
                    <option value="manual" selected>manual</option>
                    <option value="tarifa">tarifa</option>
                    <option value="motor">motor</option>
                  </select>
                </label>
                <label>Moneda
                  <input name="moneda" value="MXN" maxlength="3" />
                </label>
              </div>
              <div class="three-col">
                <label>Cliente
                  <select id="flete-cliente" name="cliente_id" required></select>
                </label>
                <label>Transportista
                  <select id="flete-transportista" name="transportista_id" required></select>
                </label>
                <label>Viaje
                  <select id="flete-viaje" name="viaje_id"></select>
                </label>
              </div>
              <div class="two-col">
                <label>Tipo unidad
                  <input name="tipo_unidad" placeholder="torton, tractocamion..." />
                </label>
                <label>Tipo carga
                  <input name="tipo_carga" placeholder="seca, refrigerada..." />
                </label>
              </div>
              <label>Descripcion de carga
                <input name="descripcion_carga" />
              </label>
              <div class="three-col">
                <label>Peso kg
                  <input name="peso_kg" type="number" step="0.001" min="0" required />
                </label>
                <label>Volumen m3
                  <input name="volumen_m3" type="number" step="0.001" min="0" />
                </label>
                <label>Numero bultos
                  <input name="numero_bultos" type="number" min="0" step="1" inputmode="numeric" title="Cantidad entera de bultos" />
                </label>
              </div>
              <div class="three-col">
                <label>Distancia km
                  <input name="distancia_km" type="number" step="0.01" min="0" />
                </label>
                <label>Precio venta
                  <input name="monto_estimado" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                </label>
                <label>Costo estimado
                  <input name="costo_transporte_estimado" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                </label>
              </div>
              <div class="two-col">
                <label>Costo real
                  <input name="costo_transporte_real" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                </label>
                <label>Margen estimado
                  <input name="margen_estimado" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                </label>
              </div>
              <div class="hint" id="flete-margen-pct-hint-new"></div>
              <div class="two-col">
                <button type="button" id="flete-cotizar-btn">Cotizar venta</button>
                <button type="button" id="flete-cotizar-compra-btn">Cotizar compra</button>
              </div>
              <div class="two-col">
                <div class="hint" id="flete-cotizacion-detalle">
                  Usa el viaje seleccionado para tomar origen y destino, buscar una tarifa activa y sugerir el precio de venta.
                </div>
                <div class="hint" id="flete-cotizacion-compra-detalle">
                  Usa el transportista elegido para sugerir el costo de compra estimado.
                </div>
              </div>
              <label>Notas
                <textarea name="notas"></textarea>
              </label>
              <button type="submit">Guardar flete</button>
            </form>
            <div id="flete-message" class="message"></div>
          </article>
          <article class="card" data-flete-tab-panel="consulta">
            <h3>Listado de fletes</h3>
            <div class="toolbar">
              <h4>Consultar fletes</h4>
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <form id="flete-filter-form">
                <div class="two-col">
                  <label class="span-2">Buscar rapido
                    <input id="flete-filter-buscar" name="buscar" type="search" list="flete-filter-buscar-dl" placeholder="Codigo flete, cliente, transportista o ID" autocomplete="off" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Estado
                    <select id="flete-filter-estado" name="estado">
                      <option value="">Todos</option>
                      <option value="cotizado">cotizado</option>
                      <option value="confirmado">confirmado</option>
                      <option value="asignado">asignado</option>
                      <option value="en_transito">en_transito</option>
                      <option value="entregado">entregado</option>
                      <option value="cancelado">cancelado</option>
                    </select>
                  </label>
                  <label>Cliente
                    <select id="flete-filter-cliente" name="cliente_id"></select>
                  </label>
                  <label>Transportista
                    <select id="flete-filter-transportista" name="transportista_id"></select>
                  </label>
                </div>
                <datalist id="flete-filter-buscar-dl"></datalist>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="flete-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="fletes-table"></div>
            <div id="flete-edit-panel" class="toolbar hidden">
              <h4>Editar flete</h4>
              <form id="flete-edit-form">
                <input id="flete-edit-form-record-id" name="id" type="hidden" autocomplete="off" />
                <div class="two-col">
                  <label>Codigo flete
                    <input name="codigo_flete" required />
                  </label>
                  <label>Estado
                    <select name="estado">
                      <option value="cotizado">cotizado</option>
                      <option value="confirmado">confirmado</option>
                      <option value="asignado">asignado</option>
                      <option value="en_transito">en_transito</option>
                      <option value="entregado">entregado</option>
                      <option value="cancelado">cancelado</option>
                    </select>
                  </label>
                </div>
                <div class="three-col">
                  <label>Tipo operacion
                    <select name="tipo_operacion">
                      <option value="propio">propio</option>
                      <option value="subcontratado">subcontratado</option>
                      <option value="fletero">fletero</option>
                      <option value="aliado">aliado</option>
                    </select>
                  </label>
                  <label>Metodo calculo
                    <select name="metodo_calculo">
                      <option value="manual">manual</option>
                      <option value="tarifa">tarifa</option>
                      <option value="motor">motor</option>
                    </select>
                  </label>
                  <label>Moneda
                    <input name="moneda" maxlength="3" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Cliente
                    <select id="edit-flete-cliente" name="cliente_id" required></select>
                  </label>
                  <label>Transportista
                    <select id="edit-flete-transportista" name="transportista_id" required></select>
                  </label>
                  <label>Viaje
                    <select id="edit-flete-viaje" name="viaje_id"></select>
                  </label>
                </div>
                <div class="two-col">
                  <label>Tipo unidad
                    <input name="tipo_unidad" />
                  </label>
                  <label>Tipo carga
                    <input name="tipo_carga" />
                  </label>
                </div>
                <label>Descripcion de carga
                  <input name="descripcion_carga" />
                </label>
                <div class="three-col">
                  <label>Peso kg
                    <input name="peso_kg" type="number" step="0.001" min="0" />
                  </label>
                  <label>Volumen m3
                    <input name="volumen_m3" type="number" step="0.001" min="0" />
                  </label>
                  <label>Numero bultos
                    <input name="numero_bultos" type="number" min="0" step="1" inputmode="numeric" title="Cantidad entera de bultos" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Distancia km
                    <input name="distancia_km" type="number" step="0.01" min="0" />
                  </label>
                  <label>Precio venta
                    <input name="monto_estimado" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                  <label>Costo estimado
                    <input name="costo_transporte_estimado" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Costo real
                    <input name="costo_transporte_real" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                  <label>Margen estimado
                    <input name="margen_estimado" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                </div>
                <div class="hint" id="flete-edit-margen-pct-hint"></div>
                <div class="two-col">
                  <button type="button" id="edit-flete-cotizar-venta-btn">Cotizar venta</button>
                  <button type="button" id="edit-flete-cotizar-compra-btn">Cotizar compra</button>
                </div>
                <div class="two-col">
                  <div class="hint" id="edit-flete-cotizacion-detalle">
                    Recalcula el precio de venta sugerido desde la tarifa comercial.
                  </div>
                  <div class="hint" id="edit-flete-cotizacion-compra-detalle">
                    Recalcula el costo estimado desde la tarifa de compra del transportista.
                  </div>
                </div>
                <label>Notas
                  <textarea name="notas"></textarea>
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="flete-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="flete-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden" data-flete-tab-panel="ordenes-servicio">
            <h3>Ordenes de servicio</h3>
            <div class="hint">Compromiso entre cotizacion aceptada y ejecucion (flete, viaje, despacho). Solo consulta en este panel; altas y cambios de estatus siguen disponibles en la API (<a href="/docs">/docs</a> &mdash; ordenes-servicio).</div>
            <div class="toolbar">
              <h4>Filtrar</h4>
              <form id="orden-servicio-filter-form">
                <div class="three-col">
                  <label>Buscar
                    <input id="orden-servicio-filter-buscar" name="buscar" type="search" placeholder="Folio, origen, destino, codigo flete" autocomplete="off" />
                  </label>
                  <label>Cliente
                    <select id="orden-servicio-filter-cliente" name="cliente_id">
                      <option value="">Todos</option>
                    </select>
                  </label>
                  <label>Estatus
                    <select id="orden-servicio-filter-estatus" name="estatus">
                      <option value="">Todos</option>
                      <option value="borrador">borrador</option>
                      <option value="confirmada">confirmada</option>
                      <option value="programada">programada</option>
                      <option value="en_ejecucion">en_ejecucion</option>
                      <option value="cerrada">cerrada</option>
                      <option value="cancelada">cancelada</option>
                    </select>
                  </label>
                </div>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="orden-servicio-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="ordenes-servicio-table"></div>
            <div id="orden-servicio-detail-panel" class="toolbar hidden" aria-hidden="true">
              <h4>Detalle de orden de servicio</h4>
              <div id="orden-servicio-detail-body" class="hint" style="white-space:pre-wrap;font-size:13px;line-height:1.5;"></div>
              <div class="toolbar-actions">
                <button type="button" id="orden-servicio-detail-close" class="secondary-button">Cerrar</button>
              </div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-flete-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Fletes</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">El flete vincula cliente, transportista y viaje con precios y márgenes. Guía formal y operativa.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-flete-toc" aria-label="Índice del manual de fletes">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-flete-1">1. Objetivo</a>
                <a href="#manual-flete-2">2. Subopciones</a>
                <a href="#manual-flete-3">3. Nuevo flete</a>
                <a href="#manual-flete-4">4. Consultar y editar</a>
                <a href="#manual-flete-5">5. Cotización y tarifas</a>
                <a href="#manual-flete-6">6. Preguntas frecuentes</a>
                <a href="#manual-flete-7">7. Mensajes y errores</a>
                <a href="#manual-flete-8">8. Referencia técnica</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="flete" tabindex="0" role="region" aria-label="Texto del manual de fletes">
            <div class="manual-note"><strong>Prerrequisitos:</strong> clientes, transportistas y viajes dados de alta para poder seleccionarlos. Para cotizar con motor: tarifas de venta (y de compra si usa el boton de cotizacion de compra) alineadas en ambito, modalidad, origen/destino y tipo de unidad/carga.</div>
            <h4 id="manual-flete-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Registrar cada ejercicio comercial de transporte (cotización, costos, venta, márgenes) asociado a cliente, transportista y viaje. Campos fiscales extendidos del flete (Carta Porte UUID/folio, factura de mercancía) pueden gestionarse por API si aún no aparecen en este formulario.</p>
            <h4 id="manual-flete-2">2. Subopciones</h4>
            <ul class="summary-list">
              <li><strong>Nuevo flete:</strong> alta del flete; botones <strong>Cotizar venta</strong> y <strong>Cotizar compra</strong> para sugerir montos según tarifas y datos capturados.</li>
              <li><strong>Consultar y editar:</strong> filtros por texto rapido, estado, cliente y transportista; <strong>Editar</strong> abre el panel de correccion.</li>
              <li><strong>Ordenes de servicio:</strong> solo <strong>consulta</strong> — filtros, tabla y <strong>Ver detalle</strong>. No se crean ni editan ordenes desde esta pestaña (use API <code>/ordenes-servicio</code> en <a href="/docs">/docs</a> o procesos internos).</li>
              <li><strong>Manual:</strong> esta guía.</li>
            </ul>
            <h4 id="manual-flete-3">3. Nuevo flete</h4>
            <p class="manual-p">Complete codigo, estado, tipo de operacion, metodo de calculo (manual, tarifa, motor), moneda, cliente, transportista y viaje, tipo unidad/carga, peso (obligatorio para cotizar), distancia, montos y notas. El viaje seleccionado alimenta origen/destino al cotizar. Tras cotizar, valide precios antes de guardar.</p>
            <h4 id="manual-flete-4">4. Consultar y editar</h4>
            <p class="manual-p">Aplique filtros y pulse <strong>Editar</strong> en la fila. Puede volver a usar <strong>Cotizar venta/compra</strong> en edicion. Actualice costos reales o estados segun su proceso.</p>
            <h4 id="manual-flete-5">5. Cotización y tarifas</h4>
            <p class="manual-p">Los botones de cotizacion llaman al motor de tarifas; los resultados se muestran en el area de detalle bajo los botones. Deben coincidir ambito (local/estatal/federal), modalidad y textos de origen/destino con la tarifa vigente. El flujo completo cotizacion guardada → aceptada → conversion formal a flete puede requerir API u homologacion con sistemas; en panel suele bastar flete confirmado con precio coherente.</p>
            <h4 id="manual-flete-6">6. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿Listas vacías en selectores?</strong> Cree primero los catálogos. <strong>¿Margen en cero?</strong> Revise precio de venta y costos capturados.</p>
            <h4 id="manual-flete-7">7. Mensajes y errores</h4>
            <p class="manual-p">Los mensajes vienen del servidor. Compruebe API y validaciones.</p>
            <h4 id="manual-flete-8">8. Referencia técnica</h4>
            <p class="manual-p"><a href="/docs">/docs</a> (Swagger).</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-facturas">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de facturas</h3>
              <div class="hint">Trabaja una parte a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="factura-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-factura-tab="alta">Nueva factura</button>
            <button type="button" class="subpage-button active" data-factura-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-factura-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-factura-tab-panel="alta">
            <h3>Nueva factura</h3>
            <div class="hint">Simulación administrativa de facturación y cobranza ligada al cliente y al flete.</div>
            <p class="hint" id="factura-nueva-ayuda-flete" style="margin:0 0 8px 0;">
              Elegir solo <strong>Cliente</strong> y <strong>Flete</strong> no rellena concepto ni importes: pulse
              <strong>Autollenar desde flete</strong> (borrador en pantalla) o
              <strong>Generar automático desde flete</strong> (crea la factura en el servidor).
              La lista de fletes se acota al cliente seleccionado.
            </p>
            <form id="factura-form">
              <div class="three-col">
                <label>Serie
                  <input name="serie" placeholder="A, B, MXN..." />
                </label>
                <label>Fecha emision
                  <input name="fecha_emision" type="date" required />
                </label>
                <label>Fecha vencimiento
                  <input name="fecha_vencimiento" type="date" />
                </label>
              </div>
              <div class="three-col">
                <label>Cliente
                  <select id="factura-cliente" name="cliente_id" required></select>
                </label>
                <label>Flete
                  <select id="factura-flete" name="flete_id"></select>
                </label>
                <label>Orden de servicio
                  <input name="orden_servicio_id" id="factura-form-orden-servicio-id" placeholder="ID numerico (opcional)" />
                </label>
              </div>
              <div class="two-col">
                <label>Buscar por folio de orden (rellena el ID)
                  <input type="text" id="factura-os-folio-buscar" placeholder="Ej. OS20260412-0001" autocomplete="off" />
                </label>
                <div class="toolbar-actions" style="align-self:flex-end;padding-top:1.25rem;">
                  <button type="button" id="factura-os-folio-aplicar" class="secondary-button">Aplicar folio</button>
                </div>
              </div>
              <div class="three-col">
                <label>Concepto
                  <input name="concepto" required />
                </label>
                <label>Referencia
                  <input name="referencia" />
                </label>
                <label>Moneda
                  <input name="moneda" value="MXN" maxlength="3" />
                </label>
              </div>
              <div class="three-col">
                <label>Subtotal
                  <input name="subtotal" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                </label>
                <label>IVA %
                  <input name="iva_pct" type="number" step="0.0001" min="0" value="0.16" />
                </label>
                <label>IVA monto
                  <input name="iva_monto" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                </label>
              </div>
              <div class="three-col">
                <label>Retencion
                  <input name="retencion_monto" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                </label>
                <label>Total
                  <input name="total" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                </label>
                <label>Saldo pendiente
                  <input name="saldo_pendiente" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                </label>
              </div>
              <div class="three-col">
                <label>Forma pago
                  <input name="forma_pago" placeholder="transferencia" />
                </label>
                <label>Metodo pago
                  <input name="metodo_pago" placeholder="PPD o PUE" />
                </label>
                <label>Uso CFDI
                  <input name="uso_cfdi" placeholder="G03, S01..." />
                </label>
              </div>
              <div class="two-col">
                <label>Estatus
                  <select name="estatus">
                    <option value="borrador" selected>borrador</option>
                    <option value="emitida">emitida</option>
                    <option value="enviada">enviada</option>
                    <option value="parcial">parcial</option>
                    <option value="cobrada">cobrada</option>
                    <option value="cancelada">cancelada</option>
                  </select>
                </label>
                <label class="check-row">
                  <input name="timbrada" type="checkbox" />
                  Marcada como timbrada
                </label>
              </div>
              <label>Observaciones
                <textarea name="observaciones"></textarea>
              </label>
              <label class="check-row">
                <input type="checkbox" id="factura-gen-usar-tarifa" />
                Al generar automático, usar precio recalculado con tarifas vigentes (si aplica)
              </label>
              <div class="toolbar-actions">
                <button type="button" id="factura-desde-flete-btn" class="secondary-button">Autollenar desde flete</button>
                <button type="button" id="factura-preview-flete-btn" class="secondary-button" title="Ver precio flete vs tarifa vigente">Vista previa (tarifa)</button>
                <button type="button" id="factura-generar-auto-btn" class="secondary-button">Generar automático desde flete</button>
                <button type="submit">Guardar factura</button>
              </div>
            </form>
            <div id="factura-message" class="message"></div>
          </article>
          <article class="card" data-factura-tab-panel="consulta">
            <h3>Listado de facturas</h3>
            <div class="toolbar">
              <h4>Consultar facturas</h4>
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <form id="factura-filter-form">
                <p class="hint" style="margin:0 0 8px 0;">El texto en <strong>Buscar</strong> filtra al escribir; cliente y estatus al cambiar o con <strong>Aplicar filtro</strong>.</p>
                <div class="three-col">
                  <label>Buscar
                    <input id="factura-filter-buscar" name="buscar" type="search" list="factura-filter-buscar-dl" placeholder="Folio, concepto o referencia" autocomplete="off" />
                  </label>
                  <label>Cliente
                    <select id="factura-filter-cliente" name="cliente_id"></select>
                  </label>
                  <label>Estatus
                    <select id="factura-filter-estatus" name="estatus">
                      <option value="">Todas</option>
                      <option value="borrador">borrador</option>
                      <option value="emitida">emitida</option>
                      <option value="enviada">enviada</option>
                      <option value="parcial">parcial</option>
                      <option value="cobrada">cobrada</option>
                      <option value="cancelada">cancelada</option>
                    </select>
                  </label>
                </div>
                <datalist id="factura-filter-buscar-dl"></datalist>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="factura-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="facturas-table"></div>
            <div id="factura-edit-panel" class="toolbar hidden">
              <h4>Editar factura</h4>
              <form id="factura-edit-form">
                <input name="id" type="hidden" />
                <div class="three-col">
                  <label>Serie
                    <input name="serie" />
                  </label>
                  <label>Fecha emision
                    <input name="fecha_emision" type="date" required />
                  </label>
                  <label>Fecha vencimiento
                    <input name="fecha_vencimiento" type="date" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Cliente
                    <select id="edit-factura-cliente" name="cliente_id" required></select>
                  </label>
                  <label>Flete
                    <select id="edit-factura-flete" name="flete_id"></select>
                  </label>
                  <label>Orden de servicio
                    <input name="orden_servicio_id" id="edit-factura-form-orden-servicio-id" placeholder="ID numerico (opcional)" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Buscar por folio de orden (rellena el ID)
                    <input type="text" id="edit-factura-os-folio-buscar" placeholder="Ej. OS20260412-0001" autocomplete="off" />
                  </label>
                  <div class="toolbar-actions" style="align-self:flex-end;padding-top:1.25rem;">
                    <button type="button" id="edit-factura-os-folio-aplicar" class="secondary-button">Aplicar folio</button>
                  </div>
                </div>
                <div class="three-col">
                  <label>Concepto
                    <input name="concepto" required />
                  </label>
                  <label>Referencia
                    <input name="referencia" />
                  </label>
                  <label>Moneda
                    <input name="moneda" maxlength="3" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Subtotal
                    <input name="subtotal" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                  </label>
                  <label>IVA %
                    <input name="iva_pct" type="number" step="0.0001" min="0" />
                  </label>
                  <label>IVA monto
                    <input name="iva_monto" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Retencion
                    <input name="retencion_monto" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                  <label>Total
                    <input name="total" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                  <label>Saldo pendiente
                    <input name="saldo_pendiente" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Forma pago
                    <input name="forma_pago" />
                  </label>
                  <label>Metodo pago
                    <input name="metodo_pago" />
                  </label>
                  <label>Uso CFDI
                    <input name="uso_cfdi" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Estatus
                    <select name="estatus">
                      <option value="borrador">borrador</option>
                      <option value="emitida">emitida</option>
                      <option value="enviada">enviada</option>
                      <option value="parcial">parcial</option>
                      <option value="cobrada">cobrada</option>
                      <option value="cancelada">cancelada</option>
                    </select>
                  </label>
                  <label class="check-row">
                    <input name="timbrada" type="checkbox" />
                    Marcada como timbrada
                  </label>
                </div>
                <label>Observaciones
                  <textarea name="observaciones"></textarea>
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="factura-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="factura-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-factura-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Facturas</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Facturación administrativa simulada: montos, impuestos, estatus y vínculo a cliente y flete.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-factura-toc" aria-label="Índice del manual de facturas">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-factura-1">1. Objetivo</a>
                <a href="#manual-factura-2">2. Subopciones</a>
                <a href="#manual-factura-3">3. Nueva factura</a>
                <a href="#manual-factura-4">4. Consultar y editar</a>
                <a href="#manual-factura-5">5. Autollenar, vista previa y generar automático</a>
                <a href="#manual-factura-6">6. Orden de servicio y folio</a>
                <a href="#manual-factura-7">7. Preguntas frecuentes</a>
                <a href="#manual-factura-8">8. Mensajes y errores</a>
                <a href="#manual-factura-9">9. Referencia técnica</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="factura" tabindex="0" role="region" aria-label="Texto del manual de facturas">
            <div class="manual-note"><strong>Alcance:</strong> registro <strong>administrativo</strong> de cobro en SIFE-MXN; no sustituye al CFDI timbrado ante el SAT. Valide montos, forma y metodo de pago, uso CFDI y politica de timbrado con su area fiscal. La casilla <strong>Marcada como timbrada</strong> es informativa si el timbrado ocurre fuera del sistema.</div>
            <h4 id="manual-factura-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Registrar folio interno (serie, fechas, importes, IVA, retenciones, forma y metodo de pago, uso CFDI, estatus), vinculo a <strong>cliente</strong> y, opcionalmente, a <strong>flete</strong> y a <strong>orden de servicio</strong> (por ID o mediante <strong>Aplicar folio</strong>).</p>
            <h4 id="manual-factura-2">2. Subopciones</h4>
            <ul class="summary-list">
              <li><strong>Nueva factura:</strong> alta del registro administrativo.</li>
              <li><strong>Consultar y editar:</strong> filtros por texto, cliente y estatus; edicion por fila.</li>
              <li><strong>Manual:</strong> esta guía.</li>
            </ul>
            <h4 id="manual-factura-3">3. Nueva factura</h4>
            <p class="manual-p">Seleccione <strong>Cliente</strong> y, si aplica, <strong>Flete</strong>. La lista de fletes se <strong>filtra al cliente</strong> elegido; si elige primero un flete, el cliente se sincroniza con el del flete. <strong>Solo elegir cliente y flete no rellena concepto ni importes:</strong> debe pulsar <strong>Autollenar desde flete</strong> (rellena el formulario en pantalla; aun debe <strong>Guardar factura</strong>) o <strong>Generar automático desde flete</strong> (crea el registro en servidor con logica de negocio; opcionalmente marque usar precio recalculado con tarifas vigentes). Puede usar <strong>Vista previa (tarifa)</strong> para comparar precio del flete frente a tarifa sin guardar.</p>
            <p class="manual-p">Complete fechas (emision obligatoria), concepto, montos o dejelos calcular tras autollenar; forma y metodo de pago (p. ej. PUE/PPD segun politica), uso CFDI, estatus (borrador hasta emitida/cobrada). Guarde con <strong>Guardar factura</strong>.</p>
            <h4 id="manual-factura-4">4. Consultar y editar</h4>
            <p class="manual-p">Use filtros; el texto en <strong>Buscar</strong> filtra al escribir. <strong>Editar</strong> abre el panel; mismo criterio de orden de servicio por ID o <strong>Aplicar folio</strong>. <strong>Limpiar</strong> restablece filtros.</p>
            <h4 id="manual-factura-5">5. Autollenar, vista previa y generar automático</h4>
            <p class="manual-p"><strong>Autollenar desde flete</strong> copia cliente, concepto, referencia, moneda y subtotal desde el precio del flete y recalcula IVA/total en pantalla; no persiste hasta Guardar. <strong>Generar automático desde flete</strong> llama al API y crea la factura con folio nuevo; tras exito suele mostrarse el listado. <strong>Vista previa (tarifa)</strong> solo muestra comparacion informativa.</p>
            <h4 id="manual-factura-6">6. Orden de servicio y folio</h4>
            <p class="manual-p">El campo <strong>Orden de servicio</strong> guarda el <strong>ID numerico</strong> de la orden, no el folio legible. Si solo conoce el folio (ej. OS…), escribalo en <strong>Buscar por folio de orden</strong> y pulse <strong>Aplicar folio</strong> para rellenar el ID. Puede obtener el ID en <strong>Fletes → Ordenes de servicio → Ver detalle</strong>.</p>
            <h4 id="manual-factura-7">7. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿No aparece el flete?</strong> Compruebe que exista para ese cliente y que el catalogo se haya cargado (F5). <strong>¿Total incorrecto?</strong> Revise subtotal, IVA %, retencion y redondeos. <strong>¿Perdi datos al cambiar de pantalla?</strong> Lo no guardado no se recupera; guarde borrador o emitida segun politica. <strong>¿Metodo de pago PUE o PPD?</strong> PUE suele usarse en pago en una exhibicion; PPD en credito o parcialidades — confirme con fiscal.</p>
            <h4 id="manual-factura-8">8. Mensajes y errores</h4>
            <p class="manual-p">Los avisos bajo el formulario reproducen la respuesta del servidor (validacion, FK inexistente, etc.).</p>
            <h4 id="manual-factura-9">9. Referencia técnica</h4>
            <p class="manual-p">Endpoints <code>/facturas</code>, <code>/facturas/generar-desde-flete</code>, <code>/facturas/preview-desde-flete/…</code> en <a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-tarifas">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de tarifas</h3>
              <div class="hint">Trabaja una parte a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="tarifa-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-tarifa-tab="alta">Nueva tarifa</button>
            <button type="button" class="subpage-button active" data-tarifa-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-tarifa-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-tarifa-tab-panel="alta">
            <h3>Nueva tarifa de flete</h3>
            <div class="hint">Define reglas base para proponer precio de venta por ruta, unidad y tipo de carga. <strong>Ambito</strong> y <strong>modalidad</strong> deben coincidir con la cotizacion; los porcentajes se aplican sobre el subtotal en el motor de cotizacion. <strong>Importes y porcentajes:</strong> formato Mexico (miles con coma, decimales con punto) al salir del campo. <strong>Enter</strong> pasa al siguiente campo; solo el boton <strong>Guardar tarifa</strong> envia el formulario.</div>
            <form id="tarifa-form">
              <div class="two-col">
                <label>Nombre tarifa
                  <input name="nombre_tarifa" id="tarifa-form-nombre-tarifa" required autocomplete="off" />
                </label>
                <label>Moneda
                  <input name="moneda" value="MXN" maxlength="3" />
                </label>
              </div>
              <p id="tarifa-form-nombre-aviso" class="hint" hidden style="margin:0;color:var(--error);font-weight:800;"></p>
              <div class="two-col">
                <label class="span-2">Tipo operacion (perfil de venta)
                  <select name="tipo_operacion">
                    <option value="propio">propio</option>
                    <option value="subcontratado" selected>subcontratado</option>
                    <option value="fletero">fletero</option>
                    <option value="aliado">aliado</option>
                  </select>
                </label>
              </div>
              <div class="two-col">
                <label>Ambito
                  <select name="ambito">
                    <option value="local">local</option>
                    <option value="estatal">estatal</option>
                    <option value="federal" selected>federal</option>
                  </select>
                </label>
                <label>Modalidad cobro
                  <select name="modalidad_cobro">
                    <option value="mixta" selected>mixta</option>
                    <option value="por_viaje">por_viaje</option>
                    <option value="por_km">por_km</option>
                    <option value="por_tonelada">por_tonelada</option>
                    <option value="por_hora">por_hora</option>
                    <option value="por_dia">por_dia</option>
                  </select>
                </label>
              </div>
              <div class="two-col">
                <label>Origen
                  <input name="origen" required />
                </label>
                <label>Destino
                  <input name="destino" required />
                </label>
              </div>
              <div class="two-col">
                <label>Tipo unidad
                  <input name="tipo_unidad" required />
                </label>
                <label>Tipo carga
                  <input name="tipo_carga" />
                </label>
              </div>
              <div class="three-col">
                <label>Tarifa base
                  <input name="tarifa_base" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                </label>
                <label>Tarifa por km
                  <input id="tarifa-venta-alta-tarifa-km" name="tarifa_km" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" title="Formato Mexico (miles con coma, decimales con punto). Minimo 2 decimales visibles, alineado a tarifa base y recargo." />
                </label>
                <label>Tarifa por kg
                  <input name="tarifa_kg" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="6" value="0" />
                </label>
              </div>
              <div class="three-col">
                <label>Tarifa por tonelada
                  <input name="tarifa_tonelada" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                </label>
                <label>Tarifa por hora
                  <input name="tarifa_hora" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                </label>
                <label>Tarifa por dia
                  <input name="tarifa_dia" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                </label>
              </div>
              <div class="three-col">
                <label>Porc. utilidad (sobre subtotal)
                  <input name="porcentaje_utilidad" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0.20" />
                </label>
                <label>Porc. riesgo
                  <input name="porcentaje_riesgo" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                </label>
                <label>Porc. urgencia (si marca urgencia en cotizacion)
                  <input name="porcentaje_urgencia" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                </label>
              </div>
              <div class="two-col">
                <label>Porc. retorno vacio (si aplica en cotizacion)
                  <input name="porcentaje_retorno_vacio" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                </label>
                <label>Porc. carga especial (refrigerada o peligrosa)
                  <input name="porcentaje_carga_especial" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                </label>
              </div>
              <div class="three-col">
                <label>Recargo minimo
                  <input name="recargo_minimo" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                </label>
                <label>Vigencia inicio
                  <input name="vigencia_inicio" type="date" title="Opcional. Use el calendario para evitar error de formato" />
                </label>
                <label>Vigencia fin
                  <input name="vigencia_fin" type="date" title="Opcional. Use el calendario para evitar error de formato" />
                </label>
              </div>
              <label class="check-row">
                <input name="activo" type="checkbox" checked />
                Tarifa activa
              </label>
              <button type="submit">Guardar tarifa</button>
            </form>
            <div id="tarifa-message" class="message"></div>
          </article>
          <article class="card" data-tarifa-tab-panel="consulta">
            <h3>Listado de tarifas</h3>
            <div class="toolbar">
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <label>Buscar rapido (nombre, ruta, unidad, ambito, ID)
                <input id="tarifa-venta-filter-buscar" type="search" list="tarifa-venta-filter-buscar-dl" placeholder="Filtra la tabla mientras escribes" autocomplete="off" style="max-width:28rem" />
              </label>
              <datalist id="tarifa-venta-filter-buscar-dl"></datalist>
            </div>
            <div id="tarifas-table"></div>
            <div id="tarifa-edit-panel" class="toolbar hidden">
              <h4>Editar tarifa de flete</h4>
              <form id="tarifa-edit-form">
                <input name="id" type="hidden" />
                <div class="two-col">
                  <label>Nombre tarifa
                    <input name="nombre_tarifa" id="tarifa-edit-form-nombre-tarifa" required autocomplete="off" />
                  </label>
                  <label>Moneda
                    <input name="moneda" maxlength="3" />
                  </label>
                </div>
                <p id="tarifa-edit-form-nombre-aviso" class="hint" hidden style="margin:0;color:var(--error);font-weight:800;"></p>
                <div class="two-col">
                  <label class="span-2">Tipo operacion (perfil de venta)
                    <select name="tipo_operacion">
                      <option value="propio">propio</option>
                      <option value="subcontratado">subcontratado</option>
                      <option value="fletero">fletero</option>
                      <option value="aliado">aliado</option>
                    </select>
                  </label>
                </div>
                <div class="two-col">
                  <label>Ambito
                    <select name="ambito">
                      <option value="local">local</option>
                      <option value="estatal">estatal</option>
                      <option value="federal">federal</option>
                    </select>
                  </label>
                  <label>Modalidad cobro
                    <select name="modalidad_cobro">
                      <option value="mixta">mixta</option>
                      <option value="por_viaje">por_viaje</option>
                      <option value="por_km">por_km</option>
                      <option value="por_tonelada">por_tonelada</option>
                      <option value="por_hora">por_hora</option>
                      <option value="por_dia">por_dia</option>
                    </select>
                  </label>
                </div>
                <div class="two-col">
                  <label>Origen
                    <input name="origen" required />
                  </label>
                  <label>Destino
                    <input name="destino" required />
                  </label>
                </div>
                <div class="two-col">
                  <label>Tipo unidad
                    <input name="tipo_unidad" required />
                  </label>
                  <label>Tipo carga
                    <input name="tipo_carga" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Tarifa base
                    <input name="tarifa_base" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                  </label>
                  <label>Tarifa por km
                    <input id="tarifa-venta-edit-tarifa-km" name="tarifa_km" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" title="Formato Mexico. Minimo 2 decimales visibles." />
                  </label>
                  <label>Tarifa por kg
                    <input name="tarifa_kg" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="6" value="0" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Tarifa por tonelada
                    <input name="tarifa_tonelada" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                  </label>
                  <label>Tarifa por hora
                    <input name="tarifa_hora" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                  </label>
                  <label>Tarifa por dia
                    <input name="tarifa_dia" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Porc. utilidad (sobre subtotal)
                    <input name="porcentaje_utilidad" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                  </label>
                  <label>Porc. riesgo
                    <input name="porcentaje_riesgo" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                  </label>
                  <label>Porc. urgencia
                    <input name="porcentaje_urgencia" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Porc. retorno vacio
                    <input name="porcentaje_retorno_vacio" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                  </label>
                  <label>Porc. carga especial
                    <input name="porcentaje_carga_especial" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Recargo minimo
                    <input name="recargo_minimo" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                  </label>
                  <label>Vigencia inicio
                    <input name="vigencia_inicio" type="date" title="Opcional. Use el calendario para evitar error de formato" />
                  </label>
                  <label>Vigencia fin
                    <input name="vigencia_fin" type="date" title="Opcional. Use el calendario para evitar error de formato" />
                  </label>
                </div>
                <label class="check-row">
                  <input name="activo" type="checkbox" />
                  Tarifa activa
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="tarifa-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="tarifa-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-tarifa-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Tarifas (venta)</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Tarifas comerciales para cotización: ruta, unidad, componentes de precio y vigencia.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-tarifa-toc" aria-label="Índice del manual de tarifas">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-tarifa-1">1. Objetivo</a>
                <a href="#manual-tarifa-2">2. Subopciones</a>
                <a href="#manual-tarifa-3">3. Nueva tarifa</a>
                <a href="#manual-tarifa-4">4. Consulta</a>
                <a href="#manual-tarifa-5">5. Vigencia</a>
                <a href="#manual-tarifa-6">6. FAQ</a>
                <a href="#manual-tarifa-7">7. Mensajes</a>
                <a href="#manual-tarifa-8">8. Referencia</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="tarifa" tabindex="0" role="region" aria-label="Texto del manual de tarifas">
            <h4 id="manual-tarifa-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Definir reglas de precio de venta por ruta (origen/destino), tipo de unidad y carga, con base, km, kg, recargo mínimo y vigencia.</p>
            <h4 id="manual-tarifa-2">2. Subopciones</h4>
            <ul class="summary-list"><li><strong>Nueva tarifa / Consultar:</strong> alta y listado.</li><li><strong>Manual:</strong> esta guía.</li></ul>
            <h4 id="manual-tarifa-3">3. Nueva tarifa</h4>
            <p class="manual-p">Complete nombre, moneda, tipo de operación (propio, subcontratado, fletero o aliado; predeterminado subcontratado), origen y destino, tipos, tarifa base y componentes opcionales, recargo mínimo, fechas de vigencia y marque si está activa. Use <strong>Enter</strong> para pasar de campo en campo; el guardado en alta ocurre solo al pulsar <strong>Guardar tarifa</strong>. Si guardó incompleta por error, en <strong>Consultar y editar</strong> use <strong>Editar</strong> en la fila para corregir y <strong>Guardar cambios</strong>.</p>
            <h4 id="manual-tarifa-4">4. Consulta</h4>
            <p class="manual-p">El listado muestra las tarifas registradas. En cada fila, <strong>Editar</strong> abre el panel para ajustar datos y vigencias.</p>
            <h4 id="manual-tarifa-5">5. Vigencia</h4>
            <p class="manual-p">Use vigencia inicio/fin para acotar el uso en <strong>Fletes</strong> con método de cálculo <strong>tarifa</strong> o <strong>motor</strong> y en los botones <strong>Cotizar venta</strong>. Las mismas reglas alimentan la <strong>Vista previa (tarifa)</strong> y la opción de recálculo al <strong>Generar automático</strong> de factura desde flete, si aplica.</p>
            <h4 id="manual-tarifa-6">6. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿No aplica en flete?</strong> Verifique tipo de unidad/carga, textos de origen/destino, tipo de operación y vigencia. <strong>¿Precio distinto en factura?</strong> Compare con “usar precio recalculado” al generar desde flete y con el precio ya guardado en el flete.</p>
            <h4 id="manual-tarifa-7">7. Mensajes y errores</h4>
            <p class="manual-p">Mensajes del servidor bajo el formulario.</p>
            <h4 id="manual-tarifa-8">8. Referencia técnica</h4>
            <p class="manual-p"><a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-tarifas-compra">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de tarifas de compra</h3>
              <div class="hint">Trabaja una parte a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="tarifa-compra-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-tarifa-compra-tab="alta">Nueva tarifa de compra</button>
            <button type="button" class="subpage-button active" data-tarifa-compra-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-tarifa-compra-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-tarifa-compra-tab-panel="alta">
            <h3>Nueva tarifa de compra</h3>
            <div class="hint">Define el costo negociado con cada transportista por ruta, unidad y tipo de carga. <strong>Importes y dias de credito:</strong> formato Mexico (miles con coma, decimales con punto) al salir del campo. <strong>Enter</strong> pasa al siguiente campo; solo el boton <strong>Guardar tarifa de compra</strong> envia el formulario.</div>
            <form id="tarifa-compra-form">
              <div class="hint form-callout">
                Aquí eliges el <strong>proveedor de transporte</strong> (catálogo de transportistas). No es el nombre de la tarifa de venta.
              </div>
              <div class="two-col">
                <label>Transportista
                  <select id="tarifa-compra-transportista" name="transportista_id" required></select>
                </label>
                <label>Nombre tarifa
                  <input name="nombre_tarifa" required />
                </label>
              </div>
              <div class="two-col">
                <label class="span-2">Tipo transportista (debe coincidir con el transportista)
                  <select id="tarifa-compra-tipo-transportista" name="tipo_transportista">
                    <option value="propio">propio</option>
                    <option value="subcontratado" selected>subcontratado</option>
                    <option value="fletero">fletero</option>
                    <option value="aliado">aliado</option>
                  </select>
                </label>
              </div>
              <div class="three-col">
                <label>Ambito
                  <select name="ambito">
                    <option value="local">local</option>
                    <option value="estatal">estatal</option>
                    <option value="federal" selected>federal</option>
                  </select>
                </label>
                <label>Modalidad
                  <select name="modalidad_cobro">
                    <option value="mixta" selected>mixta</option>
                    <option value="por_viaje">por_viaje</option>
                    <option value="por_km">por_km</option>
                    <option value="por_tonelada">por_tonelada</option>
                    <option value="por_hora">por_hora</option>
                    <option value="por_dia">por_dia</option>
                  </select>
                </label>
                <label>Moneda
                  <input name="moneda" value="MXN" maxlength="3" />
                </label>
              </div>
              <div class="two-col">
                <label>Origen
                  <input name="origen" required />
                </label>
                <label>Destino
                  <input name="destino" required />
                </label>
              </div>
              <div class="two-col">
                <label>Tipo unidad
                  <input name="tipo_unidad" required />
                </label>
                <label>Tipo carga
                  <input name="tipo_carga" />
                </label>
              </div>
              <div class="three-col">
                <label>Tarifa base
                  <input name="tarifa_base" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                </label>
                <label>Tarifa por km
                  <input id="tarifa-compra-alta-tarifa-km" name="tarifa_km" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" title="Formato Mexico (miles con coma, decimales con punto). Minimo 2 decimales visibles como el resto de importes." />
                </label>
                <label>Tarifa por kg
                  <input name="tarifa_kg" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="6" value="0" />
                </label>
              </div>
              <div class="three-col">
                <label>Tarifa por tonelada
                  <input name="tarifa_tonelada" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                </label>
                <label>Tarifa por hora
                  <input name="tarifa_hora" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                </label>
                <label>Tarifa por dia
                  <input name="tarifa_dia" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                </label>
              </div>
              <div class="three-col">
                <label>Recargo minimo
                  <input name="recargo_minimo" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                </label>
                <label>Dias credito
                  <input name="dias_credito" type="text" inputmode="numeric" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="0" value="0" title="Enteros. Miles con coma (es-MX); salga del campo para aplicar formato." />
                </label>
                <label>Estatus
                  <select name="activo">
                    <option value="true" selected>activa</option>
                    <option value="false">inactiva</option>
                  </select>
                </label>
              </div>
              <div class="two-col">
                <label>Vigencia inicio
                  <input name="vigencia_inicio" type="date" title="Opcional. Elige con el calendario para evitar error de formato" />
                </label>
                <label>Vigencia fin
                  <input name="vigencia_fin" type="date" title="Opcional. Elige con el calendario para evitar error de formato" />
                </label>
              </div>
              <p class="hint" style="margin:0;font-size:12px;">Las vigencias son opcionales. Si el navegador muestra «valor no valido», usa el icono del calendario o borra el campo. <strong>Importes y dias de credito:</strong> formato Mexico (miles con coma, decimales con punto); al salir del campo se aplica el formato.</p>
              <label>Observaciones
                <textarea name="observaciones"></textarea>
              </label>
              <button type="submit">Guardar tarifa de compra</button>
            </form>
            <div id="tarifa-compra-message" class="message"></div>
          </article>
          <article class="card" data-tarifa-compra-tab-panel="consulta">
            <h3>Listado de tarifas de compra</h3>
            <div class="toolbar">
              <h4>Consultar tarifas de compra</h4>
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <form id="tarifa-compra-filter-form">
                <div class="three-col">
                  <label>Buscar
                    <input id="tarifa-compra-filter-buscar" name="buscar" type="search" list="tarifa-compra-filter-buscar-dl" placeholder="Nombre, transportista, origen, destino" autocomplete="off" />
                  </label>
                  <label>Transportista
                    <select id="tarifa-compra-filter-transportista" name="transportista_id"></select>
                  </label>
                  <label>Estatus
                    <select id="tarifa-compra-filter-activo" name="activo">
                      <option value="">Todas</option>
                      <option value="true">activas</option>
                      <option value="false">inactivas</option>
                    </select>
                  </label>
                </div>
                <datalist id="tarifa-compra-filter-buscar-dl"></datalist>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="tarifa-compra-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="tarifas-compra-table"></div>
            <div id="tarifa-compra-edit-panel" class="toolbar hidden">
              <h4>Editar tarifa de compra</h4>
              <form id="tarifa-compra-edit-form">
                <input id="tarifa-compra-edit-record-id" name="tarifa_compra_id" type="hidden" autocomplete="off" />
                <div class="two-col">
                  <label>Transportista
                    <select id="edit-tarifa-compra-transportista" name="transportista_id" required></select>
                  </label>
                  <label>Nombre tarifa
                    <input name="nombre_tarifa" required />
                  </label>
                </div>
                <div class="two-col">
                  <label class="span-2">Tipo transportista
                    <select id="edit-tarifa-compra-tipo-transportista" name="tipo_transportista">
                      <option value="propio">propio</option>
                      <option value="subcontratado">subcontratado</option>
                      <option value="fletero">fletero</option>
                      <option value="aliado">aliado</option>
                    </select>
                  </label>
                </div>
                <div class="three-col">
                  <label>Ambito
                    <select name="ambito">
                      <option value="local">local</option>
                      <option value="estatal">estatal</option>
                      <option value="federal">federal</option>
                    </select>
                  </label>
                  <label>Modalidad
                    <select name="modalidad_cobro">
                      <option value="mixta">mixta</option>
                      <option value="por_viaje">por_viaje</option>
                      <option value="por_km">por_km</option>
                      <option value="por_tonelada">por_tonelada</option>
                      <option value="por_hora">por_hora</option>
                      <option value="por_dia">por_dia</option>
                    </select>
                  </label>
                  <label>Moneda
                    <input name="moneda" maxlength="3" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Origen
                    <input name="origen" required />
                  </label>
                  <label>Destino
                    <input name="destino" required />
                  </label>
                </div>
                <div class="two-col">
                  <label>Tipo unidad
                    <input name="tipo_unidad" required />
                  </label>
                  <label>Tipo carga
                    <input name="tipo_carga" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Tarifa base
                    <input name="tarifa_base" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                  </label>
                  <label>Tarifa por km
                    <input id="tarifa-compra-edit-tarifa-km" name="tarifa_km" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" title="Formato Mexico (miles con coma, decimales con punto). Minimo 2 decimales visibles." />
                  </label>
                  <label>Tarifa por kg
                    <input name="tarifa_kg" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="6" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Tarifa por tonelada
                    <input name="tarifa_tonelada" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" />
                  </label>
                  <label>Tarifa por hora
                    <input name="tarifa_hora" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                  <label>Tarifa por dia
                    <input name="tarifa_dia" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Recargo minimo
                    <input name="recargo_minimo" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                  <label>Dias credito
                    <input name="dias_credito" type="text" inputmode="numeric" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="0" title="Enteros. Miles con coma (es-MX); salga del campo para aplicar formato." />
                  </label>
                  <label class="check-row">
                    <input name="activo" type="checkbox" />
                    Tarifa activa
                  </label>
                </div>
                <div class="two-col">
                  <label>Vigencia inicio
                    <input name="vigencia_inicio" type="date" title="Opcional. Elige con el calendario para evitar error de formato" />
                  </label>
                  <label>Vigencia fin
                    <input name="vigencia_fin" type="date" title="Opcional. Elige con el calendario para evitar error de formato" />
                  </label>
                </div>
                <p class="hint" style="margin:0;font-size:12px;">Si aparece error en fecha, borra el campo o usa el calendario. <strong>Importes y dias de credito:</strong> formato Mexico al salir del campo.</p>
                <label>Observaciones
                  <textarea name="observaciones"></textarea>
                </label>
                <div class="toolbar-actions">
                  <button type="submit" id="tarifa-compra-edit-save">Guardar cambios</button>
                  <button type="button" id="tarifa-compra-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="tarifa-compra-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-tarifa-compra-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Tarifas de compra</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Costos negociados por transportista, ruta y modalidad de cobro.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-tarifa-compra-toc" aria-label="Índice del manual de tarifas de compra">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-tarifa-compra-1">1. Objetivo</a>
                <a href="#manual-tarifa-compra-2">2. Subopciones</a>
                <a href="#manual-tarifa-compra-3">3. Nueva tarifa</a>
                <a href="#manual-tarifa-compra-4">4. Consultar</a>
                <a href="#manual-tarifa-compra-5">5. Modalidad y ámbito</a>
                <a href="#manual-tarifa-compra-6">6. FAQ</a>
                <a href="#manual-tarifa-compra-7">7. Mensajes</a>
                <a href="#manual-tarifa-compra-8">8. Referencia</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="tarifa-compra" tabindex="0" role="region" aria-label="Texto del manual de tarifas de compra">
            <h4 id="manual-tarifa-compra-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Registrar el costo de compra acordado con cada transportista por ruta, tipo de unidad y carga, con componentes (base, km, kg, tonelada, hora, día) y días de crédito.</p>
            <h4 id="manual-tarifa-compra-2">2. Subopciones</h4>
            <ul class="summary-list"><li><strong>Nueva tarifa de compra / Consultar:</strong> alta, filtros y edición.</li><li><strong>Manual:</strong> esta guía.</li></ul>
            <h4 id="manual-tarifa-compra-3">3. Nueva tarifa de compra</h4>
            <p class="manual-p">Seleccione transportista, tipo de transportista (debe coincidir con el del transportista; predeterminado subcontratado), nombre de tarifa, ámbito (local/estatal/federal), modalidad de cobro, moneda, origen y destino, tipos, importes y vigencia. Marque activa si aplica.</p>
            <h4 id="manual-tarifa-compra-4">4. Consultar y editar</h4>
            <p class="manual-p">Filtre por transportista y criterios; use <strong>Editar</strong> o <strong>Eliminar</strong> según permisos.</p>
            <h4 id="manual-tarifa-compra-5">5. Modalidad y ámbito</h4>
            <p class="manual-p">Alinee modalidad (por viaje, km, etc.) y <strong>ámbito</strong> (local, estatal, federal) con el contrato real del transportista. Los importes y días de crédito usan <strong>formato México</strong> (miles con coma, decimales con punto) al salir del campo, igual que en el alta.</p>
            <h4 id="manual-tarifa-compra-6">6. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿No sugiere costo en flete?</strong> Verifique transportista, ruta y tarifa activa.</p>
            <h4 id="manual-tarifa-compra-7">7. Mensajes y errores</h4>
            <p class="manual-p">Respuesta del servidor bajo cada formulario.</p>
            <h4 id="manual-tarifa-compra-8">8. Referencia técnica</h4>
            <p class="manual-p"><a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-operadores">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de operadores</h3>
              <div class="hint">Trabaja una parte a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="operador-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-operador-tab="alta">Nuevo operador</button>
            <button type="button" class="subpage-button active" data-operador-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-operador-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-operador-tab-panel="alta">
            <h3>Nuevo operador</h3>
            <div class="hint">Captura basica del chofer para operacion. Los campos principales son obligatorios.</div>
            <form id="operador-form">
              <div class="three-col">
                <label>Transportista
                  <select id="operador-transportista" name="transportista_id"></select>
                </label>
                <label>Tipo contratacion
                  <select name="tipo_contratacion">
                    <option value="">Sin especificar</option>
                    <option value="interno">interno</option>
                    <option value="externo">externo</option>
                  </select>
                </label>
                <label>Estatus documental
                  <select name="estatus_documental">
                    <option value="">Sin especificar</option>
                    <option value="vigente">vigente</option>
                    <option value="vencido">vencido</option>
                    <option value="pendiente">pendiente</option>
                  </select>
                </label>
              </div>
              <div class="three-col">
                <label>Nombre
                  <input name="nombre" required />
                </label>
                <label>Apellido paterno
                  <input name="apellido_paterno" required />
                </label>
                <label>Apellido materno
                  <input name="apellido_materno" />
                </label>
              </div>
              <div class="three-col">
                <label>Fecha nacimiento
                  <input name="fecha_nacimiento" type="date" required />
                </label>
                <label>CURP
                  <input name="curp" minlength="18" maxlength="18" required />
                </label>
                <label>RFC
                  <input name="rfc" maxlength="13" required />
                </label>
              </div>
              <div class="three-col">
                <label>NSS
                  <input name="nss" minlength="11" maxlength="11" required />
                </label>
                <label>Licencia
                  <input name="licencia" />
                </label>
                <label>Tipo licencia
                  <input name="tipo_licencia" />
                </label>
              </div>
              <div class="three-col">
                <label>Vigencia licencia
                  <input name="vigencia_licencia" type="date" />
                </label>
                <label>Estado civil
                  <select name="estado_civil">
                    <option value="soltero">soltero</option>
                    <option value="casado">casado</option>
                    <option value="divorciado">divorciado</option>
                    <option value="viudo">viudo</option>
                    <option value="union_libre">union_libre</option>
                  </select>
                </label>
                <label>Tipo sangre
                  <select name="tipo_sangre">
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                  </select>
                </label>
              </div>
              <div class="two-col">
                <label>Telefono principal
                  <input name="telefono_principal" required />
                </label>
                <label>Telefono emergencia
                  <input name="telefono_emergencia" />
                </label>
              </div>
              <div class="two-col">
                <label>Contacto emergencia
                  <input name="nombre_contacto_emergencia" />
                </label>
                <label>Correo electronico
                  <input name="correo_electronico" type="email" required />
                </label>
              </div>
              <div class="two-col">
                <label>Direccion
                  <input name="direccion" required />
                </label>
                <label>Colonia
                  <input name="colonia" required />
                </label>
              </div>
              <div class="three-col">
                <label>Municipio
                  <input name="municipio" required />
                </label>
                <label>Estado geografico
                  <input name="estado_geografico" required />
                </label>
                <label>Codigo postal
                  <input name="codigo_postal" minlength="5" maxlength="5" required />
                </label>
              </div>
              <div class="two-col">
                <label>Anios experiencia
                  <input name="anios_experiencia" type="number" min="0" step="1" inputmode="numeric" title="Solo numeros enteros" />
                </label>
                <label>Fotografia URL
                  <input name="fotografia" />
                </label>
              </div>
              <div class="two-col">
                <label>Tipos de unidad
                  <input name="tipos_unidad_manejadas" placeholder="torton, tractocamion" />
                </label>
                <label>Tipos de carga
                  <input name="tipos_carga_experiencia" placeholder="seca, paletizada" />
                </label>
              </div>
              <div class="two-col">
                <label>Rutas conocidas
                  <input name="rutas_conocidas" />
                </label>
                <label>Certificaciones
                  <input name="certificaciones" placeholder="Ej. licencia federal, permiso SCT, curso MMPP" title="Texto libre: constancias o capacitaciones relevantes para cumplimiento" />
                </label>
              </div>
              <div class="three-col">
                <label>Ultima revision medica
                  <input name="ultima_revision_medica" type="date" />
                </label>
                <label>Proxima revision medica
                  <input name="proxima_revision_medica" type="date" />
                </label>
                <label class="check-row">
                  <input name="resultado_apto" type="checkbox" />
                  Resultado apto
                </label>
              </div>
              <div class="two-col">
                <label>Puntualidad
                  <input name="puntualidad" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="2" placeholder="0 a 100" title="0–100. En Mexico puede usar coma o punto como decimal; al salir del campo se aplica formato es-MX." />
                </label>
                <label>Calificacion general
                  <input name="calificacion_general" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="2" placeholder="0 a 100" title="0–100. Coma o punto decimal; formato es-MX al salir." />
                </label>
              </div>
              <div class="two-col">
                <label>Consumo diesel (prom.)
                  <input name="consumo_diesel_promedio" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="2" placeholder="ej. km/L" title="Promedio con unidades diesel (tractocamion, etc.); coma o punto decimal; formato Mexico al salir." />
                </label>
                <label>Consumo gasolina (prom.)
                  <input name="consumo_gasolina_promedio" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="2" placeholder="ej. km/L" title="Promedio con unidades de gasolina; coma o punto decimal; formato Mexico al salir." />
                </label>
              </div>
              <label>Restricciones medicas
                <input name="restricciones_medicas" />
              </label>
              <label>Incidencias de desempeno
                <input name="incidencias_desempeno" />
              </label>
              <label>Comentarios de desempeno
                <textarea name="comentarios_desempeno"></textarea>
              </label>
              <button type="submit">Guardar operador</button>
            </form>
            <div id="operador-message" class="message"></div>
          </article>
          <article class="card" data-operador-tab-panel="consulta">
            <h3>Consultar y editar</h3>
            <div class="hint">Tabla de choferes registrados (filtro solo en pantalla; no borra datos). Si falta alguien, vacie el buscador o use <strong>Limpiar busqueda</strong>. Pulse <strong>Editar</strong> en una fila para el formulario debajo; el alta nuevo sigue en <strong>Nuevo operador</strong>.</div>
            <div class="toolbar">
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <label>Buscar rapido (nombre, CURP, telefono, certificaciones, transportista, ID)
                <input id="operador-filter-buscar" type="search" list="operador-filter-buscar-dl" placeholder="Filtra la tabla mientras escribes" autocomplete="off" style="max-width:28rem" />
              </label>
              <datalist id="operador-filter-buscar-dl"></datalist>
              <div class="toolbar-actions">
                <button type="button" id="operador-filter-clear" class="secondary-button">Limpiar busqueda</button>
              </div>
            </div>
            <div id="operadores-table"></div>
            <div id="operador-edit-panel" class="toolbar hidden" aria-hidden="true">
              <h4>Editar operador seleccionado</h4>
              <p class="hint">Los cambios se guardan con el boton inferior. Para alta de otro operador use <strong>Nuevo operador</strong>.</p>
              <form id="operador-edit-form">
              <input type="hidden" name="id_operador" id="operador-edit-form-id" autocomplete="off" />
              <div class="three-col">
                <label>Transportista
                  <select id="edit-operador-transportista" name="transportista_id"></select>
                </label>
                <label>Tipo contratacion
                  <select name="tipo_contratacion">
                    <option value="">Sin especificar</option>
                    <option value="interno">interno</option>
                    <option value="externo">externo</option>
                  </select>
                </label>
                <label>Estatus documental
                  <select name="estatus_documental">
                    <option value="">Sin especificar</option>
                    <option value="vigente">vigente</option>
                    <option value="vencido">vencido</option>
                    <option value="pendiente">pendiente</option>
                  </select>
                </label>
              </div>
              <div class="three-col">
                <label>Nombre
                  <input name="nombre" required />
                </label>
                <label>Apellido paterno
                  <input name="apellido_paterno" required />
                </label>
                <label>Apellido materno
                  <input name="apellido_materno" />
                </label>
              </div>
              <div class="three-col">
                <label>Fecha nacimiento
                  <input name="fecha_nacimiento" type="date" required />
                </label>
                <label>CURP
                  <input name="curp" minlength="18" maxlength="18" required />
                </label>
                <label>RFC
                  <input name="rfc" maxlength="13" required />
                </label>
              </div>
              <div class="three-col">
                <label>NSS
                  <input name="nss" minlength="11" maxlength="11" required />
                </label>
                <label>Licencia
                  <input name="licencia" />
                </label>
                <label>Tipo licencia
                  <input name="tipo_licencia" />
                </label>
              </div>
              <div class="three-col">
                <label>Vigencia licencia
                  <input name="vigencia_licencia" type="date" />
                </label>
                <label>Estado civil
                  <select name="estado_civil">
                    <option value="soltero">soltero</option>
                    <option value="casado">casado</option>
                    <option value="divorciado">divorciado</option>
                    <option value="viudo">viudo</option>
                    <option value="union_libre">union_libre</option>
                  </select>
                </label>
                <label>Tipo sangre
                  <select name="tipo_sangre">
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                  </select>
                </label>
              </div>
              <div class="two-col">
                <label>Telefono principal
                  <input name="telefono_principal" required />
                </label>
                <label>Telefono emergencia
                  <input name="telefono_emergencia" />
                </label>
              </div>
              <div class="two-col">
                <label>Contacto emergencia
                  <input name="nombre_contacto_emergencia" />
                </label>
                <label>Correo electronico
                  <input name="correo_electronico" type="email" required />
                </label>
              </div>
              <div class="two-col">
                <label>Direccion
                  <input name="direccion" required />
                </label>
                <label>Colonia
                  <input name="colonia" required />
                </label>
              </div>
              <div class="three-col">
                <label>Municipio
                  <input name="municipio" required />
                </label>
                <label>Estado geografico
                  <input name="estado_geografico" required />
                </label>
                <label>Codigo postal
                  <input name="codigo_postal" minlength="5" maxlength="5" required />
                </label>
              </div>
              <div class="two-col">
                <label>Anios experiencia
                  <input name="anios_experiencia" type="number" min="0" step="1" inputmode="numeric" title="Solo numeros enteros" />
                </label>
                <label>Fotografia URL
                  <input name="fotografia" />
                </label>
              </div>
              <div class="two-col">
                <label>Tipos de unidad
                  <input name="tipos_unidad_manejadas" placeholder="torton, tractocamion" />
                </label>
                <label>Tipos de carga
                  <input name="tipos_carga_experiencia" placeholder="seca, paletizada" />
                </label>
              </div>
              <div class="two-col">
                <label>Rutas conocidas
                  <input name="rutas_conocidas" />
                </label>
                <label>Certificaciones
                  <input name="certificaciones" placeholder="Ej. licencia federal, permiso SCT, curso MMPP" title="Texto libre: constancias o capacitaciones relevantes para cumplimiento" />
                </label>
              </div>
              <div class="three-col">
                <label>Ultima revision medica
                  <input name="ultima_revision_medica" type="date" />
                </label>
                <label>Proxima revision medica
                  <input name="proxima_revision_medica" type="date" />
                </label>
                <label class="check-row">
                  <input name="resultado_apto" type="checkbox" />
                  Resultado apto
                </label>
              </div>
              <div class="two-col">
                <label>Puntualidad
                  <input name="puntualidad" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="2" placeholder="0 a 100" title="0–100. En Mexico puede usar coma o punto como decimal; al salir del campo se aplica formato es-MX." />
                </label>
                <label>Calificacion general
                  <input name="calificacion_general" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="2" placeholder="0 a 100" title="0–100. Coma o punto decimal; formato es-MX al salir." />
                </label>
              </div>
              <div class="two-col">
                <label>Consumo diesel (prom.)
                  <input name="consumo_diesel_promedio" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="2" placeholder="ej. km/L" title="Promedio con unidades diesel (tractocamion, etc.); coma o punto decimal; formato Mexico al salir." />
                </label>
                <label>Consumo gasolina (prom.)
                  <input name="consumo_gasolina_promedio" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="2" placeholder="ej. km/L" title="Promedio con unidades de gasolina; coma o punto decimal; formato Mexico al salir." />
                </label>
              </div>
              <label>Restricciones medicas
                <input name="restricciones_medicas" />
              </label>
              <label>Incidencias de desempeno
                <input name="incidencias_desempeno" />
              </label>
              <label>Comentarios de desempeno
                <textarea name="comentarios_desempeno"></textarea>
              </label>
              <div class="toolbar-actions">
                <button type="submit">Guardar cambios</button>
                <button type="button" id="operador-edit-cancel" class="secondary-button">Cancelar</button>
              </div>
            </form>
            <div id="operador-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-operador-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Operadores</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Expediente del chofer: datos personales, licencia, afiliación y desempeño.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-operador-toc" aria-label="Índice del manual de operadores">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-operador-1">1. Objetivo</a>
                <a href="#manual-operador-2">2. Subopciones</a>
                <a href="#manual-operador-3">3. Nuevo operador</a>
                <a href="#manual-operador-4">4. Consultar y editar</a>
                <a href="#manual-operador-5">5. FAQ</a>
                <a href="#manual-operador-6">6. Mensajes</a>
                <a href="#manual-operador-7">7. Referencia</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="operador" tabindex="0" role="region" aria-label="Texto del manual de operadores">
            <h4 id="manual-operador-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Registrar operadores con vínculo al transportista, identificación oficial, licencia, datos de contacto, salud y métricas de desempeño para asignaciones.</p>
            <h4 id="manual-operador-2">2. Subopciones</h4>
            <ul class="summary-list"><li><strong>Nuevo operador:</strong> alta.</li><li><strong>Consultar y editar:</strong> listado con boton <strong>Editar</strong> y formulario debajo; los cambios se envian como actualizacion parcial (ver <a href="/docs">/docs</a>, operadores).</li><li><strong>Manual:</strong> esta guía.</li></ul>
            <h4 id="manual-operador-3">3. Nuevo operador</h4>
            <p class="manual-p">Complete transportista, tipo de contratación, datos personales, CURP, RFC, NSS, licencia, contactos, domicilio, referencias y campos de desempeño según política.</p>
            <p class="manual-p"><strong>Certificaciones:</strong> texto libre para anotar constancias o cursos (p. ej. licencia federal vigente, permisos estatales, capacitación en materiales peligrosos). Sirve para trazabilidad; la validación documental al registrar salida de despacho usa reglas adicionales sobre licencia y apto médico.</p>
            <h4 id="manual-operador-4">4. Consultar y editar</h4>
            <p class="manual-p">El listado muestra nombre, transportista, CURP, teléfono, certificaciones y la columna <strong>Acciones</strong>. Pulse <strong>Editar</strong> para desplegar el formulario debajo del listado; <strong>Guardar cambios</strong> actualiza el expediente vía API. El alta de un operador nuevo solo esta en la subopcion <strong>Nuevo operador</strong>.</p>
            <h4 id="manual-operador-5">5. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿No aparece en asignación?</strong> Verifique que esté guardado y activo según reglas internas. <strong>¿Bloqueo de salida en Seguimiento?</strong> Complete tipo y vigencia de licencia, estatus documental y datos del expediente; parte del checklist puede considerar licencia federal tipo B/E según la configuración del sistema.</p>
            <h4 id="manual-operador-6">6. Mensajes y errores</h4>
            <p class="manual-p">Validaciones del servidor (CURP, NSS, etc.).</p>
            <h4 id="manual-operador-7">7. Referencia técnica</h4>
            <p class="manual-p"><a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-unidades">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de unidades</h3>
              <div class="hint">Trabaja una parte a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="unidad-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-unidad-tab="alta">Nueva unidad</button>
            <button type="button" class="subpage-button active" data-unidad-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-unidad-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-unidad-tab-panel="alta">
            <h3>Nueva unidad</h3>
            <div class="hint">Vehiculos disponibles para asignacion operativa.</div>
            <form id="unidad-form">
              <div class="three-col">
                <label>Transportista
                  <select id="unidad-transportista" name="transportista_id"></select>
                </label>
                <label>Tipo propiedad
                  <select name="tipo_propiedad">
                    <option value="">Sin especificar</option>
                    <option value="propia">propia</option>
                    <option value="tercero">tercero</option>
                  </select>
                </label>
                <label>Estatus documental
                  <select name="estatus_documental">
                    <option value="">Sin especificar</option>
                    <option value="vigente">vigente</option>
                    <option value="vencido">vencido</option>
                    <option value="pendiente">pendiente</option>
                  </select>
                </label>
              </div>
              <div class="two-col">
                <label>Economico
                  <input name="economico" required />
                </label>
                <label>Placas
                  <input name="placas" />
                </label>
              </div>
              <label>Descripcion
                <input name="descripcion" />
              </label>
              <label>Detalle
                <textarea name="detalle"></textarea>
              </label>
              <div class="two-col">
                <label>Vigencia permiso SCT
                  <input name="vigencia_permiso_sct" type="date" />
                </label>
                <label>Vigencia seguro
                  <input name="vigencia_seguro" type="date" />
                </label>
              </div>
              <label class="check-row">
                <input name="activo" type="checkbox" checked />
                Unidad activa
              </label>
              <button type="submit">Guardar unidad</button>
            </form>
            <div id="unidad-message" class="message"></div>
          </article>
          <article class="card" data-unidad-tab-panel="consulta">
            <h3>Consultar y editar</h3>
            <div class="hint">Filtros solo en pantalla (no borran datos en el servidor). Si no ve una unidad, deje en <strong>Todos</strong> tipo de propiedad, estatus documental y activo, vacie el buscador y pulse <strong>Limpiar filtros</strong>. El modo de busqueda de texto es compartido con otros modulos del panel. <strong>Editar</strong> abre el formulario debajo; <strong>Eliminar</strong> borra la fila si no tiene asignaciones vinculadas (pide confirmacion). El alta nueva esta en <strong>Nueva unidad</strong>.</div>
            <div class="toolbar">
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <label>Buscar rapido (economico, placas, descripcion, transportista, ID)
                <input id="unidad-filter-buscar" type="search" list="unidad-filter-buscar-dl" placeholder="Filtra la tabla mientras escribes" autocomplete="off" style="max-width:28rem" />
              </label>
              <datalist id="unidad-filter-buscar-dl"></datalist>
              <div class="three-col">
                <label>Tipo propiedad
                  <select id="unidad-filter-tipo-propiedad">
                    <option value="">Todos</option>
                    <option value="propia">propia</option>
                    <option value="tercero">tercero</option>
                  </select>
                </label>
                <label>Estatus documental
                  <select id="unidad-filter-estatus-doc">
                    <option value="">Todos</option>
                    <option value="vigente">vigente</option>
                    <option value="vencido">vencido</option>
                    <option value="pendiente">pendiente</option>
                  </select>
                </label>
                <label>Activo
                  <select id="unidad-filter-activo">
                    <option value="">Todos</option>
                    <option value="true">activa</option>
                    <option value="false">inactiva</option>
                  </select>
                </label>
              </div>
              <div class="toolbar-actions">
                <button type="button" id="unidad-filter-clear" class="secondary-button">Limpiar filtros</button>
                <button type="button" id="unidad-recargar-catalogo" class="secondary-button" title="Vuelve a pedir las unidades al servidor">Recargar catalogo</button>
              </div>
            </div>
            <div id="unidad-consulta-message" class="message" role="status" aria-live="polite"></div>
            <div id="unidades-table"></div>
            <div id="unidad-edit-panel" class="toolbar hidden" aria-hidden="true">
              <h4>Editar unidad seleccionada</h4>
              <p class="hint">Al guardar, la API devuelve fechas de alta y ultima actualizacion para auditoria; combine con filtros de la tabla para segmentar consultas.</p>
              <form id="unidad-edit-form">
              <input type="hidden" name="id_unidad" id="unidad-edit-form-id" autocomplete="off" />
              <div class="three-col">
                <label>Transportista
                  <select id="edit-unidad-transportista" name="transportista_id"></select>
                </label>
                <label>Tipo propiedad
                  <select name="tipo_propiedad">
                    <option value="">Sin especificar</option>
                    <option value="propia">propia</option>
                    <option value="tercero">tercero</option>
                  </select>
                </label>
                <label>Estatus documental
                  <select name="estatus_documental">
                    <option value="">Sin especificar</option>
                    <option value="vigente">vigente</option>
                    <option value="vencido">vencido</option>
                    <option value="pendiente">pendiente</option>
                  </select>
                </label>
              </div>
              <div class="two-col">
                <label>Economico
                  <input name="economico" required />
                </label>
                <label>Placas
                  <input name="placas" />
                </label>
              </div>
              <label>Descripcion
                <input name="descripcion" />
              </label>
              <label>Detalle
                <textarea name="detalle"></textarea>
              </label>
              <div class="two-col">
                <label>Vigencia permiso SCT
                  <input name="vigencia_permiso_sct" type="date" />
                </label>
                <label>Vigencia seguro
                  <input name="vigencia_seguro" type="date" />
                </label>
              </div>
              <label class="check-row">
                <input name="activo" type="checkbox" />
                Unidad activa
              </label>
              <div class="toolbar-actions">
                <button type="submit">Guardar cambios</button>
                <button type="button" id="unidad-edit-cancel" class="secondary-button">Cancelar</button>
              </div>
            </form>
            <div id="unidad-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-unidad-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Unidades</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Vehículos económico/placas ligados a transportista para asignación.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-unidad-toc" aria-label="Índice del manual de unidades">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-unidad-1">1. Objetivo</a>
                <a href="#manual-unidad-2">2. Subopciones</a>
                <a href="#manual-unidad-3">3. Nueva unidad</a>
                <a href="#manual-unidad-4">4. Consulta</a>
                <a href="#manual-unidad-5">5. FAQ</a>
                <a href="#manual-unidad-6">6. Mensajes</a>
                <a href="#manual-unidad-7">7. Referencia</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="unidad" tabindex="0" role="region" aria-label="Texto del manual de unidades">
            <h4 id="manual-unidad-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Catalogar unidades (económico, placas, descripción) con transportista, tipo de propiedad y estatus documental.</p>
            <h4 id="manual-unidad-2">2. Subopciones</h4>
            <ul class="summary-list"><li><strong>Nueva unidad / Consultar y editar:</strong> alta, tabla con filtros, <strong>Editar</strong> y <strong>Eliminar</strong> (con confirmación).</li><li><strong>Manual:</strong> esta guía.</li></ul>
            <h4 id="manual-unidad-3">3. Nueva unidad</h4>
            <p class="manual-p">Seleccione transportista, capture económico y placas, tipo de propiedad, estatus documental, descripción, vigencias de permiso SCT y de seguro, detalle y marque <strong>Unidad activa</strong> si aplica.</p>
            <h4 id="manual-unidad-4">4. Consulta</h4>
            <p class="manual-p">Tabla con columnas de documentación y vigencias; use el buscado rápido y los filtros (tipo de propiedad, estatus documental, activo) para segmentar. <strong>Editar</strong> abre el formulario inferior; <strong>Eliminar</strong> pide confirmación y solo procede si la unidad no tiene asignaciones vinculadas. Al guardar edición, la API mantiene fechas de alta y última actualización para auditoría e informes.</p>
            <h4 id="manual-unidad-5">5. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿Unidad inactiva?</strong> No debería usarse en nuevas asignaciones según su política. <strong>¿Validación de cumplimiento?</strong> Registre vigencias de <strong>permiso SCT</strong> y <strong>seguro</strong>; el sistema puede contrastarlas al autorizar salida en Seguimiento.</p>
            <h4 id="manual-unidad-6">6. Mensajes y errores</h4>
            <p class="manual-p">Respuesta del servidor bajo el formulario.</p>
            <h4 id="manual-unidad-7">7. Referencia técnica</h4>
            <p class="manual-p"><a href="/docs">/docs</a>. Listado <code>GET /unidades</code> admite <code>activo</code>, <code>buscar</code>, <code>transportista_id</code>, <code>tipo_propiedad</code> y <code>estatus_documental</code> para reportes o integraciones.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-gastos">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de gastos de viaje</h3>
              <div class="hint">Alta de gastos, consulta y edición del listado; en la misma vista, presupuesto y liquidación por flete.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="gasto-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-gasto-tab="alta">Nuevo gasto</button>
            <button type="button" class="subpage-button active" data-gasto-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-gasto-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-gasto-tab-panel="alta">
            <h3>Nuevo gasto de viaje</h3>
            <div class="hint">Cada gasto actualiza el <strong>costo real</strong> y el <strong>margen real</strong> del flete. Elija la <strong>categoría</strong> alineada al presupuesto y a la liquidación (operación propia: combustible, peajes, viáticos, operador, mantenimiento; terceros: pago a transportista; imprevistos y administrativos cuando aplique).</div>
            <form id="gasto-form">
              <div class="two-col">
                <label>Flete
                  <select id="gasto-flete" name="flete_id" required></select>
                </label>
                <label>Categoría de gasto
                  <select id="gasto-tipo-gasto" name="tipo_gasto" required>
                    <option value="">Seleccione…</option>
                    <option value="combustible">Combustible (diesel)</option>
                    <option value="peajes">Peajes / casetas</option>
                    <option value="viaticos">Viáticos operador</option>
                    <option value="operador">Mano de obra operador</option>
                    <option value="mantenimiento_km">Mantenimiento y desgaste (por km)</option>
                    <option value="imprevistos">Imprevistos (grúa, multas, ponchaduras…)</option>
                    <option value="administrativos">Administrativos del viaje (CP, seguro carga…)</option>
                    <option value="pago_transporte_tercero">Pago a transportista (subcontratado / fletero / aliado)</option>
                    <option value="otros">Otros (detalle en descripción)</option>
                  </select>
                </label>
              </div>
              <div class="two-col">
                <label>Monto
                  <input name="monto" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                </label>
                <label>Fecha gasto
                  <input name="fecha_gasto" type="date" required />
                </label>
              </div>
              <div class="two-col">
                <label>Referencia
                  <input name="referencia" />
                </label>
                <label>Comprobante URL
                  <input name="comprobante" />
                </label>
              </div>
              <label>Descripción (opcional, recomendada en «Otros» o para folio/ticket)
                <textarea name="descripcion" placeholder="Ej. folio caseta, litros, estación, incidencia…"></textarea>
              </label>
              <button type="submit">Guardar gasto</button>
            </form>
            <div id="gasto-message" class="message"></div>
          </article>
          <article class="card" data-gasto-tab-panel="consulta">
            <h3>Listado de gastos de viaje</h3>
            <div class="toolbar">
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <label>Buscar rapido (flete, tipo, referencia, monto, ID)
                <input id="gasto-filter-buscar" type="search" list="gasto-filter-buscar-dl" placeholder="Filtra la tabla mientras escribes" autocomplete="off" style="max-width:28rem" />
              </label>
              <datalist id="gasto-filter-buscar-dl"></datalist>
            </div>
            <div id="gasto-list-message" class="message"></div>
            <div id="gastos-table"></div>
            <div id="gasto-edit-panel" class="toolbar hidden">
              <h4>Editar gasto de viaje</h4>
              <form id="gasto-edit-form">
                <input name="id" type="hidden" />
                <div class="two-col">
                  <label>Flete
                    <select id="edit-gasto-flete" name="flete_id" required></select>
                  </label>
                  <label>Categoría de gasto
                    <select id="edit-gasto-tipo-gasto" name="tipo_gasto" required>
                      <option value="combustible">Combustible (diesel)</option>
                      <option value="peajes">Peajes / casetas</option>
                      <option value="viaticos">Viáticos operador</option>
                      <option value="operador">Mano de obra operador</option>
                      <option value="mantenimiento_km">Mantenimiento y desgaste (por km)</option>
                      <option value="imprevistos">Imprevistos (grúa, multas, ponchaduras…)</option>
                      <option value="administrativos">Administrativos del viaje (CP, seguro carga…)</option>
                      <option value="pago_transporte_tercero">Pago a transportista (subcontratado / fletero / aliado)</option>
                      <option value="otros">Otros (detalle en descripción)</option>
                    </select>
                  </label>
                </div>
                <div class="two-col">
                  <label>Monto
                    <input name="monto" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                  </label>
                  <label>Fecha gasto
                    <input name="fecha_gasto" type="date" required />
                  </label>
                </div>
                <div class="two-col">
                  <label>Referencia
                    <input name="referencia" />
                  </label>
                  <label>Comprobante URL
                    <input name="comprobante" />
                  </label>
                </div>
                <label>Descripción
                  <textarea name="descripcion" placeholder="Ej. folio, ticket, incidencia…"></textarea>
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="gasto-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="gasto-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card" data-gasto-tab-panel="consulta">
            <h3>Presupuesto y liquidación</h3>
            <div class="hint">Operación <strong>propia</strong>: genera presupuesto desglosado (combustible, peajes, viáticos, operador, mantenimiento, contingencia). <strong>Terceros</strong>: una línea con costo de transporte estimado. Compare con gastos reales capturados.</div>
            <div class="two-col" style="margin-top:0.75rem;">
              <label>Flete
                <select id="gasto-control-flete"></select>
              </label>
              <div class="row-actions" style="align-items:flex-end;padding-top:1.4rem;">
                <button type="button" class="secondary-button" id="gasto-presupuesto-generar">Generar presupuesto</button>
                <button type="button" class="secondary-button" id="gasto-liquidacion-ver">Ver liquidación</button>
              </div>
            </div>
            <pre id="gasto-control-output" class="hint" style="white-space:pre-wrap;max-height:22rem;overflow:auto;margin-top:0.75rem;font-size:0.85rem;"></pre>
          </article>
          <article class="card hidden manual-doc manual-interface" data-gasto-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Gastos de viaje</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Costos reales por flete que actualizan margen real.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-gasto-toc" aria-label="Índice del manual de gastos">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-gasto-1">1. Objetivo</a>
                <a href="#manual-gasto-2">2. Subopciones</a>
                <a href="#manual-gasto-3">3. Nuevo gasto</a>
                <a href="#manual-gasto-4">4. Lista de gastos</a>
                <a href="#manual-gasto-5">5. Presupuesto y liquidación</a>
                <a href="#manual-gasto-6">6. Preguntas frecuentes</a>
                <a href="#manual-gasto-7">7. Mensajes y errores</a>
                <a href="#manual-gasto-8">8. Referencia técnica</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="gasto" tabindex="0" role="region" aria-label="Texto del manual de gastos">
            <div class="manual-note"><strong>Misma vista “Consultar y editar”:</strong> debajo del listado de gastos aparece el bloque <strong>Presupuesto y liquidación</strong> (select de flete y botones). No es una pestaña aparte: permanezca en <strong>Consultar y editar</strong> para ver ambos.</div>
            <h4 id="manual-gasto-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Registrar gastos reales (combustible, peajes, viáticos, pago a terceros, etc.) ligados a un flete, actualizar <strong>costo real</strong> y <strong>margen real</strong>, y contrastar con presupuesto y liquidación operativa.</p>
            <h4 id="manual-gasto-2">2. Subopciones</h4>
            <ul class="summary-list">
              <li><strong>Nuevo gasto:</strong> alta de un movimiento de costo por flete y categoría.</li>
              <li><strong>Consultar y editar:</strong> buscador de texto (comparte modo de búsqueda con otros módulos), tabla con <strong>Editar</strong> y <strong>Eliminar</strong>, y debajo el área <strong>Presupuesto y liquidación</strong>.</li>
              <li><strong>Manual:</strong> esta guía.</li>
            </ul>
            <h4 id="manual-gasto-3">3. Nuevo gasto</h4>
            <p class="manual-p">Seleccione <strong>Flete</strong> y <strong>categoría de gasto</strong> alineada al presupuesto (operación propia: combustible, peajes, viáticos, operador, mantenimiento; terceros: pago a transportista; imprevistos y administrativos cuando aplique). Capture monto, fecha, referencia, URL de comprobante si aplica y descripción; en <strong>Otros</strong> el detalle en descripción es especialmente importante.</p>
            <h4 id="manual-gasto-4">4. Lista de gastos</h4>
            <p class="manual-p">El listado filtra mientras escribe en <strong>Buscar rápido</strong>. <strong>Editar</strong> abre el panel inferior; <strong>Eliminar</strong> pide confirmación y al quitar un gasto el sistema recalcula el costo real del flete.</p>
            <h4 id="manual-gasto-5">5. Presupuesto y liquidación</h4>
            <p class="manual-p">En la misma página que el listado, elija el <strong>Flete</strong> en el selector dedicado y pulse <strong>Generar presupuesto</strong> (desglose para operación propia o línea de costo de transporte para terceros). <strong>Ver liquidación</strong> compara presupuesto frente a gastos capturados y muestra alertas si el real excede al presupuesto en más del 5 % (ajuste según reglas del motor en servidor).</p>
            <h4 id="manual-gasto-6">6. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿No cambia el margen?</strong> Confirme guardado del gasto y que el flete sea el correcto. <strong>¿No veo presupuesto?</strong> Baje en la misma pestaña <strong>Consultar y editar</strong> tras la tabla. <strong>¿Listado vacío?</strong> Verifique filtro de búsqueda y que existan gastos para ese flete.</p>
            <h4 id="manual-gasto-7">7. Mensajes y errores</h4>
            <p class="manual-p">Respuesta del servidor bajo el formulario de alta o edición.</p>
            <h4 id="manual-gasto-8">8. Referencia técnica</h4>
            <p class="manual-p">Rutas de gastos, presupuesto y liquidación en <a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-asignaciones">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de asignaciones</h3>
              <div class="hint">Alta de asignacion o consulta y edicion del listado.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="asignacion-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-asignacion-tab="alta">Nueva asignacion</button>
            <button type="button" class="subpage-button active" data-asignacion-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-asignacion-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-asignacion-tab-panel="alta">
            <h3>Nueva asignacion</h3>
            <div class="hint">Conecta operador, unidad y viaje. Operadores y unidades existentes se cargan automaticamente.</div>
            <form id="asignacion-form">
              <div class="three-col">
                <label>Operador
                  <select id="asignacion-operador" name="id_operador" required></select>
                </label>
                <label>Unidad
                  <select id="asignacion-unidad" name="id_unidad" required></select>
                </label>
                <label>Viaje
                  <select id="asignacion-viaje" name="id_viaje" required></select>
                </label>
              </div>
              <div class="three-col">
                <label>Fecha salida
                  <input name="fecha_salida" type="datetime-local" required />
                </label>
                <label>Fecha regreso
                  <input name="fecha_regreso" type="datetime-local" />
                </label>
                <label>Km inicial
                  <input name="km_inicial" type="number" step="0.01" min="0" />
                </label>
              </div>
              <div class="two-col">
                <label>Km final
                  <input name="km_final" type="number" step="0.01" min="0" />
                </label>
                <label>Rendimiento combustible
                  <input name="rendimiento_combustible" type="number" step="0.001" min="0" />
                </label>
              </div>
              <button type="submit">Guardar asignacion</button>
            </form>
            <div id="asignacion-message" class="message"></div>
          </article>
          <article class="card" data-asignacion-tab-panel="consulta">
            <h3>Listado de asignaciones</h3>
            <div class="toolbar">
              <h4>Consultar asignaciones</h4>
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <form id="asignacion-filter-form">
                <div class="two-col">
                  <label class="span-2">Buscar rapido
                    <input id="asignacion-filter-buscar" name="buscar" type="search" list="asignacion-filter-buscar-dl" placeholder="Operador, economico, codigo viaje o ID" autocomplete="off" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Operador
                    <select id="asignacion-filter-operador" name="id_operador"></select>
                  </label>
                  <label>Unidad
                    <select id="asignacion-filter-unidad" name="id_unidad"></select>
                  </label>
                  <label>Viaje
                    <select id="asignacion-filter-viaje" name="id_viaje"></select>
                  </label>
                </div>
                <datalist id="asignacion-filter-buscar-dl"></datalist>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="asignacion-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="asignaciones-table"></div>
            <div id="asignacion-edit-panel" class="toolbar hidden">
              <h4>Editar asignacion</h4>
              <form id="asignacion-edit-form">
                <input name="id_asignacion" type="hidden" />
                <div class="three-col">
                  <label>Operador
                    <select id="edit-asignacion-operador" name="id_operador" required></select>
                  </label>
                  <label>Unidad
                    <select id="edit-asignacion-unidad" name="id_unidad" required></select>
                  </label>
                  <label>Viaje
                    <select id="edit-asignacion-viaje" name="id_viaje" required></select>
                  </label>
                </div>
                <div class="three-col">
                  <label>Fecha salida
                    <input name="fecha_salida" type="datetime-local" required />
                  </label>
                  <label>Fecha regreso
                    <input name="fecha_regreso" type="datetime-local" />
                  </label>
                  <label>Km inicial
                    <input name="km_inicial" type="number" step="0.01" min="0" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Km final
                    <input name="km_final" type="number" step="0.01" min="0" />
                  </label>
                  <label>Rendimiento combustible
                    <input name="rendimiento_combustible" type="number" step="0.001" min="0" />
                  </label>
                </div>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="asignacion-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="asignacion-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-asignacion-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Asignaciones</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Vincula operador, unidad y viaje con fechas y kilometraje.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-asignacion-toc" aria-label="Índice del manual de asignaciones">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-asignacion-1">1. Objetivo</a>
                <a href="#manual-asignacion-2">2. Subopciones</a>
                <a href="#manual-asignacion-3">3. Nueva asignación</a>
                <a href="#manual-asignacion-4">4. Consultar y editar</a>
                <a href="#manual-asignacion-5">5. Filtros</a>
                <a href="#manual-asignacion-6">6. FAQ</a>
                <a href="#manual-asignacion-7">7. Mensajes</a>
                <a href="#manual-asignacion-8">8. Referencia</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="asignacion" tabindex="0" role="region" aria-label="Texto del manual de asignaciones">
            <h4 id="manual-asignacion-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Crear la tripleta operador–unidad–viaje con ventana de salida/regreso y lecturas de kilometraje y rendimiento.</p>
            <h4 id="manual-asignacion-2">2. Subopciones</h4>
            <ul class="summary-list"><li><strong>Nueva asignación:</strong> alta.</li><li><strong>Consultar y editar:</strong> filtros por operador, unidad y viaje.</li><li><strong>Manual:</strong> esta guía.</li></ul>
            <h4 id="manual-asignacion-3">3. Nueva asignación</h4>
            <p class="manual-p">Elija <strong>operador</strong>, <strong>unidad</strong> y <strong>viaje</strong>; registre <strong>fecha salida</strong> (obligatoria), fecha de regreso si aplica, km inicial/final y rendimiento de combustible según su política.</p>
            <h4 id="manual-asignacion-4">4. Consultar y editar</h4>
            <p class="manual-p">Filtre por operador, unidad y viaje; use <strong>Buscar rápido</strong> (económico, código de viaje, etc.) con el mismo <strong>modo de búsqueda</strong> que otros listados del panel. <strong>Editar</strong> abre el panel inferior para actualizar fechas y kilometraje.</p>
            <h4 id="manual-asignacion-5">5. Filtros</h4>
            <p class="manual-p"><strong>Aplicar filtro</strong> y <strong>Limpiar</strong> ajustan la tabla y cierran edición si aplica. Las asignaciones sirven de base para <strong>Despachos → Nuevo despacho</strong>.</p>
            <h4 id="manual-asignacion-6">6. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿Selectores vacíos?</strong> Cree operadores, unidades y viajes primero y recargue (F5). <strong>¿No puedo crear despacho?</strong> Debe existir una asignación vigente en catálogo; verifique en Despachos los filtros.</p>
            <h4 id="manual-asignacion-7">7. Mensajes y errores</h4>
            <p class="manual-p">Respuesta del servidor en el panel de mensajes.</p>
            <h4 id="manual-asignacion-8">8. Referencia técnica</h4>
            <p class="manual-p"><a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-despachos">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de despachos</h3>
              <div class="hint">Programacion de despacho o consulta y edicion del listado.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="despacho-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-despacho-tab="alta">Nuevo despacho</button>
            <button type="button" class="subpage-button active" data-despacho-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-despacho-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-despacho-tab-panel="alta">
            <h3>Nuevo despacho</h3>
            <div class="hint">Programa la operacion usando una asignacion y, si aplica, un flete.</div>
            <form id="despacho-form">
              <div class="two-col">
                <label>Asignacion
                  <select id="despacho-asignacion" name="id_asignacion" required></select>
                </label>
                <label>Flete
                  <select id="despacho-flete" name="id_flete"></select>
                </label>
              </div>
              <label>Salida programada
                <input name="salida_programada" type="datetime-local" />
              </label>
              <label>Observaciones de transito
                <textarea name="observaciones_transito"></textarea>
              </label>
              <button type="submit">Crear despacho</button>
            </form>
            <div id="despacho-message" class="message"></div>
          </article>
          <article class="card" data-despacho-tab-panel="consulta">
            <h3>Listado de despachos</h3>
            <div class="toolbar">
              <h4>Consultar despachos</h4>
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <form id="despacho-filter-form">
                <div class="two-col">
                  <label class="span-2">Buscar rapido
                    <input id="despacho-filter-buscar" name="buscar" type="search" list="despacho-filter-buscar-dl" placeholder="Codigo flete, viaje, estatus o ID" autocomplete="off" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Estatus
                    <select id="despacho-filter-estatus" name="estatus">
                      <option value="">Todos</option>
                      <option value="programado">programado</option>
                      <option value="despachado">despachado</option>
                      <option value="entregado">entregado</option>
                      <option value="cerrado">cerrado</option>
                      <option value="cancelado">cancelado</option>
                    </select>
                  </label>
                  <label>Asignacion
                    <select id="despacho-filter-asignacion" name="id_asignacion"></select>
                  </label>
                  <label>Flete
                    <select id="despacho-filter-flete" name="id_flete"></select>
                  </label>
                </div>
                <datalist id="despacho-filter-buscar-dl"></datalist>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="despacho-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="despachos-table"></div>
            <div id="despacho-edit-panel" class="toolbar hidden">
              <h4>Editar despacho</h4>
              <form id="despacho-edit-form">
                <input type="hidden" name="id_despacho" id="despacho-edit-form-id" autocomplete="off" />
                <label>Asignacion actual
                  <input name="asignacion_label" readonly />
                </label>
                <div class="two-col">
                  <label>Flete
                    <select id="edit-despacho-flete" name="id_flete"></select>
                  </label>
                  <label>Estatus
                    <select name="estatus">
                      <option value="programado">programado</option>
                      <option value="despachado">despachado</option>
                      <option value="entregado">entregado</option>
                      <option value="cerrado">cerrado</option>
                      <option value="cancelado">cancelado</option>
                    </select>
                  </label>
                </div>
                <label>Salida programada
                  <input name="salida_programada" type="datetime-local" />
                </label>
                <label>Observaciones de transito
                  <textarea name="observaciones_transito"></textarea>
                </label>
                <label>Motivo cancelacion
                  <input name="motivo_cancelacion" />
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="despacho-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="despacho-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-despacho-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Despachos</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Programa la salida operativa vinculando asignación y flete.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-despacho-toc" aria-label="Índice del manual de despachos">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-despacho-1">1. Objetivo</a>
                <a href="#manual-despacho-2">2. Subopciones</a>
                <a href="#manual-despacho-3">3. Nuevo despacho</a>
                <a href="#manual-despacho-4">4. Consultar y editar</a>
                <a href="#manual-despacho-5">5. Estados</a>
                <a href="#manual-despacho-6">6. FAQ</a>
                <a href="#manual-despacho-7">7. Mensajes</a>
                <a href="#manual-despacho-8">8. Referencia</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="despacho" tabindex="0" role="region" aria-label="Texto del manual de despachos">
            <h4 id="manual-despacho-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Crear el registro de despacho a partir de una <strong>asignación</strong> (operador–unidad–viaje) y, opcionalmente, un <strong>flete</strong>; definir salida programada y observaciones de tránsito para uso operativo y enlaces con seguimiento.</p>
            <h4 id="manual-despacho-2">2. Subopciones</h4>
            <ul class="summary-list"><li><strong>Nuevo despacho:</strong> alta.</li><li><strong>Consultar y editar:</strong> filtros por estatus, asignación y flete; edición de estatus, motivo de cancelación y demás campos permitidos.</li><li><strong>Manual:</strong> esta guía.</li></ul>
            <p class="manual-p"><strong>Relación con Seguimiento:</strong> aquí se administra el <strong>encabezado</strong> del despacho (estatus, vínculos). La <strong>salida real</strong>, eventos en ruta, entrega, cierre y cancelación con registro de hora se capturan en <strong>Seguimiento</strong> sobre el mismo despacho.</p>
            <h4 id="manual-despacho-3">3. Nuevo despacho</h4>
            <p class="manual-p">Seleccione <strong>Asignación</strong> (obligatoria) y <strong>Flete</strong> si aplica; indique <strong>Salida programada</strong> y observaciones. Tras crear, use <strong>Seguimiento → Registrar salida</strong> cuando el vehículo efectivamente salga a ruta.</p>
            <h4 id="manual-despacho-4">4. Consultar y editar</h4>
            <p class="manual-p">Use <strong>Buscar rápido</strong> y filtros; pulse <strong>Editar</strong> para ajustar estatus, flete, salida programada, observaciones y <strong>Motivo cancelación</strong> si el estatus es o pasará a cancelado. Los eventos puntuales (kilómetros de salida/llegada, etc.) siguen en Seguimiento.</p>
            <h4 id="manual-despacho-5">5. Estados</h4>
            <p class="manual-p">programado, despachado, entregado, cerrado, cancelado — alineados con el flujo en <strong>Seguimiento</strong> (salida, entrega, cierre, cancelación). Mantenga coherencia entre lo editado aquí y lo registrado en campo.</p>
            <h4 id="manual-despacho-6">6. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿No hay asignación?</strong> Créela antes en el módulo <strong>Asignaciones</strong>. <strong>¿Bloqueo al registrar salida?</strong> Revise cumplimiento documental (Carta Porte, mercancía, seguros, licencias) en flete/transportista/operador; Seguimiento puede ofrecer omitir validación solo si su política lo autoriza.</p>
            <h4 id="manual-despacho-7">7. Mensajes y errores</h4>
            <p class="manual-p">Respuesta del servidor bajo cada formulario.</p>
            <h4 id="manual-despacho-8">8. Referencia técnica</h4>
            <p class="manual-p"><a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-seguimiento">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de seguimiento</h3>
              <div class="hint">Una accion por vista: salida, evento en ruta, entrega, cierre o cancelacion.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="seguimiento-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button active" data-seguimiento-tab="salida">Registrar salida</button>
            <button type="button" class="subpage-button" data-seguimiento-tab="evento">Evento en ruta</button>
            <button type="button" class="subpage-button" data-seguimiento-tab="entrega">Registrar entrega</button>
            <button type="button" class="subpage-button" data-seguimiento-tab="cierre">Cerrar despacho</button>
            <button type="button" class="subpage-button" data-seguimiento-tab="cancelacion">Cancelar despacho</button>
            <button type="button" class="subpage-button" data-seguimiento-tab="manual">Manual</button>
          </div>
        </div>
        <div class="grid capture-grid">
          <article class="card capture-card" data-seguimiento-tab-panel="salida">
            <h3>Registrar salida</h3>
            <div class="hint">Marca que el despacho ya salio a ruta.</div>
            <form id="salida-form">
              <div class="two-col">
                <label>Despacho
                  <select id="salida-despacho" name="id_despacho" required></select>
                </label>
                <label>Fecha y hora real
                  <input name="salida_real" type="datetime-local" required />
                </label>
              </div>
              <div class="two-col">
                <label>Km salida
                  <input name="km_salida" type="number" step="0.01" min="0" />
                </label>
                <label>Observaciones
                  <input name="observaciones_salida" />
                </label>
              </div>
              <label class="check-row salida-omitir-cumplimiento" style="align-items:flex-start;margin:12px 0;max-width:42rem;">
                <input
                  type="checkbox"
                  name="omitir_validacion_cumplimiento"
                  id="salida-omitir-validacion-cumplimiento"
                  style="margin-top:4px;width:auto;flex-shrink:0;"
                  title="Solo uso operativo excepcional: salir sin Carta Porte, RC u otros requisitos del checklist."
                />
                <span>
                  <strong>Omitir validación documental</strong>
                  — Registrar salida aunque el checklist (Carta Porte, mercancía, seguros, etc.) no autorice.
                  Riesgo operativo; use solo en pruebas o si regularizará después.
                </span>
              </label>
              <button type="submit">Guardar salida</button>
            </form>
            <div id="salida-message" class="message"></div>
          </article>

          <article class="card capture-card hidden" data-seguimiento-tab-panel="evento">
            <h3>Agregar evento</h3>
            <div class="hint">Checkpoint o incidencia del viaje.</div>
            <form id="evento-form">
              <div class="three-col">
                <label>Despacho
                  <select id="evento-despacho" name="id_despacho" required></select>
                </label>
                <label>Tipo evento
                  <select name="tipo_evento">
                    <option value="checkpoint">checkpoint</option>
                    <option value="incidencia">incidencia</option>
                    <option value="salida">salida</option>
                    <option value="entrega">entrega</option>
                    <option value="cierre">cierre</option>
                    <option value="cancelacion">cancelacion</option>
                  </select>
                </label>
                <label>Fecha evento
                  <input name="fecha_evento" type="datetime-local" required />
                </label>
              </div>
              <div class="three-col">
                <label>Ubicacion
                  <input name="ubicacion" />
                </label>
                <label>Latitud
                  <input name="latitud" type="number" step="0.0000001" />
                </label>
                <label>Longitud
                  <input name="longitud" type="number" step="0.0000001" />
                </label>
              </div>
              <label>Descripcion
                <textarea name="descripcion" required></textarea>
              </label>
              <button type="submit">Guardar evento</button>
            </form>
            <div id="evento-message" class="message"></div>
          </article>

          <article class="card capture-card hidden" data-seguimiento-tab-panel="entrega">
            <h3>Registrar entrega</h3>
            <div class="hint">Guarda la evidencia y quien recibio.</div>
            <form id="entrega-form">
              <div class="two-col">
                <label>Despacho
                  <select id="entrega-despacho" name="id_despacho" required></select>
                </label>
                <label>Fecha entrega
                  <input name="fecha_entrega" type="datetime-local" required />
                </label>
              </div>
              <div class="two-col">
                <label>Evidencia URL
                  <input name="evidencia_entrega" />
                </label>
                <label>Firma recibe
                  <input name="firma_recibe" />
                </label>
              </div>
              <label>Observaciones entrega
                <textarea name="observaciones_entrega"></textarea>
              </label>
              <button type="submit">Guardar entrega</button>
            </form>
            <div id="entrega-message" class="message"></div>
          </article>

          <article class="card capture-card hidden" data-seguimiento-tab-panel="cierre">
            <h3>Cerrar despacho</h3>
            <div class="hint">Termina la operacion cuando ya regreso o concluyo formalmente.</div>
            <form id="cierre-form">
              <div class="three-col">
                <label>Despacho
                  <select id="cierre-despacho" name="id_despacho" required></select>
                </label>
                <label>Llegada real
                  <input name="llegada_real" type="datetime-local" required />
                </label>
                <label>Km llegada
                  <input name="km_llegada" type="number" step="0.01" min="0" />
                </label>
              </div>
              <label>Observaciones cierre
                <textarea name="observaciones_cierre"></textarea>
              </label>
              <button type="submit">Cerrar despacho</button>
            </form>
            <div id="cierre-message" class="message"></div>
          </article>

          <article class="card capture-card hidden" data-seguimiento-tab-panel="cancelacion">
            <h3>Cancelar despacho</h3>
            <div class="hint">Usalo solo cuando la operacion ya no va a continuar.</div>
            <form id="cancelacion-form">
              <div class="two-col">
                <label>Despacho
                  <select id="cancelacion-despacho" name="id_despacho" required></select>
                </label>
                <label>Motivo cancelacion
                  <input name="motivo_cancelacion" required minlength="3" />
                </label>
              </div>
              <button type="submit">Cancelar despacho</button>
            </form>
            <div id="cancelacion-message" class="message"></div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-seguimiento-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Seguimiento</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Registro de salida, eventos en ruta, entrega, cierre y cancelación de despachos.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-seguimiento-toc" aria-label="Índice del manual de seguimiento">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-seguimiento-1">1. Objetivo</a>
                <a href="#manual-seguimiento-2">2. Subopciones</a>
                <a href="#manual-seguimiento-3">3. Registrar salida</a>
                <a href="#manual-seguimiento-4">4. Evento en ruta</a>
                <a href="#manual-seguimiento-5">5. Entrega y cierre</a>
                <a href="#manual-seguimiento-6">6. Cancelación</a>
                <a href="#manual-seguimiento-7">7. Preguntas frecuentes</a>
                <a href="#manual-seguimiento-8">8. Referencia técnica</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="seguimiento" tabindex="0" role="region" aria-label="Texto del manual de seguimiento">
            <div class="manual-note"><strong>Consulta de historial:</strong> este módulo no incluye tabla de eventos con editar o eliminar. Para ver y editar el <strong>despacho</strong> como registro use <strong>Despachos → Consultar y editar</strong>. Los eventos quedan asociados al despacho en el servidor; correcciones puntuales de eventos pueden requerir API o proceso de sistemas.</div>
            <h4 id="manual-seguimiento-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Documentar la ejecución del despacho: hora real de salida, eventos intermedios, entrega, cierre operativo o cancelación con motivo. Flujo de <strong>altas sucesivas</strong> (una acción por pestaña).</p>
            <h4 id="manual-seguimiento-2">2. Subopciones</h4>
            <ul class="summary-list">
              <li><strong>Registrar salida:</strong> confirma salida a ruta, km y observaciones; puede aplicar <strong>validacion documental</strong> (Carta Porte, mercancia, seguros, expediente operador). Si el checklist bloquea la salida y su proceso lo permite, use la opcion de <strong>omitir validacion documental</strong> (riesgo operativo; solo excepciones autorizadas).</li>
              <li><strong>Evento en ruta:</strong> checkpoints o incidencias con ubicación opcional y coordenadas.</li>
              <li><strong>Registrar entrega:</strong> fecha, evidencia URL y firma de quien recibe.</li>
              <li><strong>Cerrar despacho:</strong> llegada real y km finales.</li>
              <li><strong>Cancelar despacho:</strong> motivo obligatorio.</li>
              <li><strong>Manual:</strong> esta guía.</li>
            </ul>
            <h4 id="manual-seguimiento-3">3. Registrar salida</h4>
            <p class="manual-p">Seleccione el <strong>Despacho</strong> en la lista (debe existir en módulo Despachos). Capture fecha/hora real, km de salida y observaciones. Si aparece error de cumplimiento documental, complete datos en flete/transportista/operador por API o use omitir validación según política.</p>
            <h4 id="manual-seguimiento-4">4. Evento en ruta</h4>
            <p class="manual-p">Indique tipo de evento, fecha y descripción; ubicación y coordenadas opcionales.</p>
            <h4 id="manual-seguimiento-5">5. Entrega y cierre</h4>
            <p class="manual-p">En <strong>Entrega</strong> registre evidencia y receptor; en <strong>Cierre</strong> la llegada real y kilometraje final.</p>
            <h4 id="manual-seguimiento-6">6. Cancelación</h4>
            <p class="manual-p">Use solo si la operación no continuará; el motivo debe ser explícito.</p>
            <h4 id="manual-seguimiento-7">7. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿No aparece el despacho?</strong> Créelo antes en <strong>Despachos → Nuevo despacho</strong> y verifique catálogos cargados (F5). <strong>¿Me equivoqué en un evento?</strong> En panel no hay edición de eventos; escale a sistemas o registre acuerdo interno. <strong>¿Dónde veo el listado de despachos?</strong> Módulo <strong>Despachos</strong>, no Seguimiento.</p>
            <h4 id="manual-seguimiento-8">8. Referencia técnica</h4>
            <p class="manual-p">Endpoints bajo <code>/despachos/…</code> (salida, eventos, entrega, cerrar, cancelar) y <code>/cumplimiento/…</code> en <a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>
    </main>
  </div>

  <script>
    const API_BASE = "/api/v1";
    const API_KEY = __API_KEY__;
    const state = {
      clientes: [],
      transportistas: [],
      viajes: [],
      fletes: [],
      facturas: [],
      gastos: [],
      tarifas: [],
      tarifasCompra: [],
      operadores: [],
      unidades: [],
      asignaciones: [],
      despachos: [],
      ordenesServicio: [],
      catalogLoaded: false,
      unidadesTotalServidor: null,
      catalogRefreshErrors: [],
    };

    const uiState = {
      clienteFilters: { buscar: "", activo: "" },
      transportistaFilters: { buscar: "", estatus: "", tipo_transportista: "" },
      viajeFilters: { buscar: "", estado: "" },
      fleteFilters: { buscar: "", estado: "", cliente_id: "", transportista_id: "" },
      facturaFilters: { buscar: "", cliente_id: "", estatus: "" },
      tarifaCompraFilters: { buscar: "", transportista_id: "", activo: "" },
      tarifaVentaFilters: { buscar: "" },
      gastoFilters: { buscar: "" },
      operadorFilters: { buscar: "" },
      unidadFilters: { buscar: "", tipo_propiedad: "", estatus_documental: "", activo: "" },
      asignacionFilters: { buscar: "", id_operador: "", id_unidad: "", id_viaje: "" },
      despachoFilters: { buscar: "", estatus: "", id_asignacion: "", id_flete: "" },
      ordenServicioFilters: { buscar: "", cliente_id: "", estatus: "" },
      buscarModo: "contiene",
      editing: {
        clienteId: null,
        clienteContactoId: null,
        clienteDomicilioId: null,
        transportistaId: null,
        transportistaContactoId: null,
        transportistaDocumentoId: null,
        viajeId: null,
        fleteId: null,
        facturaId: null,
        tarifaCompraId: null,
        tarifaFleteId: null,
        asignacionId: null,
        despachoId: null,
        gastoId: null,
        operadorId: null,
        unidadId: null,
      },
      clienteSubpage: "alta",
      transportistaSubpage: "consulta",
      viajeSubpage: "consulta",
      fleteSubpage: "consulta",
      facturaSubpage: "consulta",
      tarifaSubpage: "consulta",
      tarifaCompraSubpage: "consulta",
      operadorSubpage: "consulta",
      unidadSubpage: "consulta",
      gastoSubpage: "consulta",
      asignacionSubpage: "consulta",
      despachoSubpage: "consulta",
      seguimientoSubpage: "salida",
    };

    let lastTarifaCompraEditId = null;

    const pageMeta = {
      inicio: ["Inicio", "Resumen del sistema y accesos a cada modulo sin mezclar pantallas."],
      clientes: ["Clientes", "Alta, consulta, contactos, domicilios, condiciones y manual en pantalla con índice y visor."],
      transportistas: ["Transportistas", "Alta, consulta, contactos, documentos y manual en pantalla con índice y visor."],
      viajes: ["Viajes", "Alta, consulta y manual en pantalla con índice y visor."],
      fletes: ["Fletes", "Alta, consulta, ordenes de servicio (solo lectura) y manual en pantalla con índice y visor."],
      facturas: ["Facturas", "Alta, consulta y manual en pantalla con índice y visor."],
      gastos: ["Gastos viaje", "Alta, consulta, presupuesto estimado y liquidación vs real."],
      tarifas: ["Tarifas", "Alta, consulta y manual en pantalla con índice y visor."],
      "tarifas-compra": ["Tarifas compra", "Alta, consulta y manual en pantalla con índice y visor."],
      operadores: ["Operadores", "Alta, consulta con edición en panel y manual en pantalla."],
      unidades: ["Unidades", "Alta, consulta con filtros, edicion y eliminacion en panel; manual integrado."],
      asignaciones: ["Asignaciones", "Alta, consulta y manual en pantalla con índice y visor."],
      despachos: ["Despachos", "Alta, consulta y manual en pantalla con índice y visor."],
      seguimiento: ["Seguimiento", "Salida, evento, entrega, cierre, cancelación y manual en pantalla con índice y visor."],
    };

    const GASTO_CATEGORIA_LABELS = {
      combustible: "Combustible (diesel)",
      peajes: "Peajes / casetas",
      viaticos: "Viáticos operador",
      operador: "Mano de obra operador",
      mantenimiento_km: "Mantenimiento y desgaste (por km)",
      imprevistos: "Imprevistos",
      administrativos: "Administrativos del viaje",
      pago_transporte_tercero: "Pago a transportista",
      otros: "Otros",
    };

    function labelGastoCategoria(code) {
      return GASTO_CATEGORIA_LABELS[code] || code;
    }

    function setMessage(id, text, kind = "ok") {
      const node = document.getElementById(id);
      node.className = `message ${kind}`;
      node.textContent = text || "";
    }

    function clearMessage(id) {
      setMessage(id, "", "ok");
    }

    function clearCaptureFormFields(formId) {
      const form = document.getElementById(formId);
      if (!form) {
        return;
      }
      const fieldList =
        form.tagName === "FORM"
          ? [...form.elements]
          : [...form.querySelectorAll("input, select, textarea")];
      for (const field of fieldList) {
        if (!field || field.disabled) {
          continue;
        }
        const tagName = field.tagName || "";
        const type = (field.type || "").toLowerCase();
        if (tagName === "BUTTON" || type === "hidden") {
          continue;
        }
        if (type === "checkbox" || type === "radio") {
          field.checked = false;
          continue;
        }
        if (tagName === "SELECT") {
          if (field.multiple) {
            for (const option of field.options) {
              option.selected = false;
            }
          } else {
            field.selectedIndex = -1;
            field.value = "";
          }
          continue;
        }
        field.value = "";
      }
    }

    function installCaptureFormCancelButtons() {
      const captureForms = [
        { formId: "cliente-form", messageId: "cliente-message" },
        {
          formId: "cliente-domicilio-form",
          messageId: "cliente-domicilio-message",
          afterClear: () => {
            syncClienteModuleSummaries();
            renderClienteDomicilios();
          },
        },
        {
          formId: "cliente-condicion-form",
          messageId: "cliente-condicion-message",
          afterClear: () => {
            syncClienteModuleSummaries();
            renderClienteCondicion();
          },
        },
        { formId: "transportista-form", messageId: "transportista-message" },
        {
          formId: "transportista-contacto-form",
          messageId: "transportista-contacto-message",
          afterClear: () => renderTransportistaContactos(),
        },
        {
          formId: "transportista-documento-form",
          messageId: "transportista-documento-message",
          afterClear: () => renderTransportistaDocumentos(),
        },
        { formId: "viaje-form", messageId: "viaje-message" },
        {
          formId: "flete-form",
          messageId: "flete-message",
          afterClear: () => {
            const venta = document.getElementById("flete-cotizacion-detalle");
            const compra = document.getElementById("flete-cotizacion-compra-detalle");
            if (venta) {
              venta.textContent = "";
            }
            if (compra) {
              compra.textContent = "";
            }
          },
        },
        { formId: "factura-form", messageId: "factura-message" },
        { formId: "tarifa-form", messageId: "tarifa-message" },
        { formId: "tarifa-compra-form", messageId: "tarifa-compra-message" },
        { formId: "operador-form", messageId: "operador-message" },
        { formId: "unidad-form", messageId: "unidad-message" },
        { formId: "gasto-form", messageId: "gasto-message" },
        { formId: "asignacion-form", messageId: "asignacion-message" },
        { formId: "despacho-form", messageId: "despacho-message" },
        { formId: "salida-form", messageId: "salida-message" },
        { formId: "evento-form", messageId: "evento-message" },
        { formId: "entrega-form", messageId: "entrega-message" },
        { formId: "cierre-form", messageId: "cierre-message" },
        { formId: "cancelacion-form", messageId: "cancelacion-message" },
      ];

      for (const config of captureForms) {
        const form = document.getElementById(config.formId);
        if (!form || form.dataset.cancelInstalled === "true") {
          continue;
        }
        const submitButton =
          form.querySelector('button[type="submit"]') ||
          form.querySelector("button[data-primary-action='save']");
        if (!submitButton) {
          continue;
        }
        let actions = submitButton.parentElement;
        if (!actions || !actions.classList.contains("toolbar-actions")) {
          actions = document.createElement("div");
          actions.className = "toolbar-actions";
          submitButton.insertAdjacentElement("beforebegin", actions);
          actions.appendChild(submitButton);
        }
        const cancelButton = document.createElement("button");
        cancelButton.type = "button";
        cancelButton.className = "secondary-button";
        cancelButton.textContent = "Cancelar y limpiar";
        cancelButton.addEventListener("click", () => {
          clearCaptureFormFields(config.formId);
          clearMessage(config.messageId);
          if (typeof config.afterClear === "function") {
            config.afterClear();
          }
        });
        actions.appendChild(cancelButton);
        form.dataset.cancelInstalled = "true";
      }
    }

    function clean(value) {
      if (value === null || value === undefined) {
        return null;
      }
      const text = String(value).trim();
      return text === "" ? null : text;
    }

    const MONEY_LOCALE = "es-MX";

    /**
     * Convierte texto de captura (MXN y variantes habituales) a numero JS.
     * Acepta: 1,234.56 / 1.234,56 / 1234,56 / 1,234 / 1.234.567 / 0,001 / 12.3456
     */
    function parseLocaleNumber(value) {
      const text = clean(value);
      if (text === null) {
        return null;
      }
      let s = String(text)
        .trim()
        .replace(/^\\s*\\$\\s*/u, "")
        .replace(/\\u00a0|\\u202f/g, "")
        .replace(/mxn/gi, "")
        .replace(/\\s+/g, "")
        .replace(/'/g, "");
      if (s === "" || s === "-" || s === "." || s === ",") {
        return null;
      }
      let sign = 1;
      if (s.startsWith("-")) {
        sign = -1;
        s = s.slice(1);
      } else if (s.startsWith("+")) {
        s = s.slice(1);
      }
      s = s.replace(/[^\\d,.]/g, "");
      if (s === "" || s === "." || s === ",") {
        return null;
      }

      const lastComma = s.lastIndexOf(",");
      const lastDot = s.lastIndexOf(".");
      let normalized;

      if (lastComma >= 0 && lastDot >= 0) {
        if (lastComma > lastDot) {
          normalized = s.replace(/\\./g, "").replace(",", ".");
        } else {
          normalized = s.replace(/,/g, "");
        }
      } else if (lastComma >= 0) {
        const parts = s.split(",");
        if (parts.length === 2) {
          const left = parts[0].replace(/\\./g, "");
          const right = parts[1];
          if (/^\\d+$/.test(left) && /^\\d+$/.test(right) && right.length >= 1) {
            if (right.length <= 2) {
              normalized = `${left}.${right}`;
            } else if (left === "0") {
              normalized = `${left}.${right}`;
            } else if (right.length === 3 && left.length === 1) {
              normalized = `${left}${right}`;
            } else {
              normalized = `${left}.${right}`;
            }
          } else {
            normalized = s.replace(/,/g, "");
          }
        } else {
          normalized = s.replace(/,/g, "");
        }
      } else if (lastDot >= 0) {
        const parts = s.split(".");
        if (parts.length > 2) {
          normalized = parts.join("");
        } else {
          normalized = s;
        }
      } else {
        normalized = s;
      }

      if (normalized === "" || normalized === "." || normalized === "-") {
        return null;
      }
      const n = Number(normalized) * sign;
      return Number.isFinite(n) ? n : null;
    }

    function numberOrNull(value) {
      return parseLocaleNumber(value);
    }

    function formatLocaleDecimal(n, minFractionDigits, maxFractionDigits) {
      if (n === null || n === undefined || !Number.isFinite(Number(n))) {
        return "";
      }
      const num = Number(n);
      return new Intl.NumberFormat(MONEY_LOCALE, {
        minimumFractionDigits: minFractionDigits,
        maximumFractionDigits: maxFractionDigits,
        useGrouping: true,
      }).format(num);
    }

    function formatMoneyInputFromEl(n, input) {
      const minF = Math.max(0, parseInt(input.dataset.minFractionDigits ?? "2", 10));
      const maxRaw = parseInt(input.dataset.maxFractionDigits ?? "2", 10);
      const maxF = Math.max(minF, maxRaw);
      return formatLocaleDecimal(n, minF, maxF);
    }

    /** Mismo criterio que al salir del campo, pero sin separadores de miles (mas facil de editar al enfocar). */
    function formatPlainMoneyInputFromEl(n, input) {
      const minF = Math.max(0, parseInt(input.dataset.minFractionDigits ?? "2", 10));
      const maxRaw = parseInt(input.dataset.maxFractionDigits ?? "2", 10);
      const maxF = Math.max(minF, maxRaw);
      if (n === null || n === undefined || !Number.isFinite(Number(n))) {
        return "";
      }
      const num = Number(n);
      return new Intl.NumberFormat(MONEY_LOCALE, {
        minimumFractionDigits: minF,
        maximumFractionDigits: maxF,
        useGrouping: false,
      }).format(num);
    }

    function fmtMoneyList(value) {
      if (value === null || value === undefined || value === "") {
        return "—";
      }
      const n = Number(value);
      if (!Number.isFinite(n)) {
        return String(value);
      }
      return formatLocaleDecimal(n, 2, 2);
    }

    function fmtPctList(value) {
      if (value === null || value === undefined || value === "") {
        return "—";
      }
      const n = Number(value);
      if (!Number.isFinite(n)) {
        return String(value);
      }
      return `${formatLocaleDecimal(n, 2, 2)} %`;
    }

    function fmtTarifaList(value, maxFractionDigits) {
      if (value === null || value === undefined || value === "") {
        return "—";
      }
      const n = Number(value);
      if (!Number.isFinite(n)) {
        return String(value);
      }
      return formatLocaleDecimal(n, 0, maxFractionDigits);
    }

    function wireMoneyInputs(root = document) {
      for (const input of root.querySelectorAll("input.field-money")) {
        if (input.dataset.moneyWired === "1") {
          continue;
        }
        input.dataset.moneyWired = "1";
        input.addEventListener("focus", () => {
          const parsed = parseLocaleNumber(input.value);
          if (parsed === null) {
            return;
          }
          input.value = formatPlainMoneyInputFromEl(parsed, input);
          input.select();
        });
        input.addEventListener("blur", () => {
          const parsed = parseLocaleNumber(input.value);
          input.value = parsed === null ? "" : formatMoneyInputFromEl(parsed, input);
        });
      }
    }

    function applyMoneyFormatToForm(form) {
      if (!form) {
        return;
      }
      for (const input of form.querySelectorAll("input.field-money")) {
        const parsed = parseLocaleNumber(input.value);
        input.value = parsed === null ? "" : formatMoneyInputFromEl(parsed, input);
      }
    }

    /** Valor para input type="number" desde API (acepta coma decimal o miles; evita texto invalido). */
    function htmlNumberInputValue(value) {
      if (value == null || value === "") {
        return "";
      }
      const n = parseLocaleNumber(String(value));
      if (n === null || !Number.isFinite(n)) {
        return "";
      }
      return String(n);
    }

    /** Texto formateado es-MX para field-money al hidratar desde API sin elemento DOM. */
    function moneyFieldFromApi(value, minFractionDigits, maxFractionDigits) {
      const minF = Math.max(0, minFractionDigits ?? 2);
      const maxF = Math.max(minF, maxFractionDigits ?? 2);
      const n = parseLocaleNumber(value == null ? "" : String(value));
      if (n === null) {
        return "";
      }
      return formatLocaleDecimal(n, minF, maxF);
    }

    function integerOrNull(value) {
      const n = parseLocaleNumber(value);
      if (n === null || !Number.isFinite(n)) {
        return null;
      }
      return Math.trunc(n);
    }

    function requirePositiveIntOrThrow(raw, contexto) {
      const id = integerOrNull(raw);
      if (id === null || id < 1) {
        throw new Error(
          `${contexto}: identificador invalido. Cierra el panel de edicion, vuelve a abrirlo con Editar e intenta de nuevo.`,
        );
      }
      return id;
    }

    /** PK entero (sin reglas de miles/decimales de dinero). */
    function parsePositiveIntId(raw) {
      if (raw === null || raw === undefined) {
        return null;
      }
      if (typeof raw === "number" && Number.isFinite(raw)) {
        const t = Math.trunc(raw);
        return t >= 1 ? t : null;
      }
      const s = String(raw).trim();
      if (!s || s === "undefined" || s === "null") {
        return null;
      }
      const id = Number.parseInt(s, 10);
      return Number.isFinite(id) && id >= 1 ? id : null;
    }

    function requirePositiveIntIdOrThrow(raw, contexto) {
      const id = parsePositiveIntId(raw);
      if (id === null) {
        throw new Error(
          `${contexto}: identificador invalido. Cierra el panel de edicion, vuelve a abrirlo con Editar e intenta de nuevo.`,
        );
      }
      return id;
    }

    /** PK del flete en edición: oculto + estado + dataset + búsqueda por código (evita fallos tras refresh o IDs string/number). */
    function resolveFleteEditRecordId(formElement) {
      const idEl = document.getElementById("flete-edit-form-record-id");
      const fromHidden = idEl ? String(idEl.value || "").trim() : "";
      if (fromHidden && fromHidden !== "undefined" && fromHidden !== "null") {
        const n = integerOrNull(fromHidden);
        if (n !== null && n >= 1) {
          return String(n);
        }
      }
      if (formElement && formElement.dataset && formElement.dataset.sifeEditingFleteId) {
        const n = integerOrNull(String(formElement.dataset.sifeEditingFleteId).trim());
        if (n !== null && n >= 1) {
          return String(n);
        }
      }
      if (uiState.editing.fleteId != null && uiState.editing.fleteId !== "") {
        const n = Number(uiState.editing.fleteId);
        if (Number.isFinite(n) && n >= 1) {
          return String(Math.trunc(n));
        }
      }
      const codigo =
        formElement && formElement.elements && formElement.elements.codigo_flete
          ? clean(formElement.elements.codigo_flete.value)
          : null;
      if (codigo) {
        const row = state.fletes.find((f) => f.codigo_flete === codigo);
        if (row && row.id != null) {
          return String(row.id);
        }
      }
      return "";
    }

    /** PK del despacho en edicion: oculto + dataset + estado + id_asignacion en etiqueta (unica por despacho en BD). */
    function resolveDespachoEditRecordId(formElement) {
      const idEl = document.getElementById("despacho-edit-form-id");
      const fromHidden = idEl ? String(idEl.value || "").trim() : "";
      if (fromHidden && fromHidden !== "undefined" && fromHidden !== "null") {
        const n = parsePositiveIntId(fromHidden);
        if (n !== null) {
          return String(n);
        }
      }
      if (formElement && formElement.dataset && formElement.dataset.sifeEditingDespachoId) {
        const n = parsePositiveIntId(String(formElement.dataset.sifeEditingDespachoId).trim());
        if (n !== null) {
          return String(n);
        }
      }
      if (uiState.editing.despachoId != null && uiState.editing.despachoId !== "") {
        const n = parsePositiveIntId(uiState.editing.despachoId);
        if (n !== null) {
          return String(n);
        }
      }
      const label =
        formElement && formElement.elements && formElement.elements.asignacion_label
          ? clean(formElement.elements.asignacion_label.value)
          : "";
      const m = label.match(/^(\d+)\s*-\s*/);
      if (m) {
        const idAsig = Number.parseInt(m[1], 10);
        if (Number.isFinite(idAsig) && idAsig >= 1) {
          const row = state.despachos.find((d) => Number(d.id_asignacion) === idAsig);
          if (row && row.id_despacho != null) {
            const n = parsePositiveIntId(row.id_despacho);
            if (n !== null) {
              return String(n);
            }
          }
        }
      }
      return "";
    }

    function resyncFleteEditPkAfterRefresh() {
      if (uiState.editing.fleteId == null || uiState.editing.fleteId === "") {
        return;
      }
      const panel = document.getElementById("flete-edit-panel");
      if (!panel || panel.classList.contains("hidden")) {
        return;
      }
      const sid = String(uiState.editing.fleteId).trim();
      const idPk = document.getElementById("flete-edit-form-record-id");
      if (idPk) {
        idPk.value = sid;
      }
      const form = document.getElementById("flete-edit-form");
      if (form) {
        form.dataset.sifeEditingFleteId = sid;
      }
    }

    function resyncDespachoEditPkAfterRefresh() {
      if (uiState.editing.despachoId == null || uiState.editing.despachoId === "") {
        return;
      }
      const panel = document.getElementById("despacho-edit-panel");
      if (!panel || panel.classList.contains("hidden")) {
        return;
      }
      const sid = String(uiState.editing.despachoId).trim();
      const idPk = document.getElementById("despacho-edit-form-id");
      if (idPk) {
        idPk.value = sid;
      }
      const form = document.getElementById("despacho-edit-form");
      if (form) {
        form.dataset.sifeEditingDespachoId = sid;
      }
    }

    const SIFE_TARIFA_COMPRA_EDIT_ID_KEY = "sife_tarifa_compra_edit_id";

    function setTarifaCompraEditIdStorage(sid) {
      try {
        if (sid == null || String(sid).trim() === "") {
          sessionStorage.removeItem(SIFE_TARIFA_COMPRA_EDIT_ID_KEY);
        } else {
          sessionStorage.setItem(SIFE_TARIFA_COMPRA_EDIT_ID_KEY, String(sid).trim());
        }
      } catch (_e) {
        /* ignore (private mode, disabled storage) */
      }
    }

    function getTarifaCompraEditIdStorage() {
      try {
        return sessionStorage.getItem(SIFE_TARIFA_COMPRA_EDIT_ID_KEY);
      } catch (_e) {
        return null;
      }
    }

    function tarifaCompraEditIdForPatch(formElement) {
      if (formElement && formElement._sifeTarifaCompraId != null && formElement._sifeTarifaCompraId !== "") {
        const t0 = String(formElement._sifeTarifaCompraId).trim();
        if (t0 !== "" && t0 !== "undefined" && t0 !== "null") {
          return t0;
        }
      }
      const fromStorage = getTarifaCompraEditIdStorage();
      if (fromStorage != null && String(fromStorage).trim() !== "") {
        const ts = String(fromStorage).trim();
        if (ts !== "undefined" && ts !== "null") {
          return ts;
        }
      }
      const saveBtn = document.getElementById("tarifa-compra-edit-save");
      const hiddenEl = document.getElementById("tarifa-compra-edit-record-id");
      let winId = null;
      try {
        winId = typeof window !== "undefined" ? window.__SIFE_tarifaCompraEditId : null;
      } catch (_e) {
        winId = null;
      }
      const candidates = [
        lastTarifaCompraEditId,
        uiState.editing.tarifaCompraId,
        winId,
        saveBtn ? saveBtn.getAttribute("data-tarifa-compra-record-id") : null,
        hiddenEl ? hiddenEl.value : null,
        formElement ? formElement.getAttribute("data-tarifa-compra-id") : null,
      ];
      for (const c of candidates) {
        if (c == null) {
          continue;
        }
        const t = String(c).trim();
        if (t !== "" && t !== "undefined" && t !== "null") {
          return t;
        }
      }
      return null;
    }

    function normalizeDateOnlyForApi(value) {
      const text = clean(value);
      if (text === null) {
        return null;
      }
      let s = String(text).trim();
      if (s === "") {
        return null;
      }
      if (/^\d{4}-\d{2}-\d{2}$/.test(s)) {
        return s;
      }
      if (/^\d{4}-\d{2}-\d{2}[T\s]/.test(s)) {
        return s.slice(0, 10);
      }
      const mLoose = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
      if (mLoose) {
        const yyyy = mLoose[1];
        const mm = mLoose[2].padStart(2, "0");
        const dd = mLoose[3].padStart(2, "0");
        const cand = `${yyyy}-${mm}-${dd}`;
        if (/^\d{4}-\d{2}-\d{2}$/.test(cand)) {
          return cand;
        }
      }
      const mSlash = s.match(/^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})$/);
      if (mSlash) {
        const dd = mSlash[1].padStart(2, "0");
        const mm = mSlash[2].padStart(2, "0");
        const yyyy = mSlash[3];
        return `${yyyy}-${mm}-${dd}`;
      }
      return null;
    }

    function normalizeDateTimeForApi(value) {
      const text = clean(value);
      if (text === null) {
        return null;
      }
      let s = String(text).trim().replace(" ", "T");
      s = s.replace(/([+-]\d{2}(:\d{2})?|Z)$/i, "");
      if (s.includes(".")) {
        s = s.slice(0, s.indexOf("."));
      }
      if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(s)) {
        return `${s}:00`;
      }
      const mFull = s.match(/^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})/);
      if (mFull) {
        return mFull[1];
      }
      if (/^\d{4}-\d{2}-\d{2}$/.test(s)) {
        return `${s}T00:00:00`;
      }
      const m = s.match(
        /^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})[T ](\d{1,2}):(\d{2})(?::(\d{2}))?/,
      );
      if (m) {
        const dd = m[1].padStart(2, "0");
        const mm = m[2].padStart(2, "0");
        const yyyy = m[3];
        const hh = m[4].padStart(2, "0");
        const min = m[5].padStart(2, "0");
        const ss = (m[6] || "00").padStart(2, "0");
        return `${yyyy}-${mm}-${dd}T${hh}:${min}:${ss}`;
      }
      return null;
    }

    function toDateInputValue(value) {
      if (value == null || value === "") {
        return "";
      }
      if (typeof value === "number" && Number.isFinite(value)) {
        const d = new Date(value);
        if (!Number.isNaN(d.getTime())) {
          const y = d.getUTCFullYear();
          const m = String(d.getUTCMonth() + 1).padStart(2, "0");
          const day = String(d.getUTCDate()).padStart(2, "0");
          return `${y}-${m}-${day}`;
        }
      }
      const n = normalizeDateOnlyForApi(value);
      return typeof n === "string" && /^\d{4}-\d{2}-\d{2}$/.test(n) ? n : "";
    }

    function integerStringForNumberInput(n) {
      if (n == null || n === "") {
        return "0";
      }
      const x = Number(n);
      if (!Number.isFinite(x)) {
        return "0";
      }
      return String(Math.max(0, Math.trunc(x)));
    }

    function optionalNonNegativeIntString(n) {
      if (n == null || n === "") {
        return "";
      }
      const x = Number(n);
      if (!Number.isFinite(x)) {
        return "";
      }
      return String(Math.max(0, Math.trunc(x)));
    }

    function formatLocalDateTimeLocal(d) {
      if (!(d instanceof Date) || Number.isNaN(d.getTime())) {
        return "";
      }
      const y = d.getFullYear();
      const mo = String(d.getMonth() + 1).padStart(2, "0");
      const day = String(d.getDate()).padStart(2, "0");
      const hh = String(d.getHours()).padStart(2, "0");
      const mm = String(d.getMinutes()).padStart(2, "0");
      return `${y}-${mo}-${day}T${hh}:${mm}`;
    }

    /** Valor para input datetime-local (YYYY-MM-DDTHH:mm) desde API ISO, SQL o fechas sueltas. */
    function toDateTimeLocal(value) {
      if (value == null || value === "") {
        return "";
      }
      if (typeof value === "number" && Number.isFinite(value)) {
        return formatLocalDateTimeLocal(new Date(value));
      }
      let s = String(value).trim().replace(/[\\u00a0\\u202f]/g, " ");
      if (s === "") {
        return "";
      }
      const onlyDate = s.match(/^(\\d{4})-(\\d{1,2})-(\\d{1,2})$/);
      if (onlyDate) {
        return `${onlyDate[1]}-${onlyDate[2].padStart(2, "0")}-${onlyDate[3].padStart(2, "0")}T00:00`;
      }
      if (!s.includes("T") && /^\\d{4}-\\d{1,2}-\\d{1,2}\\s+\\d/.test(s)) {
        s = s.replace(/\\s+/, "T");
      }
      const parsed = new Date(s);
      if (!Number.isNaN(parsed.getTime())) {
        return formatLocalDateTimeLocal(parsed);
      }
      const noTz = s.replace(/([+-]\\d{2}(:\\d{2})?|Z)$/i, "");
      const noFrac = /T\\d{2}:\\d{2}:\\d{2}\\./.test(noTz) ? noTz.slice(0, noTz.indexOf(".")) : noTz;
      const normalized = noFrac.includes("T") ? noFrac : noFrac.replace(/\\s+/, "T");
      const mLoose = normalized.match(/^(\\d{4})-(\\d{1,2})-(\\d{1,2})[T ](\\d{1,2}):(\\d{2})(?::(\\d{2}))?/);
      if (mLoose) {
        const yyyy = mLoose[1];
        const mo = mLoose[2].padStart(2, "0");
        const dd = mLoose[3].padStart(2, "0");
        const hh = mLoose[4].padStart(2, "0");
        const min = mLoose[5].padStart(2, "0");
        return `${yyyy}-${mo}-${dd}T${hh}:${min}`;
      }
      const mIsoSpace = noFrac.match(/^(\\d{4}-\\d{2}-\\d{2}) (\\d{2}):(\\d{2})/);
      if (mIsoSpace) {
        return `${mIsoSpace[1]}T${mIsoSpace[2]}:${mIsoSpace[3]}`;
      }
      const mDateOnly = normalized.match(/^(\\d{4}-\\d{2}-\\d{2})$/);
      if (mDateOnly) {
        return `${mDateOnly[1]}T00:00`;
      }
      const mSlash = noFrac.match(/^(\\d{1,2})[\\/\\-](\\d{1,2})[\\/\\-](\\d{4})[T ](\\d{1,2}):(\\d{2})/);
      if (mSlash) {
        const dd = mSlash[1].padStart(2, "0");
        const mm = mSlash[2].padStart(2, "0");
        const yyyy = mSlash[3];
        const hh = mSlash[4].padStart(2, "0");
        const min = mSlash[5].padStart(2, "0");
        return `${yyyy}-${mm}-${dd}T${hh}:${min}`;
      }
      return "";
    }

    function buildClientePayload(form) {
      return {
        razon_social: clean(form.get("razon_social")),
        nombre_comercial: clean(form.get("nombre_comercial")),
        rfc: clean(form.get("rfc")),
        tipo_cliente: clean(form.get("tipo_cliente")) || "mixto",
        sector: clean(form.get("sector")),
        origen_prospecto: clean(form.get("origen_prospecto")),
        email: clean(form.get("email")),
        telefono: clean(form.get("telefono")),
        direccion: clean(form.get("direccion")),
        domicilio_fiscal: clean(form.get("direccion")),
        sitio_web: clean(form.get("sitio_web")),
        notas_operativas: clean(form.get("notas_operativas")),
        notas_comerciales: clean(form.get("notas_comerciales")),
        activo: form.get("activo") === "on",
      };
    }

    function buildTransportistaPayload(form) {
      return {
        nombre: clean(form.get("nombre")),
        nombre_razon_social: clean(form.get("nombre")),
        tipo_transportista: clean(form.get("tipo_transportista")) || "subcontratado",
        tipo_persona: clean(form.get("tipo_persona")) || "moral",
        nombre_comercial: clean(form.get("nombre_comercial")),
        rfc: clean(form.get("rfc")),
        curp: clean(form.get("curp")),
        regimen_fiscal: clean(form.get("regimen_fiscal")),
        fecha_alta: normalizeDateOnlyForApi(form.get("fecha_alta")),
        estatus: clean(form.get("estatus")) || "activo",
        contacto: clean(form.get("contacto")),
        telefono: clean(form.get("telefono")),
        telefono_general: clean(form.get("telefono")),
        email: clean(form.get("email")),
        email_general: clean(form.get("email")),
        sitio_web: clean(form.get("sitio_web")),
        direccion_fiscal: clean(form.get("direccion_fiscal")),
        direccion_operativa: clean(form.get("direccion_operativa")),
        ciudad: clean(form.get("ciudad")),
        estado: clean(form.get("estado")),
        pais: clean(form.get("pais")),
        codigo_postal: clean(form.get("codigo_postal")),
        nivel_confianza: clean(form.get("nivel_confianza")) || "medio",
        blacklist: form.get("blacklist") === "on",
        prioridad_asignacion: integerOrNull(form.get("prioridad_asignacion")) ?? 0,
        notas: clean(form.get("notas_operativas")),
        notas_operativas: clean(form.get("notas_operativas")),
        notas_comerciales: clean(form.get("notas_comerciales")),
        activo: form.get("activo") === "on",
      };
    }

    function buildTransportistaContactoPayload(form) {
      return {
        transportista_id: integerOrNull(form.get("transportista_id")),
        nombre: clean(form.get("nombre")),
        area: clean(form.get("area")),
        puesto: clean(form.get("puesto")),
        telefono: clean(form.get("telefono")),
        extension: clean(form.get("extension")),
        celular: clean(form.get("celular")),
        email: clean(form.get("email")),
        principal: form.get("principal") === "on",
        activo: form.get("activo") === "on",
      };
    }

    function buildTransportistaDocumentoPayload(form) {
      return {
        transportista_id: integerOrNull(form.get("transportista_id")),
        tipo_documento: clean(form.get("tipo_documento")),
        numero_documento: clean(form.get("numero_documento")),
        fecha_emision: normalizeDateOnlyForApi(form.get("fecha_emision")),
        fecha_vencimiento: normalizeDateOnlyForApi(form.get("fecha_vencimiento")),
        archivo_url: clean(form.get("archivo_url")),
        estatus: clean(form.get("estatus")) || "pendiente",
        observaciones: clean(form.get("observaciones")),
      };
    }

    function buildViajePayload(form) {
      const km = numberOrNull(form.get("kilometros_estimados"));
      return {
        codigo_viaje: clean(form.get("codigo_viaje")),
        descripcion: clean(form.get("descripcion")),
        origen: clean(form.get("origen")),
        destino: clean(form.get("destino")),
        fecha_salida: normalizeDateTimeForApi(form.get("fecha_salida")),
        fecha_llegada_estimada: normalizeDateTimeForApi(form.get("fecha_llegada_estimada")),
        fecha_llegada_real: normalizeDateTimeForApi(form.get("fecha_llegada_real")),
        estado: clean(form.get("estado")),
        kilometros_estimados: km === null ? null : Number(km),
        notas: clean(form.get("notas")),
      };
    }

    function buildAsignacionPayload(form) {
      return {
        id_operador: integerOrNull(form.get("id_operador")),
        id_unidad: integerOrNull(form.get("id_unidad")),
        id_viaje: integerOrNull(form.get("id_viaje")),
        fecha_salida: normalizeDateTimeForApi(form.get("fecha_salida")),
        fecha_regreso: normalizeDateTimeForApi(form.get("fecha_regreso")),
        km_inicial: numberOrNull(form.get("km_inicial")),
        km_final: numberOrNull(form.get("km_final")),
        rendimiento_combustible: numberOrNull(form.get("rendimiento_combustible")),
      };
    }

    const TARIFA_VENTA_NOMBRE_DUPLICADO_MSG =
      "Este nombre de tarifa ya está en uso por otra tarifa activa. Usa otro nombre distintivo.";

    function normalizeTarifaVentaNombreKey(raw) {
      return String(raw || "").trim().toLowerCase();
    }

    function findActiveTarifaVentaNombreDuplicado(nombreRaw, excludeId) {
      const key = normalizeTarifaVentaNombreKey(nombreRaw);
      if (!key) {
        return null;
      }
      for (const t of state.tarifas || []) {
        if (!t.activo) {
          continue;
        }
        if (excludeId != null && Number(t.id) === Number(excludeId)) {
          continue;
        }
        if (normalizeTarifaVentaNombreKey(t.nombre_tarifa) === key) {
          return t;
        }
      }
      return null;
    }

    function refreshTarifaVentaNombreAviso(inputEl, avisoEl, submitBtn, excludeId) {
      if (!inputEl || !avisoEl) {
        return;
      }
      const dup = findActiveTarifaVentaNombreDuplicado(inputEl.value, excludeId);
      if (dup) {
        avisoEl.textContent = TARIFA_VENTA_NOMBRE_DUPLICADO_MSG;
        avisoEl.hidden = false;
        inputEl.setAttribute("aria-invalid", "true");
        if (submitBtn) {
          submitBtn.disabled = true;
        }
      } else {
        avisoEl.textContent = "";
        avisoEl.hidden = true;
        inputEl.removeAttribute("aria-invalid");
        if (submitBtn) {
          submitBtn.disabled = false;
        }
      }
    }

    function initTarifaVentaNombreUnico() {
      const tfNombre = document.getElementById("tarifa-form-nombre-tarifa");
      const tfAviso = document.getElementById("tarifa-form-nombre-aviso");
      const tfForm = document.getElementById("tarifa-form");
      const tfSubmit = tfForm ? tfForm.querySelector('button[type="submit"]') : null;
      if (tfNombre && tfAviso) {
        const runAlta = () => refreshTarifaVentaNombreAviso(tfNombre, tfAviso, tfSubmit, null);
        tfNombre.addEventListener("input", runAlta);
        tfNombre.addEventListener("change", runAlta);
      }
      const teNombre = document.getElementById("tarifa-edit-form-nombre-tarifa");
      const teAviso = document.getElementById("tarifa-edit-form-nombre-aviso");
      const teForm = document.getElementById("tarifa-edit-form");
      const teSubmit = teForm ? teForm.querySelector('button[type="submit"]') : null;
      if (teNombre && teAviso && teForm) {
        const runEdit = () => {
          const sid = teForm.elements.id && teForm.elements.id.value;
          const ex = sid ? Number(sid) : null;
          refreshTarifaVentaNombreAviso(
            teNombre,
            teAviso,
            teSubmit,
            Number.isFinite(ex) && ex > 0 ? ex : null,
          );
        };
        teNombre.addEventListener("input", runEdit);
        teNombre.addEventListener("change", runEdit);
      }
    }

    function buildTarifaFleteVentaPayload(form) {
      const pu = numberOrNull(form.get("porcentaje_utilidad"));
      const pr = numberOrNull(form.get("porcentaje_riesgo"));
      const pug = numberOrNull(form.get("porcentaje_urgencia"));
      const prv = numberOrNull(form.get("porcentaje_retorno_vacio"));
      const pce = numberOrNull(form.get("porcentaje_carga_especial"));
      return {
        nombre_tarifa: clean(form.get("nombre_tarifa")),
        tipo_operacion: clean(form.get("tipo_operacion")) || "subcontratado",
        ambito: clean(form.get("ambito")) || "federal",
        modalidad_cobro: clean(form.get("modalidad_cobro")) || "mixta",
        origen: clean(form.get("origen")),
        destino: clean(form.get("destino")),
        tipo_unidad: clean(form.get("tipo_unidad")),
        tipo_carga: clean(form.get("tipo_carga")),
        tarifa_base: numberOrNull(form.get("tarifa_base")),
        tarifa_km: numberOrNull(form.get("tarifa_km")) ?? 0,
        tarifa_kg: numberOrNull(form.get("tarifa_kg")) ?? 0,
        tarifa_tonelada: numberOrNull(form.get("tarifa_tonelada")) ?? 0,
        tarifa_hora: numberOrNull(form.get("tarifa_hora")) ?? 0,
        tarifa_dia: numberOrNull(form.get("tarifa_dia")) ?? 0,
        recargo_minimo: numberOrNull(form.get("recargo_minimo")) ?? 0,
        porcentaje_utilidad: pu != null ? pu : 0.2,
        porcentaje_riesgo: pr != null ? pr : 0,
        porcentaje_urgencia: pug != null ? pug : 0,
        porcentaje_retorno_vacio: prv != null ? prv : 0,
        porcentaje_carga_especial: pce != null ? pce : 0,
        moneda: clean(form.get("moneda")) || "MXN",
        activo: form.get("activo") === "on",
        vigencia_inicio: normalizeDateOnlyForApi(form.get("vigencia_inicio")),
        vigencia_fin: normalizeDateOnlyForApi(form.get("vigencia_fin")),
      };
    }

    function buildFacturaPayload(form) {
      return {
        serie: clean(form.get("serie")),
        cliente_id: integerOrNull(form.get("cliente_id")),
        flete_id: integerOrNull(form.get("flete_id")),
        orden_servicio_id: integerOrNull(form.get("orden_servicio_id")),
        fecha_emision: normalizeDateOnlyForApi(form.get("fecha_emision")),
        fecha_vencimiento: normalizeDateOnlyForApi(form.get("fecha_vencimiento")),
        concepto: clean(form.get("concepto")),
        referencia: clean(form.get("referencia")),
        moneda: clean(form.get("moneda")) || "MXN",
        subtotal: numberOrNull(form.get("subtotal")),
        iva_pct: numberOrNull(form.get("iva_pct")) ?? 0.16,
        iva_monto: numberOrNull(form.get("iva_monto")),
        retencion_monto: numberOrNull(form.get("retencion_monto")) ?? 0,
        total: numberOrNull(form.get("total")),
        saldo_pendiente: numberOrNull(form.get("saldo_pendiente")),
        forma_pago: clean(form.get("forma_pago")),
        metodo_pago: clean(form.get("metodo_pago")),
        uso_cfdi: clean(form.get("uso_cfdi")),
        estatus: clean(form.get("estatus")) || "borrador",
        timbrada: form.get("timbrada") === "on",
        observaciones: clean(form.get("observaciones")),
      };
    }

    function buildTarifaCompraPayload(form) {
      const activoRaw = form.get("activo");
      return {
        transportista_id: integerOrNull(form.get("transportista_id")),
        tipo_transportista: clean(form.get("tipo_transportista")) || "subcontratado",
        nombre_tarifa: clean(form.get("nombre_tarifa")),
        ambito: clean(form.get("ambito")) || "federal",
        modalidad_cobro: clean(form.get("modalidad_cobro")) || "mixta",
        origen: clean(form.get("origen")),
        destino: clean(form.get("destino")),
        tipo_unidad: clean(form.get("tipo_unidad")),
        tipo_carga: clean(form.get("tipo_carga")),
        tarifa_base: numberOrNull(form.get("tarifa_base")),
        tarifa_km: numberOrNull(form.get("tarifa_km")) ?? 0,
        tarifa_kg: numberOrNull(form.get("tarifa_kg")) ?? 0,
        tarifa_tonelada: numberOrNull(form.get("tarifa_tonelada")) ?? 0,
        tarifa_hora: numberOrNull(form.get("tarifa_hora")) ?? 0,
        tarifa_dia: numberOrNull(form.get("tarifa_dia")) ?? 0,
        recargo_minimo: numberOrNull(form.get("recargo_minimo")) ?? 0,
        dias_credito: integerOrNull(form.get("dias_credito")) ?? 0,
        moneda: clean(form.get("moneda")) || "MXN",
        activo: activoRaw === "on" || activoRaw === "true",
        vigencia_inicio: normalizeDateOnlyForApi(form.get("vigencia_inicio")),
        vigencia_fin: normalizeDateOnlyForApi(form.get("vigencia_fin")),
        observaciones: clean(form.get("observaciones")),
      };
    }

    function buildDespachoPayload(form) {
      return {
        id_flete: integerOrNull(form.get("id_flete")),
        salida_programada: normalizeDateTimeForApi(form.get("salida_programada")),
        estatus: clean(form.get("estatus")),
        observaciones_transito: clean(form.get("observaciones_transito")),
        motivo_cancelacion: clean(form.get("motivo_cancelacion")),
      };
    }

    function buildClienteContactoPayload(form) {
      return {
        cliente_id: integerOrNull(form.get("cliente_id")),
        nombre: clean(form.get("nombre")),
        area: clean(form.get("area")),
        puesto: clean(form.get("puesto")),
        telefono: clean(form.get("telefono")),
        extension: clean(form.get("extension")),
        celular: clean(form.get("celular")),
        email: clean(form.get("email")),
        principal: form.get("principal") === "on",
        activo: form.get("activo") === "on",
      };
    }

    function clienteContactoCaptureToFormData() {
      const fd = new FormData();
      fd.append("cliente_id", document.getElementById("cliente-contacto-cliente").value);
      fd.append("nombre", document.getElementById("cliente-contacto-nombre").value);
      fd.append("area", document.getElementById("cliente-contacto-area").value);
      fd.append("puesto", document.getElementById("cliente-contacto-puesto").value);
      fd.append("email", document.getElementById("cliente-contacto-email").value);
      fd.append("telefono", document.getElementById("cliente-contacto-telefono").value);
      fd.append("extension", document.getElementById("cliente-contacto-extension").value);
      fd.append("celular", document.getElementById("cliente-contacto-celular").value);
      if (document.getElementById("cliente-contacto-principal").checked) {
        fd.append("principal", "on");
      }
      if (document.getElementById("cliente-contacto-activo").checked) {
        fd.append("activo", "on");
      }
      return fd;
    }

    function validateClienteContactoCapture() {
      const cliente = document.getElementById("cliente-contacto-cliente");
      const nombre = document.getElementById("cliente-contacto-nombre");
      const email = document.getElementById("cliente-contacto-email");
      if (!cliente.value) {
        setMessage("cliente-contacto-message", "Selecciona un cliente.", "error");
        cliente.focus();
        return false;
      }
      if (!nombre.value.trim()) {
        setMessage("cliente-contacto-message", "Captura el nombre del contacto.", "error");
        nombre.focus();
        return false;
      }
      if (email.value && typeof email.checkValidity === "function" && !email.checkValidity()) {
        setMessage("cliente-contacto-message", "Revisa el formato del email.", "error");
        email.focus();
        return false;
      }
      return true;
    }

    function buildClienteDomicilioPayload(form) {
      return {
        cliente_id: integerOrNull(form.get("cliente_id")),
        tipo_domicilio: clean(form.get("tipo_domicilio")),
        nombre_sede: clean(form.get("nombre_sede")),
        direccion_completa: clean(form.get("direccion_completa")),
        municipio: clean(form.get("municipio")),
        estado: clean(form.get("estado")),
        codigo_postal: clean(form.get("codigo_postal")),
        horario_carga: clean(form.get("horario_carga")),
        horario_descarga: clean(form.get("horario_descarga")),
        instrucciones_acceso: clean(form.get("instrucciones_acceso")),
        activo: form.get("activo") === "on",
      };
    }

    function normBusquedaText(s) {
      return String(s || "").toLowerCase().trim();
    }

    function busquedaWordCandidates(fields) {
      const words = [];
      for (const f of fields) {
        const txt = normBusquedaText(f);
        if (!txt) {
          continue;
        }
        words.push(txt);
        txt.split(/[\s/.,\-_|]+/).forEach((chunk) => {
          if (chunk) {
            words.push(chunk);
          }
        });
      }
      return words;
    }

    function matchesBusqueda(query, fields, modo) {
      const q = normBusquedaText(query);
      if (!q) {
        return true;
      }
      const flat = fields.map((f) => normBusquedaText(f));
      const haystack = flat.join(" ");
      if (modo === "todas_palabras") {
        const tokens = q.split(/\s+/).filter(Boolean);
        if (!tokens.length) {
          return true;
        }
        return tokens.every((t) => haystack.includes(t));
      }
      if (modo === "prefijo_palabras") {
        const tokens = q.split(/\s+/).filter(Boolean);
        if (!tokens.length) {
          return true;
        }
        const words = busquedaWordCandidates(fields);
        return tokens.every((tok) => words.some((w) => w.startsWith(tok)));
      }
      return flat.some((x) => x.includes(q)) || haystack.includes(q);
    }

    function escapeDatalistValue(value) {
      return String(value).replace(/&/g, "&amp;").replace(/"/g, "&quot;");
    }

    function updateBusquedaDatalist(inputId, datalistId, allItems, labelFn, getFields) {
      const input = document.getElementById(inputId);
      const dl = document.getElementById(datalistId);
      if (!input || !dl) {
        return;
      }
      const modo = uiState.buscarModo || "contiene";
      const qRaw = (input.value || "").trim();
      let ranked = allItems.filter((item) =>
        matchesBusqueda(qRaw, getFields(item), modo),
      );
      if (!qRaw) {
        ranked = allItems.slice();
      }
      const seen = new Set();
      const parts = [];
      for (const item of ranked) {
        const lab = labelFn(item);
        if (!lab || seen.has(lab)) {
          continue;
        }
        seen.add(lab);
        parts.push(`<option value="${escapeDatalistValue(lab)}"></option>`);
        if (parts.length >= 18) {
          break;
        }
      }
      dl.innerHTML = parts.join("");
    }

    const BUSQUEDA_DL_BY_INPUT = {
      "cliente-filter-buscar": {
        datalistId: "cliente-filter-buscar-dl",
        getItems: () => state.clientes,
        label: (c) => c.razon_social || c.nombre_comercial || `Cliente ${c.id}`,
        fields: (c) => [c.razon_social, c.nombre_comercial, c.rfc],
      },
      "transportista-filter-buscar": {
        datalistId: "transportista-filter-buscar-dl",
        getItems: () => state.transportistas,
        label: (t) => t.nombre || t.nombre_comercial || `Transportista ${t.id}`,
        fields: (t) => [t.nombre, t.nombre_comercial, t.rfc],
      },
      "viaje-filter-buscar": {
        datalistId: "viaje-filter-buscar-dl",
        getItems: () => state.viajes,
        label: (v) => v.codigo_viaje || `Viaje ${v.id}`,
        fields: (v) => [v.codigo_viaje || "", v.origen || "", v.destino || "", String(v.id ?? "")],
      },
      "flete-filter-buscar": {
        datalistId: "flete-filter-buscar-dl",
        getItems: () => state.fletes,
        label: (x) => x.codigo_flete || `Flete ${x.id}`,
        fields: (x) => {
          const cliente = x.cliente?.razon_social || x.cliente?.nombre_comercial || "";
          const transp = x.transportista?.nombre || x.transportista?.nombre_comercial || "";
          return [String(x.id ?? ""), x.codigo_flete || "", cliente, transp, x.estado || ""];
        },
      },
      "factura-filter-buscar": {
        datalistId: "factura-filter-buscar-dl",
        getItems: () => state.facturas,
        label: (x) => x.folio || `Factura ${x.id}`,
        fields: (x) => [x.folio || "", x.concepto || "", x.referencia || "", String(x.id ?? "")],
      },
      "tarifa-venta-filter-buscar": {
        datalistId: "tarifa-venta-filter-buscar-dl",
        getItems: () => state.tarifas,
        label: (x) => x.nombre_tarifa || `Tarifa ${x.id}`,
        fields: (x) => [
          String(x.id ?? ""),
          x.nombre_tarifa || "",
          x.origen || "",
          x.destino || "",
          x.tipo_unidad || "",
          x.tipo_carga || "",
          x.tipo_operacion || "",
          String(x.ambito || ""),
          String(x.modalidad_cobro || ""),
        ],
      },
      "tarifa-compra-filter-buscar": {
        datalistId: "tarifa-compra-filter-buscar-dl",
        getItems: () => state.tarifasCompra,
        label: (x) => {
          const tn = state.transportistas.find((t) => Number(t.id) === Number(x.transportista_id))?.nombre || "";
          return x.nombre_tarifa || tn || `Tarifa compra ${x.id}`;
        },
        fields: (x) => {
          const tn = state.transportistas.find((t) => Number(t.id) === Number(x.transportista_id))?.nombre || "";
          return [
            x.nombre_tarifa || "",
            x.origen || "",
            x.destino || "",
            x.tipo_unidad || "",
            tn,
            String(x.id ?? ""),
          ];
        },
      },
      "gasto-filter-buscar": {
        datalistId: "gasto-filter-buscar-dl",
        getItems: () => state.gastos,
        label: (x) => x.referencia || x.tipo_gasto || `Gasto ${x.id}`,
        fields: (x) => [
          String(x.id ?? ""),
          String(x.flete_id ?? ""),
          x.tipo_gasto || "",
          x.referencia || "",
          x.descripcion || "",
          String(x.monto ?? ""),
        ],
      },
      "operador-filter-buscar": {
        datalistId: "operador-filter-buscar-dl",
        getItems: () => state.operadores,
        label: (x) =>
          [x.nombre, x.apellido_paterno, x.apellido_materno].filter(Boolean).join(" ").trim() ||
          `Operador ${x.id_operador}`,
        fields: (x) => {
          const transp = state.transportistas.find((t) => t.id === x.transportista_id)?.nombre || "";
          return [
            String(x.id_operador ?? ""),
            x.nombre || "",
            x.apellido_paterno || "",
            x.apellido_materno || "",
            x.curp || "",
            x.telefono_principal || "",
            x.certificaciones || "",
            transp,
          ];
        },
      },
      "unidad-filter-buscar": {
        datalistId: "unidad-filter-buscar-dl",
        getItems: () => state.unidades,
        label: (x) => x.economico || `Unidad ${x.id_unidad}`,
        fields: (x) => {
          const transp = state.transportistas.find((t) => t.id === x.transportista_id)?.nombre || "";
          return [String(x.id_unidad ?? ""), x.economico || "", x.placas || "", x.descripcion || "", transp];
        },
      },
      "asignacion-filter-buscar": {
        datalistId: "asignacion-filter-buscar-dl",
        getItems: () => state.asignaciones,
        label: (x) => x.unidad?.economico || `Asignacion ${x.id_asignacion}`,
        fields: (x) => {
          const nom = `${x.operador?.nombre || ""} ${x.operador?.apellido_paterno || ""} ${x.operador?.apellido_materno || ""}`;
          const ec = x.unidad?.economico || "";
          const cv = x.viaje?.codigo_viaje || "";
          return [String(x.id_asignacion), nom, ec, cv];
        },
      },
      "despacho-filter-buscar": {
        datalistId: "despacho-filter-buscar-dl",
        getItems: () => state.despachos,
        label: (x) => x.flete?.codigo_flete || `Despacho ${x.id_despacho}`,
        fields: (x) => {
          const cf = x.flete?.codigo_flete || "";
          const cv = x.asignacion?.viaje?.codigo_viaje || "";
          return [String(x.id_despacho), x.estatus || "", cf, cv];
        },
      },
    };

    function refreshBusquedaDatalist(inputId) {
      const cfg = BUSQUEDA_DL_BY_INPUT[inputId];
      if (!cfg) {
        return;
      }
      updateBusquedaDatalist(inputId, cfg.datalistId, cfg.getItems(), cfg.label, cfg.fields);
    }

    function refreshAllBusquedaDatalists() {
      Object.keys(BUSQUEDA_DL_BY_INPUT).forEach((id) => refreshBusquedaDatalist(id));
    }

    function refreshAllConsultaTables() {
      renderClientes();
      renderTransportistas();
      renderViajes();
      renderFletes();
      renderOrdenesServicio();
      renderFacturas();
      renderTarifas();
      renderTarifasCompra();
      renderGastos();
      renderOperadores();
      renderUnidades();
      renderAsignaciones();
      renderDespachos();
      refreshAllBusquedaDatalists();
    }

    function filteredClientes() {
      const buscar = uiState.clienteFilters.buscar.trim();
      const activo = uiState.clienteFilters.activo;
      const modo = uiState.buscarModo || "contiene";
      return state.clientes.filter((item) => {
        if (
          buscar &&
          !matchesBusqueda(buscar, [item.razon_social, item.nombre_comercial, item.rfc], modo)
        ) {
          return false;
        }
        if (activo === "true" && !item.activo) {
          return false;
        }
        if (activo === "false" && item.activo) {
          return false;
        }
        return true;
      });
    }

    function filteredFletes() {
      const buscar = (uiState.fleteFilters.buscar || "").trim();
      const modo = uiState.buscarModo || "contiene";
      return state.fletes.filter((item) => {
        if (buscar) {
          const cliente = item.cliente?.razon_social || item.cliente?.nombre_comercial || "";
          const transp = item.transportista?.nombre || item.transportista?.nombre_comercial || "";
          const viajeCod = item.viaje?.codigo_viaje || "";
          if (
            !matchesBusqueda(
              buscar,
              [
                String(item.id ?? ""),
                item.codigo_flete || "",
                cliente,
                transp,
                item.estado || "",
                viajeCod,
              ],
              modo,
            )
          ) {
            return false;
          }
        }
        if (uiState.fleteFilters.estado && item.estado !== uiState.fleteFilters.estado) {
          return false;
        }
        if (uiState.fleteFilters.cliente_id && String(item.cliente_id) !== uiState.fleteFilters.cliente_id) {
          return false;
        }
        if (uiState.fleteFilters.transportista_id && String(item.transportista_id) !== uiState.fleteFilters.transportista_id) {
          return false;
        }
        return true;
      });
    }

    function filteredTarifasVenta() {
      const buscar = (uiState.tarifaVentaFilters.buscar || "").trim();
      const modo = uiState.buscarModo || "contiene";
      return state.tarifas.filter((item) => {
        if (!buscar) {
          return true;
        }
        return matchesBusqueda(
          buscar,
          [
            String(item.id ?? ""),
            item.nombre_tarifa || "",
            item.origen || "",
            item.destino || "",
            item.tipo_unidad || "",
            item.tipo_carga || "",
            item.tipo_operacion || "",
            String(item.ambito || ""),
            String(item.modalidad_cobro || ""),
          ],
          modo,
        );
      });
    }

    function filteredGastos() {
      const buscar = (uiState.gastoFilters.buscar || "").trim();
      const modo = uiState.buscarModo || "contiene";
      return state.gastos.filter((item) => {
        if (!buscar) {
          return true;
        }
        return matchesBusqueda(
          buscar,
          [
            String(item.id ?? ""),
            String(item.flete_id ?? ""),
            item.tipo_gasto || "",
            item.referencia || "",
            item.descripcion || "",
            String(item.monto ?? ""),
          ],
          modo,
        );
      });
    }

    function filteredOperadores() {
      const buscar = (uiState.operadorFilters.buscar || "").trim();
      const modo = uiState.buscarModo || "contiene";
      return state.operadores.filter((item) => {
        if (!buscar) {
          return true;
        }
        const transp = state.transportistas.find((t) => t.id === item.transportista_id)?.nombre || "";
        return matchesBusqueda(
          buscar,
          [
            String(item.id_operador ?? ""),
            item.nombre || "",
            item.apellido_paterno || "",
            item.apellido_materno || "",
            item.curp || "",
            item.telefono_principal || "",
            item.certificaciones || "",
            transp,
          ],
          modo,
        );
      });
    }

    function filteredUnidades() {
      const buscar = (uiState.unidadFilters.buscar || "").trim();
      const modo = uiState.buscarModo || "contiene";
      const ft = uiState.unidadFilters.tipo_propiedad || "";
      const fe = uiState.unidadFilters.estatus_documental || "";
      const fa = uiState.unidadFilters.activo || "";
      return state.unidades.filter((item) => {
        if (ft && (item.tipo_propiedad || "") !== ft) {
          return false;
        }
        if (fe && (item.estatus_documental || "") !== fe) {
          return false;
        }
        if (fa !== "" && String(Boolean(item.activo)) !== fa) {
          return false;
        }
        if (!buscar) {
          return true;
        }
        const transp =
          state.transportistas.find((t) => String(t.id) === String(item.transportista_id))?.nombre || "";
        const tipoP = item.tipo_propiedad || "";
        const estDoc = item.estatus_documental || "";
        return matchesBusqueda(
          buscar,
          [
            String(item.id_unidad ?? ""),
            item.economico || "",
            item.placas || "",
            item.descripcion || "",
            transp,
            tipoP,
            estDoc,
          ],
          modo,
        );
      });
    }

    function filteredTransportistas() {
      const buscar = uiState.transportistaFilters.buscar.trim();
      const modo = uiState.buscarModo || "contiene";
      return state.transportistas.filter((item) => {
        if (buscar && !matchesBusqueda(buscar, [item.nombre, item.nombre_comercial, item.rfc], modo)) {
          return false;
        }
        if (
          uiState.transportistaFilters.estatus &&
          (item.estatus || (item.activo ? "activo" : "inactivo")) !== uiState.transportistaFilters.estatus
        ) {
          return false;
        }
        if (
          uiState.transportistaFilters.tipo_transportista &&
          item.tipo_transportista !== uiState.transportistaFilters.tipo_transportista
        ) {
          return false;
        }
        return true;
      });
    }

    function filteredViajes() {
      const buscar = uiState.viajeFilters.buscar.trim();
      const modo = uiState.buscarModo || "contiene";
      return state.viajes.filter((item) => {
        if (
          buscar &&
          !matchesBusqueda(buscar, [item.codigo_viaje, item.origen, item.destino, String(item.id ?? "")], modo)
        ) {
          return false;
        }
        if (uiState.viajeFilters.estado && item.estado !== uiState.viajeFilters.estado) {
          return false;
        }
        return true;
      });
    }

    function filteredFacturas() {
      const buscar = uiState.facturaFilters.buscar.trim();
      const modo = uiState.buscarModo || "contiene";
      return state.facturas.filter((item) => {
        if (
          buscar &&
          !matchesBusqueda(buscar, [item.folio, item.concepto, item.referencia, String(item.id ?? "")], modo)
        ) {
          return false;
        }
        if (
          uiState.facturaFilters.cliente_id &&
          String(item.cliente_id) !== uiState.facturaFilters.cliente_id
        ) {
          return false;
        }
        if (uiState.facturaFilters.estatus && item.estatus !== uiState.facturaFilters.estatus) {
          return false;
        }
        return true;
      });
    }

    function filteredTarifasCompra() {
      const buscar = uiState.tarifaCompraFilters.buscar.trim();
      const modo = uiState.buscarModo || "contiene";
      return state.tarifasCompra.filter((item) => {
        const transpNombre =
          state.transportistas.find((t) => Number(t.id) === Number(item.transportista_id))?.nombre || "";
        if (
          buscar &&
          !matchesBusqueda(
            buscar,
            [item.nombre_tarifa, item.origen, item.destino, item.tipo_unidad, transpNombre, String(item.id ?? "")],
            modo,
          )
        ) {
          return false;
        }
        if (
          uiState.tarifaCompraFilters.transportista_id &&
          String(item.transportista_id) !== uiState.tarifaCompraFilters.transportista_id
        ) {
          return false;
        }
        if (
          uiState.tarifaCompraFilters.activo &&
          String(Boolean(item.activo)) !== uiState.tarifaCompraFilters.activo
        ) {
          return false;
        }
        return true;
      });
    }

    function filteredAsignaciones() {
      const buscar = (uiState.asignacionFilters.buscar || "").trim();
      const modo = uiState.buscarModo || "contiene";
      return state.asignaciones.filter((item) => {
        if (buscar) {
          const nom = `${item.operador?.nombre || ""} ${item.operador?.apellido_paterno || ""} ${item.operador?.apellido_materno || ""}`;
          const ec = item.unidad?.economico || "";
          const cv = item.viaje?.codigo_viaje || "";
          if (!matchesBusqueda(buscar, [String(item.id_asignacion), nom, ec, cv], modo)) {
            return false;
          }
        }
        if (
          uiState.asignacionFilters.id_operador &&
          String(item.id_operador) !== uiState.asignacionFilters.id_operador
        ) {
          return false;
        }
        if (
          uiState.asignacionFilters.id_unidad &&
          String(item.id_unidad) !== uiState.asignacionFilters.id_unidad
        ) {
          return false;
        }
        if (
          uiState.asignacionFilters.id_viaje &&
          String(item.id_viaje) !== uiState.asignacionFilters.id_viaje
        ) {
          return false;
        }
        return true;
      });
    }

    function filteredDespachos() {
      const buscar = (uiState.despachoFilters.buscar || "").trim();
      const modo = uiState.buscarModo || "contiene";
      return state.despachos.filter((item) => {
        if (buscar) {
          const cf = item.flete?.codigo_flete || "";
          const cv = item.asignacion?.viaje?.codigo_viaje || "";
          if (!matchesBusqueda(buscar, [String(item.id_despacho), item.estatus || "", cf, cv], modo)) {
            return false;
          }
        }
        if (uiState.despachoFilters.estatus && item.estatus !== uiState.despachoFilters.estatus) {
          return false;
        }
        if (uiState.despachoFilters.id_asignacion && String(item.id_asignacion) !== uiState.despachoFilters.id_asignacion) {
          return false;
        }
        if (uiState.despachoFilters.id_flete && String(item.id_flete || "") !== uiState.despachoFilters.id_flete) {
          return false;
        }
        return true;
      });
    }

    function buildFletePayload(form) {
      return {
        codigo_flete: clean(form.get("codigo_flete")),
        cliente_id: integerOrNull(form.get("cliente_id")),
        transportista_id: integerOrNull(form.get("transportista_id")),
        viaje_id: integerOrNull(form.get("viaje_id")),
        tipo_operacion: clean(form.get("tipo_operacion")) || "subcontratado",
        tipo_unidad: clean(form.get("tipo_unidad")),
        tipo_carga: clean(form.get("tipo_carga")),
        descripcion_carga: clean(form.get("descripcion_carga")),
        peso_kg: numberOrNull(form.get("peso_kg")),
        volumen_m3: numberOrNull(form.get("volumen_m3")),
        numero_bultos: integerOrNull(form.get("numero_bultos")),
        distancia_km: numberOrNull(form.get("distancia_km")),
        monto_estimado: numberOrNull(form.get("monto_estimado")),
        precio_venta: numberOrNull(form.get("monto_estimado")),
        costo_transporte_estimado: numberOrNull(form.get("costo_transporte_estimado")),
        costo_transporte_real: numberOrNull(form.get("costo_transporte_real")),
        margen_estimado: numberOrNull(form.get("margen_estimado")),
        metodo_calculo: clean(form.get("metodo_calculo")) || "manual",
        moneda: clean(form.get("moneda")) || "MXN",
        estado: clean(form.get("estado")) || "cotizado",
        notas: clean(form.get("notas")),
      };
    }

    function buildOperadorPayload(form) {
      return {
        transportista_id: integerOrNull(form.get("transportista_id")),
        tipo_contratacion: clean(form.get("tipo_contratacion")),
        licencia: clean(form.get("licencia")),
        tipo_licencia: clean(form.get("tipo_licencia")),
        vigencia_licencia: normalizeDateOnlyForApi(form.get("vigencia_licencia")),
        estatus_documental: clean(form.get("estatus_documental")),
        nombre: clean(form.get("nombre")),
        apellido_paterno: clean(form.get("apellido_paterno")),
        apellido_materno: clean(form.get("apellido_materno")),
        fecha_nacimiento: normalizeDateOnlyForApi(form.get("fecha_nacimiento")),
        curp: clean(form.get("curp")),
        rfc: clean(form.get("rfc")),
        nss: clean(form.get("nss")),
        estado_civil: clean(form.get("estado_civil")),
        tipo_sangre: clean(form.get("tipo_sangre")),
        fotografia: clean(form.get("fotografia")),
        telefono_principal: clean(form.get("telefono_principal")),
        telefono_emergencia: clean(form.get("telefono_emergencia")),
        nombre_contacto_emergencia: clean(form.get("nombre_contacto_emergencia")),
        direccion: clean(form.get("direccion")),
        colonia: clean(form.get("colonia")),
        municipio: clean(form.get("municipio")),
        estado_geografico: clean(form.get("estado_geografico")),
        codigo_postal: clean(form.get("codigo_postal")),
        correo_electronico: clean(form.get("correo_electronico")),
        anios_experiencia: integerOrNull(form.get("anios_experiencia")),
        tipos_unidad_manejadas: clean(form.get("tipos_unidad_manejadas"))
          ? clean(form.get("tipos_unidad_manejadas"))
              .split(",")
              .map((item) => item.trim())
              .filter(Boolean)
          : null,
        rutas_conocidas: clean(form.get("rutas_conocidas")),
        tipos_carga_experiencia: clean(form.get("tipos_carga_experiencia"))
          ? clean(form.get("tipos_carga_experiencia"))
              .split(",")
              .map((item) => item.trim())
              .filter(Boolean)
          : null,
        certificaciones: clean(form.get("certificaciones")),
        ultima_revision_medica: normalizeDateOnlyForApi(form.get("ultima_revision_medica")),
        resultado_apto: form.get("resultado_apto") === "on" ? true : null,
        restricciones_medicas: clean(form.get("restricciones_medicas")),
        proxima_revision_medica: normalizeDateOnlyForApi(form.get("proxima_revision_medica")),
        puntualidad: numberOrNull(form.get("puntualidad")),
        consumo_diesel_promedio: numberOrNull(form.get("consumo_diesel_promedio")),
        consumo_gasolina_promedio: numberOrNull(form.get("consumo_gasolina_promedio")),
        incidencias_desempeno: clean(form.get("incidencias_desempeno")),
        calificacion_general: numberOrNull(form.get("calificacion_general")),
        comentarios_desempeno: clean(form.get("comentarios_desempeno")),
      };
    }

    function operadorCsvFromApi(value) {
      if (value == null || value === undefined) {
        return "";
      }
      if (Array.isArray(value)) {
        return value.map((x) => String(x).trim()).filter(Boolean).join(", ");
      }
      return String(value).trim();
    }

    function buildUnidadPayload(formData) {
      return {
        transportista_id: integerOrNull(formData.get("transportista_id")),
        economico: clean(formData.get("economico")),
        placas: clean(formData.get("placas")),
        tipo_propiedad: clean(formData.get("tipo_propiedad")),
        estatus_documental: clean(formData.get("estatus_documental")),
        descripcion: clean(formData.get("descripcion")),
        detalle: clean(formData.get("detalle")),
        activo: formData.get("activo") === "on",
        vigencia_permiso_sct: normalizeDateOnlyForApi(formData.get("vigencia_permiso_sct")),
        vigencia_seguro: normalizeDateOnlyForApi(formData.get("vigencia_seguro")),
      };
    }

    function updateFleteMargenPctHint(formSelector) {
      const ventaField = document.querySelector(`${formSelector} [name="monto_estimado"]`);
      const margenInput = document.querySelector(`${formSelector} [name="margen_estimado"]`);
      const pctHintId =
        formSelector === "#flete-edit-form" ? "flete-edit-margen-pct-hint" : "flete-margen-pct-hint-new";
      const pctHint = document.getElementById(pctHintId);
      if (!ventaField || !margenInput || !pctHint) {
        return;
      }
      const venta = numberOrNull(ventaField.value);
      const margenNum = numberOrNull(margenInput.value);
      if (venta !== null && venta > 0 && margenNum !== null) {
        const pct = (margenNum / venta) * 100;
        pctHint.textContent = `Margen estimado sobre venta: ${formatLocaleDecimal(pct, 2, 2)} %`;
      } else {
        pctHint.textContent = "";
      }
    }

    function refreshMarginForForm(formSelector) {
      const ventaField = document.querySelector(`${formSelector} [name="monto_estimado"]`);
      const costoField = document.querySelector(`${formSelector} [name="costo_transporte_estimado"]`);
      const margenInput = document.querySelector(`${formSelector} [name="margen_estimado"]`);
      if (!ventaField || !costoField || !margenInput) {
        return;
      }
      const venta = numberOrNull(ventaField.value);
      const costo = numberOrNull(costoField.value);
      if (!margenInput) {
        return;
      }
      if (venta !== null && costo !== null) {
        margenInput.value = formatMoneyInputFromEl(venta - costo, margenInput);
      } else {
        margenInput.value = "";
      }
      updateFleteMargenPctHint(formSelector);
    }

    /** Enter en inputs/selects pasa al siguiente campo (no envia el formulario). */
    function wireEnterAvanzaCampo(formSelector) {
      const form = document.querySelector(formSelector);
      if (!form) {
        return;
      }
      form.addEventListener("keydown", (e) => {
        if (e.key !== "Enter") {
          return;
        }
        if (e.target.tagName === "TEXTAREA") {
          return;
        }
        if (e.target.closest && e.target.closest("button")) {
          return;
        }
        const t = e.target.tagName;
        if (t !== "INPUT" && t !== "SELECT") {
          return;
        }
        if (t === "INPUT" && (e.target.type === "submit" || e.target.type === "button")) {
          return;
        }
        e.preventDefault();
        const focusables = Array.from(
          form.querySelectorAll(
            'input:not([type="hidden"]):not([disabled]), select:not([disabled]), textarea:not([disabled])',
          ),
        ).filter((el) => el.offsetParent !== null);
        const idx = focusables.indexOf(e.target);
        if (idx >= 0 && idx < focusables.length - 1) {
          focusables[idx + 1].focus();
        }
      });
    }

    /** Igual que en el backend: si el flete no trae km, usar kilometros_estimados del viaje. */
    function resolveDistanciaKmForQuote(payload, viaje) {
      if (payload.distancia_km !== null && payload.distancia_km !== undefined) {
        return payload.distancia_km;
      }
      const km = viaje && viaje.kilometros_estimados;
      if (km === null || km === undefined || km === "") {
        return null;
      }
      const n = typeof km === "number" ? km : parseLocaleNumber(String(km));
      return n !== null && Number.isFinite(n) ? n : null;
    }

    /** Viaje del catalogo en memoria (API /viajes). Normaliza ID para evitar fallo 1 vs "1". */
    function findViajeForFleteQuote(payload) {
      const raw = payload.viaje_id;
      if (raw === null || raw === undefined || raw === "") {
        throw new Error("Selecciona un viaje en la lista (origen y destino salen del viaje).");
      }
      const n = Number(raw);
      if (!Number.isFinite(n) || n < 1) {
        throw new Error("El viaje seleccionado no es valido. Vuelve a elegirlo en la lista.");
      }
      const viaje = state.viajes.find((item) => Number(item.id) === n);
      if (viaje) {
        return viaje;
      }
      if (!state.viajes.length) {
        throw new Error(
          "No hay viajes cargados en pantalla. Actualiza la pagina (F5) o abre el modulo Viajes y espera a que cargue el listado.",
        );
      }
      throw new Error(
        "No se encontro el viaje en el catalogo. Vuelve a elegir el viaje en el selector o actualiza la pagina.",
      );
    }

    function initFleteCotizador() {
      const ventaButton = document.getElementById("flete-cotizar-btn");
      const compraButton = document.getElementById("flete-cotizar-compra-btn");
      const editVentaButton = document.getElementById("edit-flete-cotizar-venta-btn");
      const editCompraButton = document.getElementById("edit-flete-cotizar-compra-btn");
      if (!ventaButton && !compraButton && !editVentaButton && !editCompraButton) {
        return;
      }

      const costoInput = document.querySelector('#flete-form [name="costo_transporte_estimado"]');
      const ventaInput = document.querySelector('#flete-form [name="monto_estimado"]');
      const editCostoInput = document.querySelector('#flete-edit-form [name="costo_transporte_estimado"]');
      const editVentaInput = document.querySelector('#flete-edit-form [name="monto_estimado"]');

      if (costoInput) {
        costoInput.addEventListener("input", () => refreshMarginForForm("#flete-form"));
      }
      if (ventaInput) {
        ventaInput.addEventListener("input", () => refreshMarginForForm("#flete-form"));
      }
      if (editCostoInput) {
        editCostoInput.addEventListener("input", () => refreshMarginForForm("#flete-edit-form"));
      }
      if (editVentaInput) {
        editVentaInput.addEventListener("input", () => refreshMarginForForm("#flete-edit-form"));
      }
      const margenNewInput = document.querySelector('#flete-form [name="margen_estimado"]');
      const margenEditInput = document.querySelector('#flete-edit-form [name="margen_estimado"]');
      if (margenNewInput) {
        margenNewInput.addEventListener("input", () => updateFleteMargenPctHint("#flete-form"));
      }
      if (margenEditInput) {
        margenEditInput.addEventListener("input", () => updateFleteMargenPctHint("#flete-edit-form"));
      }

      async function quoteVenta(formSelector, detailId, messageId, options = {}) {
        if (!options.silent) {
          clearMessage(messageId);
        }
        const formElement = document.querySelector(formSelector);
        const detail = document.getElementById(detailId);
        try {
          const payload = buildFletePayload(new FormData(formElement));
          const viaje = findViajeForFleteQuote(payload);
          if (!payload.tipo_unidad) {
            throw new Error("Escribe el tipo de unidad antes de cotizar venta.");
          }
          const distanciaKm = resolveDistanciaKmForQuote(payload, viaje);
          if (distanciaKm === null) {
            throw new Error(
              "Captura la distancia en km en el flete o define kilometros estimados en el viaje.",
            );
          }
          if (payload.peso_kg === null) {
            throw new Error("Captura el peso en kg antes de cotizar venta.");
          }

          const quote = await api("/fletes/cotizar", {
            method: "POST",
            body: JSON.stringify({
              cliente_id: payload.cliente_id,
              tipo_operacion: payload.tipo_operacion || "subcontratado",
              origen: viaje.origen,
              destino: viaje.destino,
              tipo_unidad: payload.tipo_unidad,
              tipo_carga: payload.tipo_carga,
              distancia_km: distanciaKm,
              peso_kg: payload.peso_kg,
              recargos: 0,
            }),
          });

          const ventaEl = document.querySelector(`${formSelector} [name="monto_estimado"]`);
          if (!ventaEl) {
            throw new Error("No se encontro el campo Precio venta en el formulario.");
          }
          const distInput = document.querySelector(`${formSelector} [name="distancia_km"]`);
          if (
            distInput &&
            (!String(distInput.value || "").trim() || payload.distancia_km === null) &&
            distanciaKm !== null
          ) {
            distInput.value = htmlNumberInputValue(distanciaKm);
          }
          ventaEl.value = formatMoneyInputFromEl(Number(quote.precio_venta_sugerido), ventaEl);
          document.querySelector(`${formSelector} [name="moneda"]`).value = quote.moneda;
          document.querySelector(`${formSelector} [name="metodo_calculo"]`).value = "tarifa";
          refreshMarginForForm(formSelector);
          const advVenta =
            quote.advertencias && quote.advertencias.length
              ? ` Advertencias: ${quote.advertencias.join(" | ")}`
              : "";
          detail.textContent = `Tarifa venta: ${quote.nombre_tarifa}. ${quote.detalle_calculo}${advVenta}`;
          if (!options.silent) {
            setMessage(
              messageId,
              `Venta sugerida: ${formatLocaleDecimal(Number(quote.precio_venta_sugerido), 2, 2)} ${quote.moneda}`,
              "ok",
            );
          }
          return true;
        } catch (error) {
          if (!options.silent) {
            detail.textContent = "No se pudo cotizar automaticamente la venta.";
            setMessage(messageId, error.message, "error");
          }
          return false;
        }
      }

      async function quoteCompra(formSelector, detailId, messageId, options = {}) {
        if (!options.silent) {
          clearMessage(messageId);
        }
        const formElement = document.querySelector(formSelector);
        const detail = document.getElementById(detailId);
        try {
          const payload = buildFletePayload(new FormData(formElement));
          const viaje = findViajeForFleteQuote(payload);
          if (!payload.transportista_id) {
            throw new Error("Selecciona el transportista antes de cotizar compra.");
          }
          if (!payload.tipo_unidad) {
            throw new Error("Escribe el tipo de unidad antes de cotizar compra.");
          }
          const distanciaKm = resolveDistanciaKmForQuote(payload, viaje);
          if (distanciaKm === null) {
            throw new Error(
              "Captura la distancia en km en el flete o define kilometros estimados en el viaje.",
            );
          }
          if (payload.peso_kg === null) {
            throw new Error("Captura el peso en kg antes de cotizar compra.");
          }

          const quote = await api("/fletes/cotizar-compra", {
            method: "POST",
            body: JSON.stringify({
              transportista_id: payload.transportista_id,
              origen: viaje.origen,
              destino: viaje.destino,
              tipo_unidad: payload.tipo_unidad,
              tipo_carga: payload.tipo_carga,
              distancia_km: distanciaKm,
              peso_kg: payload.peso_kg,
              recargos: 0,
            }),
          });

          const compraEl = document.querySelector(`${formSelector} [name="costo_transporte_estimado"]`);
          if (!compraEl) {
            throw new Error("No se encontro el campo Costo estimado en el formulario.");
          }
          const distInput = document.querySelector(`${formSelector} [name="distancia_km"]`);
          if (
            distInput &&
            (!String(distInput.value || "").trim() || payload.distancia_km === null) &&
            distanciaKm !== null
          ) {
            distInput.value = htmlNumberInputValue(distanciaKm);
          }
          compraEl.value = formatMoneyInputFromEl(Number(quote.costo_compra_sugerido), compraEl);
          if (!document.querySelector(`${formSelector} [name="moneda"]`).value) {
            document.querySelector(`${formSelector} [name="moneda"]`).value = quote.moneda;
          }
          refreshMarginForForm(formSelector);
          const advCompra =
            quote.advertencias && quote.advertencias.length
              ? ` Advertencias: ${quote.advertencias.join(" | ")}`
              : "";
          detail.textContent = `Tarifa compra: ${quote.nombre_tarifa}. ${quote.detalle_calculo}. Credito: ${quote.dias_credito} dias.${advCompra}`;
          if (!options.silent) {
            setMessage(
              messageId,
              `Compra sugerida: ${formatLocaleDecimal(Number(quote.costo_compra_sugerido), 2, 2)} ${quote.moneda}`,
              "ok",
            );
          }
          return true;
        } catch (error) {
          if (!options.silent) {
            detail.textContent = "No se pudo cotizar automaticamente la compra.";
            setMessage(messageId, error.message, "error");
          }
          return false;
        }
      }

      const autoQuoteTimers = {};

      function scheduleAutoQuote(formSelector, ventaDetailId, compraDetailId, messageId) {
        const formElement = document.querySelector(formSelector);
        if (!formElement) {
          return;
        }
        const payload = buildFletePayload(new FormData(formElement));
        if (payload.metodo_calculo !== "tarifa") {
          return;
        }
        let viajeAq = null;
        try {
          viajeAq = findViajeForFleteQuote(payload);
        } catch (_e) {
          return;
        }
        const distanciaAq = resolveDistanciaKmForQuote(payload, viajeAq);
        if (!payload.viaje_id || !payload.tipo_unidad || distanciaAq === null || payload.peso_kg === null) {
          return;
        }

        window.clearTimeout(autoQuoteTimers[formSelector]);
        autoQuoteTimers[formSelector] = window.setTimeout(async () => {
          await quoteVenta(formSelector, ventaDetailId, messageId, { silent: true });
          if (payload.transportista_id) {
            await quoteCompra(formSelector, compraDetailId, messageId, { silent: true });
          }
        }, 350);
      }

      function attachAutoQuote(formSelector, ventaDetailId, compraDetailId, messageId) {
        const formElement = document.querySelector(formSelector);
        if (!formElement) {
          return;
        }
        const watchedNames = [
          "cliente_id",
          "transportista_id",
          "viaje_id",
          "tipo_unidad",
          "tipo_carga",
          "distancia_km",
          "peso_kg",
          "metodo_calculo",
        ];
        for (const name of watchedNames) {
          const input = formElement.querySelector(`[name="${name}"]`);
          if (!input) {
            continue;
          }
          const eventName = input.tagName === "SELECT" ? "change" : "input";
          input.addEventListener(eventName, () => {
            scheduleAutoQuote(formSelector, ventaDetailId, compraDetailId, messageId);
          });
          if (eventName !== "change") {
            input.addEventListener("change", () => {
              scheduleAutoQuote(formSelector, ventaDetailId, compraDetailId, messageId);
            });
          }
        }
      }

      if (ventaButton) {
        ventaButton.addEventListener("click", () => quoteVenta("#flete-form", "flete-cotizacion-detalle", "flete-message"));
      }
      if (compraButton) {
        compraButton.addEventListener("click", () => quoteCompra("#flete-form", "flete-cotizacion-compra-detalle", "flete-message"));
      }
      if (editVentaButton) {
        editVentaButton.addEventListener("click", () => quoteVenta("#flete-edit-form", "edit-flete-cotizacion-detalle", "flete-edit-message"));
      }
      if (editCompraButton) {
        editCompraButton.addEventListener("click", () => quoteCompra("#flete-edit-form", "edit-flete-cotizacion-compra-detalle", "flete-edit-message"));
      }

      attachAutoQuote("#flete-form", "flete-cotizacion-detalle", "flete-cotizacion-compra-detalle", "flete-message");
      attachAutoQuote("#flete-edit-form", "edit-flete-cotizacion-detalle", "edit-flete-cotizacion-compra-detalle", "flete-edit-message");
    }

    function initFacturaModule() {
      const today = new Date().toISOString().slice(0, 10);
      const facturaForm = document.getElementById("factura-form");
      if (facturaForm && !facturaForm.elements.fecha_emision.value) {
        facturaForm.elements.fecha_emision.value = today;
      }

      if (!window.__facturaClienteFleteSyncBound) {
        window.__facturaClienteFleteSyncBound = true;
        const fc = document.getElementById("factura-cliente");
        const ff = document.getElementById("factura-flete");
        if (fc && ff) {
          fc.addEventListener("change", () => {
            const prevFlete = integerOrNull(ff.value);
            fillFacturaFleteSelectFiltered(fc.value);
            if (
              prevFlete != null &&
              [...ff.options].some((o) => o.value === String(prevFlete))
            ) {
              ff.value = String(prevFlete);
            }
          });
          ff.addEventListener("change", () => {
            const fid = integerOrNull(ff.value);
            if (!fid) {
              return;
            }
            const f = state.fletes.find((x) => x.id === fid);
            if (f && fc) {
              fc.value = String(f.cliente_id);
              fillFacturaFleteSelectFiltered(fc.value);
              ff.value = String(fid);
            }
          });
        }
      }

      const watchedSelectors = [
        '#factura-form [name="subtotal"]',
        '#factura-form [name="iva_pct"]',
        '#factura-form [name="retencion_monto"]',
        '#factura-edit-form [name="subtotal"]',
        '#factura-edit-form [name="iva_pct"]',
        '#factura-edit-form [name="retencion_monto"]',
      ];
      for (const selector of watchedSelectors) {
        const input = document.querySelector(selector);
        if (!input) {
          continue;
        }
        const formSelector = selector.startsWith("#factura-edit-form") ? "#factura-edit-form" : "#factura-form";
        input.addEventListener("input", () => recalculateFacturaForm(formSelector));
      }

      const autoFillButton = document.getElementById("factura-desde-flete-btn");
      if (autoFillButton) {
        autoFillButton.addEventListener("click", () => {
          clearMessage("factura-message");
          try {
            fillFacturaFromFlete("#factura-form");
            setMessage("factura-message", "Factura autollenada desde el flete.", "ok");
          } catch (error) {
            setMessage("factura-message", error.message, "error");
          }
        });
      }

      const previewFleteBtn = document.getElementById("factura-preview-flete-btn");
      if (previewFleteBtn) {
        previewFleteBtn.addEventListener("click", async () => {
          clearMessage("factura-message");
          const fleteId = integerOrNull(new FormData(document.getElementById("factura-form")).get("flete_id"));
          if (!fleteId) {
            setMessage("factura-message", "Selecciona un flete en el formulario.", "error");
            return;
          }
          try {
            const data = await api(`/facturas/preview-desde-flete/${fleteId}`);
            const fmtN = (v) =>
              v === null || v === undefined ? "—" : formatLocaleDecimal(Number(v), 2, 2);
            const linea1 = `Precio en flete: ${fmtN(data.subtotal_desde_flete)} → IVA ${fmtN(data.iva_monto)} → Total ${fmtN(data.total)} (${data.moneda}).`;
            const linea2 =
              data.subtotal_desde_tarifa_recalculado != null
                ? `Tarifa vigente «${data.nombre_tarifa || "?"}»: ${fmtN(data.subtotal_desde_tarifa_recalculado)} → total ${fmtN(data.total_si_precio_tarifa)}.`
                : `Tarifa automática: ${data.observaciones_sistema}`;
            setMessage("factura-message", `${linea1} ${linea2}`, "ok");
          } catch (error) {
            setMessage("factura-message", error.message, "error");
          }
        });
      }

      const generarAutoBtn = document.getElementById("factura-generar-auto-btn");
      if (generarAutoBtn) {
        generarAutoBtn.addEventListener("click", async () => {
          clearMessage("factura-message");
          const fleteId = integerOrNull(new FormData(document.getElementById("factura-form")).get("flete_id"));
          if (!fleteId) {
            setMessage("factura-message", "Selecciona un flete en el formulario.", "error");
            return;
          }
          const usarTarifa = document.getElementById("factura-gen-usar-tarifa")?.checked || false;
          try {
            const today = new Date().toISOString().slice(0, 10);
            await api("/facturas/generar-desde-flete", {
              method: "POST",
              body: JSON.stringify({
                flete_id: fleteId,
                fecha_emision: today,
                estatus: "emitida",
                usar_precio_tarifa_recalculado: usarTarifa,
              }),
            });
            setMessage("factura-message", "Factura generada. Actualizando datos…", "ok");
            await refreshData();
            setGenericSubpage("factura", "facturaSubpage", "consulta", "consulta");
          } catch (error) {
            setMessage("factura-message", error.message, "error");
          }
        });
      }

      const facturaOsFolioAplicar = document.getElementById("factura-os-folio-aplicar");
      if (facturaOsFolioAplicar) {
        facturaOsFolioAplicar.addEventListener("click", () => {
          aplicarFolioOrdenServicioAFactura("factura-message", "factura-os-folio-buscar", "factura-form-orden-servicio-id");
        });
      }
      const editFacturaOsFolioAplicar = document.getElementById("edit-factura-os-folio-aplicar");
      if (editFacturaOsFolioAplicar) {
        editFacturaOsFolioAplicar.addEventListener("click", () => {
          aplicarFolioOrdenServicioAFactura("factura-edit-message", "edit-factura-os-folio-buscar", "edit-factura-form-orden-servicio-id");
        });
      }
    }

    function setPage(page) {
      const target = pageMeta[page] ? page : "inicio";
      for (const section of document.querySelectorAll(".page")) {
        section.classList.toggle("active", section.id === `page-${target}`);
      }
      for (const button of document.querySelectorAll(".nav-button[data-page]")) {
        button.classList.toggle("active", button.dataset.page === target);
      }
      document.getElementById("page-title").textContent = pageMeta[target][0];
      document.getElementById("page-description").textContent = pageMeta[target][1];
      window.location.hash = target;
      if (target === "fletes" && typeof populateSelects === "function") {
        populateSelects();
      }
      if (
        target === "unidades" &&
        state.catalogLoaded &&
        Array.isArray(state.unidades) &&
        state.unidades.length === 0
      ) {
        void refreshData().catch((e) => {
          setMessage("unidad-consulta-message", e.message || "No se pudo recargar el catalogo.", "error");
        });
      }
    }

    function initNavigation() {
      const sidebar = document.querySelector("aside.sidebar");
      if (sidebar) {
        sidebar.addEventListener("click", (event) => {
          const btn = event.target && event.target.closest
            ? event.target.closest("button.nav-button[data-page]")
            : null;
          if (!btn) return;
          event.preventDefault();
          setPage(btn.dataset.page);
        });
      }
      window.addEventListener("hashchange", () => {
        const h = window.location.hash.replace(/^#/, "").split("&")[0];
        if (h && pageMeta[h]) {
          setPage(h);
        }
      });
      const initialHash = window.location.hash.replace(/^#/, "").split("&")[0];
      setPage(initialHash && pageMeta[initialHash] ? initialHash : "inicio");
      window.sifeSetPage = setPage;
    }

    async function api(path, options = {}) {
      const headers = {
        "Accept": "application/json",
        "X-API-Key": API_KEY,
        ...(options.body ? {"Content-Type": "application/json"} : {}),
        ...(options.headers || {}),
      };

      const response = await fetch(`${API_BASE}${path}`, {
        method: options.method || "GET",
        headers,
        body: options.body,
      });

      if (!response.ok) {
        let detail = `HTTP ${response.status}`;
        const raw = await response.text();
        try {
          const payload = raw ? JSON.parse(raw) : {};
          if (typeof payload.detail === "string") {
            detail = payload.detail;
          } else if (Array.isArray(payload.detail)) {
            detail = payload.detail.map((item) => item.msg || JSON.stringify(item)).join(" | ");
          } else if (
            payload.detail &&
            typeof payload.detail === "object" &&
            payload.detail.tipo === "cumplimiento_documental"
          ) {
            const b = (payload.detail.bloqueos || []).join("\\n• ");
            const a = (payload.detail.advertencias || []).join("\\n• ");
            detail =
              (payload.detail.mensaje || "Validación documental.") +
              (b ? "\\n\\nPendientes:\\n• " + b : "") +
              (a ? "\\n\\nAdvertencias:\\n• " + a : "");
          } else if (payload.detail !== undefined) {
            detail = JSON.stringify(payload.detail);
          } else if (raw) {
            detail = raw;
          }
        } catch (_parseError) {
          if (raw) {
            detail = raw;
          }
        }
        throw new Error(detail);
      }

      if (response.status === 204) {
        return null;
      }

      return response.json();
    }

    const SELECT_CLASS = {
      cliente: { tag: "Cliente", title: "Catalogo comercial: clientes (razon social, RFC)." },
      transportista: { tag: "Transportista", title: "Catalogo de proveedores de transporte." },
      viaje: { tag: "Viaje", title: "Planes de ruta (codigo, origen, destino)." },
      flete: { tag: "Flete", title: "Servicios de flete vinculados a cliente y viaje." },
      operador: { tag: "Operador", title: "Choferes dados de alta para operacion." },
      unidad: { tag: "Unidad", title: "Vehiculos (economico, placas) por transportista." },
      asignacion: { tag: "Asignacion", title: "Combinacion operador + unidad + viaje." },
      despacho: { tag: "Despacho", title: "Salidas programadas ligadas a asignacion y flete." },
    };

    function escapeSelectAttr(value) {
      return String(value)
        .replace(/&/g, "&amp;")
        .replace(/"/g, "&quot;");
    }

    function escapeSelectText(value) {
      return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
    }

    function fillSelect(selectId, items, getValue, getLabel, options = {}) {
      const select = document.getElementById(selectId);
      if (!select) {
        return;
      }

      const current = select.value;
      const includeEmpty = options.includeEmpty ?? true;
      const emptyLabel = options.emptyLabel || "Selecciona...";
      const classKey = options.classKey || null;
      const meta = classKey && SELECT_CLASS[classKey] ? SELECT_CLASS[classKey] : null;
      const prefix = meta ? `${meta.tag} · ` : "";

      if (meta) {
        select.title = meta.title;
        select.dataset.catalog = classKey;
      } else {
        select.removeAttribute("title");
        select.removeAttribute("data-catalog");
      }

      const html = [];

      if (includeEmpty) {
        html.push(`<option value="">${escapeSelectText(emptyLabel)}</option>`);
      }

      for (const item of items) {
        const value = getValue(item);
        const label = prefix + getLabel(item);
        html.push(`<option value="${escapeSelectAttr(value)}">${escapeSelectText(label)}</option>`);
      }

      select.innerHTML = html.join("");
      if (current && [...select.options].some((option) => option.value === current)) {
        select.value = current;
      }
    }

    function fillClienteContactoEditSelect(filterText, selectedClienteId) {
      const selectId = "cliente-contacto-edit-cliente";
      const select = document.getElementById(selectId);
      if (!select) {
        return;
      }
      const q = (filterText || "").trim().toLowerCase();
      let items = state.clientes;
      if (q) {
        items = state.clientes.filter((c) => {
          const blob = [c.razon_social, c.nombre_comercial, c.rfc, String(c.id)]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();
          return blob.includes(q);
        });
      }
      const ensureId =
        selectedClienteId != null && selectedClienteId !== ""
          ? String(selectedClienteId)
          : select.value || "";
      if (q && ensureId && !items.some((c) => String(c.id) === ensureId)) {
        const missing = state.clientes.find((c) => String(c.id) === ensureId);
        if (missing) {
          items = [missing, ...items];
        }
      }
      if (!state.clientes.length) {
        select.innerHTML = '<option value="">Sin clientes en catalogo</option>';
        select.disabled = true;
        return;
      }
      if (items.length === 0) {
        select.innerHTML = '<option value="">Sin coincidencias</option>';
        select.disabled = true;
        return;
      }
      select.disabled = false;
      fillSelect(selectId, items, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: false, classKey: "cliente" });
      if (ensureId && [...select.options].some((option) => option.value === ensureId)) {
        select.value = ensureId;
      }
    }

    function fillClienteDomicilioSelect(filterText, selectedClienteId) {
      const selectId = "cliente-domicilio-cliente";
      const select = document.getElementById(selectId);
      if (!select) {
        return;
      }
      const q = (filterText || "").trim().toLowerCase();
      let items = state.clientes;
      if (q) {
        items = state.clientes.filter((c) => {
          const blob = [c.razon_social, c.nombre_comercial, c.rfc, String(c.id)]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();
          return blob.includes(q);
        });
      }
      const ensureId =
        selectedClienteId != null && selectedClienteId !== ""
          ? String(selectedClienteId)
          : select.value || "";
      if (q && ensureId && !items.some((c) => String(c.id) === ensureId)) {
        const missing = state.clientes.find((c) => String(c.id) === ensureId);
        if (missing) {
          items = [missing, ...items];
        }
      }
      if (!state.clientes.length) {
        select.innerHTML = '<option value="">Sin clientes en catalogo</option>';
        select.disabled = true;
        return;
      }
      if (items.length === 0) {
        select.innerHTML = '<option value="">Sin coincidencias</option>';
        select.disabled = true;
        return;
      }
      select.disabled = false;
      fillSelect(selectId, items, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, {
        includeEmpty: true,
        emptyLabel: "Selecciona cliente",
        classKey: "cliente",
      });
      if (ensureId && [...select.options].some((option) => option.value === ensureId)) {
        select.value = ensureId;
      }
    }

    function renderStats() {
      const metrics = [
        ["Clientes", state.clientes.length],
        ["Transportistas", state.transportistas.length],
        ["Viajes", state.viajes.length],
        ["Fletes", state.fletes.length],
        ["Facturas", state.facturas.length],
        ["Gastos", state.gastos.length],
        ["Tarifas", state.tarifas.length],
        ["Tarifas compra", state.tarifasCompra.length],
        ["Operadores", state.operadores.length],
        ["Unidades", state.unidades.length],
        ["Asignaciones", state.asignaciones.length],
        ["Despachos", state.despachos.length],
        ["Ordenes servicio", state.ordenesServicio.length],
      ];

      document.getElementById("stats").innerHTML = metrics.map(([label, value]) => `
        <div class="stat">
          <strong>${value}</strong>
          <div>${label}</div>
        </div>
      `).join("");
    }

    function renderClientes() {
      const items = filteredClientes();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id}</td>
          <td>${item.razon_social}</td>
          <td>${item.nombre_comercial || "-"}</td>
          <td>${item.tipo_cliente || "-"}</td>
          <td>${item.rfc || "-"}</td>
          <td>${item.contactos?.length || 0}</td>
          <td>${item.domicilios?.length || 0}</td>
          <td><span class="pill">${item.activo ? "activo" : "inactivo"}</span></td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startClienteEdit(${item.id})">Editar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("clientes-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Razon social</th><th>Nombre comercial</th><th>Tipo</th><th>RFC</th><th>Contactos</th><th>Domicilios</th><th>Estatus</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="9">Sin clientes con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function getClienteBySelect(selectId) {
      const value = document.getElementById(selectId)?.value || "";
      if (!value) {
        return null;
      }
      return state.clientes.find((item) => String(item.id) === value) || null;
    }

    function clienteModuleSummaryText(cliente) {
      if (!cliente) {
        return "Selecciona un cliente para continuar.";
      }
      return `Cliente ${cliente.id} - ${cliente.razon_social}. Comercial: ${cliente.nombre_comercial || "-"}. RFC: ${cliente.rfc || "-"}. Contactos: ${cliente.contactos?.length || 0}. Domicilios: ${cliente.domicilios?.length || 0}.`;
    }

    function syncClienteModuleSummaries() {
      const contactoCliente = getClienteBySelect("cliente-contacto-cliente");
      const domicilioCliente = getClienteBySelect("cliente-domicilio-cliente");
      const condicionCliente = getClienteBySelect("cliente-condicion-cliente");
      const contactoNode = document.getElementById("cliente-contacto-summary");
      const domicilioNode = document.getElementById("cliente-domicilio-summary");
      const condicionNode = document.getElementById("cliente-condicion-selected-summary");
      if (contactoNode) {
        contactoNode.textContent = clienteModuleSummaryText(contactoCliente);
      }
      if (domicilioNode) {
        domicilioNode.textContent = clienteModuleSummaryText(domicilioCliente);
      }
      if (condicionNode) {
        condicionNode.textContent = clienteModuleSummaryText(condicionCliente);
      }
    }

    function syncClienteModuleSelection(sourceSelectId) {
      cancelClienteContactoEdit();
      const source = document.getElementById(sourceSelectId);
      const value = source?.value || "";
      if (value) {
        for (const selectId of [
          "cliente-contacto-cliente",
          "cliente-domicilio-cliente",
          "cliente-condicion-cliente",
        ]) {
          const select = document.getElementById(selectId);
          if (select) {
            select.value = value;
          }
        }
      }
      const domicilioBuscarEl = document.getElementById("cliente-domicilio-buscar");
      const domicilioSelectEl = document.getElementById("cliente-domicilio-cliente");
      if (domicilioBuscarEl && domicilioSelectEl) {
        fillClienteDomicilioSelect(domicilioBuscarEl.value, value || domicilioSelectEl.value || null);
      }
      if (sourceSelectId === "cliente-contacto-cliente") {
        setClienteSubpage("contactos");
      } else if (sourceSelectId === "cliente-domicilio-cliente") {
        setClienteSubpage("domicilios");
      } else if (sourceSelectId === "cliente-condicion-cliente") {
        setClienteSubpage("condiciones");
      }
      syncClienteModuleSummaries();
      renderClienteContactos();
      flushClienteDomiciliosForSelectedClient(value);
      syncClienteCondicionForm();
    }

    function syncTransportistaModuleSelection(sourceSelectId) {
      cancelTransportistaContactoEdit();
      const source = document.getElementById(sourceSelectId);
      const value = source?.value || "";
      if (value) {
        for (const selectId of [
          "transportista-contacto-transportista",
          "transportista-documento-transportista",
        ]) {
          const select = document.getElementById(selectId);
          if (select) {
            select.value = value;
          }
        }
      }
      if (sourceSelectId === "transportista-contacto-transportista") {
        setTransportistaSubpage("contactos");
      } else if (sourceSelectId === "transportista-documento-transportista") {
        setTransportistaSubpage("documentos");
      }
      renderTransportistaContactos();
      renderTransportistaDocumentos();
    }

    async function refreshClienteDomiciliosFromApi(clienteId) {
      const id = typeof clienteId === "number" ? clienteId : parseInt(clienteId, 10);
      if (!Number.isFinite(id) || id <= 0) {
        return;
      }
      try {
        const res = await api(`/clientes/${id}/domicilios`);
        const idx = state.clientes.findIndex((c) => Number(c.id) === Number(id));
        if (idx >= 0) {
          state.clientes[idx].domicilios = res.items;
        }
      } catch (e) {
        /* dejar datos en memoria */
      }
    }

    function flushClienteDomiciliosForSelectedClient(selectedValue) {
      void (async () => {
        const v = selectedValue != null ? String(selectedValue).trim() : "";
        if (v) {
          await refreshClienteDomiciliosFromApi(parseInt(v, 10));
        }
        renderClienteDomicilios();
      })();
    }

    function renderClienteContactos() {
      const cliente = getClienteBySelect("cliente-contacto-cliente");
      syncClienteModuleSummaries();
      if (!cliente) {
        document.getElementById("cliente-contactos-table").innerHTML = '<div class="hint">Selecciona un cliente para ver sus contactos.</div>';
        return;
      }
      const rows = (cliente.contactos || []).map((item) => `
        <tr>
          <td>${item.nombre}</td>
          <td>${item.area || "-"}</td>
          <td>${item.puesto || "-"}</td>
          <td>${item.email || "-"}</td>
          <td>${item.telefono || item.celular || "-"}</td>
          <td>${item.principal ? '<span class="pill">principal</span>' : '-'}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startClienteContactoEdit(${cliente.id}, ${item.id})">Editar</button>
              <button type="button" class="secondary-button small-button" onclick="deleteClienteContacto(${cliente.id}, ${item.id})">Eliminar</button>
            </div>
          </td>
        </tr>
      `).join("");
      document.getElementById("cliente-contactos-table").innerHTML = `
        <table>
          <thead><tr><th>Nombre</th><th>Area</th><th>Puesto</th><th>Email</th><th>Telefono</th><th>Principal</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="7">Sin contactos para este cliente.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderClienteDomicilios() {
      const cliente = getClienteBySelect("cliente-domicilio-cliente");
      syncClienteModuleSummaries();
      if (!cliente) {
        document.getElementById("cliente-domicilios-table").innerHTML = '<div class="hint">Selecciona un cliente para ver sus domicilios.</div>';
        return;
      }
      const rows = (cliente.domicilios || []).map((item) => `
        <tr>
          <td>${item.tipo_domicilio}</td>
          <td>${item.nombre_sede}</td>
          <td>${item.municipio || "-"}</td>
          <td>${item.estado || "-"}</td>
          <td>${item.horario_carga || "-"}</td>
          <td>${item.horario_descarga || "-"}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startClienteDomicilioEdit(${cliente.id}, ${item.id})">Editar</button>
              <button type="button" class="secondary-button small-button" onclick="deleteClienteDomicilio(${cliente.id}, ${item.id})">Eliminar</button>
            </div>
          </td>
        </tr>
      `).join("");
      document.getElementById("cliente-domicilios-table").innerHTML = `
        <table>
          <thead><tr><th>Tipo</th><th>Sede</th><th>Municipio</th><th>Estado</th><th>Horario carga</th><th>Horario descarga</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="7">Sin domicilios para este cliente.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderClienteCondicion() {
      const cliente = getClienteBySelect("cliente-condicion-cliente");
      const node = document.getElementById("cliente-condicion-summary");
      syncClienteModuleSummaries();
      if (!cliente) {
        node.textContent = "Selecciona un cliente para ver o capturar sus condiciones comerciales.";
        return;
      }
      const condicion = cliente.condicion_comercial;
      if (!condicion) {
        node.textContent = "Este cliente aun no tiene condiciones comerciales registradas.";
        return;
      }
      const limFmt =
        condicion.limite_credito === null || condicion.limite_credito === undefined
          ? "0.00"
          : formatLocaleDecimal(Number(condicion.limite_credito), 2, 2);
      node.textContent = `Credito: ${condicion.dias_credito ?? 0} dias. Limite: ${limFmt} ${condicion.moneda_preferida}. Forma pago: ${condicion.forma_pago || "-"}.`;
    }

    function syncClienteCondicionForm() {
      const form = document.getElementById("cliente-condicion-form");
      const cliente = getClienteBySelect("cliente-condicion-cliente");
      if (!form) {
        return;
      }
      syncClienteModuleSummaries();
      if (!cliente) {
        form.reset();
        form.elements.moneda_preferida.value = "MXN";
        renderClienteCondicion();
        return;
      }
      const condicion = cliente.condicion_comercial;
      form.elements.cliente_id.value = String(cliente.id);
      form.elements.dias_credito.value =
        condicion == null ? "" : integerStringForNumberInput(condicion.dias_credito);
      form.elements.limite_credito.value =
        condicion == null ? "" : moneyFieldFromApi(condicion.limite_credito, 2, 2);
      form.elements.moneda_preferida.value = condicion?.moneda_preferida || "MXN";
      form.elements.forma_pago.value = condicion?.forma_pago || "";
      form.elements.uso_cfdi.value = condicion?.uso_cfdi || "";
      form.elements.requiere_oc.checked = Boolean(condicion?.requiere_oc);
      form.elements.requiere_cita.checked = Boolean(condicion?.requiere_cita);
      form.elements.bloqueado_credito.checked = Boolean(condicion?.bloqueado_credito);
      form.elements.observaciones_credito.value = condicion?.observaciones_credito || "";
      applyMoneyFormatToForm(form);
      renderClienteCondicion();
    }

    function startClienteContactoEdit(clienteId, contactoId) {
      const cliente = state.clientes.find((item) => item.id === clienteId);
      const contacto = cliente?.contactos?.find((item) => item.id === contactoId);
      if (!cliente || !contacto) {
        return;
      }
      uiState.editing.clienteContactoId = contactoId;
      setClienteSubpage("contactos");
      const buscar = document.getElementById("cliente-contacto-edit-buscar");
      if (buscar) {
        buscar.value = "";
      }
      const form = document.getElementById("cliente-contacto-edit-form");
      form.elements.id.value = contacto.id;
      document.getElementById("cliente-contacto-path-cliente").value = String(clienteId);
      fillClienteContactoEditSelect("", cliente.id);
      form.elements.nombre.value = contacto.nombre || "";
      form.elements.area.value = contacto.area || "";
      form.elements.puesto.value = contacto.puesto || "";
      form.elements.email.value = contacto.email || "";
      form.elements.telefono.value = contacto.telefono || "";
      form.elements.extension.value = contacto.extension || "";
      form.elements.celular.value = contacto.celular || "";
      form.elements.principal.checked = Boolean(contacto.principal);
      form.elements.activo.checked = Boolean(contacto.activo);
      showPanel("cliente-contacto-edit-panel");
      clearMessage("cliente-contacto-edit-message");
    }

    function cancelClienteContactoEdit() {
      uiState.editing.clienteContactoId = null;
      const buscar = document.getElementById("cliente-contacto-edit-buscar");
      if (buscar) {
        buscar.value = "";
      }
      document.getElementById("cliente-contacto-edit-form").reset();
      hidePanel("cliente-contacto-edit-panel", "cliente-contacto-edit-message");
    }

    async function deleteClienteContacto(clienteId, contactoId) {
      if (!window.confirm("¿Eliminar este contacto del cliente?")) {
        return;
      }
      clearMessage("cliente-contacto-message");
      try {
        await api(`/clientes/${clienteId}/contactos/${contactoId}`, { method: "DELETE" });
        if (uiState.editing.clienteContactoId === contactoId) {
          cancelClienteContactoEdit();
        }
        setMessage("cliente-contacto-message", "Contacto eliminado.", "ok");
        await refreshData();
        document.getElementById("cliente-contacto-cliente").value = String(clienteId);
        renderClienteContactos();
      } catch (error) {
        setMessage("cliente-contacto-message", error.message, "error");
      }
    }

    async function startClienteDomicilioEdit(clienteId, domicilioId) {
      const cliente = state.clientes.find((item) => item.id === clienteId);
      if (!cliente) {
        return;
      }
      uiState.editing.clienteDomicilioId = domicilioId;
      let domicilio = cliente.domicilios?.find((item) => item.id === domicilioId) || null;
      try {
        const res = await api(`/clientes/${clienteId}/domicilios`);
        const fresh = res.items.find((item) => item.id === domicilioId);
        if (fresh) {
          domicilio = fresh;
        }
      } catch (e) {
        /* usar domicilio en memoria si el listado falla */
      }
      if (!domicilio) {
        uiState.editing.clienteDomicilioId = null;
        return;
      }
      const form = document.getElementById("cliente-domicilio-edit-form");
      const setText = (name, value) => {
        const el = form.querySelector(`[name="${name}"]`);
        if (el && "value" in el) {
          el.value = value == null ? "" : String(value);
        }
      };
      setText("id", domicilio.id);
      setText("cliente_id", cliente.id);
      setText("cliente_label", `${cliente.id} - ${cliente.razon_social}`);
      setText("tipo_domicilio", domicilio.tipo_domicilio);
      setText("nombre_sede", domicilio.nombre_sede);
      setText("direccion_completa", domicilio.direccion_completa);
      setText("municipio", domicilio.municipio);
      setText("estado", domicilio.estado);
      setText("codigo_postal", domicilio.codigo_postal);
      setText("horario_carga", domicilio.horario_carga);
      setText("horario_descarga", domicilio.horario_descarga);
      setText("instrucciones_acceso", domicilio.instrucciones_acceso);
      const activoEl = form.querySelector('[name="activo"]');
      if (activoEl) {
        activoEl.checked = Boolean(domicilio.activo);
      }
      showPanel("cliente-domicilio-edit-panel");
      clearMessage("cliente-domicilio-edit-message");
      const panel = document.getElementById("cliente-domicilio-edit-panel");
      if (panel && typeof panel.scrollIntoView === "function") {
        panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    }

    function cancelClienteDomicilioEdit() {
      uiState.editing.clienteDomicilioId = null;
      document.getElementById("cliente-domicilio-edit-form").reset();
      hidePanel("cliente-domicilio-edit-panel", "cliente-domicilio-edit-message");
    }

    async function deleteClienteDomicilio(clienteId, domicilioId) {
      if (!window.confirm("¿Eliminar este domicilio del cliente?")) {
        return;
      }
      clearMessage("cliente-domicilio-message");
      try {
        await api(`/clientes/${clienteId}/domicilios/${domicilioId}`, { method: "DELETE" });
        if (uiState.editing.clienteDomicilioId === domicilioId) {
          cancelClienteDomicilioEdit();
        }
        setMessage("cliente-domicilio-message", "Domicilio eliminado.", "ok");
        await refreshData();
        document.getElementById("cliente-domicilio-cliente").value = String(clienteId);
        flushClienteDomiciliosForSelectedClient(String(clienteId));
      } catch (error) {
        setMessage("cliente-domicilio-message", error.message, "error");
      }
    }

    function renderTransportistas() {
      const items = filteredTransportistas();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id}</td>
          <td>${item.nombre_razon_social || item.nombre}</td>
          <td>${item.nombre_comercial || "-"}</td>
          <td>${item.tipo_transportista || "-"}</td>
          <td>${item.rfc || "-"}</td>
          <td>${item.contactos?.length || 0}</td>
          <td>${item.documentos?.length || 0}</td>
          <td><span class="pill">${item.estatus || (item.activo ? "activo" : "inactivo")}</span></td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startTransportistaEdit(${item.id})">Editar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("transportistas-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Razon social</th><th>Nombre comercial</th><th>Tipo</th><th>RFC</th><th>Contactos</th><th>Documentos</th><th>Estatus</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="9">Sin transportistas con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function getTransportistaBySelect(selectId) {
      const value = document.getElementById(selectId)?.value || "";
      if (!value) {
        return null;
      }
      return state.transportistas.find((item) => String(item.id) === value) || null;
    }

    function renderTransportistaContactos() {
      const transportista = getTransportistaBySelect("transportista-contacto-transportista");
      if (!transportista) {
        document.getElementById("transportista-contactos-table").innerHTML = '<div class="hint">Selecciona un transportista para ver sus contactos.</div>';
        return;
      }
      const rows = (transportista.contactos || []).map((item) => `
        <tr>
          <td>${item.nombre}</td>
          <td>${item.area || "-"}</td>
          <td>${item.puesto || "-"}</td>
          <td>${item.email || "-"}</td>
          <td>${item.telefono || item.celular || "-"}</td>
          <td>${item.principal ? '<span class="pill">principal</span>' : '-'}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startTransportistaContactoEdit(${transportista.id}, ${item.id})">Editar</button>
              <button type="button" class="secondary-button small-button" onclick="deleteTransportistaContacto(${transportista.id}, ${item.id})">Eliminar</button>
            </div>
          </td>
        </tr>
      `).join("");
      document.getElementById("transportista-contactos-table").innerHTML = `
        <table>
          <thead><tr><th>Nombre</th><th>Area</th><th>Puesto</th><th>Email</th><th>Telefono</th><th>Principal</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="7">Sin contactos para este transportista.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderTransportistaDocumentos() {
      const transportista = getTransportistaBySelect("transportista-documento-transportista");
      if (!transportista) {
        document.getElementById("transportista-documentos-table").innerHTML = '<div class="hint">Selecciona un transportista para ver sus documentos.</div>';
        return;
      }
      const rows = (transportista.documentos || []).map((item) => `
        <tr>
          <td>${item.tipo_documento}</td>
          <td>${item.numero_documento || "-"}</td>
          <td>${item.fecha_vencimiento || "-"}</td>
          <td><span class="pill">${item.estatus}</span></td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startTransportistaDocumentoEdit(${transportista.id}, ${item.id})">Editar</button>
              <button type="button" class="secondary-button small-button" onclick="deleteTransportistaDocumento(${transportista.id}, ${item.id})">Eliminar</button>
            </div>
          </td>
        </tr>
      `).join("");
      document.getElementById("transportista-documentos-table").innerHTML = `
        <table>
          <thead><tr><th>Tipo</th><th>Numero</th><th>Vencimiento</th><th>Estatus</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="5">Sin documentos para este transportista.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderViajes() {
      const items = filteredViajes();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id}</td>
          <td>${item.codigo_viaje}</td>
          <td>${item.origen} -> ${item.destino}</td>
          <td><span class="pill">${item.estado}</span></td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startViajeEdit(${item.id})">Editar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("viajes-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Codigo</th><th>Ruta</th><th>Estado</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="5">Sin viajes con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderFacturas() {
      const items = filteredFacturas();
      const rows = items.map((item) => `
        <tr>
          <td>${item.folio}</td>
          <td>${item.cliente?.razon_social || item.cliente_id}</td>
          <td>${item.concepto}</td>
          <td class="table-money">${fmtMoneyList(item.subtotal)}</td>
          <td class="table-money">${fmtMoneyList(item.total)}</td>
          <td class="table-money">${fmtMoneyList(item.saldo_pendiente)}</td>
          <td><span class="pill">${item.estatus}</span></td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startFacturaEdit(${item.id})">Editar</button>
            </div>
          </td>
        </tr>
      `).join("");

      const emptyMsg =
        state.facturas.length === 0
          ? "Aún no hay facturas. Use la subopción <strong>Nueva factura</strong> o el script <code>scripts/demo_flujo_factura.py</code>."
          : "Sin facturas con ese filtro. Pruebe Limpiar o ajuste búsqueda, cliente o estatus.";

      document.getElementById("facturas-table").innerHTML = `
        <table>
          <thead><tr><th>Folio</th><th>Cliente</th><th>Concepto</th><th>Subtotal</th><th>Total</th><th>Saldo</th><th>Estatus</th><th>Acciones</th></tr></thead>
          <tbody>${rows || `<tr><td colspan="8">${emptyMsg}</td></tr>`}</tbody>
        </table>
      `;
    }

    function renderFletes() {
      const items = filteredFletes();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id}</td>
          <td>${item.codigo_flete}</td>
          <td>${item.tipo_operacion || "-"}</td>
          <td>${item.cliente?.razon_social || item.cliente_id}</td>
          <td>${item.transportista?.nombre || item.transportista_id}</td>
          <td class="table-money">${fmtMoneyList(item.precio_venta ?? item.monto_estimado)}</td>
          <td class="table-money">${fmtMoneyList(item.margen_estimado)}</td>
          <td class="table-money">${fmtPctList(item.margen_estimado_pct)}</td>
          <td class="table-money">${fmtMoneyList(item.costo_transporte_real)}</td>
          <td class="table-money">${fmtMoneyList(item.margen_real)}</td>
          <td><span class="pill">${item.estado}</span></td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startFleteEdit(${item.id})">Editar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("fletes-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Codigo</th><th>Tipo</th><th>Cliente</th><th>Transportista</th><th>Venta</th><th>Margen est.</th><th>Margen est. % s/ venta</th><th>Costo real</th><th>Margen real</th><th>Estado</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="12">Sin fletes con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function filteredOrdenesServicio() {
      const buscar = (uiState.ordenServicioFilters.buscar || "").trim();
      const modo = uiState.buscarModo || "contiene";
      return (state.ordenesServicio || []).filter((item) => {
        if (buscar) {
          const cotFol = item.cotizacion?.folio || "";
          const fleteCod = item.flete?.codigo_flete || "";
          const viajeCod = item.viaje?.codigo_viaje || "";
          if (
            !matchesBusqueda(
              buscar,
              [
                String(item.id ?? ""),
                item.folio || "",
                item.cliente?.razon_social || "",
                item.origen || "",
                item.destino || "",
                item.estatus || "",
                cotFol,
                fleteCod,
                viajeCod,
              ],
              modo,
            )
          ) {
            return false;
          }
        }
        if (uiState.ordenServicioFilters.cliente_id && String(item.cliente_id) !== uiState.ordenServicioFilters.cliente_id) {
          return false;
        }
        if (uiState.ordenServicioFilters.estatus && item.estatus !== uiState.ordenServicioFilters.estatus) {
          return false;
        }
        return true;
      });
    }

    function fmtIsoShort(iso) {
      if (!iso) {
        return "—";
      }
      const s = String(iso);
      if (s.length >= 16) {
        return s.slice(0, 16).replace("T", " ");
      }
      return s;
    }

    function renderOrdenServicioDetailBody(o) {
      const lines = [
        `Folio: ${o.folio}`,
        `ID: ${o.id}   Estatus: ${o.estatus}`,
        `Cliente: ${o.cliente?.razon_social || o.cliente_id}`,
        `Origen → Destino: ${o.origen} → ${o.destino}`,
        `Unidad / Carga: ${o.tipo_unidad || "—"} / ${o.tipo_carga || "—"}`,
        `Peso kg: ${o.peso_kg != null ? o.peso_kg : "—"}   Distancia km: ${o.distancia_km != null ? o.distancia_km : "—"}`,
        `Precio comprometido: ${fmtMoneyList(o.precio_comprometido)} ${o.moneda || "MXN"}`,
        `Fecha solicitud: ${fmtIsoShort(o.fecha_solicitud)}`,
        `Fecha programada: ${fmtIsoShort(o.fecha_programada)}`,
        `Cotizacion: ${o.cotizacion ? o.cotizacion.folio + " (id " + o.cotizacion.id + ")" : "—"}`,
        `Flete: ${o.flete ? o.flete.codigo_flete + " (id " + o.flete.id + ")" : "—"}`,
        `Viaje: ${o.viaje ? o.viaje.codigo_viaje + " (id " + o.viaje.id + ")" : "—"}`,
        `Despacho: ${o.despacho ? "id " + o.despacho.id_despacho + " (" + o.despacho.estatus + ")" : "—"}`,
        `Observaciones: ${o.observaciones || "—"}`,
      ];
      return lines.join(String.fromCharCode(10));
    }

    function showOrdenServicioDetail(ordenId) {
      const o = state.ordenesServicio.find((row) => Number(row.id) === Number(ordenId));
      if (!o) {
        return;
      }
      const body = document.getElementById("orden-servicio-detail-body");
      const panel = document.getElementById("orden-servicio-detail-panel");
      if (body) {
        body.textContent = renderOrdenServicioDetailBody(o);
      }
      if (panel) {
        panel.classList.remove("hidden");
        panel.setAttribute("aria-hidden", "false");
        panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    }

    function hideOrdenServicioDetail() {
      hidePanel("orden-servicio-detail-panel", null);
    }

    function renderOrdenesServicio() {
      const items = filteredOrdenesServicio();
      const rows = items
        .map(
          (item) => `
        <tr>
          <td>${item.id}</td>
          <td>${item.folio}</td>
          <td>${item.cliente?.razon_social || item.cliente_id}</td>
          <td><span class="pill">${item.estatus}</span></td>
          <td>${item.cotizacion?.folio || "—"}</td>
          <td>${item.flete?.codigo_flete || "—"}</td>
          <td>${fmtIsoShort(item.fecha_programada)}</td>
          <td class="table-money">${fmtMoneyList(item.precio_comprometido)}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="showOrdenServicioDetail(${item.id})">Ver detalle</button>
            </div>
          </td>
        </tr>
      `,
        )
        .join("");
      const emptyMsg =
        (state.ordenesServicio || []).length === 0
          ? "No hay ordenes de servicio. Puede crearlas por API (Swagger /docs, tag ordenes-servicio) o con el script de demo."
          : "Sin ordenes con ese filtro. Pruebe Limpiar o ajuste criterios.";
      const tableEl = document.getElementById("ordenes-servicio-table");
      if (!tableEl) {
        return;
      }
      tableEl.innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Folio</th><th>Cliente</th><th>Estatus</th><th>Cotizacion</th><th>Flete</th><th>Fecha prog.</th><th>Precio comp.</th><th>Acciones</th></tr></thead>
          <tbody>${rows || `<tr><td colspan="9">${emptyMsg}</td></tr>`}</tbody>
        </table>
      `;
    }

    function aplicarFolioOrdenServicioAFactura(messageId, folioInputId, ordenIdInputId) {
      clearMessage(messageId);
      const folioEl = document.getElementById(folioInputId);
      const idEl = document.getElementById(ordenIdInputId);
      const raw = folioEl && folioEl.value ? folioEl.value.trim() : "";
      if (!idEl) {
        return;
      }
      if (!raw) {
        setMessage(messageId, "Escriba un folio de orden de servicio.", "error");
        return;
      }
      const list = state.ordenesServicio || [];
      const low = raw.toLowerCase();
      const exact = list.find((o) => String(o.folio).toLowerCase() === low);
      const loose = exact || list.find((o) => String(o.folio).toLowerCase().includes(low));
      if (!loose) {
        setMessage(
          messageId,
          "No se encontro orden con ese folio. Actualice la pagina (F5) o verifique en Fletes > Ordenes de servicio.",
          "error",
        );
        return;
      }
      idEl.value = String(loose.id);
      setMessage(messageId, `Orden ${loose.folio} (ID ${loose.id}) aplicada.`, "ok");
    }

    function renderGastos() {
      const items = filteredGastos();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id}</td>
          <td>${item.flete_id}</td>
          <td title="${item.tipo_gasto}">${labelGastoCategoria(item.tipo_gasto)}</td>
          <td class="table-money">${fmtMoneyList(item.monto)}</td>
          <td>${item.fecha_gasto}</td>
          <td>${item.referencia || "-"}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startGastoEdit(${item.id})">Editar</button>
              <button type="button" class="secondary-button small-button" onclick="deleteGasto(${item.id})">Eliminar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("gastos-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Flete</th><th>Categoría</th><th>Monto</th><th>Fecha</th><th>Referencia</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="7">Sin gastos con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderTarifas() {
      const items = filteredTarifasVenta();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id}</td>
          <td>${item.nombre_tarifa}</td>
          <td>${item.tipo_operacion || "subcontratado"}</td>
          <td>${item.ambito || "—"}</td>
          <td>${item.modalidad_cobro || "—"}</td>
          <td>${item.origen} -> ${item.destino}</td>
          <td>${item.tipo_unidad}</td>
          <td class="table-money">${fmtMoneyList(item.tarifa_base)}</td>
          <td class="table-money">${fmtTarifaList(item.tarifa_km, 4)}</td>
          <td><span class="pill">${item.activo ? "activa" : "inactiva"}</span></td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startTarifaFleteEdit(${item.id})">Editar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("tarifas-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Nombre</th><th>Tipo op.</th><th>Ambito</th><th>Modalidad</th><th>Ruta</th><th>Unidad</th><th>Base</th><th>Km</th><th>Estatus</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="11">Sin tarifas con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderTarifasCompra() {
      const items = filteredTarifasCompra();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id}</td>
          <td>${state.transportistas.find((t) => t.id === item.transportista_id)?.nombre || item.transportista_id}</td>
          <td>${item.tipo_transportista || "subcontratado"}</td>
          <td>${item.nombre_tarifa}</td>
          <td>${item.origen} -> ${item.destino}</td>
          <td>${item.tipo_unidad}</td>
          <td class="table-money">${fmtMoneyList(item.tarifa_base)}</td>
          <td>${item.dias_credito ?? 0}</td>
          <td><span class="pill">${item.activo ? "activa" : "inactiva"}</span></td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startTarifaCompraEdit(${item.id})">Editar</button>
              <button type="button" class="secondary-button small-button" onclick="deleteTarifaCompra(${item.id})">Eliminar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("tarifas-compra-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Transportista</th><th>Tipo</th><th>Nombre</th><th>Ruta</th><th>Unidad</th><th>Base</th><th>Credito</th><th>Estatus</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="10">Sin tarifas de compra con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function escapeHtml(text) {
      return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    function fmtUnidadDateCell(value) {
      if (value == null || value === "") {
        return "—";
      }
      const s = typeof value === "string" ? value.slice(0, 10) : String(value);
      return s || "—";
    }

    function unidadDescripcionCorta(text) {
      const raw = (text || "").trim();
      if (!raw) {
        return "—";
      }
      const shown = raw.length > 64 ? `${raw.slice(0, 61)}…` : raw;
      return escapeHtml(shown);
    }

    function operadorCertificacionesCorta(text) {
      const s = (text || "").trim();
      if (!s) {
        return "—";
      }
      const raw = s.length > 56 ? `${s.slice(0, 53)}…` : s;
      return escapeHtml(raw);
    }

    function renderOperadores() {
      const items = filteredOperadores();
      const rows = items.map((item) => {
        const cert = (item.certificaciones || "").trim();
        const titleAttr = cert ? ` title="${escapeHtml(cert)}"` : "";
        return `
        <tr>
          <td>${item.id_operador}</td>
          <td>${item.nombre} ${item.apellido_paterno}</td>
          <td>${state.transportistas.find((t) => t.id === item.transportista_id)?.nombre || item.transportista_id || "-"}</td>
          <td>${item.curp}</td>
          <td>${item.telefono_principal || "-"}</td>
          <td${titleAttr}>${operadorCertificacionesCorta(item.certificaciones)}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startOperadorEdit(${item.id_operador})">Editar</button>
            </div>
          </td>
        </tr>
      `;
      }).join("");

      document.getElementById("operadores-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Nombre</th><th>Transportista</th><th>CURP</th><th>Telefono</th><th>Certificaciones</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="7">Sin operadores con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderUnidades() {
      const totalUnidades = state.unidades.length;
      const items = filteredUnidades();
      const rows = items
        .map((item) => {
          const transp =
            state.transportistas.find((t) => String(t.id) === String(item.transportista_id))?.nombre ||
            item.transportista_id ||
            "—";
          const tipoP = (item.tipo_propiedad || "").trim() || "—";
          const estDoc = (item.estatus_documental || "").trim() || "—";
          return `
        <tr>
          <td>${item.id_unidad}</td>
          <td>${escapeHtml(item.economico || "")}</td>
          <td>${escapeHtml(String(transp))}</td>
          <td>${escapeHtml(item.placas || "—")}</td>
          <td>${escapeHtml(tipoP)}</td>
          <td>${escapeHtml(estDoc)}</td>
          <td>${unidadDescripcionCorta(item.descripcion)}</td>
          <td><span class="pill">${item.activo ? "activa" : "inactiva"}</span></td>
          <td>${fmtUnidadDateCell(item.vigencia_permiso_sct)}</td>
          <td>${fmtUnidadDateCell(item.vigencia_seguro)}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startUnidadEdit(${item.id_unidad})">Editar</button>
              <button type="button" class="secondary-button small-button" onclick="deleteUnidad(${item.id_unidad})">Eliminar</button>
            </div>
          </td>
        </tr>
      `;
        })
        .join("");

      let emptyHint = "";
      if (!rows) {
        if (!state.catalogLoaded) {
          emptyHint =
            '<tr><td colspan="11">Cargando catalogo… Si no aparece nada en unos segundos, actualice la pagina (F5) o revise el mensaje de error en la parte superior.</td></tr>';
        } else if (unidadesEndpointFailed()) {
          emptyHint =
            '<tr><td colspan="11"><strong>No se pudo cargar el listado de unidades</strong> (fallo de red, API o servidor). Esto <strong>no</strong> significa necesariamente que no haya datos en MySQL. Revise el aviso amarillo arriba, la API key en <code>.env</code>, que MySQL este en marcha y pulse <strong>Recargar catalogo</strong>. Pruebe tambien <a href="/docs">/docs</a> → <code>GET /api/v1/unidades</code>.</td></tr>';
        } else if (totalUnidades === 0) {
          emptyHint =
            '<tr><td colspan="11"><strong>Situacion normal si aun no dio de alta vehiculos:</strong> en la base configurada (<code>MYSQL_DB</code> en <code>.env</code>, suele ser <code>sife_mxn</code>) la tabla <code>unidades</code> tiene 0 filas. Use <strong>Nueva unidad</strong> (economico obligatorio) o ejecute <code>python scripts/seed_unidad_ejemplo.py</code> si ya tiene transportista. Si <em>creyó</em> tener datos, confirme que el servidor usa el mismo <code>.env</code> que la base de datos que inspecciona en MySQL.</td></tr>';
        } else {
          emptyHint =
            '<tr><td colspan="11">Ninguna fila coincide con el filtro actual. Vacie el buscador, deje <strong>Todos</strong> en los tres listados y pulse <strong>Limpiar filtros</strong> (restablece el modo de busqueda a <strong>Contiene</strong>). Si aun asi no aparece, use <strong>Recargar catalogo</strong>.</td></tr>';
        }
      }

      document.getElementById("unidades-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Economico</th><th>Transportista</th><th>Placas</th><th>Tipo prop.</th><th>Estatus doc.</th><th>Descripcion</th><th>Activo</th><th>Vig. SCT</th><th>Vig. seguro</th><th>Acciones</th></tr></thead>
          <tbody>${rows || emptyHint}</tbody>
        </table>
      `;
    }

    function renderAsignaciones() {
      const items = filteredAsignaciones();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id_asignacion}</td>
          <td>${item.operador?.nombre || ""} ${item.operador?.apellido_paterno || ""}</td>
          <td>${item.unidad?.economico || item.id_unidad}</td>
          <td>${item.viaje?.codigo_viaje || item.id_viaje}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startAsignacionEdit(${item.id_asignacion})">Editar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("asignaciones-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Operador</th><th>Unidad</th><th>Viaje</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="5">Sin asignaciones con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderDespachos() {
      const items = filteredDespachos();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id_despacho}</td>
          <td>${item.asignacion?.viaje?.codigo_viaje || item.id_asignacion}</td>
          <td>${item.flete?.codigo_flete || "-"}</td>
          <td><span class="pill">${item.estatus}</span></td>
          <td>${item.eventos?.length || 0}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startDespachoEdit(${item.id_despacho})">Editar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("despachos-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Viaje</th><th>Flete</th><th>Estatus</th><th>Eventos</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="6">Sin despachos con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function hidePanel(panelId, messageId) {
      const el = document.getElementById(panelId);
      if (el) {
        el.classList.add("hidden");
        el.setAttribute("aria-hidden", "true");
      }
      if (messageId) {
        clearMessage(messageId);
      }
    }

    function showPanel(panelId) {
      const el = document.getElementById(panelId);
      if (el) {
        el.classList.remove("hidden");
        el.setAttribute("aria-hidden", "false");
      }
    }

    function getPrimarySaveButton(formElement) {
      const fid = formElement.getAttribute("id");
      if (fid === "cliente-contacto-form") {
        return document.getElementById("cliente-contacto-guardar");
      }
      if (fid === "cliente-contacto-edit-form") {
        return document.getElementById("cliente-contacto-edit-guardar");
      }
      if (fid) {
        const linked = document.querySelector(`button[form="${fid}"][data-primary-action='save']`);
        if (linked) {
          return linked;
        }
      }
      return (
        formElement.querySelector('button[type="submit"]') ||
        formElement.querySelector("button[data-primary-action='save']") ||
        null
      );
    }

    function getSequentialFields(formElement) {
      return [...formElement.querySelectorAll("input, select, textarea, button")]
        .filter((field) => {
          if (field.disabled) {
            return false;
          }
          if (field.type === "hidden") {
            return false;
          }
          if (field.tagName === "BUTTON" && field.type === "button") {
            return false;
          }
          return true;
        });
    }

    function focusNextSequentialField(formElement, fromField) {
      if (!formElement || !fromField) {
        return;
      }
      const fields = getSequentialFields(formElement);
      const index = fields.indexOf(fromField);
      if (index === -1) {
        return;
      }
      const nextField = fields[index + 1];
      if (nextField && typeof nextField.focus === "function") {
        nextField.focus();
        if (nextField.select && nextField.tagName === "INPUT") {
          const t = (nextField.type || "").toLowerCase();
          if (t !== "checkbox" && t !== "radio" && t !== "file") {
            nextField.select();
          }
        }
        return;
      }
      const submitButton = getPrimarySaveButton(formElement);
      if (submitButton && typeof submitButton.focus === "function") {
        submitButton.focus();
      }
    }

    function wireImplicitSubmitGuard(formId) {
      const form = document.getElementById(formId);
      if (!form || form.dataset.implicitSubmitGuard === "true") {
        return;
      }
      form.dataset.implicitSubmitGuard = "true";
      form.addEventListener(
        "submit",
        (event) => {
          const saveBtn = getPrimarySaveButton(form);
          if (!saveBtn) {
            return;
          }
          if (event.submitter === saveBtn) {
            return;
          }
          event.preventDefault();
          event.stopImmediatePropagation();
          const active = document.activeElement;
          if (form.contains(active) && active !== saveBtn) {
            focusNextSequentialField(form, active);
          }
        },
        true
      );
    }

    function enableEnterToNextField(formId) {
      const formElement = document.getElementById(formId);
      if (!formElement || formElement.dataset.enterNavInstalled === "true") {
        return;
      }
      formElement.dataset.enterNavInstalled = "true";
      const onEnterNavKeydown = (event) => {
        const isEnter =
          event.key === "Enter" ||
          event.code === "Enter" ||
          event.code === "NumpadEnter" ||
          event.keyCode === 13;
        if (!isEnter) {
          return;
        }
        const target = event.target;
        if (!(target instanceof HTMLElement)) {
          return;
        }
        const tagName = target.tagName;
        if (!["INPUT", "SELECT", "TEXTAREA"].includes(tagName)) {
          return;
        }
        if (tagName === "INPUT") {
          const inputType = (target.type || "").toLowerCase();
          if (inputType === "submit" || inputType === "button" || inputType === "file" || inputType === "hidden") {
            return;
          }
        }
        if (tagName === "TEXTAREA") {
          return;
        }
        if (!formElement.contains(target)) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        focusNextSequentialField(formElement, target);
      };
      formElement.addEventListener("keydown", onEnterNavKeydown, true);
    }

    const CLIENTE_CONTACTO_ENTER_ORDER = [
      "cliente-contacto-cliente",
      "cliente-contacto-nombre",
      "cliente-contacto-area",
      "cliente-contacto-puesto",
      "cliente-contacto-email",
      "cliente-contacto-telefono",
      "cliente-contacto-extension",
      "cliente-contacto-celular",
      "cliente-contacto-principal",
      "cliente-contacto-activo",
    ];

    function wireClienteContactoEnterNavigation() {
      const form = document.getElementById("cliente-contacto-form");
      if (!form || window.__sifeClienteContactoEnterNav) {
        return;
      }
      window.__sifeClienteContactoEnterNav = true;
      const saveId = "cliente-contacto-guardar";
      const onEnter = (event) => {
        const isEnter =
          event.key === "Enter" ||
          event.code === "Enter" ||
          event.code === "NumpadEnter" ||
          event.keyCode === 13;
        if (!isEnter) {
          return;
        }
        const rawTarget = event.target;
        if (!(rawTarget instanceof HTMLElement)) {
          return;
        }
        if (!form || !form.contains(rawTarget)) {
          return;
        }
        const target = rawTarget.tagName === "INPUT" || rawTarget.tagName === "SELECT" || rawTarget.tagName === "TEXTAREA"
          ? rawTarget
          : null;
        if (!target) {
          return;
        }
        if (target.tagName === "INPUT") {
          const ty = (target.type || "").toLowerCase();
          if (ty === "submit" || ty === "button" || ty === "file" || ty === "hidden") {
            return;
          }
        }
        if (target.tagName === "TEXTAREA") {
          return;
        }
        if (target.id === saveId) {
          return;
        }
        if (!CLIENTE_CONTACTO_ENTER_ORDER.includes(target.id)) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();
        const idx = CLIENTE_CONTACTO_ENTER_ORDER.indexOf(target.id);
        for (let step = idx + 1; step < CLIENTE_CONTACTO_ENTER_ORDER.length; step += 1) {
          const next = document.getElementById(CLIENTE_CONTACTO_ENTER_ORDER[step]);
          if (next && !next.disabled) {
            next.focus();
            if (next.select && next.tagName === "INPUT") {
              const t = (next.type || "").toLowerCase();
              if (!["checkbox", "radio", "file"].includes(t)) {
                next.select();
              }
            }
            return;
          }
        }
        const saveBtn = document.getElementById(saveId);
        if (saveBtn && typeof saveBtn.focus === "function") {
          saveBtn.focus();
        }
      };
      window.addEventListener("keydown", onEnter, true);
      window.addEventListener("keypress", (event) => {
        const isEnter = event.key === "Enter" || event.keyCode === 13;
        if (!isEnter) {
          return;
        }
        const t = event.target;
        if (!(t instanceof HTMLElement) || !form || !form.contains(t)) {
          return;
        }
        if (t.id === saveId) {
          return;
        }
        if (t.tagName === "INPUT" || t.tagName === "SELECT") {
          const ty = t.tagName === "INPUT" ? (t.type || "").toLowerCase() : "";
          if (ty === "submit" || ty === "button" || ty === "hidden" || ty === "file") {
            return;
          }
          if (CLIENTE_CONTACTO_ENTER_ORDER.includes(t.id)) {
            event.preventDefault();
            event.stopImmediatePropagation();
          }
        }
      }, true);
    }

    function openSingleClienteFromFilter() {
      const items = filteredClientes();
      if (items.length !== 1) {
        return false;
      }
      startClienteEdit(items[0].id);
      return true;
    }

    function openSingleTransportistaFromFilter() {
      const items = filteredTransportistas();
      if (items.length !== 1) {
        return false;
      }
      startTransportistaEdit(items[0].id);
      return true;
    }

    function setClienteSubpage(tab) {
      const target = tab || "alta";
      uiState.clienteSubpage = target;
      if (target !== "contactos") {
        cancelClienteContactoEdit();
      }
      for (const button of document.querySelectorAll("[data-cliente-tab]")) {
        button.classList.toggle("active", button.dataset.clienteTab === target);
      }
      for (const panel of document.querySelectorAll("[data-cliente-tab-panel]")) {
        panel.classList.toggle("hidden", panel.dataset.clienteTabPanel !== target);
      }
      if (target === "manual") {
        const manualScroll = document.querySelector("[data-manual-scroll='clientes']");
        if (manualScroll) {
          manualScroll.scrollTop = 0;
        }
      }
    }

    function setTransportistaSubpage(tab) {
      const target = tab || "consulta";
      uiState.transportistaSubpage = target;
      if (target !== "contactos") {
        cancelTransportistaContactoEdit();
      }
      for (const button of document.querySelectorAll("[data-transportista-tab]")) {
        button.classList.toggle("active", button.dataset.transportistaTab === target);
      }
      for (const panel of document.querySelectorAll("[data-transportista-tab-panel]")) {
        panel.classList.toggle("hidden", panel.dataset.transportistaTabPanel !== target);
      }
      if (target === "manual") {
        const manualScroll = document.querySelector("[data-manual-scroll='transportistas']");
        if (manualScroll) {
          manualScroll.scrollTop = 0;
        }
      }
    }

    function setGenericSubpage(prefix, stateKey, defaultTab, tab) {
      const target = tab || defaultTab;
      uiState[stateKey] = target;
      for (const button of document.querySelectorAll(`[data-${prefix}-tab]`)) {
        const btnTab = button.getAttribute(`data-${prefix}-tab`);
        button.classList.toggle("active", btnTab === target);
      }
      for (const panel of document.querySelectorAll(`[data-${prefix}-tab-panel]`)) {
        const panelTab = panel.getAttribute(`data-${prefix}-tab-panel`);
        panel.classList.toggle("hidden", panelTab !== target);
      }
      if (target === "manual") {
        const manualScroll = document.querySelector(`[data-manual-scroll="${prefix}"]`);
        if (manualScroll) {
          manualScroll.scrollTop = 0;
        }
      }
      if (prefix === "flete" && target === "alta" && typeof populateSelects === "function") {
        populateSelects();
      }
      if (prefix === "tarifa" && target === "alta") {
        const tfa = document.getElementById("tarifa-form");
        if (tfa && typeof applyMoneyFormatToForm === "function") {
          applyMoneyFormatToForm(tfa);
        }
      }
      if (prefix === "tarifa-compra" && target === "alta") {
        const tcf = document.getElementById("tarifa-compra-form");
        if (tcf && typeof applyMoneyFormatToForm === "function") {
          applyMoneyFormatToForm(tcf);
        }
      }
      if (prefix === "flete" && target === "ordenes-servicio" && typeof renderOrdenesServicio === "function") {
        renderOrdenesServicio();
      }
      if (prefix === "operador" && target !== "consulta") {
        cancelOperadorEdit();
      }
      if (prefix === "unidad" && target !== "consulta") {
        cancelUnidadEdit();
      }
      if (prefix === "despacho" && target !== "consulta") {
        cancelDespachoEdit();
      }
    }

    function initCrudSubpageModules() {
      const modules = [
        { prefix: "viaje", stateKey: "viajeSubpage", defaultTab: "consulta" },
        { prefix: "flete", stateKey: "fleteSubpage", defaultTab: "consulta" },
        { prefix: "factura", stateKey: "facturaSubpage", defaultTab: "consulta" },
        { prefix: "tarifa", stateKey: "tarifaSubpage", defaultTab: "consulta" },
        { prefix: "tarifa-compra", stateKey: "tarifaCompraSubpage", defaultTab: "consulta" },
        { prefix: "operador", stateKey: "operadorSubpage", defaultTab: "consulta" },
        { prefix: "unidad", stateKey: "unidadSubpage", defaultTab: "consulta" },
        { prefix: "gasto", stateKey: "gastoSubpage", defaultTab: "consulta" },
        { prefix: "asignacion", stateKey: "asignacionSubpage", defaultTab: "consulta" },
        { prefix: "despacho", stateKey: "despachoSubpage", defaultTab: "consulta" },
        { prefix: "seguimiento", stateKey: "seguimientoSubpage", defaultTab: "salida" },
      ];
      for (const { prefix, stateKey, defaultTab } of modules) {
        for (const button of document.querySelectorAll(`[data-${prefix}-tab]`)) {
          button.addEventListener("click", () => {
            const tab = button.getAttribute(`data-${prefix}-tab`);
            setGenericSubpage(prefix, stateKey, defaultTab, tab);
          });
        }
        const manualToc = document.getElementById(`manual-${prefix}-toc`);
        if (manualToc) {
          manualToc.addEventListener("click", (event) => {
            const link = event.target.closest(`a[href^='#manual-${prefix}-']`);
            if (!link) {
              return;
            }
            event.preventDefault();
            const id = link.getAttribute("href").slice(1);
            const targetEl = document.getElementById(id);
            if (targetEl) {
              targetEl.scrollIntoView({ behavior: "smooth", block: "start" });
            }
          });
        }
        const openManualBtn = document.getElementById(`${prefix}-open-manual-btn`);
        if (openManualBtn) {
          openManualBtn.addEventListener("click", () => {
            setGenericSubpage(prefix, stateKey, defaultTab, "manual");
          });
        }
        setGenericSubpage(prefix, stateKey, defaultTab, uiState[stateKey]);
      }
    }

    function startClienteEdit(clienteId) {
      const item = state.clientes.find((row) => row.id === clienteId);
      if (!item) {
        return;
      }
      uiState.editing.clienteId = clienteId;
      const form = document.getElementById("cliente-edit-form");
      form.elements.id.value = item.id;
      form.elements.razon_social.value = item.razon_social || "";
      form.elements.nombre_comercial.value = item.nombre_comercial || "";
      form.elements.tipo_cliente.value = item.tipo_cliente || "mixto";
      form.elements.rfc.value = item.rfc || "";
      form.elements.sector.value = item.sector || "";
      form.elements.origen_prospecto.value = item.origen_prospecto || "";
      form.elements.email.value = item.email || "";
      form.elements.telefono.value = item.telefono || "";
      form.elements.direccion.value = item.domicilio_fiscal || item.direccion || "";
      form.elements.sitio_web.value = item.sitio_web || "";
      form.elements.notas_operativas.value = item.notas_operativas || "";
      form.elements.notas_comerciales.value = item.notas_comerciales || "";
      form.elements.activo.checked = Boolean(item.activo);
      setClienteSubpage("consulta");
      showPanel("cliente-edit-panel");
      clearMessage("cliente-edit-message");
      document.getElementById("cliente-edit-panel").scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function cancelClienteEdit() {
      uiState.editing.clienteId = null;
      document.getElementById("cliente-edit-form").reset();
      hidePanel("cliente-edit-panel", "cliente-edit-message");
    }

    function startTransportistaEdit(transportistaId) {
      const item = state.transportistas.find((row) => row.id === transportistaId);
      if (!item) {
        return;
      }
      uiState.editing.transportistaId = transportistaId;
      const form = document.getElementById("transportista-edit-form");
      form.elements.id.value = item.id;
      form.elements.nombre.value = item.nombre || "";
      form.elements.nombre_comercial.value = item.nombre_comercial || "";
      form.elements.tipo_transportista.value = item.tipo_transportista || "subcontratado";
      form.elements.tipo_persona.value = item.tipo_persona || "moral";
      form.elements.estatus.value = item.estatus || "activo";
      form.elements.rfc.value = item.rfc || "";
      form.elements.curp.value = item.curp || "";
      form.elements.regimen_fiscal.value = item.regimen_fiscal || "";
      form.elements.fecha_alta.value = toDateInputValue(item.fecha_alta);
      form.elements.nivel_confianza.value = item.nivel_confianza || "medio";
      form.elements.prioridad_asignacion.value = integerStringForNumberInput(item.prioridad_asignacion);
      form.elements.contacto.value = item.contacto || "";
      form.elements.telefono.value = item.telefono || item.telefono_general || "";
      form.elements.email.value = item.email || item.email_general || "";
      form.elements.sitio_web.value = item.sitio_web || "";
      form.elements.codigo_postal.value = item.codigo_postal || "";
      form.elements.ciudad.value = item.ciudad || "";
      form.elements.estado.value = item.estado || "";
      form.elements.pais.value = item.pais || "";
      form.elements.direccion_fiscal.value = item.direccion_fiscal || "";
      form.elements.direccion_operativa.value = item.direccion_operativa || "";
      form.elements.notas_operativas.value = item.notas_operativas || item.notas || "";
      form.elements.notas_comerciales.value = item.notas_comerciales || "";
      form.elements.blacklist.checked = Boolean(item.blacklist);
      form.elements.activo.checked = Boolean(item.activo);
      setTransportistaSubpage("consulta");
      showPanel("transportista-edit-panel");
      clearMessage("transportista-edit-message");
      const editPanel = document.getElementById("transportista-edit-panel");
      if (editPanel) {
        editPanel.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }

    function cancelTransportistaEdit() {
      uiState.editing.transportistaId = null;
      document.getElementById("transportista-edit-form").reset();
      hidePanel("transportista-edit-panel", "transportista-edit-message");
    }

    function cancelOperadorEdit() {
      uiState.editing.operadorId = null;
      const form = document.getElementById("operador-edit-form");
      if (form) {
        form.reset();
        applyMoneyFormatToForm(form);
      }
      hidePanel("operador-edit-panel", "operador-edit-message");
    }

    function cancelUnidadEdit() {
      uiState.editing.unidadId = null;
      const form = document.getElementById("unidad-edit-form");
      if (form) {
        form.reset();
      }
      hidePanel("unidad-edit-panel", "unidad-edit-message");
    }

    function startUnidadEdit(id) {
      const uid = Number(id);
      const item = state.unidades.find((row) => Number(row.id_unidad) === uid);
      if (!item) {
        setMessage(
          "unidad-consulta-message",
          "No se encontro esa unidad en el catalogo cargado (memoria). Pulse Recargar catalogo; si tiene mas de 500 unidades en el servidor, el panel solo muestra las primeras 500 por economico.",
          "error",
        );
        return;
      }
      uiState.editing.unidadId = item.id_unidad;
      fillSelect("edit-unidad-transportista", state.transportistas, (t) => t.id, (t) => `${t.id} - ${t.nombre}`, {
        includeEmpty: true,
        emptyLabel: "Sin transportista",
        classKey: "transportista",
      });
      const form = document.getElementById("unidad-edit-form");
      const idEl = document.getElementById("unidad-edit-form-id");
      if (idEl) {
        idEl.value = String(item.id_unidad);
      }
      form.elements.transportista_id.value = item.transportista_id != null ? String(item.transportista_id) : "";
      form.elements.tipo_propiedad.value = item.tipo_propiedad || "";
      form.elements.estatus_documental.value = item.estatus_documental || "";
      form.elements.economico.value = item.economico || "";
      form.elements.placas.value = item.placas || "";
      form.elements.descripcion.value = item.descripcion || "";
      form.elements.detalle.value = item.detalle || "";
      form.elements.vigencia_permiso_sct.value = toDateInputValue(item.vigencia_permiso_sct);
      form.elements.vigencia_seguro.value = toDateInputValue(item.vigencia_seguro);
      form.elements.activo.checked = item.activo === true;
      setGenericSubpage("unidad", "unidadSubpage", "consulta", "consulta");
      showPanel("unidad-edit-panel");
      clearMessage("unidad-edit-message");
      const panel = document.getElementById("unidad-edit-panel");
      if (panel) {
        panel.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }

    async function deleteUnidad(idUnidad) {
      const uid = Number(idUnidad);
      if (!Number.isFinite(uid) || uid < 1) {
        return;
      }
      if (
        !window.confirm(
          "¿Eliminar esta unidad? La accion no se puede deshacer. Si existen asignaciones que la usen, el servidor rechazara el borrado.",
        )
      ) {
        return;
      }
      clearMessage("unidad-consulta-message");
      try {
        await api(`/unidades/${uid}`, { method: "DELETE" });
        if (uiState.editing.unidadId != null && Number(uiState.editing.unidadId) === uid) {
          cancelUnidadEdit();
        }
        setMessage("unidad-consulta-message", "Unidad eliminada.", "ok");
        await refreshData();
      } catch (error) {
        setMessage("unidad-consulta-message", error.message, "error");
      }
    }

    function startOperadorEdit(operadorId) {
      const oid = Number(operadorId);
      const item = state.operadores.find((row) => Number(row.id_operador) === oid);
      if (!item) {
        return;
      }
      uiState.editing.operadorId = item.id_operador;
      const form = document.getElementById("operador-edit-form");
      const idEl = document.getElementById("operador-edit-form-id");
      if (idEl) {
        idEl.value = String(item.id_operador);
      }
      form.elements.transportista_id.value = item.transportista_id != null ? String(item.transportista_id) : "";
      form.elements.tipo_contratacion.value = item.tipo_contratacion || "";
      form.elements.licencia.value = item.licencia || "";
      form.elements.tipo_licencia.value = item.tipo_licencia || "";
      form.elements.vigencia_licencia.value = toDateInputValue(item.vigencia_licencia);
      form.elements.estatus_documental.value = item.estatus_documental || "";
      form.elements.nombre.value = item.nombre || "";
      form.elements.apellido_paterno.value = item.apellido_paterno || "";
      form.elements.apellido_materno.value = item.apellido_materno || "";
      form.elements.fecha_nacimiento.value = toDateInputValue(item.fecha_nacimiento);
      form.elements.curp.value = item.curp || "";
      form.elements.rfc.value = item.rfc || "";
      form.elements.nss.value = item.nss || "";
      form.elements.estado_civil.value = item.estado_civil || "soltero";
      form.elements.tipo_sangre.value = item.tipo_sangre || "O+";
      form.elements.fotografia.value = item.fotografia || "";
      form.elements.telefono_principal.value = item.telefono_principal || "";
      form.elements.telefono_emergencia.value = item.telefono_emergencia || "";
      form.elements.nombre_contacto_emergencia.value = item.nombre_contacto_emergencia || "";
      form.elements.correo_electronico.value = item.correo_electronico || "";
      form.elements.direccion.value = item.direccion || "";
      form.elements.colonia.value = item.colonia || "";
      form.elements.municipio.value = item.municipio || "";
      form.elements.estado_geografico.value = item.estado_geografico || "";
      form.elements.codigo_postal.value = item.codigo_postal || "";
      form.elements.anios_experiencia.value = optionalNonNegativeIntString(item.anios_experiencia);
      form.elements.tipos_unidad_manejadas.value = operadorCsvFromApi(item.tipos_unidad_manejadas);
      form.elements.tipos_carga_experiencia.value = operadorCsvFromApi(item.tipos_carga_experiencia);
      form.elements.rutas_conocidas.value = item.rutas_conocidas || "";
      form.elements.certificaciones.value = item.certificaciones || "";
      form.elements.ultima_revision_medica.value = toDateInputValue(item.ultima_revision_medica);
      form.elements.proxima_revision_medica.value = toDateInputValue(item.proxima_revision_medica);
      form.elements.resultado_apto.checked = item.resultado_apto === true;
      form.elements.restricciones_medicas.value = item.restricciones_medicas || "";
      form.elements.puntualidad.value = item.puntualidad != null && item.puntualidad !== "" ? String(item.puntualidad) : "";
      form.elements.consumo_diesel_promedio.value =
        item.consumo_diesel_promedio != null && item.consumo_diesel_promedio !== ""
          ? String(item.consumo_diesel_promedio)
          : "";
      form.elements.consumo_gasolina_promedio.value =
        item.consumo_gasolina_promedio != null && item.consumo_gasolina_promedio !== ""
          ? String(item.consumo_gasolina_promedio)
          : "";
      form.elements.calificacion_general.value =
        item.calificacion_general != null && item.calificacion_general !== "" ? String(item.calificacion_general) : "";
      form.elements.incidencias_desempeno.value = item.incidencias_desempeno || "";
      form.elements.comentarios_desempeno.value = item.comentarios_desempeno || "";
      applyMoneyFormatToForm(form);
      setGenericSubpage("operador", "operadorSubpage", "consulta", "consulta");
      showPanel("operador-edit-panel");
      clearMessage("operador-edit-message");
      const panel = document.getElementById("operador-edit-panel");
      if (panel) {
        panel.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }

    function startTransportistaContactoEdit(transportistaId, contactoId) {
      const transportista = state.transportistas.find((item) => item.id === transportistaId);
      const contacto = transportista?.contactos?.find((item) => item.id === contactoId);
      if (!transportista || !contacto) {
        return;
      }
      uiState.editing.transportistaContactoId = contactoId;
      const form = document.getElementById("transportista-contacto-edit-form");
      form.elements.id.value = contacto.id;
      form.elements.transportista_id.value = transportista.id;
      form.elements.transportista_label.value = `${transportista.id} - ${transportista.nombre}`;
      form.elements.nombre.value = contacto.nombre || "";
      form.elements.area.value = contacto.area || "";
      form.elements.puesto.value = contacto.puesto || "";
      form.elements.email.value = contacto.email || "";
      form.elements.telefono.value = contacto.telefono || "";
      form.elements.extension.value = contacto.extension || "";
      form.elements.celular.value = contacto.celular || "";
      form.elements.principal.checked = Boolean(contacto.principal);
      form.elements.activo.checked = Boolean(contacto.activo);
      setTransportistaSubpage("contactos");
      showPanel("transportista-contacto-edit-panel");
      clearMessage("transportista-contacto-edit-message");
    }

    function cancelTransportistaContactoEdit() {
      uiState.editing.transportistaContactoId = null;
      document.getElementById("transportista-contacto-edit-form").reset();
      hidePanel("transportista-contacto-edit-panel", "transportista-contacto-edit-message");
    }

    async function deleteTransportistaContacto(transportistaId, contactoId) {
      if (!window.confirm("¿Eliminar este contacto del transportista?")) {
        return;
      }
      clearMessage("transportista-contacto-message");
      try {
        await api(`/transportistas/${transportistaId}/contactos/${contactoId}`, { method: "DELETE" });
        if (uiState.editing.transportistaContactoId === contactoId) {
          cancelTransportistaContactoEdit();
        }
        setMessage("transportista-contacto-message", "Contacto eliminado.", "ok");
        await refreshData();
        document.getElementById("transportista-contacto-transportista").value = String(transportistaId);
        syncTransportistaModuleSelection("transportista-contacto-transportista");
      } catch (error) {
        setMessage("transportista-contacto-message", error.message, "error");
      }
    }

    function startTransportistaDocumentoEdit(transportistaId, documentoId) {
      const transportista = state.transportistas.find((item) => item.id === transportistaId);
      const documento = transportista?.documentos?.find((item) => item.id === documentoId);
      if (!transportista || !documento) {
        return;
      }
      uiState.editing.transportistaDocumentoId = documentoId;
      const form = document.getElementById("transportista-documento-edit-form");
      form.elements.id.value = documento.id;
      form.elements.transportista_id.value = transportista.id;
      form.elements.transportista_label.value = `${transportista.id} - ${transportista.nombre}`;
      form.elements.tipo_documento.value = documento.tipo_documento || "otro";
      form.elements.numero_documento.value = documento.numero_documento || "";
      form.elements.fecha_emision.value = toDateInputValue(documento.fecha_emision);
      form.elements.fecha_vencimiento.value = toDateInputValue(documento.fecha_vencimiento);
      form.elements.archivo_url.value = documento.archivo_url || "";
      form.elements.estatus.value = documento.estatus || "pendiente";
      form.elements.observaciones.value = documento.observaciones || "";
      setTransportistaSubpage("documentos");
      showPanel("transportista-documento-edit-panel");
      clearMessage("transportista-documento-edit-message");
    }

    function cancelTransportistaDocumentoEdit() {
      uiState.editing.transportistaDocumentoId = null;
      document.getElementById("transportista-documento-edit-form").reset();
      hidePanel("transportista-documento-edit-panel", "transportista-documento-edit-message");
    }

    async function deleteTransportistaDocumento(transportistaId, documentoId) {
      if (!window.confirm("¿Eliminar este documento del transportista?")) {
        return;
      }
      clearMessage("transportista-documento-message");
      try {
        await api(`/transportistas/${transportistaId}/documentos/${documentoId}`, { method: "DELETE" });
        if (uiState.editing.transportistaDocumentoId === documentoId) {
          cancelTransportistaDocumentoEdit();
        }
        setMessage("transportista-documento-message", "Documento eliminado.", "ok");
        await refreshData();
        document.getElementById("transportista-documento-transportista").value = String(transportistaId);
        syncTransportistaModuleSelection("transportista-documento-transportista");
      } catch (error) {
        setMessage("transportista-documento-message", error.message, "error");
      }
    }

    function startViajeEdit(viajeId) {
      const item = state.viajes.find((row) => row.id === viajeId);
      if (!item) {
        return;
      }
      uiState.editing.viajeId = viajeId;
      const form = document.getElementById("viaje-edit-form");
      form.elements.id.value = item.id;
      form.elements.codigo_viaje.value = item.codigo_viaje || "";
      form.elements.descripcion.value = item.descripcion || "";
      form.elements.origen.value = item.origen || "";
      form.elements.destino.value = item.destino || "";
      form.elements.fecha_salida.value = toDateTimeLocal(item.fecha_salida);
      form.elements.fecha_llegada_estimada.value = toDateTimeLocal(item.fecha_llegada_estimada);
      form.elements.fecha_llegada_real.value = toDateTimeLocal(item.fecha_llegada_real);
      form.elements.estado.value = item.estado || "planificado";
      form.elements.kilometros_estimados.value = htmlNumberInputValue(item.kilometros_estimados);
      form.elements.notas.value = item.notas || "";
      setGenericSubpage("viaje", "viajeSubpage", "consulta", "consulta");
      showPanel("viaje-edit-panel");
      clearMessage("viaje-edit-message");
    }

    function cancelViajeEdit() {
      uiState.editing.viajeId = null;
      document.getElementById("viaje-edit-form").reset();
      hidePanel("viaje-edit-panel", "viaje-edit-message");
    }

    function recalculateFacturaForm(formSelector) {
      const subtotalInput = document.querySelector(`${formSelector} [name="subtotal"]`);
      const ivaPctInput = document.querySelector(`${formSelector} [name="iva_pct"]`);
      const ivaMontoInput = document.querySelector(`${formSelector} [name="iva_monto"]`);
      const retencionInput = document.querySelector(`${formSelector} [name="retencion_monto"]`);
      const totalInput = document.querySelector(`${formSelector} [name="total"]`);
      const saldoInput = document.querySelector(`${formSelector} [name="saldo_pendiente"]`);
      if (!subtotalInput || !ivaPctInput || !ivaMontoInput || !retencionInput || !totalInput || !saldoInput) {
        return;
      }
      const subtotal = numberOrNull(subtotalInput.value);
      const ivaPct = numberOrNull(ivaPctInput.value);
      const retencion = numberOrNull(retencionInput.value) ?? 0;
      if (subtotal === null || ivaPct === null) {
        return;
      }
      const ivaMonto = subtotal * ivaPct;
      const total = subtotal + ivaMonto - retencion;
      ivaMontoInput.value = formatMoneyInputFromEl(ivaMonto, ivaMontoInput);
      totalInput.value = formatMoneyInputFromEl(total, totalInput);
      if (parseLocaleNumber(saldoInput.value) === null || String(saldoInput.value).trim() === "") {
        saldoInput.value = formatMoneyInputFromEl(total, saldoInput);
      }
    }

    function fillFacturaFleteSelectFiltered(clienteIdStr) {
      const raw = clienteIdStr != null ? String(clienteIdStr).trim() : "";
      const cid = raw === "" ? null : Number(raw);
      let items = Array.isArray(state.fletes) ? state.fletes : [];
      if (cid != null && Number.isFinite(cid)) {
        items = items.filter((f) => Number(f.cliente_id) === cid);
      }
      const emptyLabel =
        cid != null && Number.isFinite(cid)
          ? items.length
            ? "Selecciona flete"
            : "Sin fletes para este cliente"
          : "Sin flete";
      fillSelect("factura-flete", items, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, {
        includeEmpty: true,
        emptyLabel,
        classKey: "flete",
      });
    }

    function fillFacturaFromFlete(formSelector) {
      const form = document.querySelector(formSelector);
      const fleteId = integerOrNull(form.querySelector('[name="flete_id"]').value);
      if (!fleteId) {
        throw new Error("Selecciona primero un flete.");
      }
      const flete = state.fletes.find((item) => item.id === fleteId);
      if (!flete) {
        throw new Error("Flete no encontrado en memoria.");
      }
      form.querySelector('[name="cliente_id"]').value = String(flete.cliente_id);
      form.querySelector('[name="concepto"]').value = `Servicio de flete ${flete.codigo_flete}`;
      form.querySelector('[name="referencia"]').value = flete.codigo_flete || "";
      form.querySelector('[name="moneda"]').value = flete.moneda || "MXN";
      const subtotalEl = form.querySelector('[name="subtotal"]');
      subtotalEl.value = formatMoneyInputFromEl(
        Number(flete.precio_venta ?? flete.monto_estimado ?? 0),
        subtotalEl,
      );
      if (form.querySelector('[name="orden_servicio_id"]') && !form.querySelector('[name="orden_servicio_id"]').value) {
        form.querySelector('[name="orden_servicio_id"]').value = "";
      }
      recalculateFacturaForm(formSelector);
    }

    function startFacturaEdit(facturaId) {
      const item = state.facturas.find((row) => row.id === facturaId);
      if (!item) {
        return;
      }
      uiState.editing.facturaId = facturaId;
      const form = document.getElementById("factura-edit-form");
      form.elements.id.value = item.id;
      form.elements.serie.value = item.serie || "";
      form.elements.cliente_id.value = String(item.cliente_id || "");
      form.elements.flete_id.value = item.flete_id ? String(item.flete_id) : "";
      form.elements.orden_servicio_id.value = item.orden_servicio_id ? String(item.orden_servicio_id) : "";
      form.elements.fecha_emision.value = toDateInputValue(item.fecha_emision);
      form.elements.fecha_vencimiento.value = toDateInputValue(item.fecha_vencimiento);
      form.elements.concepto.value = item.concepto || "";
      form.elements.referencia.value = item.referencia || "";
      form.elements.moneda.value = item.moneda || "MXN";
      form.elements.subtotal.value = item.subtotal ?? "";
      form.elements.iva_pct.value = htmlNumberInputValue(item.iva_pct != null ? item.iva_pct : 0.16);
      form.elements.iva_monto.value = item.iva_monto ?? "";
      form.elements.retencion_monto.value = item.retencion_monto ?? 0;
      form.elements.total.value = item.total ?? "";
      form.elements.saldo_pendiente.value = item.saldo_pendiente ?? "";
      form.elements.forma_pago.value = item.forma_pago || "";
      form.elements.metodo_pago.value = item.metodo_pago || "";
      form.elements.uso_cfdi.value = item.uso_cfdi || "";
      form.elements.estatus.value = item.estatus || "borrador";
      form.elements.timbrada.checked = Boolean(item.timbrada);
      form.elements.observaciones.value = item.observaciones || "";
      applyMoneyFormatToForm(form);
      setGenericSubpage("factura", "facturaSubpage", "consulta", "consulta");
      showPanel("factura-edit-panel");
      clearMessage("factura-edit-message");
    }

    function cancelFacturaEdit() {
      uiState.editing.facturaId = null;
      document.getElementById("factura-edit-form").reset();
      hidePanel("factura-edit-panel", "factura-edit-message");
    }

    function startTarifaCompraEdit(tarifaId) {
      const tid = Number(tarifaId);
      if (!Number.isFinite(tid) || tid < 1) {
        return;
      }
      const item = state.tarifasCompra.find((row) => Number(row.id) === tid);
      if (!item) {
        return;
      }
      uiState.editing.tarifaCompraId = tid;
      lastTarifaCompraEditId = tid;
      try {
        window.__SIFE_tarifaCompraEditId = tid;
      } catch (_e) {
        /* ignore */
      }
      const form = document.getElementById("tarifa-compra-edit-form");
      const sid = String(item.id);
      form._sifeTarifaCompraId = tid;
      setTarifaCompraEditIdStorage(sid);
      form.setAttribute("data-tarifa-compra-id", sid);
      const idInput = document.getElementById("tarifa-compra-edit-record-id");
      if (idInput) {
        idInput.value = sid;
        idInput.defaultValue = sid;
      }
      const saveBtn = document.getElementById("tarifa-compra-edit-save");
      if (saveBtn) {
        saveBtn.setAttribute("data-tarifa-compra-record-id", sid);
      }
      form.elements.transportista_id.value = String(item.transportista_id || "");
      form.elements.nombre_tarifa.value = item.nombre_tarifa || "";
      form.elements.tipo_transportista.value = item.tipo_transportista || "subcontratado";
      form.elements.ambito.value = item.ambito || "federal";
      form.elements.modalidad_cobro.value = item.modalidad_cobro || "mixta";
      form.elements.origen.value = item.origen || "";
      form.elements.destino.value = item.destino || "";
      form.elements.tipo_unidad.value = item.tipo_unidad || "";
      form.elements.tipo_carga.value = item.tipo_carga || "";
      form.elements.tarifa_base.value = item.tarifa_base ?? "";
      form.elements.tarifa_km.value = item.tarifa_km ?? "";
      form.elements.tarifa_kg.value = item.tarifa_kg ?? "";
      form.elements.tarifa_tonelada.value = item.tarifa_tonelada ?? "";
      form.elements.tarifa_hora.value = item.tarifa_hora ?? "";
      form.elements.tarifa_dia.value = item.tarifa_dia ?? "";
      form.elements.recargo_minimo.value = item.recargo_minimo ?? "";
      form.elements.dias_credito.value =
        item.dias_credito != null && item.dias_credito !== "" ? String(item.dias_credito) : "";
      form.elements.moneda.value = item.moneda || "MXN";
      form.elements.activo.checked = Boolean(item.activo);
      form.elements.vigencia_inicio.value = toDateInputValue(item.vigencia_inicio);
      form.elements.vigencia_fin.value = toDateInputValue(item.vigencia_fin);
      form.elements.observaciones.value = item.observaciones || "";
      applyMoneyFormatToForm(form);
      for (const name of ["tarifa_km", "tarifa_kg", "tarifa_tonelada"]) {
        const el = form.querySelector(`input.field-money[name="${name}"]`);
        if (!el) {
          continue;
        }
        const p = parseLocaleNumber(el.value);
        el.value = p === null ? "" : formatMoneyInputFromEl(p, el);
      }
      setGenericSubpage("tarifa-compra", "tarifaCompraSubpage", "consulta", "consulta");
      showPanel("tarifa-compra-edit-panel");
      clearMessage("tarifa-compra-edit-message");
    }

    function cancelTarifaCompraEdit() {
      uiState.editing.tarifaCompraId = null;
      lastTarifaCompraEditId = null;
      try {
        window.__SIFE_tarifaCompraEditId = null;
      } catch (_e) {
        /* ignore */
      }
      const form = document.getElementById("tarifa-compra-edit-form");
      try {
        delete form._sifeTarifaCompraId;
      } catch (_e) {
        form._sifeTarifaCompraId = null;
      }
      setTarifaCompraEditIdStorage(null);
      form.removeAttribute("data-tarifa-compra-id");
      const idInput = document.getElementById("tarifa-compra-edit-record-id");
      if (idInput) {
        idInput.value = "";
        idInput.defaultValue = "";
      }
      const saveBtn = document.getElementById("tarifa-compra-edit-save");
      if (saveBtn) {
        saveBtn.removeAttribute("data-tarifa-compra-record-id");
      }
      form.reset();
      hidePanel("tarifa-compra-edit-panel", "tarifa-compra-edit-message");
    }

    function tarifaFleteDateInput(value) {
      return toDateInputValue(value);
    }

    function setEnumSelectSafe(selectEl, rawValue, allowed, fallback) {
      if (!selectEl) {
        return;
      }
      const s = rawValue != null && String(rawValue).trim() !== "" ? String(rawValue).trim().toLowerCase() : "";
      const pick = allowed.includes(s) ? s : fallback;
      selectEl.value = pick;
    }

    async function startTarifaFleteEdit(tarifaId) {
      const tid = Number(tarifaId);
      if (!Number.isFinite(tid) || tid < 1) {
        setMessage("tarifa-message", "ID de tarifa no valido.", "error");
        return;
      }
      let item = state.tarifas.find((row) => Number(row.id) === tid);
      try {
        item = await api(`/tarifas-flete/${tid}`);
      } catch (_err) {
        if (!item) {
          setMessage(
            "tarifa-message",
            "No se pudo cargar la tarifa desde el servidor. Actualice la pagina (F5) e intente de nuevo.",
            "error",
          );
          return;
        }
      }
      if (!item) {
        setMessage("tarifa-message", "No se encontro la tarifa en el listado cargado. Pulse F5.", "error");
        return;
      }
      uiState.editing.tarifaFleteId = item.id;
      const form = document.getElementById("tarifa-edit-form");
      form.elements.id.value = item.id;
      form.elements.nombre_tarifa.value = item.nombre_tarifa || "";
      form.elements.moneda.value = item.moneda || "MXN";
      form.elements.tipo_operacion.value = item.tipo_operacion || "subcontratado";
      if (form.elements.ambito) {
        setEnumSelectSafe(form.elements.ambito, item.ambito, ["local", "estatal", "federal"], "federal");
      }
      if (form.elements.modalidad_cobro) {
        setEnumSelectSafe(
          form.elements.modalidad_cobro,
          item.modalidad_cobro,
          ["mixta", "por_viaje", "por_km", "por_tonelada", "por_hora", "por_dia"],
          "mixta",
        );
      }
      form.elements.origen.value = item.origen || "";
      form.elements.destino.value = item.destino || "";
      form.elements.tipo_unidad.value = item.tipo_unidad || "";
      form.elements.tipo_carga.value = item.tipo_carga || "";
      form.elements.tarifa_base.value = item.tarifa_base ?? "";
      form.elements.tarifa_km.value = item.tarifa_km ?? "";
      form.elements.tarifa_kg.value = item.tarifa_kg ?? "";
      if (form.elements.tarifa_tonelada) {
        form.elements.tarifa_tonelada.value = item.tarifa_tonelada ?? "";
      }
      if (form.elements.tarifa_hora) {
        form.elements.tarifa_hora.value = item.tarifa_hora ?? "";
      }
      if (form.elements.tarifa_dia) {
        form.elements.tarifa_dia.value = item.tarifa_dia ?? "";
      }
      if (form.elements.porcentaje_utilidad) {
        form.elements.porcentaje_utilidad.value = item.porcentaje_utilidad ?? "";
      }
      if (form.elements.porcentaje_riesgo) {
        form.elements.porcentaje_riesgo.value = item.porcentaje_riesgo ?? "";
      }
      if (form.elements.porcentaje_urgencia) {
        form.elements.porcentaje_urgencia.value = item.porcentaje_urgencia ?? "";
      }
      if (form.elements.porcentaje_retorno_vacio) {
        form.elements.porcentaje_retorno_vacio.value = item.porcentaje_retorno_vacio ?? "";
      }
      if (form.elements.porcentaje_carga_especial) {
        form.elements.porcentaje_carga_especial.value = item.porcentaje_carga_especial ?? "";
      }
      form.elements.recargo_minimo.value = item.recargo_minimo ?? "";
      form.elements.vigencia_inicio.value = tarifaFleteDateInput(item.vigencia_inicio);
      form.elements.vigencia_fin.value = tarifaFleteDateInput(item.vigencia_fin);
      form.elements.activo.checked = Boolean(item.activo);
      applyMoneyFormatToForm(form);
      for (const name of ["tarifa_km", "tarifa_kg", "tarifa_tonelada"]) {
        const el = form.querySelector(`input.field-money[name="${name}"]`);
        if (!el) {
          continue;
        }
        const p = parseLocaleNumber(el.value);
        el.value = p === null ? "" : formatMoneyInputFromEl(p, el);
      }
      setGenericSubpage("tarifa", "tarifaSubpage", "consulta", "consulta");
      showPanel("tarifa-edit-panel");
      clearMessage("tarifa-edit-message");
      const teNombre = document.getElementById("tarifa-edit-form-nombre-tarifa");
      const teAviso = document.getElementById("tarifa-edit-form-nombre-aviso");
      const teSubmit = form.querySelector('button[type="submit"]');
      refreshTarifaVentaNombreAviso(teNombre, teAviso, teSubmit, item.id);
      document.getElementById("tarifa-edit-panel").scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    function cancelTarifaFleteEdit() {
      uiState.editing.tarifaFleteId = null;
      document.getElementById("tarifa-edit-form").reset();
      const teAviso = document.getElementById("tarifa-edit-form-nombre-aviso");
      if (teAviso) {
        teAviso.textContent = "";
        teAviso.hidden = true;
      }
      hidePanel("tarifa-edit-panel", "tarifa-edit-message");
    }

    async function deleteTarifaCompra(tarifaId) {
      if (!window.confirm("¿Eliminar esta tarifa de compra?")) {
        return;
      }
      clearMessage("tarifa-compra-message");
      try {
        await api(`/tarifas-compra-transportista/${tarifaId}`, { method: "DELETE" });
        if (Number(uiState.editing.tarifaCompraId) === Number(tarifaId)) {
          cancelTarifaCompraEdit();
        }
        setMessage("tarifa-compra-message", "Tarifa de compra eliminada.", "ok");
        await refreshData();
      } catch (error) {
        setMessage("tarifa-compra-message", error.message, "error");
      }
    }

    function startAsignacionEdit(asignacionId) {
      const item = state.asignaciones.find((row) => row.id_asignacion === asignacionId);
      if (!item) {
        return;
      }
      uiState.editing.asignacionId = asignacionId;
      const form = document.getElementById("asignacion-edit-form");
      form.elements.id_asignacion.value = item.id_asignacion;
      form.elements.id_operador.value = String(item.id_operador || "");
      form.elements.id_unidad.value = String(item.id_unidad || "");
      form.elements.id_viaje.value = String(item.id_viaje || "");
      form.elements.fecha_salida.value = toDateTimeLocal(item.fecha_salida);
      form.elements.fecha_regreso.value = toDateTimeLocal(item.fecha_regreso);
      form.elements.km_inicial.value = htmlNumberInputValue(item.km_inicial);
      form.elements.km_final.value = htmlNumberInputValue(item.km_final);
      form.elements.rendimiento_combustible.value = htmlNumberInputValue(item.rendimiento_combustible);
      setGenericSubpage("asignacion", "asignacionSubpage", "consulta", "consulta");
      showPanel("asignacion-edit-panel");
      clearMessage("asignacion-edit-message");
    }

    function cancelAsignacionEdit() {
      uiState.editing.asignacionId = null;
      document.getElementById("asignacion-edit-form").reset();
      hidePanel("asignacion-edit-panel", "asignacion-edit-message");
    }

    function startFleteEdit(fleteId) {
      const fid = Number(fleteId);
      const item = state.fletes.find((row) => Number(row.id) === fid);
      if (!item) {
        return;
      }
      uiState.editing.fleteId = item.id;
      const form = document.getElementById("flete-edit-form");
      const idPk = document.getElementById("flete-edit-form-record-id");
      if (idPk) {
        idPk.value = String(item.id);
      }
      if (form) {
        form.dataset.sifeEditingFleteId = String(item.id);
      }
      form.elements.codigo_flete.value = item.codigo_flete || "";
      form.elements.estado.value = item.estado || "cotizado";
      form.elements.tipo_operacion.value = item.tipo_operacion || "subcontratado";
      form.elements.metodo_calculo.value = item.metodo_calculo || "manual";
      form.elements.moneda.value = item.moneda || "MXN";
      form.elements.cliente_id.value = String(item.cliente_id || "");
      form.elements.transportista_id.value = String(item.transportista_id || "");
      form.elements.viaje_id.value = item.viaje_id ? String(item.viaje_id) : "";
      form.elements.tipo_unidad.value = item.tipo_unidad || "";
      form.elements.tipo_carga.value = item.tipo_carga || "";
      form.elements.descripcion_carga.value = item.descripcion_carga || "";
      form.elements.peso_kg.value = htmlNumberInputValue(item.peso_kg);
      form.elements.volumen_m3.value = htmlNumberInputValue(item.volumen_m3);
      form.elements.numero_bultos.value = optionalNonNegativeIntString(item.numero_bultos);
      form.elements.distancia_km.value = htmlNumberInputValue(item.distancia_km);
      form.elements.monto_estimado.value = item.precio_venta ?? item.monto_estimado ?? "";
      form.elements.costo_transporte_estimado.value = item.costo_transporte_estimado ?? "";
      form.elements.costo_transporte_real.value = item.costo_transporte_real ?? "";
      form.elements.margen_estimado.value = item.margen_estimado ?? "";
      form.elements.notas.value = item.notas || "";
      applyMoneyFormatToForm(form);
      refreshMarginForForm("#flete-edit-form");
      setGenericSubpage("flete", "fleteSubpage", "consulta", "consulta");
      showPanel("flete-edit-panel");
      clearMessage("flete-edit-message");
    }

    function cancelFleteEdit() {
      uiState.editing.fleteId = null;
      const form = document.getElementById("flete-edit-form");
      if (form) {
        delete form.dataset.sifeEditingFleteId;
        form.reset();
      }
      hidePanel("flete-edit-panel", "flete-edit-message");
    }

    function startGastoEdit(gastoId) {
      const item = state.gastos.find((row) => row.id === gastoId);
      if (!item) {
        return;
      }
      const valid = Object.keys(GASTO_CATEGORIA_LABELS);
      uiState.editing.gastoId = gastoId;
      const form = document.getElementById("gasto-edit-form");
      form.elements.id.value = item.id;
      form.elements.flete_id.value = String(item.flete_id);
      form.elements.tipo_gasto.value = valid.includes(item.tipo_gasto) ? item.tipo_gasto : "otros";
      form.elements.monto.value = item.monto ?? "";
      form.elements.fecha_gasto.value = toDateInputValue(item.fecha_gasto);
      form.elements.referencia.value = item.referencia || "";
      form.elements.comprobante.value = item.comprobante || "";
      form.elements.descripcion.value = item.descripcion || "";
      applyMoneyFormatToForm(form);
      setGenericSubpage("gasto", "gastoSubpage", "consulta", "consulta");
      showPanel("gasto-edit-panel");
      clearMessage("gasto-edit-message");
    }

    function cancelGastoEdit() {
      uiState.editing.gastoId = null;
      document.getElementById("gasto-edit-form").reset();
      hidePanel("gasto-edit-panel", "gasto-edit-message");
    }

    async function deleteGasto(gastoId) {
      if (
        !window.confirm(
          "¿Eliminar este gasto de viaje? Se recalculará el costo real y el margen del flete.",
        )
      ) {
        return;
      }
      clearMessage("gasto-list-message");
      try {
        await api(`/gastos-viaje/${gastoId}`, { method: "DELETE" });
        if (uiState.editing.gastoId === gastoId) {
          cancelGastoEdit();
        }
        setMessage("gasto-list-message", "Gasto eliminado.", "ok");
        await refreshData();
      } catch (error) {
        setMessage("gasto-list-message", error.message, "error");
      }
    }

    function startDespachoEdit(despachoId) {
      const did = Number(despachoId);
      if (!Number.isFinite(did) || did < 1) {
        return;
      }
      const item = state.despachos.find((row) => Number(row.id_despacho) === did);
      if (!item) {
        return;
      }
      uiState.editing.despachoId = item.id_despacho;
      const form = document.getElementById("despacho-edit-form");
      if (!form) {
        return;
      }
      form.dataset.sifeEditingDespachoId = String(item.id_despacho);
      const idEl = document.getElementById("despacho-edit-form-id");
      if (idEl) {
        idEl.value = String(item.id_despacho);
      }
      form.elements.asignacion_label.value = `${item.id_asignacion} - ${item.asignacion?.viaje?.codigo_viaje || "sin viaje"}`;
      form.elements.id_flete.value = item.id_flete ? String(item.id_flete) : "";
      form.elements.estatus.value = item.estatus || "programado";
      form.elements.salida_programada.value = toDateTimeLocal(item.salida_programada);
      form.elements.observaciones_transito.value = item.observaciones_transito || "";
      form.elements.motivo_cancelacion.value = item.motivo_cancelacion || "";
      setGenericSubpage("despacho", "despachoSubpage", "consulta", "consulta");
      showPanel("despacho-edit-panel");
      clearMessage("despacho-edit-message");
    }

    function cancelDespachoEdit() {
      uiState.editing.despachoId = null;
      const form = document.getElementById("despacho-edit-form");
      if (form) {
        delete form.dataset.sifeEditingDespachoId;
        form.reset();
      }
      hidePanel("despacho-edit-panel", "despacho-edit-message");
    }

    function populateSelects() {
      fillSelect("flete-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: false, classKey: "cliente" });
      fillSelect("flete-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: false, classKey: "transportista" });
      fillSelect("flete-viaje", state.viajes, (item) => item.id, (item) => `${item.id} - ${item.codigo_viaje}`, { includeEmpty: true, emptyLabel: "Sin viaje", classKey: "viaje" });
      fillSelect("factura-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: false, classKey: "cliente" });
      fillSelect("factura-filter-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: true, emptyLabel: "Todos", classKey: "cliente" });
      fillSelect("orden-servicio-filter-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: true, emptyLabel: "Todos", classKey: "cliente" });
      fillSelect("edit-factura-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: false, classKey: "cliente" });
      fillSelect("factura-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: true, emptyLabel: "Sin flete", classKey: "flete" });
      fillSelect("edit-factura-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: true, emptyLabel: "Sin flete", classKey: "flete" });
      fillSelect("gasto-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: false, classKey: "flete" });
      fillSelect("edit-gasto-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: false, classKey: "flete" });
      fillSelect("gasto-control-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: false, classKey: "flete" });
      fillSelect("cliente-contacto-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: true, emptyLabel: "Selecciona cliente", classKey: "cliente" });
      fillClienteContactoEditSelect("", null);
      const domBuscar = document.getElementById("cliente-domicilio-buscar");
      fillClienteDomicilioSelect(domBuscar ? domBuscar.value : "", document.getElementById("cliente-domicilio-cliente")?.value ?? null);
      fillSelect("cliente-condicion-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: true, emptyLabel: "Selecciona cliente", classKey: "cliente" });
      fillSelect("transportista-contacto-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: false, classKey: "transportista" });
      fillSelect("transportista-documento-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: false, classKey: "transportista" });
      fillSelect("tarifa-compra-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: false });
      fillSelect("tarifa-compra-filter-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: true, emptyLabel: "Todos", classKey: "transportista" });
      fillSelect("edit-tarifa-compra-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: false });
      fillSelect("operador-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: true, emptyLabel: "Sin transportista", classKey: "transportista" });
      fillSelect("edit-operador-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: true, emptyLabel: "Sin transportista", classKey: "transportista" });
      fillSelect("unidad-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: true, emptyLabel: "Sin transportista", classKey: "transportista" });
      fillSelect("edit-unidad-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: true, emptyLabel: "Sin transportista", classKey: "transportista" });
      fillSelect("asignacion-filter-operador", state.operadores, (item) => item.id_operador, (item) => `${item.id_operador} - ${item.nombre} ${item.apellido_paterno}`, { includeEmpty: true, emptyLabel: "Todos", classKey: "operador" });
      fillSelect("asignacion-filter-unidad", state.unidades, (item) => item.id_unidad, (item) => `${item.id_unidad} - ${item.economico}`, { includeEmpty: true, emptyLabel: "Todas", classKey: "unidad" });
      fillSelect("asignacion-filter-viaje", state.viajes, (item) => item.id, (item) => `${item.id} - ${item.codigo_viaje}`, { includeEmpty: true, emptyLabel: "Todos", classKey: "viaje" });
      fillSelect("flete-filter-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: true, emptyLabel: "Todos", classKey: "cliente" });
      fillSelect("flete-filter-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: true, emptyLabel: "Todos", classKey: "transportista" });
      fillSelect("edit-flete-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: false, classKey: "cliente" });
      fillSelect("edit-flete-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: false, classKey: "transportista" });
      fillSelect("edit-flete-viaje", state.viajes, (item) => item.id, (item) => `${item.id} - ${item.codigo_viaje}`, { includeEmpty: true, emptyLabel: "Sin viaje", classKey: "viaje" });

      fillSelect("asignacion-operador", state.operadores, (item) => item.id_operador, (item) => `${item.id_operador} - ${item.nombre} ${item.apellido_paterno}`, { includeEmpty: false, classKey: "operador" });
      fillSelect("asignacion-unidad", state.unidades, (item) => item.id_unidad, (item) => `${item.id_unidad} - ${item.economico}`, { includeEmpty: false, classKey: "unidad" });
      fillSelect("asignacion-viaje", state.viajes, (item) => item.id, (item) => `${item.id} - ${item.codigo_viaje}`, { includeEmpty: false, classKey: "viaje" });
      fillSelect("edit-asignacion-operador", state.operadores, (item) => item.id_operador, (item) => `${item.id_operador} - ${item.nombre} ${item.apellido_paterno}`, { includeEmpty: false, classKey: "operador" });
      fillSelect("edit-asignacion-unidad", state.unidades, (item) => item.id_unidad, (item) => `${item.id_unidad} - ${item.economico}`, { includeEmpty: false, classKey: "unidad" });
      fillSelect("edit-asignacion-viaje", state.viajes, (item) => item.id, (item) => `${item.id} - ${item.codigo_viaje}`, { includeEmpty: false, classKey: "viaje" });

      fillSelect("despacho-asignacion", state.asignaciones, (item) => item.id_asignacion, (item) => {
        const operador = item.operador ? `${item.operador.nombre} ${item.operador.apellido_paterno}` : `Operador ${item.id_operador}`;
        const unidad = item.unidad?.economico || `Unidad ${item.id_unidad}`;
        const viaje = item.viaje?.codigo_viaje || `Viaje ${item.id_viaje}`;
        return `${item.id_asignacion} - ${viaje} / ${operador} / ${unidad}`;
      }, { includeEmpty: false, classKey: "asignacion" });
      fillSelect("despacho-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: true, emptyLabel: "Sin flete", classKey: "flete" });
      fillSelect("despacho-filter-asignacion", state.asignaciones, (item) => item.id_asignacion, (item) => {
        const viaje = item.viaje?.codigo_viaje || `Viaje ${item.id_viaje}`;
        return `${item.id_asignacion} - ${viaje}`;
      }, { includeEmpty: true, emptyLabel: "Todas", classKey: "asignacion" });
      fillSelect("despacho-filter-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: true, emptyLabel: "Todos", classKey: "flete" });
      fillSelect("edit-despacho-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: true, emptyLabel: "Sin flete", classKey: "flete" });

      const despachoLabel = (item) => `${item.id_despacho} - ${item.estatus} - ${item.asignacion?.viaje?.codigo_viaje || "sin viaje"}`;
      fillSelect("salida-despacho", state.despachos, (item) => item.id_despacho, despachoLabel, { includeEmpty: false, classKey: "despacho" });
      fillSelect("evento-despacho", state.despachos, (item) => item.id_despacho, despachoLabel, { includeEmpty: false, classKey: "despacho" });
      fillSelect("entrega-despacho", state.despachos, (item) => item.id_despacho, despachoLabel, { includeEmpty: false, classKey: "despacho" });
      fillSelect("cierre-despacho", state.despachos, (item) => item.id_despacho, despachoLabel, { includeEmpty: false, classKey: "despacho" });
      fillSelect("cancelacion-despacho", state.despachos, (item) => item.id_despacho, despachoLabel, { includeEmpty: false, classKey: "despacho" });

      const elFacturaCliente = document.getElementById("factura-cliente");
      if (elFacturaCliente && elFacturaCliente.value) {
        fillFacturaFleteSelectFiltered(elFacturaCliente.value);
      }

      if (!window.__tarifaCompraTipoSyncBound) {
        window.__tarifaCompraTipoSyncBound = true;
        document.addEventListener("change", (e) => {
          if (e.target.id !== "tarifa-compra-transportista" && e.target.id !== "edit-tarifa-compra-transportista") {
            return;
          }
          const t = state.transportistas.find((x) => String(x.id) === String(e.target.value));
          if (!t || !t.tipo_transportista) {
            return;
          }
          if (e.target.id === "tarifa-compra-transportista") {
            const tipoEl = document.getElementById("tarifa-compra-tipo-transportista");
            if (tipoEl) {
              tipoEl.value = t.tipo_transportista;
            }
          } else {
            const tipoEdit = document.getElementById("edit-tarifa-compra-tipo-transportista");
            if (tipoEdit) {
              tipoEdit.value = t.tipo_transportista;
            }
          }
        });
      }
    }

    function unidadesEndpointFailed() {
      return (state.catalogRefreshErrors || []).some((e) => String(e).startsWith("Unidades:"));
    }

    function updateCatalogRefreshBanner() {
      const el = document.getElementById("catalog-refresh-banner");
      if (!el) {
        return;
      }
      const errs = state.catalogRefreshErrors || [];
      if (errs.length === 0) {
        el.innerHTML = "";
        el.hidden = true;
        return;
      }
      const li = errs.map((e) => `<li>${escapeHtml(e)}</li>`).join("");
      el.hidden = false;
      el.innerHTML =
        "<strong>Carga parcial del catalogo</strong>Algunos listados no se pudieron cargar; el resto del panel puede mostrarse con normalidad. Revise la API key en <code>.env</code>, que Uvicorn este en marcha y que MySQL acepte conexiones. Reintente con F5 o con <strong>Recargar catalogo</strong> en el modulo afectado." +
        `<ul>${li}</ul>`;
    }

    async function refreshData() {
      const pickItems = (res) => (Array.isArray(res?.items) ? res.items : []);

      const catalogFetches = [
        { label: "Clientes", stateKey: "clientes", path: "/clientes?limit=500" },
        { label: "Transportistas", stateKey: "transportistas", path: "/transportistas?limit=500" },
        { label: "Viajes", stateKey: "viajes", path: "/viajes?limit=500" },
        { label: "Fletes", stateKey: "fletes", path: "/fletes?limit=500" },
        { label: "Facturas", stateKey: "facturas", path: "/facturas?limit=500" },
        { label: "Gastos viaje", stateKey: "gastos", path: "/gastos-viaje?limit=500" },
        { label: "Tarifas venta", stateKey: "tarifas", path: "/tarifas-flete?limit=500" },
        { label: "Tarifas compra", stateKey: "tarifasCompra", path: "/tarifas-compra-transportista?limit=500" },
        { label: "Operadores", stateKey: "operadores", path: "/operadores?limit=500" },
        { label: "Unidades", stateKey: "unidades", path: "/unidades?limit=500" },
        { label: "Asignaciones", stateKey: "asignaciones", path: "/asignaciones?limit=500" },
        { label: "Despachos", stateKey: "despachos", path: "/despachos?limit=500" },
        { label: "Ordenes servicio", stateKey: "ordenesServicio", path: "/ordenes-servicio?limit=500" },
      ];

      state.catalogRefreshErrors = [];
      const settled = await Promise.allSettled(catalogFetches.map((f) => api(f.path)));

      settled.forEach((result, i) => {
        const f = catalogFetches[i];
        if (result.status === "fulfilled") {
          const val = result.value;
          if (f.stateKey === "unidades") {
            state.unidades = pickItems(val);
            state.unidadesTotalServidor =
              typeof val?.total === "number" ? val.total : state.unidades.length;
          } else {
            state[f.stateKey] = pickItems(val);
          }
        } else {
          const msg =
            result.reason && result.reason.message ? result.reason.message : String(result.reason);
          state.catalogRefreshErrors.push(`${f.label}: ${msg}`);
        }
      });

      state.catalogLoaded = true;
      updateCatalogRefreshBanner();

      renderStats();
      renderClientes();
      renderTransportistas();
      renderTransportistaContactos();
      renderTransportistaDocumentos();
      renderViajes();
      renderFletes();
      renderOrdenesServicio();
      renderFacturas();
      renderGastos();
      renderTarifas();
      renderTarifasCompra();
      renderOperadores();
      renderUnidades();
      renderAsignaciones();
      renderDespachos();
      populateSelects();
      refreshAllBusquedaDatalists();
      renderClienteContactos();
      flushClienteDomiciliosForSelectedClient(document.getElementById("cliente-domicilio-cliente")?.value || "");
      syncClienteCondicionForm();
      resyncFleteEditPkAfterRefresh();
      resyncDespachoEditPkAfterRefresh();
    }

    function createdEntitySuffix(data) {
      if (!data || typeof data !== "object") {
        return "";
      }
      const parts = [];
      if (data.id != null) {
        parts.push("ID " + data.id);
      }
      if (data.id_unidad != null) {
        parts.push("ID unidad " + data.id_unidad);
      }
      if (data.id_operador != null) {
        parts.push("ID operador " + data.id_operador);
      }
      if (data.id_asignacion != null) {
        parts.push("ID asignacion " + data.id_asignacion);
      }
      if (data.id_despacho != null) {
        parts.push("ID despacho " + data.id_despacho);
      }
      if (data.folio != null) {
        parts.push("folio " + data.folio);
      }
      if (parts.length === 0) {
        return "";
      }
      return " — " + parts.join(", ") + ".";
    }

    function attachSubmit(formId, messageId, builder, requestFactory, successText) {
      document.getElementById(formId).addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage(messageId);
        const form = event.currentTarget;
        try {
          const payload = builder(new FormData(form));
          const data = await requestFactory(payload);
          form.reset();
          applyMoneyFormatToForm(form);
          setMessage(messageId, successText + createdEntitySuffix(data), "ok");
          await refreshData();
        } catch (error) {
          setMessage(messageId, error.message, "error");
        }
      });
    }

    function initForms() {
      enableEnterToNextField("cliente-form");
      enableEnterToNextField("cliente-edit-form");
      wireClienteContactoEnterNavigation();
      enableEnterToNextField("cliente-contacto-edit-form");
      enableEnterToNextField("cliente-domicilio-form");
      enableEnterToNextField("cliente-domicilio-edit-form");
      enableEnterToNextField("transportista-form");
      enableEnterToNextField("transportista-edit-form");
      enableEnterToNextField("tarifa-form");
      enableEnterToNextField("tarifa-edit-form");
      enableEnterToNextField("tarifa-compra-form");
      enableEnterToNextField("tarifa-compra-edit-form");
      wireImplicitSubmitGuard("tarifa-form");
      wireImplicitSubmitGuard("tarifa-edit-form");
      wireImplicitSubmitGuard("tarifa-compra-form");
      wireImplicitSubmitGuard("tarifa-compra-edit-form");
      enableEnterToNextField("cliente-condicion-form");
      wireImplicitSubmitGuard("cliente-condicion-form");
      enableEnterToNextField("viaje-form");
      wireImplicitSubmitGuard("viaje-form");
      enableEnterToNextField("factura-form");
      wireImplicitSubmitGuard("factura-form");
      enableEnterToNextField("flete-form");
      wireImplicitSubmitGuard("flete-form");
      wireImplicitSubmitGuard("flete-edit-form");
      enableEnterToNextField("gasto-form");
      wireImplicitSubmitGuard("gasto-form");
      enableEnterToNextField("gasto-edit-form");
      wireImplicitSubmitGuard("gasto-edit-form");
      enableEnterToNextField("transportista-contacto-form");
      wireImplicitSubmitGuard("transportista-contacto-form");
      enableEnterToNextField("transportista-documento-form");
      wireImplicitSubmitGuard("transportista-documento-form");
      enableEnterToNextField("transportista-documento-edit-form");
      wireImplicitSubmitGuard("transportista-documento-edit-form");
      enableEnterToNextField("operador-form");
      wireImplicitSubmitGuard("operador-form");
      enableEnterToNextField("operador-edit-form");
      wireImplicitSubmitGuard("operador-edit-form");
      enableEnterToNextField("unidad-form");
      wireImplicitSubmitGuard("unidad-form");
      enableEnterToNextField("unidad-edit-form");
      wireImplicitSubmitGuard("unidad-edit-form");
      enableEnterToNextField("asignacion-form");
      wireImplicitSubmitGuard("asignacion-form");
      enableEnterToNextField("despacho-form");
      wireImplicitSubmitGuard("despacho-form");
      enableEnterToNextField("salida-form");
      wireImplicitSubmitGuard("salida-form");
      enableEnterToNextField("evento-form");
      wireImplicitSubmitGuard("evento-form");
      enableEnterToNextField("entrega-form");
      wireImplicitSubmitGuard("entrega-form");
      enableEnterToNextField("cierre-form");
      wireImplicitSubmitGuard("cierre-form");
      enableEnterToNextField("cancelacion-form");
      wireImplicitSubmitGuard("cancelacion-form");
      wireImplicitSubmitGuard("cliente-form");
      wireImplicitSubmitGuard("cliente-edit-form");
      wireImplicitSubmitGuard("transportista-form");
      attachSubmit("cliente-form", "cliente-message", (form) => buildClientePayload(form), (payload) => api("/clientes", { method: "POST", body: JSON.stringify(payload) }), "Cliente guardado.");

      document.getElementById("cliente-contacto-cancel-clear").addEventListener("click", () => {
        cancelClienteContactoEdit();
        clearCaptureFormFields("cliente-contacto-form");
        document.getElementById("cliente-contacto-activo").checked = true;
        clearMessage("cliente-contacto-message");
        syncClienteModuleSummaries();
        renderClienteContactos();
      });
      document.getElementById("cliente-contacto-guardar").addEventListener("click", async () => {
        clearMessage("cliente-contacto-message");
        if (!validateClienteContactoCapture()) {
          return;
        }
        try {
          const payload = buildClienteContactoPayload(clienteContactoCaptureToFormData());
          const created = await api(`/clientes/${payload.cliente_id}/contactos`, {
            method: "POST",
            body: JSON.stringify({
              nombre: payload.nombre,
              area: payload.area,
              puesto: payload.puesto,
              telefono: payload.telefono,
              extension: payload.extension,
              celular: payload.celular,
              email: payload.email,
              principal: payload.principal,
              activo: payload.activo,
            }),
          });
          const selected = String(payload.cliente_id);
          clearCaptureFormFields("cliente-contacto-form");
          document.getElementById("cliente-contacto-activo").checked = true;
          setMessage(
            "cliente-contacto-message",
            "Contacto guardado." + createdEntitySuffix(created),
            "ok",
          );
          await refreshData();
          document.getElementById("cliente-contacto-cliente").value = selected;
          cancelClienteContactoEdit();
          renderClienteContactos();
        } catch (error) {
          setMessage("cliente-contacto-message", error.message, "error");
        }
      });

      document.getElementById("cliente-domicilio-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("cliente-domicilio-message");
        const form = event.currentTarget;
        try {
          const payload = buildClienteDomicilioPayload(new FormData(form));
          const createdDom = await api(`/clientes/${payload.cliente_id}/domicilios`, {
            method: "POST",
            body: JSON.stringify({
              tipo_domicilio: payload.tipo_domicilio,
              nombre_sede: payload.nombre_sede,
              direccion_completa: payload.direccion_completa,
              municipio: payload.municipio,
              estado: payload.estado,
              codigo_postal: payload.codigo_postal,
              horario_carga: payload.horario_carga,
              horario_descarga: payload.horario_descarga,
              instrucciones_acceso: payload.instrucciones_acceso,
              activo: payload.activo,
            }),
          });
          const selected = String(payload.cliente_id);
          form.reset();
          setMessage("cliente-domicilio-message", "Domicilio guardado." + createdEntitySuffix(createdDom), "ok");
          await refreshData();
          document.getElementById("cliente-domicilio-cliente").value = selected;
          flushClienteDomiciliosForSelectedClient(selected);
        } catch (error) {
          setMessage("cliente-domicilio-message", error.message, "error");
        }
      });

      attachSubmit("cliente-condicion-form", "cliente-condicion-message", (form) => ({
        cliente_id: integerOrNull(form.get("cliente_id")),
        dias_credito: integerOrNull(form.get("dias_credito")),
        limite_credito: numberOrNull(form.get("limite_credito")),
        moneda_preferida: clean(form.get("moneda_preferida")) || "MXN",
        forma_pago: clean(form.get("forma_pago")),
        uso_cfdi: clean(form.get("uso_cfdi")),
        requiere_oc: form.get("requiere_oc") === "on",
        requiere_cita: form.get("requiere_cita") === "on",
        bloqueado_credito: form.get("bloqueado_credito") === "on",
        observaciones_credito: clean(form.get("observaciones_credito")),
      }), async (payload) => {
        if (payload.cliente_id === null || payload.cliente_id < 1) {
          throw new Error("Selecciona un cliente en la lista antes de guardar condiciones comerciales.");
        }
        return api(`/clientes/${payload.cliente_id}/condiciones-comerciales`, {
          method: "PUT",
          body: JSON.stringify({
            dias_credito: payload.dias_credito,
            limite_credito: payload.limite_credito,
            moneda_preferida: payload.moneda_preferida,
            forma_pago: payload.forma_pago,
            uso_cfdi: payload.uso_cfdi,
            requiere_oc: payload.requiere_oc,
            requiere_cita: payload.requiere_cita,
            bloqueado_credito: payload.bloqueado_credito,
            observaciones_credito: payload.observaciones_credito,
          }),
        });
      }, "Condiciones comerciales guardadas.");

      attachSubmit("transportista-form", "transportista-message", (form) => buildTransportistaPayload(form), (payload) => api("/transportistas", { method: "POST", body: JSON.stringify(payload) }), "Transportista guardado.");

      document.getElementById("transportista-contacto-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("transportista-contacto-message");
        const form = event.currentTarget;
        try {
          const payload = buildTransportistaContactoPayload(new FormData(form));
          const createdTc = await api(`/transportistas/${payload.transportista_id}/contactos`, {
            method: "POST",
            body: JSON.stringify({
              nombre: payload.nombre,
              area: payload.area,
              puesto: payload.puesto,
              telefono: payload.telefono,
              extension: payload.extension,
              celular: payload.celular,
              email: payload.email,
              principal: payload.principal,
              activo: payload.activo,
            }),
          });
          const selected = String(payload.transportista_id);
          form.reset();
          setMessage("transportista-contacto-message", "Contacto guardado." + createdEntitySuffix(createdTc), "ok");
          await refreshData();
          document.getElementById("transportista-contacto-transportista").value = selected;
          syncTransportistaModuleSelection("transportista-contacto-transportista");
        } catch (error) {
          setMessage("transportista-contacto-message", error.message, "error");
        }
      });

      document.getElementById("transportista-documento-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("transportista-documento-message");
        const form = event.currentTarget;
        try {
          const payload = buildTransportistaDocumentoPayload(new FormData(form));
          const createdTd = await api(`/transportistas/${payload.transportista_id}/documentos`, {
            method: "POST",
            body: JSON.stringify({
              tipo_documento: payload.tipo_documento,
              numero_documento: payload.numero_documento,
              fecha_emision: payload.fecha_emision,
              fecha_vencimiento: payload.fecha_vencimiento,
              archivo_url: payload.archivo_url,
              estatus: payload.estatus,
              observaciones: payload.observaciones,
            }),
          });
          const selected = String(payload.transportista_id);
          form.reset();
          setMessage("transportista-documento-message", "Documento guardado." + createdEntitySuffix(createdTd), "ok");
          await refreshData();
          document.getElementById("transportista-documento-transportista").value = selected;
          syncTransportistaModuleSelection("transportista-documento-transportista");
        } catch (error) {
          setMessage("transportista-documento-message", error.message, "error");
        }
      });

      attachSubmit("viaje-form", "viaje-message", (form) => ({
        ...buildViajePayload(form),
        fecha_llegada_real: null,
      }), (payload) => api("/viajes", { method: "POST", body: JSON.stringify(payload) }), "Viaje guardado.");

      attachSubmit("factura-form", "factura-message", (form) => buildFacturaPayload(form), (payload) => api("/facturas", { method: "POST", body: JSON.stringify(payload) }), "Factura guardada.");

      attachSubmit("flete-form", "flete-message", (form) => buildFletePayload(form), (payload) => api("/fletes", { method: "POST", body: JSON.stringify(payload) }), "Flete guardado.");

      attachSubmit("gasto-form", "gasto-message", (form) => ({
        flete_id: integerOrNull(form.get("flete_id")),
        tipo_gasto: clean(form.get("tipo_gasto")),
        monto: numberOrNull(form.get("monto")),
        fecha_gasto: normalizeDateOnlyForApi(form.get("fecha_gasto")),
        descripcion: clean(form.get("descripcion")),
        referencia: clean(form.get("referencia")),
        comprobante: clean(form.get("comprobante")),
      }), (payload) => api("/gastos-viaje", { method: "POST", body: JSON.stringify(payload) }), "Gasto guardado.");

      document.getElementById("gasto-presupuesto-generar").addEventListener("click", async () => {
        const out = document.getElementById("gasto-control-output");
        const fid = document.getElementById("gasto-control-flete").value;
        if (!fid) {
          out.textContent = "Seleccione un flete.";
          return;
        }
        out.textContent = "Generando…";
        try {
          const data = await api(`/fletes/${fid}/presupuesto-gasto/generar`, {
            method: "POST",
            body: JSON.stringify({}),
          });
          out.textContent = JSON.stringify(data, null, 2);
          await refreshData();
        } catch (error) {
          out.textContent = error.message;
        }
      });
      document.getElementById("gasto-liquidacion-ver").addEventListener("click", async () => {
        const out = document.getElementById("gasto-control-output");
        const fid = document.getElementById("gasto-control-flete").value;
        if (!fid) {
          out.textContent = "Seleccione un flete.";
          return;
        }
        out.textContent = "Cargando…";
        try {
          const data = await api(`/fletes/${fid}/liquidacion-gastos`);
          out.textContent = JSON.stringify(data, null, 2);
        } catch (error) {
          out.textContent = error.message;
        }
      });

      document.getElementById("gasto-edit-cancel").addEventListener("click", cancelGastoEdit);
      document.getElementById("gasto-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("gasto-edit-message");
        const formElement = event.currentTarget;
        try {
          const payload = {
            flete_id: integerOrNull(formElement.elements.flete_id.value),
            tipo_gasto: clean(formElement.elements.tipo_gasto.value),
            monto: numberOrNull(formElement.elements.monto.value),
            fecha_gasto: normalizeDateOnlyForApi(formElement.elements.fecha_gasto.value),
            descripcion: clean(formElement.elements.descripcion.value),
            referencia: clean(formElement.elements.referencia.value),
            comprobante: clean(formElement.elements.comprobante.value),
          };
          const id = requirePositiveIntOrThrow(formElement.elements.id.value, "Gasto");
          await api(`/gastos-viaje/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("gasto-edit-message", "Gasto actualizado.", "ok");
          cancelGastoEdit();
          await refreshData();
        } catch (error) {
          setMessage("gasto-edit-message", error.message, "error");
        }
      });

      attachSubmit(
        "tarifa-form",
        "tarifa-message",
        (form) => {
          const nombre = clean(new FormData(form).get("nombre_tarifa"));
          if (findActiveTarifaVentaNombreDuplicado(nombre, null)) {
            throw new Error(TARIFA_VENTA_NOMBRE_DUPLICADO_MSG);
          }
          return buildTarifaFleteVentaPayload(form);
        },
        (payload) => api("/tarifas-flete", { method: "POST", body: JSON.stringify(payload) }),
        "Tarifa guardada."
      );

      document.getElementById("tarifa-edit-cancel").addEventListener("click", cancelTarifaFleteEdit);
      document.getElementById("tarifa-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("tarifa-edit-message");
        const formElement = event.currentTarget;
        try {
          const id = requirePositiveIntOrThrow(formElement.elements.id.value, "Tarifa de venta");
          const nombre = clean(formElement.elements.nombre_tarifa.value);
          if (findActiveTarifaVentaNombreDuplicado(nombre, id)) {
            throw new Error(TARIFA_VENTA_NOMBRE_DUPLICADO_MSG);
          }
          const payload = buildTarifaFleteVentaPayload(new FormData(formElement));
          await api(`/tarifas-flete/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("tarifa-edit-message", "Tarifa actualizada.", "ok");
          cancelTarifaFleteEdit();
          await refreshData();
        } catch (error) {
          setMessage("tarifa-edit-message", error.message, "error");
        }
      });

      attachSubmit("tarifa-compra-form", "tarifa-compra-message", (form) => buildTarifaCompraPayload(form), (payload) => api("/tarifas-compra-transportista", { method: "POST", body: JSON.stringify(payload) }), "Tarifa de compra guardada.");

      attachSubmit(
        "operador-form",
        "operador-message",
        (form) => buildOperadorPayload(form),
        (payload) => api("/operadores", { method: "POST", body: JSON.stringify(payload) }),
        "Operador guardado.",
      );

      document.getElementById("operador-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("operador-edit-message");
        const form = event.currentTarget;
        try {
          const id = requirePositiveIntOrThrow(form.elements.id_operador.value, "Operador");
          const payload = buildOperadorPayload(new FormData(form));
          await api(`/operadores/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("operador-edit-message", "Operador actualizado.", "ok");
          cancelOperadorEdit();
          await refreshData();
        } catch (error) {
          setMessage("operador-edit-message", error.message, "error");
        }
      });
      document.getElementById("operador-edit-cancel").addEventListener("click", cancelOperadorEdit);

      attachSubmit(
        "unidad-form",
        "unidad-message",
        (formData) => buildUnidadPayload(formData),
        (payload) => api("/unidades", { method: "POST", body: JSON.stringify(payload) }),
        "Unidad guardada.",
      );

      document.getElementById("unidad-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("unidad-edit-message");
        const form = event.currentTarget;
        try {
          const id = requirePositiveIntOrThrow(form.elements.id_unidad.value, "Unidad");
          const payload = buildUnidadPayload(new FormData(form));
          await api(`/unidades/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("unidad-edit-message", "Unidad actualizada.", "ok");
          cancelUnidadEdit();
          await refreshData();
        } catch (error) {
          setMessage("unidad-edit-message", error.message, "error");
        }
      });
      document.getElementById("unidad-edit-cancel").addEventListener("click", cancelUnidadEdit);

      attachSubmit("asignacion-form", "asignacion-message", (form) => buildAsignacionPayload(form), (payload) => api("/asignaciones", { method: "POST", body: JSON.stringify(payload) }), "Asignacion guardada.");

      attachSubmit("despacho-form", "despacho-message", (form) => ({
        id_asignacion: integerOrNull(form.get("id_asignacion")),
        id_flete: integerOrNull(form.get("id_flete")),
        salida_programada: normalizeDateTimeForApi(form.get("salida_programada")),
        observaciones_transito: clean(form.get("observaciones_transito")),
      }), (payload) => api("/despachos", { method: "POST", body: JSON.stringify(payload) }), "Despacho guardado.");

      document.getElementById("salida-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("salida-message");
        const form = event.currentTarget;
        try {
          const fd = new FormData(form);
          const payload = {
            id_despacho: integerOrNull(fd.get("id_despacho")),
            salida_real: normalizeDateTimeForApi(fd.get("salida_real")),
            km_salida: numberOrNull(fd.get("km_salida")),
            observaciones_salida: clean(fd.get("observaciones_salida")),
          };
          const omitir = fd.get("omitir_validacion_cumplimiento") === "on";
          const q = omitir ? "?omitir_validacion_cumplimiento=true" : "";
          const response = await fetch(`${API_BASE}/despachos/${payload.id_despacho}/salida${q}`, {
            method: "POST",
            headers: {
              "Accept": "application/json",
              "Content-Type": "application/json",
              "X-API-Key": API_KEY,
            },
            body: JSON.stringify({
              salida_real: payload.salida_real,
              km_salida: payload.km_salida,
              observaciones_salida: payload.observaciones_salida,
            }),
          });
          const data = await response.json().catch(() => ({}));
          if (!response.ok) {
            if (response.status === 422 && data.detail && data.detail.tipo === "cumplimiento_documental") {
              const bloqueos = (data.detail.bloqueos || []).join("\\n• ");
              const adv = (data.detail.advertencias || []).length
                ? "\\n\\nAdvertencias:\\n• " + (data.detail.advertencias || []).join("\\n• ")
                : "";
              setMessage(
                "salida-message",
                (data.detail.mensaje || "La validación documental no autoriza la salida.") +
                  (bloqueos ? "\\n\\nPendientes:\\n• " + bloqueos : "") +
                  adv +
                  "\\n\\nSi debe salir igual, marque la casilla de confirmación abajo y vuelva a guardar.",
                "error"
              );
              return;
            }
            let detail = `HTTP ${response.status}`;
            if (typeof data.detail === "string") {
              detail = data.detail;
            } else if (data.detail) {
              detail = JSON.stringify(data.detail);
            }
            throw new Error(detail);
          }
          form.reset();
          setMessage("salida-message", "Salida registrada.", "ok");
          await refreshData();
        } catch (error) {
          setMessage("salida-message", error.message, "error");
        }
      });

      attachSubmit("evento-form", "evento-message", (form) => ({
        id_despacho: integerOrNull(form.get("id_despacho")),
        tipo_evento: clean(form.get("tipo_evento")),
        fecha_evento: normalizeDateTimeForApi(form.get("fecha_evento")),
        ubicacion: clean(form.get("ubicacion")),
        descripcion: clean(form.get("descripcion")),
        latitud: numberOrNull(form.get("latitud")),
        longitud: numberOrNull(form.get("longitud")),
      }), (payload) => api(`/despachos/${payload.id_despacho}/eventos`, {
        method: "POST",
        body: JSON.stringify({
          tipo_evento: payload.tipo_evento,
          fecha_evento: payload.fecha_evento,
          ubicacion: payload.ubicacion,
          descripcion: payload.descripcion,
          latitud: payload.latitud,
          longitud: payload.longitud,
        }),
      }), "Evento guardado.");

      attachSubmit("entrega-form", "entrega-message", (form) => ({
        id_despacho: integerOrNull(form.get("id_despacho")),
        fecha_entrega: normalizeDateTimeForApi(form.get("fecha_entrega")),
        evidencia_entrega: clean(form.get("evidencia_entrega")),
        firma_recibe: clean(form.get("firma_recibe")),
        observaciones_entrega: clean(form.get("observaciones_entrega")),
      }), (payload) => api(`/despachos/${payload.id_despacho}/entrega`, {
        method: "POST",
        body: JSON.stringify({
          fecha_entrega: payload.fecha_entrega,
          evidencia_entrega: payload.evidencia_entrega,
          firma_recibe: payload.firma_recibe,
          observaciones_entrega: payload.observaciones_entrega,
        }),
      }), "Entrega registrada.");

      attachSubmit("cierre-form", "cierre-message", (form) => ({
        id_despacho: integerOrNull(form.get("id_despacho")),
        llegada_real: normalizeDateTimeForApi(form.get("llegada_real")),
        km_llegada: numberOrNull(form.get("km_llegada")),
        observaciones_cierre: clean(form.get("observaciones_cierre")),
      }), (payload) => api(`/despachos/${payload.id_despacho}/cerrar`, {
        method: "POST",
        body: JSON.stringify({
          llegada_real: payload.llegada_real,
          km_llegada: payload.km_llegada,
          observaciones_cierre: payload.observaciones_cierre,
        }),
      }), "Despacho cerrado.");

      attachSubmit("cancelacion-form", "cancelacion-message", (form) => ({
        id_despacho: integerOrNull(form.get("id_despacho")),
        motivo_cancelacion: clean(form.get("motivo_cancelacion")),
      }), (payload) => api(`/despachos/${payload.id_despacho}/cancelar`, {
        method: "POST",
        body: JSON.stringify({
          motivo_cancelacion: payload.motivo_cancelacion,
        }),
      }), "Despacho cancelado.");
    }

    function initFilters() {
      try {
        const m = sessionStorage.getItem("SIFE_buscar_modo");
        if (m === "contiene" || m === "prefijo_palabras" || m === "todas_palabras") {
          uiState.buscarModo = m;
        }
      } catch (_) {
        /* ignore */
      }
      document.querySelectorAll(".buscar-modo-sync").forEach((el) => {
        el.value = uiState.buscarModo;
      });
      document.addEventListener("change", (e) => {
        const t = e.target;
        if (!t || !t.classList.contains("buscar-modo-sync")) {
          return;
        }
        uiState.buscarModo = t.value;
        try {
          sessionStorage.setItem("SIFE_buscar_modo", t.value);
        } catch (_) {
          /* ignore */
        }
        document.querySelectorAll(".buscar-modo-sync").forEach((x) => {
          if (x !== t) {
            x.value = t.value;
          }
        });
        refreshAllConsultaTables();
      });

      const applyClienteFilter = () => {
        const formNode = document.getElementById("cliente-filter-form");
        const form = new FormData(formNode);
        uiState.clienteFilters.buscar = clean(form.get("buscar")) || "";
        uiState.clienteFilters.activo = clean(form.get("activo")) || "";
        renderClientes();
        refreshBusquedaDatalist("cliente-filter-buscar");
        openSingleClienteFromFilter();
      };

      document.getElementById("cliente-filter-form").addEventListener("submit", (event) => {
        event.preventDefault();
        applyClienteFilter();
      });
      document.getElementById("cliente-filter-buscar").addEventListener("input", () => {
        applyClienteFilter();
      });
      document.getElementById("cliente-filter-activo").addEventListener("change", () => {
        applyClienteFilter();
      });
      document.getElementById("cliente-filter-clear").addEventListener("click", () => {
        document.getElementById("cliente-filter-form").reset();
        uiState.clienteFilters = { buscar: "", activo: "" };
        renderClientes();
        cancelClienteEdit();
      });

      const applyFleteFilter = () => {
        const formNode = document.getElementById("flete-filter-form");
        const form = new FormData(formNode);
        uiState.fleteFilters.buscar = clean(form.get("buscar")) || "";
        uiState.fleteFilters.estado = clean(form.get("estado")) || "";
        uiState.fleteFilters.cliente_id = clean(form.get("cliente_id")) || "";
        uiState.fleteFilters.transportista_id = clean(form.get("transportista_id")) || "";
        renderFletes();
        refreshBusquedaDatalist("flete-filter-buscar");
      };
      document.getElementById("flete-filter-form").addEventListener("submit", (event) => {
        event.preventDefault();
        applyFleteFilter();
      });
      document.getElementById("flete-filter-buscar").addEventListener("input", () => {
        applyFleteFilter();
      });
      document.getElementById("flete-filter-clear").addEventListener("click", () => {
        document.getElementById("flete-filter-form").reset();
        uiState.fleteFilters = { buscar: "", estado: "", cliente_id: "", transportista_id: "" };
        renderFletes();
      });

      const applyDespachoFilter = () => {
        const formNode = document.getElementById("despacho-filter-form");
        const form = new FormData(formNode);
        uiState.despachoFilters.buscar = clean(form.get("buscar")) || "";
        uiState.despachoFilters.estatus = clean(form.get("estatus")) || "";
        uiState.despachoFilters.id_asignacion = clean(form.get("id_asignacion")) || "";
        uiState.despachoFilters.id_flete = clean(form.get("id_flete")) || "";
        renderDespachos();
        refreshBusquedaDatalist("despacho-filter-buscar");
      };
      document.getElementById("despacho-filter-form").addEventListener("submit", (event) => {
        event.preventDefault();
        applyDespachoFilter();
      });
      document.getElementById("despacho-filter-buscar").addEventListener("input", () => {
        applyDespachoFilter();
      });
      document.getElementById("despacho-filter-clear").addEventListener("click", () => {
        document.getElementById("despacho-filter-form").reset();
        uiState.despachoFilters = { buscar: "", estatus: "", id_asignacion: "", id_flete: "" };
        renderDespachos();
        cancelDespachoEdit();
      });

      const applyTransportistaFilter = () => {
        const formNode = document.getElementById("transportista-filter-form");
        const form = new FormData(formNode);
        uiState.transportistaFilters.buscar = clean(form.get("buscar")) || "";
        uiState.transportistaFilters.estatus = clean(form.get("estatus")) || "";
        uiState.transportistaFilters.tipo_transportista = clean(form.get("tipo_transportista")) || "";
        renderTransportistas();
        refreshBusquedaDatalist("transportista-filter-buscar");
        openSingleTransportistaFromFilter();
      };

      document.getElementById("transportista-filter-form").addEventListener("submit", (event) => {
        event.preventDefault();
        applyTransportistaFilter();
      });
      document.getElementById("transportista-filter-buscar").addEventListener("input", () => {
        applyTransportistaFilter();
      });
      document.getElementById("transportista-filter-estatus").addEventListener("change", () => {
        applyTransportistaFilter();
      });
      document.getElementById("transportista-filter-tipo").addEventListener("change", () => {
        applyTransportistaFilter();
      });
      document.getElementById("transportista-filter-clear").addEventListener("click", () => {
        document.getElementById("transportista-filter-form").reset();
        uiState.transportistaFilters = { buscar: "", estatus: "", tipo_transportista: "" };
        renderTransportistas();
        cancelTransportistaEdit();
      });

      const applyViajeFilter = () => {
        const formNode = document.getElementById("viaje-filter-form");
        const form = new FormData(formNode);
        uiState.viajeFilters.buscar = clean(form.get("buscar")) || "";
        uiState.viajeFilters.estado = clean(form.get("estado")) || "";
        renderViajes();
        refreshBusquedaDatalist("viaje-filter-buscar");
      };
      document.getElementById("viaje-filter-form").addEventListener("submit", (event) => {
        event.preventDefault();
        applyViajeFilter();
      });
      document.getElementById("viaje-filter-buscar").addEventListener("input", () => {
        applyViajeFilter();
      });
      document.getElementById("viaje-filter-clear").addEventListener("click", () => {
        document.getElementById("viaje-filter-form").reset();
        uiState.viajeFilters = { buscar: "", estado: "" };
        renderViajes();
        cancelViajeEdit();
      });

      const applyFacturaFilter = () => {
        const formNode = document.getElementById("factura-filter-form");
        const form = new FormData(formNode);
        uiState.facturaFilters.buscar = clean(form.get("buscar")) || "";
        uiState.facturaFilters.cliente_id = clean(form.get("cliente_id")) || "";
        uiState.facturaFilters.estatus = clean(form.get("estatus")) || "";
        renderFacturas();
        refreshBusquedaDatalist("factura-filter-buscar");
      };
      document.getElementById("factura-filter-form").addEventListener("submit", (event) => {
        event.preventDefault();
        applyFacturaFilter();
      });
      document.getElementById("factura-filter-buscar").addEventListener("input", () => {
        applyFacturaFilter();
      });
      document.getElementById("factura-filter-cliente").addEventListener("change", () => {
        applyFacturaFilter();
      });
      document.getElementById("factura-filter-estatus").addEventListener("change", () => {
        applyFacturaFilter();
      });
      document.getElementById("factura-filter-clear").addEventListener("click", () => {
        document.getElementById("factura-filter-form").reset();
        uiState.facturaFilters = { buscar: "", cliente_id: "", estatus: "" };
        renderFacturas();
        cancelFacturaEdit();
      });

      const applyOrdenServicioFilter = () => {
        const formNode = document.getElementById("orden-servicio-filter-form");
        if (!formNode) {
          return;
        }
        const form = new FormData(formNode);
        uiState.ordenServicioFilters.buscar = clean(form.get("buscar")) || "";
        uiState.ordenServicioFilters.cliente_id = clean(form.get("cliente_id")) || "";
        uiState.ordenServicioFilters.estatus = clean(form.get("estatus")) || "";
        renderOrdenesServicio();
        hideOrdenServicioDetail();
      };
      const ordenServicioFilterForm = document.getElementById("orden-servicio-filter-form");
      if (ordenServicioFilterForm) {
        ordenServicioFilterForm.addEventListener("submit", (event) => {
          event.preventDefault();
          applyOrdenServicioFilter();
        });
        document.getElementById("orden-servicio-filter-buscar")?.addEventListener("input", () => {
          applyOrdenServicioFilter();
        });
        document.getElementById("orden-servicio-filter-cliente")?.addEventListener("change", () => {
          applyOrdenServicioFilter();
        });
        document.getElementById("orden-servicio-filter-estatus")?.addEventListener("change", () => {
          applyOrdenServicioFilter();
        });
        document.getElementById("orden-servicio-filter-clear")?.addEventListener("click", () => {
          ordenServicioFilterForm.reset();
          uiState.ordenServicioFilters = { buscar: "", cliente_id: "", estatus: "" };
          renderOrdenesServicio();
          hideOrdenServicioDetail();
        });
        document.getElementById("orden-servicio-detail-close")?.addEventListener("click", () => {
          hideOrdenServicioDetail();
        });
      }

      const applyTarifaCompraFilter = () => {
        const formNode = document.getElementById("tarifa-compra-filter-form");
        const form = new FormData(formNode);
        uiState.tarifaCompraFilters.buscar = clean(form.get("buscar")) || "";
        uiState.tarifaCompraFilters.transportista_id = clean(form.get("transportista_id")) || "";
        uiState.tarifaCompraFilters.activo = clean(form.get("activo")) || "";
        renderTarifasCompra();
        refreshBusquedaDatalist("tarifa-compra-filter-buscar");
      };
      document.getElementById("tarifa-compra-filter-form").addEventListener("submit", (event) => {
        event.preventDefault();
        applyTarifaCompraFilter();
      });
      document.getElementById("tarifa-compra-filter-buscar").addEventListener("input", () => {
        applyTarifaCompraFilter();
      });
      document.getElementById("tarifa-compra-filter-transportista").addEventListener("change", () => {
        applyTarifaCompraFilter();
      });
      document.getElementById("tarifa-compra-filter-activo").addEventListener("change", () => {
        applyTarifaCompraFilter();
      });
      document.getElementById("tarifa-compra-filter-clear").addEventListener("click", () => {
        document.getElementById("tarifa-compra-filter-form").reset();
        uiState.tarifaCompraFilters = { buscar: "", transportista_id: "", activo: "" };
        renderTarifasCompra();
        cancelTarifaCompraEdit();
      });

      const applyAsignacionFilter = () => {
        const formNode = document.getElementById("asignacion-filter-form");
        const form = new FormData(formNode);
        uiState.asignacionFilters.buscar = clean(form.get("buscar")) || "";
        uiState.asignacionFilters.id_operador = clean(form.get("id_operador")) || "";
        uiState.asignacionFilters.id_unidad = clean(form.get("id_unidad")) || "";
        uiState.asignacionFilters.id_viaje = clean(form.get("id_viaje")) || "";
        renderAsignaciones();
        refreshBusquedaDatalist("asignacion-filter-buscar");
      };
      document.getElementById("asignacion-filter-form").addEventListener("submit", (event) => {
        event.preventDefault();
        applyAsignacionFilter();
      });
      document.getElementById("asignacion-filter-buscar").addEventListener("input", () => {
        applyAsignacionFilter();
      });
      document.getElementById("asignacion-filter-clear").addEventListener("click", () => {
        document.getElementById("asignacion-filter-form").reset();
        uiState.asignacionFilters = { buscar: "", id_operador: "", id_unidad: "", id_viaje: "" };
        renderAsignaciones();
        cancelAsignacionEdit();
      });

      document.getElementById("tarifa-venta-filter-buscar").addEventListener("input", (event) => {
        uiState.tarifaVentaFilters.buscar = clean(event.target.value) || "";
        renderTarifas();
        refreshBusquedaDatalist("tarifa-venta-filter-buscar");
      });
      document.getElementById("gasto-filter-buscar").addEventListener("input", (event) => {
        uiState.gastoFilters.buscar = clean(event.target.value) || "";
        renderGastos();
        refreshBusquedaDatalist("gasto-filter-buscar");
      });
      document.getElementById("operador-filter-buscar").addEventListener("input", (event) => {
        uiState.operadorFilters.buscar = clean(event.target.value) || "";
        renderOperadores();
        refreshBusquedaDatalist("operador-filter-buscar");
      });
      document.getElementById("operador-filter-clear").addEventListener("click", () => {
        uiState.operadorFilters.buscar = "";
        const inp = document.getElementById("operador-filter-buscar");
        if (inp) {
          inp.value = "";
        }
        renderOperadores();
        refreshBusquedaDatalist("operador-filter-buscar");
      });
      document.getElementById("unidad-filter-buscar").addEventListener("input", (event) => {
        uiState.unidadFilters.buscar = clean(event.target.value) || "";
        renderUnidades();
        refreshBusquedaDatalist("unidad-filter-buscar");
      });
      document.getElementById("unidad-filter-tipo-propiedad").addEventListener("change", (event) => {
        uiState.unidadFilters.tipo_propiedad = clean(event.target.value) || "";
        renderUnidades();
      });
      document.getElementById("unidad-filter-estatus-doc").addEventListener("change", (event) => {
        uiState.unidadFilters.estatus_documental = clean(event.target.value) || "";
        renderUnidades();
      });
      document.getElementById("unidad-filter-activo").addEventListener("change", (event) => {
        uiState.unidadFilters.activo = clean(event.target.value) || "";
        renderUnidades();
      });
      document.getElementById("unidad-filter-clear").addEventListener("click", () => {
        uiState.unidadFilters = { buscar: "", tipo_propiedad: "", estatus_documental: "", activo: "" };
        uiState.buscarModo = "contiene";
        try {
          sessionStorage.setItem("SIFE_buscar_modo", "contiene");
        } catch (_) {
          /* ignore */
        }
        document.querySelectorAll(".buscar-modo-sync").forEach((el) => {
          el.value = "contiene";
        });
        const ub = document.getElementById("unidad-filter-buscar");
        if (ub) {
          ub.value = "";
        }
        document.getElementById("unidad-filter-tipo-propiedad").value = "";
        document.getElementById("unidad-filter-estatus-doc").value = "";
        document.getElementById("unidad-filter-activo").value = "";
        clearMessage("unidad-consulta-message");
        refreshAllConsultaTables();
        refreshBusquedaDatalist("unidad-filter-buscar");
      });
      document.getElementById("unidad-recargar-catalogo").addEventListener("click", async () => {
        clearMessage("unidad-consulta-message");
        try {
          await refreshData();
          const t = state.unidadesTotalServidor;
          const n = state.unidades.length;
          const uErr = unidadesEndpointFailed();
          let hint = "";
          if (uErr) {
            hint =
              " No se pudieron leer unidades desde la API (vea el aviso amarillo arriba). El total mostrado puede no ser fiable hasta que la peticion funcione.";
          } else if (t === 0) {
            hint =
              " No hay filas en la tabla unidades de MySQL en esta conexion: cree al menos una en Nueva unidad (economico obligatorio) o ejecute un script de demo si lo tiene.";
          }
          const tDisp = t == null ? "?" : t;
          setMessage(
            "unidad-consulta-message",
            `Catalogo actualizado: total en servidor = ${tDisp} (${n} cargadas en el panel, limite 500).` + hint,
            uErr ? "error" : "ok",
          );
        } catch (error) {
          setMessage("unidad-consulta-message", error.message || "No se pudo recargar el catalogo.", "error");
        }
      });
    }

    function initClienteModule() {
      const contactoSelect = document.getElementById("cliente-contacto-cliente");
      const domicilioSelect = document.getElementById("cliente-domicilio-cliente");
      const condicionSelect = document.getElementById("cliente-condicion-cliente");
      const clienteTabButtons = document.querySelectorAll("[data-cliente-tab]");

      for (const button of clienteTabButtons) {
        button.addEventListener("click", () => {
          setClienteSubpage(button.dataset.clienteTab);
        });
      }

      const manualToc = document.getElementById("manual-clientes-toc");
      if (manualToc) {
        manualToc.addEventListener("click", (event) => {
          const link = event.target.closest("a[href^='#manual-clientes-']");
          if (!link) {
            return;
          }
          event.preventDefault();
          const id = link.getAttribute("href").slice(1);
          const target = document.getElementById(id);
          if (target) {
            target.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        });
      }

      const clienteOpenManualBtn = document.getElementById("cliente-open-manual-btn");
      if (clienteOpenManualBtn) {
        clienteOpenManualBtn.addEventListener("click", () => setClienteSubpage("manual"));
      }

      if (contactoSelect) {
        contactoSelect.addEventListener("change", () => syncClienteModuleSelection("cliente-contacto-cliente"));
      }
      if (domicilioSelect) {
        domicilioSelect.addEventListener("change", () => syncClienteModuleSelection("cliente-domicilio-cliente"));
      }
      const domicilioBuscar = document.getElementById("cliente-domicilio-buscar");
      if (domicilioBuscar) {
        domicilioBuscar.addEventListener("input", () => {
          const sel = document.getElementById("cliente-domicilio-cliente");
          fillClienteDomicilioSelect(domicilioBuscar.value, sel ? sel.value : null);
          syncClienteModuleSummaries();
          renderClienteDomicilios();
        });
      }
      if (condicionSelect) {
        condicionSelect.addEventListener("change", () => syncClienteModuleSelection("cliente-condicion-cliente"));
      }

      const clienteEditOpenContactos = document.getElementById("cliente-edit-open-contactos");
      if (clienteEditOpenContactos) {
        clienteEditOpenContactos.addEventListener("click", () => {
          const id = uiState.editing.clienteId;
          if (!id) {
            return;
          }
          const sel = document.getElementById("cliente-contacto-cliente");
          if (sel) {
            sel.value = String(id);
          }
          syncClienteModuleSelection("cliente-contacto-cliente");
          const contactoPanel = document.querySelector("[data-cliente-tab-panel='contactos']");
          if (contactoPanel) {
            contactoPanel.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        });
      }

      const clienteEditOpenDomicilios = document.getElementById("cliente-edit-open-domicilios");
      if (clienteEditOpenDomicilios) {
        clienteEditOpenDomicilios.addEventListener("click", () => {
          const id = uiState.editing.clienteId;
          if (!id) {
            return;
          }
          const sel = document.getElementById("cliente-domicilio-cliente");
          if (sel) {
            sel.value = String(id);
          }
          syncClienteModuleSelection("cliente-domicilio-cliente");
          const domPanel = document.querySelector("[data-cliente-tab-panel='domicilios']");
          if (domPanel) {
            domPanel.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        });
      }

      setClienteSubpage(uiState.clienteSubpage);
      syncClienteModuleSummaries();

      document.getElementById("cliente-contacto-edit-cancel").addEventListener("click", cancelClienteContactoEdit);
      const contactoEditBuscar = document.getElementById("cliente-contacto-edit-buscar");
      if (contactoEditBuscar) {
        contactoEditBuscar.addEventListener("input", () => {
          const sel = document.getElementById("cliente-contacto-edit-cliente");
          const cur = sel?.value || "";
          fillClienteContactoEditSelect(contactoEditBuscar.value, cur || null);
        });
      }
      document.getElementById("cliente-domicilio-edit-cancel").addEventListener("click", cancelClienteDomicilioEdit);

      const clienteContactoEditForm = document.getElementById("cliente-contacto-edit-form");
      clienteContactoEditForm.addEventListener("submit", (event) => event.preventDefault());
      document.getElementById("cliente-contacto-edit-guardar").addEventListener("click", async () => {
        clearMessage("cliente-contacto-edit-message");
        const form = clienteContactoEditForm;
        if (!form.reportValidity()) {
          return;
        }
        try {
          const contactoId = requirePositiveIntOrThrow(form.elements.id.value, "Contacto del cliente");
          const pathClienteId = requirePositiveIntOrThrow(
            document.getElementById("cliente-contacto-path-cliente").value,
            "Cliente",
          );
          const payload = buildClienteContactoPayload(new FormData(form));
          const patchBody = {
            nombre: payload.nombre,
            area: payload.area,
            puesto: payload.puesto,
            telefono: payload.telefono,
            extension: payload.extension,
            celular: payload.celular,
            email: payload.email,
            principal: payload.principal,
            activo: payload.activo,
          };
          if (payload.cliente_id !== pathClienteId) {
            patchBody.cliente_id = payload.cliente_id;
          }
          await api(`/clientes/${pathClienteId}/contactos/${contactoId}`, {
            method: "PATCH",
            body: JSON.stringify(patchBody),
          });
          setMessage("cliente-contacto-edit-message", "Contacto actualizado.", "ok");
          cancelClienteContactoEdit();
          await refreshData();
          document.getElementById("cliente-contacto-cliente").value = String(payload.cliente_id);
          renderClienteContactos();
        } catch (error) {
          setMessage("cliente-contacto-edit-message", error.message, "error");
        }
      });

      document.getElementById("cliente-domicilio-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("cliente-domicilio-edit-message");
        const form = event.currentTarget;
        try {
          const domicilioId = requirePositiveIntOrThrow(form.elements.id.value, "Domicilio");
          const clienteId = requirePositiveIntOrThrow(form.elements.cliente_id.value, "Cliente");
          const payload = buildClienteDomicilioPayload(new FormData(form));
          await api(`/clientes/${clienteId}/domicilios/${domicilioId}`, {
            method: "PATCH",
            body: JSON.stringify({
              tipo_domicilio: payload.tipo_domicilio,
              nombre_sede: payload.nombre_sede,
              direccion_completa: payload.direccion_completa,
              municipio: payload.municipio,
              estado: payload.estado,
              codigo_postal: payload.codigo_postal,
              horario_carga: payload.horario_carga,
              horario_descarga: payload.horario_descarga,
              instrucciones_acceso: payload.instrucciones_acceso,
              activo: payload.activo,
            }),
          });
          setMessage("cliente-domicilio-edit-message", "Domicilio actualizado.", "ok");
          cancelClienteDomicilioEdit();
          await refreshData();
          document.getElementById("cliente-domicilio-cliente").value = String(clienteId);
          flushClienteDomiciliosForSelectedClient(String(clienteId));
        } catch (error) {
          setMessage("cliente-domicilio-edit-message", error.message, "error");
        }
      });
    }

    function initTransportistaModule() {
      const contactoSelect = document.getElementById("transportista-contacto-transportista");
      const documentoSelect = document.getElementById("transportista-documento-transportista");
      const transportistaTabButtons = document.querySelectorAll("[data-transportista-tab]");

      for (const button of transportistaTabButtons) {
        button.addEventListener("click", () => {
          setTransportistaSubpage(button.dataset.transportistaTab);
        });
      }

      const manualTransportistasToc = document.getElementById("manual-transportistas-toc");
      if (manualTransportistasToc) {
        manualTransportistasToc.addEventListener("click", (event) => {
          const link = event.target.closest("a[href^='#manual-transportistas-']");
          if (!link) {
            return;
          }
          event.preventDefault();
          const id = link.getAttribute("href").slice(1);
          const target = document.getElementById(id);
          if (target) {
            target.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        });
      }

      const transportistaOpenManualBtn = document.getElementById("transportista-open-manual-btn");
      if (transportistaOpenManualBtn) {
        transportistaOpenManualBtn.addEventListener("click", () => setTransportistaSubpage("manual"));
      }

      if (contactoSelect) {
        contactoSelect.addEventListener("change", () => syncTransportistaModuleSelection("transportista-contacto-transportista"));
      }
      if (documentoSelect) {
        documentoSelect.addEventListener("change", () => syncTransportistaModuleSelection("transportista-documento-transportista"));
      }

      setTransportistaSubpage(uiState.transportistaSubpage);

      document.getElementById("transportista-edit-cancel").addEventListener("click", cancelTransportistaEdit);
      document.getElementById("transportista-contacto-edit-cancel").addEventListener("click", cancelTransportistaContactoEdit);
      document.getElementById("transportista-documento-edit-cancel").addEventListener("click", cancelTransportistaDocumentoEdit);

      document.getElementById("transportista-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("transportista-edit-message");
        const form = event.currentTarget;
        try {
          const id = requirePositiveIntOrThrow(form.elements.id.value, "Transportista");
          const payload = buildTransportistaPayload(new FormData(form));
          await api(`/transportistas/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("transportista-edit-message", "Transportista actualizado.", "ok");
          cancelTransportistaEdit();
          await refreshData();
        } catch (error) {
          setMessage("transportista-edit-message", error.message, "error");
        }
      });

      document.getElementById("transportista-contacto-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("transportista-contacto-edit-message");
        const form = event.currentTarget;
        try {
          const contactoId = requirePositiveIntOrThrow(form.elements.id.value, "Contacto del transportista");
          const transportistaId = requirePositiveIntOrThrow(form.elements.transportista_id.value, "Transportista");
          const payload = buildTransportistaContactoPayload(new FormData(form));
          await api(`/transportistas/${transportistaId}/contactos/${contactoId}`, {
            method: "PATCH",
            body: JSON.stringify({
              nombre: payload.nombre,
              area: payload.area,
              puesto: payload.puesto,
              telefono: payload.telefono,
              extension: payload.extension,
              celular: payload.celular,
              email: payload.email,
              principal: payload.principal,
              activo: payload.activo,
            }),
          });
          setMessage("transportista-contacto-edit-message", "Contacto actualizado.", "ok");
          cancelTransportistaContactoEdit();
          await refreshData();
          document.getElementById("transportista-contacto-transportista").value = String(transportistaId);
          syncTransportistaModuleSelection("transportista-contacto-transportista");
        } catch (error) {
          setMessage("transportista-contacto-edit-message", error.message, "error");
        }
      });

      document.getElementById("transportista-documento-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("transportista-documento-edit-message");
        const form = event.currentTarget;
        try {
          const documentoId = requirePositiveIntOrThrow(form.elements.id.value, "Documento del transportista");
          const transportistaId = requirePositiveIntOrThrow(form.elements.transportista_id.value, "Transportista");
          const payload = buildTransportistaDocumentoPayload(new FormData(form));
          await api(`/transportistas/${transportistaId}/documentos/${documentoId}`, {
            method: "PATCH",
            body: JSON.stringify({
              tipo_documento: payload.tipo_documento,
              numero_documento: payload.numero_documento,
              fecha_emision: payload.fecha_emision,
              fecha_vencimiento: payload.fecha_vencimiento,
              archivo_url: payload.archivo_url,
              estatus: payload.estatus,
              observaciones: payload.observaciones,
            }),
          });
          setMessage("transportista-documento-edit-message", "Documento actualizado.", "ok");
          cancelTransportistaDocumentoEdit();
          await refreshData();
          document.getElementById("transportista-documento-transportista").value = String(transportistaId);
          syncTransportistaModuleSelection("transportista-documento-transportista");
        } catch (error) {
          setMessage("transportista-documento-edit-message", error.message, "error");
        }
      });
    }

    function initEditors() {
      document.getElementById("cliente-edit-cancel").addEventListener("click", cancelClienteEdit);
      document.getElementById("cliente-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("cliente-edit-message");
        const formElement = event.currentTarget;
        try {
          const payload = buildClientePayload(new FormData(formElement));
          const id = requirePositiveIntOrThrow(formElement.elements.id.value, "Cliente");
          await api(`/clientes/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("cliente-edit-message", "Cliente actualizado.", "ok");
          cancelClienteEdit();
          await refreshData();
        } catch (error) {
          setMessage("cliente-edit-message", error.message, "error");
        }
      });

      document.getElementById("viaje-edit-cancel").addEventListener("click", cancelViajeEdit);
      document.getElementById("viaje-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("viaje-edit-message");
        const formElement = event.currentTarget;
        try {
          const payload = buildViajePayload(new FormData(formElement));
          const id = requirePositiveIntOrThrow(formElement.elements.id.value, "Viaje");
          await api(`/viajes/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("viaje-edit-message", "Viaje actualizado.", "ok");
          cancelViajeEdit();
          await refreshData();
        } catch (error) {
          setMessage("viaje-edit-message", error.message, "error");
        }
      });

      document.getElementById("factura-edit-cancel").addEventListener("click", cancelFacturaEdit);
      document.getElementById("factura-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("factura-edit-message");
        const formElement = event.currentTarget;
        try {
          const payload = buildFacturaPayload(new FormData(formElement));
          const id = requirePositiveIntOrThrow(formElement.elements.id.value, "Factura");
          await api(`/facturas/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("factura-edit-message", "Factura actualizada.", "ok");
          cancelFacturaEdit();
          await refreshData();
        } catch (error) {
          setMessage("factura-edit-message", error.message, "error");
        }
      });

      document.getElementById("tarifa-compra-edit-cancel").addEventListener("click", cancelTarifaCompraEdit);
      document.getElementById("tarifa-compra-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("tarifa-compra-edit-message");
        const formElement = event.currentTarget;
        try {
          const fd = new FormData(formElement);
          const payload = buildTarifaCompraPayload(fd);
          const rawId = tarifaCompraEditIdForPatch(formElement);
          const id = requirePositiveIntOrThrow(rawId, "Tarifa de compra");
          await api(`/tarifas-compra-transportista/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("tarifa-compra-edit-message", "Tarifa de compra actualizada.", "ok");
          cancelTarifaCompraEdit();
          await refreshData();
        } catch (error) {
          setMessage("tarifa-compra-edit-message", error.message, "error");
        }
      });

      document.getElementById("flete-edit-cancel").addEventListener("click", cancelFleteEdit);
      document.getElementById("flete-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("flete-edit-message");
        const formElement = event.currentTarget;
        try {
          const payload = buildFletePayload(new FormData(formElement));
          const idRaw = resolveFleteEditRecordId(formElement);
          const id = requirePositiveIntOrThrow(idRaw, "Flete");
          await api(`/fletes/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("flete-edit-message", "Flete actualizado.", "ok");
          cancelFleteEdit();
          await refreshData();
        } catch (error) {
          setMessage("flete-edit-message", error.message, "error");
        }
      });

      document.getElementById("asignacion-edit-cancel").addEventListener("click", cancelAsignacionEdit);
      document.getElementById("asignacion-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("asignacion-edit-message");
        const formElement = event.currentTarget;
        try {
          const payload = buildAsignacionPayload(new FormData(formElement));
          const id = requirePositiveIntOrThrow(formElement.elements.id_asignacion.value, "Asignacion");
          await api(`/asignaciones/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("asignacion-edit-message", "Asignacion actualizada.", "ok");
          cancelAsignacionEdit();
          await refreshData();
        } catch (error) {
          setMessage("asignacion-edit-message", error.message, "error");
        }
      });

      document.getElementById("despacho-edit-cancel").addEventListener("click", cancelDespachoEdit);
      document.getElementById("despacho-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("despacho-edit-message");
        const formElement = event.currentTarget;
        try {
          const payload = buildDespachoPayload(new FormData(formElement));
          const idCandidate = resolveDespachoEditRecordId(formElement);
          const id = requirePositiveIntIdOrThrow(idCandidate, "Despacho");
          await api(`/despachos/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("despacho-edit-message", "Despacho actualizado.", "ok");
          cancelDespachoEdit();
          await refreshData();
        } catch (error) {
          setMessage("despacho-edit-message", error.message, "error");
        }
      });
    }

    async function fetchHealthIntoPanel() {
      const el = document.getElementById("health-conn-info");
      if (!el) {
        return;
      }
      try {
        const r = await fetch("/health", { headers: { Accept: "application/json" } });
        if (!r.ok) {
          throw new Error(`HTTP ${r.status}`);
        }
        const data = await r.json();
        const host = data.mysql_host != null ? String(data.mysql_host) : "?";
        const port = data.mysql_port != null ? String(data.mysql_port) : "?";
        const db = data.mysql_db != null ? String(data.mysql_db) : "?";
        el.innerHTML =
          "<strong>Base de datos (este proceso):</strong> <code>" +
          escapeHtml(db) +
          "</code> en <code>" +
          escapeHtml(host) +
          ":" +
          escapeHtml(port) +
          '</code>. Comparala con la base que abres en MySQL: si no coincide, el panel y el cliente SQL estan mirando otro servidor o base. JSON: <a href="/health">/health</a>.';
      } catch (e) {
        el.textContent =
          "No se pudo leer /health: " +
          (e && e.message ? e.message : "error") +
          ". Verifique que Uvicorn este en marcha.";
      }
    }

    async function boot() {
      initNavigation();
      installCaptureFormCancelButtons();
      initForms();
      wireMoneyInputs();
      for (const form of document.querySelectorAll("form")) {
        applyMoneyFormatToForm(form);
      }
      initClienteModule();
      initTransportistaModule();
      initCrudSubpageModules();
      initFacturaModule();
      initFilters();
      initTarifaVentaNombreUnico();
      initEditors();
      initFleteCotizador();
      wireEnterAvanzaCampo("#flete-form");
      wireEnterAvanzaCampo("#flete-edit-form");
      try {
        await Promise.all([refreshData(), fetchHealthIntoPanel()]);
      } catch (error) {
        document.body.insertAdjacentHTML(
          "afterbegin",
          `<div style="margin:16px;padding:12px;border:1px solid #fecaca;background:#fef2f2;color:#991b1b;border-radius:12px;">
            No se pudo cargar el panel: ${error.message}
          </div>`
        );
      }
    }

    boot();
  </script>
</body>
</html>
"""


def _render_ui() -> str:
    html = _UI_TEMPLATE.replace("__PROJECT_NAME__", escape(settings.PROJECT_NAME))
    return html.replace("__API_KEY__", json.dumps(settings.API_KEY))


@router.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/ui", status_code=307)


@router.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=204)


@router.get("/manual/cumplimiento", include_in_schema=False)
def manual_cumplimiento() -> HTMLResponse:
    path = Path(__file__).resolve().parent / "static" / "cumplimiento_manual.html"
    if not path.is_file():
        return HTMLResponse("<p>Manual no encontrado.</p>", status_code=404)
    return HTMLResponse(path.read_text(encoding="utf-8"))


@router.get("/ui", include_in_schema=False)
def ui_dashboard() -> HTMLResponse:
    return HTMLResponse(
        _render_ui(),
        headers={"Cache-Control": "no-store, no-cache, max-age=0, must-revalidate"},
    )
