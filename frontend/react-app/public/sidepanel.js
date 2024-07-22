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

// Side panel's content script: Captures the URL and saves it
document.addEventListener('DOMContentLoaded', () => {
  chrome.storage.session.get('currentUrl', ({ currentUrl }) => {
    console.log('currentUrl', currentUrl)
    localStorage.setItem('currentUrl', currentUrl)
    window.dispatchEvent(new Event('storage'))
  })
});

chrome.storage.session.onChanged.addListener(changes => {
  if (changes.currentUrl) {
    localStorage.setItem('currentUrl', changes.currentUrl.newValue)
    // trigger new event
    window.dispatchEvent(new Event('storage'))
  }
})
