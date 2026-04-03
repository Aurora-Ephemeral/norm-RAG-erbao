export default function About() {
  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
        关于项目
      </h1>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 space-y-4">
        <p className="text-gray-600 dark:text-gray-400">
          这是一个基于以下技术栈构建的 React 项目：
        </p>
        <ul className="list-disc list-inside space-y-2 text-gray-600 dark:text-gray-400">
          <li><strong className="text-gray-900 dark:text-white">React 19</strong> — 用户界面库</li>
          <li><strong className="text-gray-900 dark:text-white">TypeScript</strong> — 类型安全</li>
          <li><strong className="text-gray-900 dark:text-white">Vite</strong> — 快速构建工具</li>
          <li><strong className="text-gray-900 dark:text-white">React Router</strong> — 客户端路由</li>
          <li><strong className="text-gray-900 dark:text-white">Redux Toolkit</strong> — 状态管理</li>
          <li><strong className="text-gray-900 dark:text-white">Tailwind CSS</strong> — 原子化样式</li>
          <li><strong className="text-gray-900 dark:text-white">Axios</strong> — HTTP 请求</li>
        </ul>
      </div>
    </div>
  )
}
