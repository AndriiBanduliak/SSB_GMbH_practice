import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const Reports = () => {
  const { API_URL } = useAuth();
  const [period, setPeriod] = useState('monthly');
  const [loading, setLoading] = useState(false);

  const handleGenerateReport = async () => {
    try {
      setLoading(true);
      alert('Report generation feature will be implemented with PDF export');
      // In production, this would download a PDF report
      // const response = await axios.get(`${API_URL}/reports/generate`, {
      //   params: { period },
      //   responseType: 'blob'
      // });
      // const url = window.URL.createObjectURL(new Blob([response.data]));
      // const link = document.createElement('a');
      // link.href = url;
      // link.setAttribute('download', `report_${period}_${Date.now()}.pdf`);
      // document.body.appendChild(link);
      // link.click();
    } catch (error) {
      console.error('Failed to generate report:', error);
      alert('Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
        <p className="mt-1 text-sm text-gray-600">Generate performance reports for clients</p>
      </div>

      {/* Report generation form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Generate Client Report</h2>
        
        <div className="max-w-md space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Report Period
            </label>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="yearly">Yearly</option>
              <option value="all_time">All Time</option>
            </select>
          </div>

          <button
            onClick={handleGenerateReport}
            disabled={loading}
            className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Generating...' : 'Generate PDF Report'}
          </button>
        </div>
      </div>

      {/* Report templates */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <span className="text-3xl mr-3">📊</span>
            <div>
              <h3 className="text-lg font-medium text-gray-900">Performance Summary</h3>
              <p className="text-sm text-gray-600">Comprehensive P&L analysis</p>
            </div>
          </div>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>• Portfolio value over time</li>
            <li>• P&L breakdown by exchange</li>
            <li>• ROI and performance metrics</li>
            <li>• Trade statistics</li>
          </ul>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <span className="text-3xl mr-3">📈</span>
            <div>
              <h3 className="text-lg font-medium text-gray-900">Trade History</h3>
              <p className="text-sm text-gray-600">Detailed transaction log</p>
            </div>
          </div>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>• All trades with timestamps</li>
            <li>• Buy/Sell analysis</li>
            <li>• Fee breakdown</li>
            <li>• Asset allocation</li>
          </ul>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <span className="text-3xl mr-3">📉</span>
            <div>
              <h3 className="text-lg font-medium text-gray-900">Risk Analysis</h3>
              <p className="text-sm text-gray-600">Risk metrics and drawdowns</p>
            </div>
          </div>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>• Maximum drawdown</li>
            <li>• Volatility metrics</li>
            <li>• Risk-adjusted returns</li>
            <li>• Sharpe ratio</li>
          </ul>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <span className="text-3xl mr-3">💼</span>
            <div>
              <h3 className="text-lg font-medium text-gray-900">Portfolio Overview</h3>
              <p className="text-sm text-gray-600">Asset allocation and diversification</p>
            </div>
          </div>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>• Current holdings</li>
            <li>• Asset distribution</li>
            <li>• Exchange breakdown</li>
            <li>• Historical balance</li>
          </ul>
        </div>
      </div>

      {/* Scheduled reports */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Scheduled Reports</h2>
        <p className="text-sm text-gray-600 mb-4">
          Automatically send reports to clients on a recurring schedule
        </p>
        <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
          Configure Scheduled Reports
        </button>
      </div>
    </div>
  );
};

export default Reports;

