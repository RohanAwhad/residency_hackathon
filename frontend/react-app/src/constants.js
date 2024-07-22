import { loadCSS, loadJS } from 'markmap-common';
import { Transformer } from 'markmap-lib';

export const transformer = new Transformer();
const { scripts, styles } = transformer.getAssets();
loadCSS(styles);
loadJS(scripts);

// // Side panel's content script: Captures the URL and saves it
// document.addEventListener('DOMContentLoaded', () => {
//   chrome.storage.session.get('currentUrl', ({ currentUrl }) => {
//     localStorage.setItem('currentUrl', currentUrl);
//   })
// });