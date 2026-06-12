/**
 * sidebar.js — App shell sidebar toggle + mobile drawer.
 * Spec: out/analysis/design/app-shell-spec.md §11
 * Vanilla JS only, no build step, 50 lines or less.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'sidebar-collapsed';
  var MOBILE_BP = 768;

  function isMobile() {
    return window.innerWidth <= MOBILE_BP;
  }

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

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('sidebar-toggle-btn');
    var body = document.getElementById('app-body');
    var sidebar = document.getElementById('app-sidebar');
    var backdrop = document.getElementById('drawer-backdrop');
    if (!btn || !body || !sidebar || !backdrop) { return; }

    // Restore desktop collapsed state from localStorage
    if (!isMobile()) {
      var saved = localStorage.getItem(STORAGE_KEY);
      if (saved === '1') { applyCollapsed(body, sidebar, btn, true); }
    }

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

    backdrop.addEventListener('click', function () {
      closeDrawer(sidebar, backdrop, btn);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && sidebar.classList.contains('app-sidebar--open')) {
        closeDrawer(sidebar, backdrop, btn);
        btn.focus();
      }
    });
  });
}());
