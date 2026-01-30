import { useNavigate } from 'react-router-dom';
import { ShieldX } from 'lucide-react';

/**
 * Unauthorized access page.
 *
 * Shown when user tries to access a page their role doesn't allow.
 */
export function UnauthorizedPage() {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 px-4">
      <div className="text-center">
        <ShieldX className="mx-auto h-16 w-16 text-red-500" />
        <h1 className="mt-4 text-2xl font-bold text-gray-900">
          Acesso Negado
        </h1>
        <p className="mt-2 text-gray-600">
          Voce nao tem permissao para acessar esta pagina.
        </p>
        <button
          onClick={() => navigate(-1)}
          className="
            mt-6 inline-flex items-center rounded-lg
            bg-blue-600 px-4 py-2 text-white
            hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500
          "
        >
          Voltar
        </button>
      </div>
    </div>
  );
}
