import axios from 'axios';

const testInsertDummyUser = async () => {
  try {
    console.log("🔵 Sending dummy user insert request...");
    const response = await axios.post('/api/test-insert', {}, { withCredentials: true });
    console.log("🟢 Dummy Insert Response:", response.data);
    alert(response.data.message);
  } catch (error) {
    console.error("🔴 Dummy Insert Error:", error.response?.data?.message || error.message);
    alert('Failed to insert dummy user.');
  }
};

export default function TestPage() {
  return (
    <div>
      <h1>Test Page</h1>
      <button onClick={testInsertDummyUser}>Insert Dummy User</button>
    </div>
  );
}