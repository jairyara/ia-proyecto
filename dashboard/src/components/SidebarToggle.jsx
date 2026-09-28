import Icon from './Icon.jsx'

export default function SidebarToggle({ collapsed, onToggle }) {
  return <button
    type="button"
    className={`content-sidebar-toggle ${collapsed ? 'content-sidebar-toggle--collapsed' : ''}`}
    onClick={onToggle}
    aria-label={collapsed ? 'Expandir menú lateral' : 'Contraer menú lateral'}
    aria-controls="sidebar-navigation"
    aria-expanded={!collapsed}
    title={collapsed ? 'Expandir menú lateral' : 'Contraer menú lateral'}
  >
    <Icon name="panelLeft" size={22} />
  </button>
}
