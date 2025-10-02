const ProfileHeader = ({ user }) => {
  const getInitials = (name) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  return (
    <div className="profile-header">
      <div className="profile-avatar">
        <span id="avatar-initials">{getInitials(user.name)}</span>
      </div>
      <h1 id="profile-name">{user.name}</h1>
      <p id="profile-email">{user.email}</p>
    </div>
  );
};

export default ProfileHeader;