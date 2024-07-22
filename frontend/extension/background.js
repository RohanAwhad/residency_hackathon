// Copyright 2023 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// function setupContextMenu() {
//   chrome.contextMenus.create({
//     id: 'define-word',
//     title: 'Define',
//     contexts: ['selection']
//   });
// }

// chrome.runtime.onInstalled.addListener(() => {
//   setupContextMenu();
// });

// chrome.contextMenus.onClicked.addListener((data, tab) => {
//   // Store the last word in chrome.storage.session.
//   chrome.storage.session.set({ lastWord: data.selectionText });

//   // Make sure the side panel is open.
//   chrome.sidePanel.open({ tabId: tab.id });
// });


// Background script: Opens the side panel when the context menu item is clicked
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'openSidePanel',
    title: 'Open side panel',
    contexts: ['all']
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  // get curr url
  const currentUrl = tab.url;
  // save it in local storage
  chrome.storage.session.set({ currentUrl: currentUrl }, () => {
    console.log(`URL saved successfully: ${currentUrl}`);
  });
  if (info.menuItemId === 'openSidePanel') {
    chrome.sidePanel.open({ tabId: tab.id});
  }
});

// // Side panel's content script: Captures the URL and saves it
// document.addEventListener('DOMContentLoaded', () => {
//   const currentUrl = window.location.href;
//   console.log(currentUrl); // Debugging

//   chrome.storage.local.set({ currentUrl: currentUrl }, () => {
//     console.log(`URL saved successfully: ${currentUrl}`);
//   });
// });

const ARXIV_ORIGIN = 'https://www.arxiv.org';
chrome.tabs.onUpdated.addListener(async (tabId, info, tab) => {
  if (!tab.url) return;

  const currentUrl = tab.url;
  chrome.storage.session.set({ currentUrl: currentUrl }, () => {
    console.log(`URL saved successfully: ${currentUrl}`);
  });

  // const url = new URL(tab.url);
  // // Enables the side panel on arxiv.org
  // if (url.origin === ARXIV_ORIGIN) {
  //   await chrome.sidePanel.setOptions({
  //     tabId,
  //     path: 'sidepanel.html',
  //     enabled: true
  //   });
  // } else {
  //   // Disables the side panel on all other sites
  //   await chrome.sidePanel.setOptions({
  //     tabId,
  //     enabled: false
  //   });
  // }
});