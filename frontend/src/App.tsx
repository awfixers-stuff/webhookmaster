import { useState, useCallback } from 'react'

function App() {
  const [payload, setPayload] = useState('');
  const [source, setSource] = useState('default');
  const [format, setFormat] = useState('default');
  const [transformedPayload, setTransformedPayload] = useState('');
  const [isTransforming, setIsTransforming] = useState(false);

  const debounce = (func: (...args: any[]) => void, delay: number) => {
    let timeout: NodeJS.Timeout;
    return (...args: any[]) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), delay);
    };
  };

  const handleTransform = useCallback(async () => {
    setIsTransforming(true);
    try {
      const response = await fetch(`/webhook?source=${source}&format=${format}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: payload,
      });
      const data = await response.json();
      setTransformedPayload(JSON.stringify(data, null, 2));
    } catch (error) {
      console.error('Error transforming webhook:', error);
      setTransformedPayload('Error transforming webhook.');
    } finally {
      setIsTransforming(false);
    }
  }, [payload, source, format]);

  const debouncedHandleTransform = useCallback(debounce(handleTransform, 500), [handleTransform]);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Webhook Transformer</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h2 className="text-xl font-semibold mb-2">Input Webhook Payload</h2>
          <textarea
            className="w-full p-2 border rounded-md h-64 bg-gray-800 text-white"
            value={payload}
            onChange={(e) => setPayload(e.target.value)}
            placeholder="Paste your webhook JSON payload here..."
          />
        </div>

        <div>
          <h2 className="text-xl font-semibold mb-2">Transformed Payload</h2>
          <textarea
            className="w-full p-2 border rounded-md h-64 bg-gray-800 text-white"
            value={transformedPayload}
            readOnly
            placeholder="Transformed payload will appear here..."
          />
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-4 mt-4">
        <div className="flex-1">
          <label htmlFor="source-select" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Source</label>
          <select
            id="source-select"
            className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-gray-700 text-white"
            value={source}
            onChange={(e) => setSource(e.target.value)}
          >
            <option value="default">Default</option>
            <option value="github">GitHub</option>
            <option value="stripe">Stripe</option>
            <option value="shopify">Shopify</option>
            <option value="wix">Wix</option>
            <option value="cloudflare">Cloudflare</option>
            <option value="webflow">Webflow</option>
          </select>
        </div>

        <div className="flex-1">
          <label htmlFor="format-select" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Output Format</label>
          <select
            id="format-select"
            className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-gray-700 text-white"
            value={format}
            onChange={(e) => setFormat(e.target.value)}
          >
            <option value="default">Default</option>
            <option value="slack">Slack</option>
            <option value="discord">Discord</option>
            <option value="msteams">Microsoft Teams</option>
            <option value="email">Email</option>
          </select>
        </div>

        <button
          onClick={debouncedHandleTransform}
          disabled={isTransforming}
          className="mt-6 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          {isTransforming ? 'Transforming...' : 'Transform Webhook'}
        </button>
      </div>
    </div>
  );
}

export default App;