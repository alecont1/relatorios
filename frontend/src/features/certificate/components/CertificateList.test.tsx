import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/test/utils'
import userEvent from '@testing-library/user-event'
import { CertificateList } from './CertificateList'
import type { Certificate, CertificateListResponse } from '../api/certificateApi'

// ---- Mock the hooks used by CertificateList ----

const mockMutateAsync = vi.fn()

vi.mock('../hooks/useCertificates', () => ({
  useCertificates: vi.fn(),
  useDeleteCertificate: vi.fn(() => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  })),
}))

// Import the mocked module so we can control return values per test
import { useCertificates } from '../hooks/useCertificates'
const mockUseCertificates = vi.mocked(useCertificates)

// ---- Fixtures ----

function makeCert(overrides: Partial<Certificate> = {}): Certificate {
  return {
    id: 'cert-1',
    tenant_id: 'tenant-1',
    equipment_name: 'Multimetro Digital',
    certificate_number: 'CAL-2024-001',
    manufacturer: 'Fluke',
    model: '87V',
    serial_number: 'SN-12345678',
    laboratory: 'Lab ABC',
    calibration_date: '2024-01-15',
    expiry_date: '2025-01-15',
    file_key: null,
    status: 'valid',
    is_active: true,
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
    ...overrides,
  }
}

function makeListResponse(certs: Certificate[]): Partial<ReturnType<typeof useCertificates>> {
  return {
    data: { certificates: certs, total: certs.length } as CertificateListResponse,
    isLoading: false,
    error: null,
  }
}

describe('CertificateList', () => {
  const onEdit = vi.fn()
  const onUpload = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders certificate cards with equipment name, number, and status badge', () => {
    const cert = makeCert()
    mockUseCertificates.mockReturnValue(makeListResponse([cert]) as ReturnType<typeof useCertificates>)

    const { container } = render(<CertificateList onEdit={onEdit} onUpload={onUpload} />)

    expect(screen.getByText('CAL-2024-001')).toBeInTheDocument()
    expect(screen.getByText('Multimetro Digital')).toBeInTheDocument()
    // "Valido" appears both in filter <option> and in the badge <span>
    // Check that the green badge exists
    const badge = container.querySelector('.bg-green-100.text-green-700')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveTextContent('Valido')
    expect(screen.getByText('1 certificado(s) encontrado(s)')).toBeInTheDocument()
  })

  it('shows loading spinner while fetching', () => {
    mockUseCertificates.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as unknown as ReturnType<typeof useCertificates>)

    const { container } = render(<CertificateList onEdit={onEdit} onUpload={onUpload} />)

    // The Loader2 icon renders an SVG with the animate-spin class
    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })

  it('shows status badges with correct colors for each status', () => {
    const certs = [
      makeCert({ id: '1', certificate_number: 'C-001', status: 'valid' }),
      makeCert({ id: '2', certificate_number: 'C-002', status: 'expiring' }),
      makeCert({ id: '3', certificate_number: 'C-003', status: 'expired' }),
    ]
    mockUseCertificates.mockReturnValue(makeListResponse(certs) as ReturnType<typeof useCertificates>)

    const { container } = render(<CertificateList onEdit={onEdit} onUpload={onUpload} />)

    // Green badge for "Valido"
    const greenBadge = container.querySelector('.bg-green-100.text-green-700')
    expect(greenBadge).toBeInTheDocument()
    expect(greenBadge).toHaveTextContent('Valido')

    // Yellow badge for "Vencendo"
    const yellowBadge = container.querySelector('.bg-yellow-100.text-yellow-700')
    expect(yellowBadge).toBeInTheDocument()
    expect(yellowBadge).toHaveTextContent('Vencendo')

    // Red badge for "Vencido"
    const redBadge = container.querySelector('.bg-red-100.text-red-700')
    expect(redBadge).toBeInTheDocument()
    expect(redBadge).toHaveTextContent('Vencido')
  })

  it('edit button calls onEdit with the certificate', async () => {
    const cert = makeCert()
    mockUseCertificates.mockReturnValue(makeListResponse([cert]) as ReturnType<typeof useCertificates>)

    render(<CertificateList onEdit={onEdit} onUpload={onUpload} />)

    const user = userEvent.setup()
    const editButton = screen.getByTitle('Editar')
    await user.click(editButton)

    expect(onEdit).toHaveBeenCalledTimes(1)
    expect(onEdit).toHaveBeenCalledWith(cert)
  })

  it('delete button triggers confirm dialog and calls delete mutation', async () => {
    const cert = makeCert({ id: 'cert-delete', equipment_name: 'Termopar' })
    mockUseCertificates.mockReturnValue(makeListResponse([cert]) as ReturnType<typeof useCertificates>)
    mockMutateAsync.mockResolvedValue(undefined)

    // Simulate user confirming the dialog
    vi.spyOn(window, 'confirm').mockReturnValue(true)

    render(<CertificateList onEdit={onEdit} onUpload={onUpload} />)

    const user = userEvent.setup()
    const deleteButton = screen.getByTitle('Excluir')
    await user.click(deleteButton)

    expect(window.confirm).toHaveBeenCalledWith(
      'Deseja realmente excluir o certificado "Termopar"?'
    )
    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalledWith('cert-delete')
    })
  })

  it('shows empty state when no certificates exist', () => {
    mockUseCertificates.mockReturnValue(makeListResponse([]) as ReturnType<typeof useCertificates>)

    render(<CertificateList onEdit={onEdit} onUpload={onUpload} />)

    expect(screen.getByText('Nenhum certificado encontrado')).toBeInTheDocument()
  })

  it('renders the search input with correct placeholder', () => {
    mockUseCertificates.mockReturnValue(makeListResponse([]) as ReturnType<typeof useCertificates>)

    render(<CertificateList onEdit={onEdit} onUpload={onUpload} />)

    const searchInput = screen.getByPlaceholderText(
      'Buscar por equipamento, numero ou fabricante...'
    )
    expect(searchInput).toBeInTheDocument()
  })
})
