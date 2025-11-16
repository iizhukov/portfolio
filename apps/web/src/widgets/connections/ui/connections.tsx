import { useConnections, useStatus, useWorking, useImage } from '../api/hooks'

export const Connections = () => {
  const { connections, loading: connectionsLoading } = useConnections()
  const { status, loading: statusLoading } = useStatus()
  const { working, loading: workingLoading } = useWorking()
  const { image, loading: imageLoading, error: imageError } = useImage()

  const loading = connectionsLoading || statusLoading || workingLoading || imageLoading
  const defaultProfileImage = '/assets/default/profile.jpg'
  const profileImageUrl = image?.url && !imageError ? image.url : defaultProfileImage

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    if (e.currentTarget.src !== defaultProfileImage) {
      e.currentTarget.src = defaultProfileImage
    }
  }

  return (
    <div className="w-full h-full bg-gradient-to-br from-purple-600 via-pink-500 to-orange-500">
      <div className="h-full overflow-auto px-6 py-10">
        <div className="max-w-xl mx-auto text-white space-y-8">
          <div className="flex flex-col items-center space-y-4">
            <div className="relative">
              <img
                src={profileImageUrl}
                alt="Connections"
                className="w-36 h-36 rounded-full border-[5px] border-connections shadow-2xl"
                onError={handleImageError}
              />
              <span
                className={`absolute bottom-1 right-1 w-9 h-9 rounded-full border-[5px] border-connections ${
                  status?.status === 'active' ? 'bg-status-green' : 'bg-status-red'
                }`}
              ></span>
            </div>
            <div className="text-center">
              <p className="text-3xl font-extrabold">Илья Жуков</p>
            </div>
          </div>

          <div className="bg-connections rounded-3xl p-6 shadow-xl space-y-8">
            <section>
              <header className="flex items-center justify-between mb-4">
                <p className="text-sm tracking-widest text-window-text-secondary font-semibold">
                  CONNECTIONS
                </p>
                <span className="flex-1 h-px bg-window-text-secondary ml-3"></span>
              </header>
              {loading ? (
                <p className="text-window-text-secondary">Loading connections...</p>
              ) : (
                <ul className="space-y-4">
                  {connections.map(connection => (
                    <li
                      key={connection.id}
                      className="flex flex-col sm:flex-row sm:items-center sm:justify-between bg-white/5 rounded-2xl px-4 py-3"
                    >
                      <span className="text-base font-semibold">{connection.label}</span>
                      <a
                        href={connection.href}
                        target={connection.type === 'social' ? '_blank' : undefined}
                        rel={connection.type === 'social' ? 'noopener noreferrer' : undefined}
                        className="text-sm text-pink-300 hover:text-white underline-offset-4 hover:underline transition-colors"
                      >
                        {connection.value}
                      </a>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section>
              <header className="flex items-center justify-between mb-4">
                <p className="text-sm tracking-widest text-window-text-secondary font-semibold">
                  WORKING ON
                </p>
                <span className="flex-1 h-px bg-window-text-secondary ml-3"></span>
              </header>
              {loading ? (
                <p className="text-window-text-secondary">Loading project...</p>
              ) : working ? (
                <div className="bg-white/5 rounded-2xl p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <p className="text-lg font-semibold">{working.working_on}</p>
                    <span className="text-sm text-window-text-secondary">
                      {working.percentage}%
                    </span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-700 ease-out"
                      style={{ width: `${working.percentage}%` }}
                    ></div>
                  </div>
                </div>
              ) : null}
            </section>
          </div>
        </div>
      </div>
    </div>
  )
}
