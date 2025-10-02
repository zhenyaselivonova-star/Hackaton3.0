import { useState } from 'react';

const Tabs = ({ tabs, activeTab, onTabChange }) => {
  return (
    <div className="tabs">
      {tabs.map((tab) => (
        <div
          key={tab.id}
          className={`tab ${activeTab === tab.id ? 'active' : ''}`}
          onClick={() => onTabChange(tab.id)}
        >
          {tab.label}
        </div>
      ))}
    </div>
  );
};

export default Tabs;