const CONNECTIONS_DATA = [
  {
    label: 'GitHub',
    value: 'iizhukov',
    href: 'https://github.com/iizhukov',
    type: 'social',
  },
  {
    label: 'Mail',
    value: 'iizhukov@icloud.com',
    href: 'mailto:iizhukov@icloud.com',
    type: 'email',
  },
  {
    label: 'Telegram',
    value: '@ii_zhukov',
    href: 'https://t.me/ii_zhukov',
    type: 'social',
  },
  {
    label: 'VK',
    value: 'ii_zhukov',
    href: 'https://vk.com/ii_zhukov',
    type: 'social',
  },
]

export const Connections = () => {
  return (
    <div className="w-full h-full relative bg-gradient-to-br from-purple-600 via-pink-500 to-orange-500">
      <div className="absolute inset-0">
        <div className="mt-[30%] px-4 bg-connections h-[81%] w-full relative">
          <div className="absolute -top-[12%] w-[150px]">
            <img
              src="/profile.jpg"
              alt="Connections"
              className="rounded-full border-[8px] border-connections"
            />

            <div className="w-11 h-11 bg-status-green rounded-full absolute bottom-2 right-2 border-[8px] border-connections"></div>
          </div>

          <div className="absolute top-[14%] text-white left-4 right-4 bottom-4 flex flex-col px-4">
            <div>
              <p className="text-2xl font-extrabold">iizhukov</p>
              <p className="text-m mt-2 text-window-text-secondary">Status...</p>
            </div>

            <div className="mt-10">
              <div className="flex items-center">
                <p className="text-m text-window-text-secondary font-bold">CONNECTIONS</p>
                <div className="flex-1 h-0.5 bg-window-text-secondary ml-2"></div>
              </div>

              <div className="mt-4">
                <ul className="space-y-3">
                  {CONNECTIONS_DATA.map(connection => (
                    <li
                      key={connection.label}
                      className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-white/10 transition-all duration-200"
                    >
                      <span className="text-m font-bold">{connection.label}:</span>
                      <a
                        href={connection.href}
                        target={connection.type === 'social' ? '_blank' : undefined}
                        rel={connection.type === 'social' ? 'noopener noreferrer' : undefined}
                        className="text-sm text-pink-500 hover:text-blue-300 hover:underline underline-offset-2 transition-colors duration-200"
                      >
                        {connection.value}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="mt-10">
              <div className="flex items-center">
                <p className="text-m text-window-text-secondary font-bold">WORKING ON</p>
                <div className="flex-1 h-0.5 bg-window-text-secondary ml-2"></div>
              </div>

              <div className="mt-4">
                <div className="px-3 py-3 rounded-lg hover:bg-white/10 transition-all duration-200">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-m font-bold">Portfolio</p>
                    <span className="text-xs text-window-text-secondary">30%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-1000 ease-out"
                      style={{ width: '30%' }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
