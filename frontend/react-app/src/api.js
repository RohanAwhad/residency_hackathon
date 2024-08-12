// ===
// Actual API
// ===
const localApiUrl = 'http://localhost:8080';

export const getMindmapMd = async url => {
    try {
        const response = await fetch(`${localApiUrl}/get_mindmap?url=${url}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json()
    } catch (error) {
        console.error('Error: ', error)
    }
}

export const getCode = async (mindmap, url) => {
    try {
        const response = await fetch(`${localApiUrl}/get_code`, {
            method: 'POST',
            headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
            body: JSON.stringify({ mindmap: mindmap, paper_url: url })
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json()
    } catch (error) {
        console.error('Error: ', error)
    }
}

export const getRefIds = async (paper_url) => {
    const response = await fetch(`${localApiUrl}/process_paper?paper_url=${paper_url}`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
    })
    if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
    }
    return await response.json();
}

const sleep = ms => new Promise(r => setTimeout(r, ms))
export const getRefData = async (paper_url, ref_id) => {

    while (true) {
        const response = await fetch(`${localApiUrl}/process_reference?paper_url=${paper_url}&ref_id=${ref_id}`, {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        })
        if (response.ok) {
            console.log(response.status);
            return await response.json();
        }
        await sleep(1000)
    }
}

export const getChatResponse = async (paper_url, messages) => {
    const response = await fetch(`${localApiUrl}/chat/response`, {
        method: 'POST',
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({ paper_url, messages })
    })

    if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
    }
    return await response.json();
}

export const validateApiKey = async (apiKey) => {
    try {
        const response = await fetch(`${localApiUrl}/validate/apiKey`, {
            method: 'POST',
            headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
            body: JSON.stringify({ apiKey })
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json()
    } catch (error) {
        console.error('Error: ', error)
    }
}

