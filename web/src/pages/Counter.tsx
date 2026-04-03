import { useAppDispatch, useAppSelector } from '@/hooks/store'
import { increment, decrement, incrementByAmount } from '@/store/counterSlice'

export default function Counter() {
  const count = useAppSelector((state) => state.counter.value)
  const dispatch = useAppDispatch()

  return (
    <div className="text-center">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
        Redux 计数器示例
      </h1>
      <div className="inline-block p-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
        <p className="text-6xl font-bold text-indigo-600 dark:text-indigo-400 mb-8">
          {count}
        </p>
        <div className="flex gap-3 justify-center">
          <button
            onClick={() => dispatch(decrement())}
            className="px-5 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-medium"
          >
            - 减少
          </button>
          <button
            onClick={() => dispatch(increment())}
            className="px-5 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors font-medium"
          >
            + 增加
          </button>
          <button
            onClick={() => dispatch(incrementByAmount(5))}
            className="px-5 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors font-medium"
          >
            +5
          </button>
        </div>
      </div>
    </div>
  )
}
