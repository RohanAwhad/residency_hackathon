import React, { useState, useEffect } from 'react';

const StreamingText = () => {
  const [text, setText] = useState('');

  useEffect(() => {
    const fetchStream = async () => {
      try {
        const response = await fetch('http://localhost:8080/stream');
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value);
          setText(prevText => prevText + chunk + ' ');
        }
      } catch (error) {
        console.error('Error fetching stream:', error);
      }
    };

    fetchStream();
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Streaming Text</h2>
      <p className="text-gray-700">{text}</p>
    </div>
  );
};

export default StreamingText;