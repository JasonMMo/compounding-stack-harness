/**
 * sidebar.js — App shell sidebar toggle + mobile drawer + accordion groups.
 * Spec: out/analysis/design/accordion-sidebar-spec.md (Hostinger-style light theme)
 * Vanilla JS only, no build step.
 */
(function () {
  'use strict';

  var STORAGE_KEY   = 'sidebar-collapsed';
  var ACCORDION_KEY = 'sidebar-accordion-open';
  var MOBILE_BP     = 768;

  function isMobile() { return window.innerWidth <= MOBILE_BP; }

  function applyCollapsed(body, sidebar, btn, collapsed) {
    if (collapsed) {
      body.classList.add('app-body--sidebar-collapsed');
      sidebar.classList.add('app-sidebar--collapsed');
    } else {
      body.classList.remove('app-body--sidebar-collapsed');
      sidebar.classList.remove('app-sidebar--collapsed');
    }
    btn.setAttribute('aria-expanded', String(!collapsed));
  }

  function openDrawer(sidebar, backdrop, btn) {
    sidebar.classList.add('app-sidebar--open');
    backdrop.classList.add('drawer-backdrop--visible');
    btn.setAttribute('aria-expanded', 'true');
    var first = sidebar.querySelector('a, button');
    if (first) { first.focus(); }
  }

  function closeDrawer(sidebar, backdrop, btn) {
    sidebar.classList.remove('app-sidebar--open');
    backdrop.classList.remove('drawer-backdrop--visible');
    btn.setAttribute('aria-expanded', 'false');
  }

  function getOpenGroups() {
    try {
      var raw = localStorage.getItem(ACCORDION_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
  }

  function saveOpenGroups(keys) {
    try { localStorage.setItem(ACCORDION_KEY, JSON.stringify(keys)); } catch (e) {}
  }

  function setGroupOpen(header, nav, open) {
    header.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('is-open', open);
  }

  function initAccordion(sidebar) {
    var headers = sidebar.querySelectorAll('.sidebar-group__header');
    if (!headers.length) { return; }
    var saved = getOpenGroups();

    headers.forEach(function (header) {
      var group    = header.closest('.sidebar-group');
      var groupKey = group ? group.dataset.groupKey : null;
      var nav      = document.getElementById(header.getAttribute('aria-controls'));
      if (!nav) { return; }

      var isOpen = (saved !== null && groupKey) ? (saved.indexOf(groupKey) !== -1) : true;
      setGroupOpen(header, nav, isOpen);

      header.addEventListener('click', function () {
        var nowOpen = nav.classList.contains('is-open');
        setGroupOpen(header, nav, !nowOpen);
        var openKeys = [];
        sidebar.querySelectorAll('.sidebar-group__header').forEach(function (h) {
          var g = h.closest('.sidebar-group');
          if (g && h.getAttribute('aria-expanded') === 'true') {
            openKeys.push(g.dataset.groupKey || '');
          }
        });
        saveOpenGroups(openKeys);
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var btn      = document.getElementById('sidebar-toggle-btn');
    var body     = document.getElementById('app-body');
    var sidebar  = document.getElementById('app-sidebar');
    var backdrop = document.getElementById('drawer-backdrop');
    if (!btn || !body || !sidebar || !backdrop) { return; }

    if (!isMobile()) {
      if (localStorage.getItem(STORAGE_KEY) === '1') {
        applyCollapsed(body, sidebar, btn, true);
      }
    }

    initAccordion(sidebar);

    btn.addEventListener('click', function () {
      if (isMobile()) {
        var isOpen = sidebar.classList.contains('app-sidebar--open');
        if (isOpen) { closeDrawer(sidebar, backdrop, btn); }
        else { openDrawer(sidebar, backdrop, btn); }
      } else {
        var isCollapsed = sidebar.classList.contains('app-sidebar--collapsed');
        applyCollapsed(body, sidebar, btn, !isCollapsed);
        localStorage.setItem(STORAGE_KEY, isCollapsed ? '0' : '1');
      }
    });

    backdrop.addEventListener('click', function () { closeDrawer(sidebar, backdrop, btn); });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && sidebar.classList.contains('app-sidebar--open')) {
        closeDrawer(sidebar, backdrop, btn);
        btn.focus();
      }
    });
  });
}());
