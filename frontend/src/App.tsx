import { useForm } from 'react-hook-form'
import { useAppStore } from './stores/appStore'

function App() {
  const isOnline = useAppStore((state) => state.isOnline)
  const { register, handleSubmit } = useForm()

  const onSubmit = (data: unknown) => {
    console.log('Form submitted:', data)
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">SmartHand</h1>

      <div className="mb-4 p-3 bg-gray-100 rounded">
        <p className="text-sm">
          Status: <span className={isOnline ? 'text-green-600' : 'text-red-600'}>
            {isOnline ? 'Online' : 'Offline'}
          </span>
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
        <div>
          <label htmlFor="test-input" className="block text-sm font-medium mb-1">
            Test Input (React Hook Form):
          </label>
          <input
            id="test-input"
            {...register('testField')}
            className="border border-gray-300 rounded px-3 py-2 w-full"
            placeholder="Enter some text"
          />
        </div>
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Submit
        </button>
      </form>
    </div>
  )
}

export default App
