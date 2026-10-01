import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { FileText, Box, ArrowRightLeft, Code2, TestTube, Play, ShieldAlert } from 'lucide-react';

type NodeTypeKey = 'Requirement' | 'SoftwareComponent' | 'Port' | 'Runnable' | 'C_Function' | 'C_Variable' | 'Test' | 'ChangeSeed' | 'default';

const TYPE_CONFIG: Record<NodeTypeKey, {
  icon: any;
  label: string;
  headerBg: string;
  headerText: string;
  bodyBorder: string;
  bodyBg: string;
}> = {
  Requirement: {
    icon: FileText,
    label: 'Requirement',
    headerBg: '#d97706',   // amber-600
    headerText: '#ffffff',
    bodyBorder: '#fbbf24',
    bodyBg: '#fffbeb',
  },
  SoftwareComponent: {
    icon: Box,
    label: 'Software Component',
    headerBg: '#ea580c',   // orange-600
    headerText: '#ffffff',
    bodyBorder: '#fb923c',
    bodyBg: '#fff7ed',
  },
  Port: {
    icon: ArrowRightLeft,
    label: 'Port',
    headerBg: '#16a34a',   // green-600
    headerText: '#ffffff',
    bodyBorder: '#4ade80',
    bodyBg: '#f0fdf4',
  },
  Runnable: {
    icon: Play,
    label: 'Runnable',
    headerBg: '#15803d',
    headerText: '#ffffff',
    bodyBorder: '#4ade80',
    bodyBg: '#f0fdf4',
  },
  C_Function: {
    icon: Code2,
    label: 'C Function',
    headerBg: '#2563eb',   // blue-600
    headerText: '#ffffff',
    bodyBorder: '#60a5fa',
    bodyBg: '#eff6ff',
  },
  C_Variable: {
    icon: Code2,
    label: 'C Variable',
    headerBg: '#1d4ed8',
    headerText: '#ffffff',
    bodyBorder: '#60a5fa',
    bodyBg: '#eff6ff',
  },
  Test: {
    icon: TestTube,
    label: 'Test Case',
    headerBg: '#0891b2',   // cyan-600
    headerText: '#ffffff',
    bodyBorder: '#22d3ee',
    bodyBg: '#ecfeff',
  },
  ChangeSeed: {
    icon: ShieldAlert,
    label: 'Change Seed',
    headerBg: '#1e293b',   // slate-800
    headerText: '#ffffff',
    bodyBorder: '#475569',
    bodyBg: '#f8fafc',
  },
  default: {
    icon: Box,
    label: 'Artifact',
    headerBg: '#6b7280',
    headerText: '#ffffff',
    bodyBorder: '#d1d5db',
    bodyBg: '#f9fafb',
  },
};

const ASIL_CONFIG: Record<string, { bg: string; text: string; border: string }> = {
  'ASIL-D': { bg: '#dc2626', text: '#ffffff', border: '#b91c1c' },
  'ASIL-C': { bg: '#f97316', text: '#ffffff', border: '#ea580c' },
  'ASIL-B': { bg: '#eab308', text: '#1c1917', border: '#ca8a04' },
  'ASIL-A': { bg: '#fde047', text: '#1c1917', border: '#ca8a04' },
  'QM':     { bg: '#e5e7eb', text: '#374151', border: '#d1d5db' },
};

const CustomNode = ({ data, selected }: any) => {
  const { type, safety_level, isImpacted, isTest, isSeed, name } = data;
  const nodeId: string = data.id || '';

  const configKey = (isSeed ? 'ChangeSeed' : type) as NodeTypeKey;
  const config = TYPE_CONFIG[configKey] || TYPE_CONFIG.default;
  const Icon = config.icon;

  const asilKey = safety_level && safety_level !== 'QM' ? safety_level : null;
  const asilStyle = asilKey ? ASIL_CONFIG[asilKey] : null;

  // Override header for impact states
  let headerBg = config.headerBg;
  if (isImpacted && !isSeed) headerBg = '#dc2626';    // red-600 for impacted
  if (isTest) headerBg = '#0284c7';                    // sky-600 for tests

  const borderColor = isImpacted && !isSeed ? '#fca5a5' : isTest ? '#7dd3fc' : config.bodyBorder;
  const boxShadow = selected
    ? '0 0 0 2px #3b82f6, 0 4px 12px rgba(0,0,0,0.12)'
    : isImpacted && !isSeed
    ? '0 0 0 2px rgba(220,38,38,0.3), 0 2px 8px rgba(0,0,0,0.08)'
    : '0 2px 6px rgba(0,0,0,0.07)';

  const displayId = nodeId.length > 22 ? nodeId.slice(0, 20) + '…' : nodeId;
  const displayName = name && name !== nodeId
    ? (name.length > 28 ? name.slice(0, 26) + '…' : name)
    : null;

  return (
    <div
      style={{
        minWidth: 200,
        maxWidth: 240,
        borderRadius: 8,
        border: `2px solid ${borderColor}`,
        boxShadow,
        overflow: 'hidden',
        background: '#fff',
        transition: 'box-shadow 0.15s, border-color 0.15s',
      }}
    >
      <Handle
        type="target"
        position={Position.Left}
        style={{ width: 10, height: 10, borderRadius: '50%', background: '#94a3b8', border: '2px solid #fff', boxShadow: '0 0 0 1px #94a3b8' }}
      />

      {/* Header */}
      <div
        style={{
          background: headerBg,
          padding: '6px 10px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 6,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 5, overflow: 'hidden' }}>
          <Icon style={{ width: 12, height: 12, color: '#fff', flexShrink: 0 }} />
          <span style={{ fontSize: 9, fontWeight: 700, color: '#fff', textTransform: 'uppercase', letterSpacing: '0.08em', whiteSpace: 'nowrap' }}>
            {isSeed ? '⚡ CHANGE SEED' : config.label.toUpperCase()}
          </span>
        </div>
        {asilStyle && (
          <span style={{
            fontSize: 9, fontWeight: 800,
            background: asilStyle.bg, color: asilStyle.text,
            border: `1px solid ${asilStyle.border}`,
            borderRadius: 4, padding: '1px 5px',
            flexShrink: 0,
          }}>
            {safety_level}
          </span>
        )}
      </div>

      {/* Body */}
      <div style={{ padding: '8px 10px', background: isImpacted && !isSeed ? '#fef2f2' : isTest ? '#f0f9ff' : config.bodyBg }}>
        {/* ID - monospace, prominent */}
        <div style={{ fontFamily: 'monospace', fontSize: 12, fontWeight: 700, color: '#1e293b', marginBottom: displayName ? 2 : 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={nodeId}>
          {displayId}
        </div>
        {/* Name / description */}
        {displayName && (
          <div style={{ fontSize: 10, color: '#64748b', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={name}>
            {displayName}
          </div>
        )}
        {/* Impact indicator */}
        {(isImpacted && !isSeed) && (
          <div style={{ marginTop: 4, display: 'flex', alignItems: 'center', gap: 3 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#ef4444', display: 'inline-block' }} />
            <span style={{ fontSize: 9, color: '#dc2626', fontWeight: 600 }}>IMPACTED</span>
          </div>
        )}
        {isTest && (
          <div style={{ marginTop: 4, display: 'flex', alignItems: 'center', gap: 3 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#0ea5e9', display: 'inline-block' }} />
            <span style={{ fontSize: 9, color: '#0284c7', fontWeight: 600 }}>RETEST REQUIRED</span>
          </div>
        )}
        {isSeed && (
          <div style={{ marginTop: 4, display: 'flex', alignItems: 'center', gap: 3 }}>
            <span style={{ fontSize: 9, color: '#94a3b8' }}>Change origin</span>
          </div>
        )}
      </div>

      <Handle
        type="source"
        position={Position.Right}
        style={{ width: 10, height: 10, borderRadius: '50%', background: '#94a3b8', border: '2px solid #fff', boxShadow: '0 0 0 1px #94a3b8' }}
      />
    </div>
  );
};

export default memo(CustomNode);
