import React from 'react';
import { useTranslation } from 'react-i18next';

function Dashboard() {
  const { t } = useTranslation();

  return (
    <div>
      <h2>{t('dashboard.title')}</h2>
      <p>Welcome to your CRM dashboard.</p>
      {/* TODO: Add widgets, charts, summaries etc. */}
    </div>
  );
}

export default Dashboard;
