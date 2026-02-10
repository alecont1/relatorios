import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/test/utils'
import userEvent from '@testing-library/user-event'
import { CertificateSelectionModal } from './CertificateSelectionModal'
import type { Certificate } from '@/features/certificate'

// ---- Mock the certificate API ----

const mockList = vi.fn()
const mockLinkToReport = vi.fn()

vi.mock('@/features/certificate', () => ({
  certificateApi: {
    list: (...args: unknown[]) => mockList(...args),
    linkToReport: (...args: unknown[]) => mockLinkToReport(...args),
  },
}))

// ---- Fixtures ----

function makeCert(overrides: Partial<Certificate> = {}): Certificate {
  return {
    id: 'cert-1',
    tenant_id: 'tenant-1',
    equipment_name: 'Multimetro Digital',
    certificate_number: 'CAL-2024-001',
    manufacturer: 'Fluke',
    model: '87V',
    serial_number: 'SN-123',
    laboratory: 'Lab ABC',
    calibration_date: '2024-01-15',
    expiry_date: '2025-01-15',
    file_key: null,
    status: 'valid' as const,
    is_active: true,
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
    ...overrides,
  }
}

const sampleCerts = [
  makeCert({ id: 'c1', certificate_number: 'CAL-001', equipment_name: 'Multimetro' }),
  makeCert({
    id: 'c2',
    certificate_number: 'CAL-002',
    equipment_name: 'Termopar',
    status: 'expiring',
  }),
]

describe('CertificateSelectionModal', () => {
  const onClose = vi.fn()
  const onConfirm = vi.fn()
  const reportId = 'report-123'

  beforeEach(() => {
    vi.clearAllMocks()
    mockList.mockResolvedValue({ certificates: sampleCerts, total: 2 })
    mockLinkToReport.mockResolvedValue(undefined)
  })

  it('renders loading state while fetching certificates', () => {
    // Make the list promise hang to simulate loading
    mockList.mockReturnValue(new Promise(() => {}))

    const { container } = render(
      <CertificateSelectionModal
        isOpen={true}
        onClose={onClose}
        onConfirm={onConfirm}
        reportId={reportId}
      />
    )

    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })

  it('displays certificates from API after loading', async () => {
    render(
      <CertificateSelectionModal
        isOpen={true}
        onClose={onClose}
        onConfirm={onConfirm}
        reportId={reportId}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('CAL-001')).toBeInTheDocument()
    })

    expect(screen.getByText('CAL-002')).toBeInTheDocument()
    expect(screen.getByText('Multimetro')).toBeInTheDocument()
    expect(screen.getByText('Termopar')).toBeInTheDocument()
  })

  it('toggles certificate selection on click', async () => {
    render(
      <CertificateSelectionModal
        isOpen={true}
        onClose={onClose}
        onConfirm={onConfirm}
        reportId={reportId}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('CAL-001')).toBeInTheDocument()
    })

    const user = userEvent.setup()

    // Initially 0 selected
    expect(screen.getByText('0 certificado(s) selecionado(s)')).toBeInTheDocument()

    // Click the first certificate card to select it
    await user.click(screen.getByText('CAL-001'))

    expect(screen.getByText('1 certificado(s) selecionado(s)')).toBeInTheDocument()

    // Click again to deselect
    await user.click(screen.getByText('CAL-001'))

    expect(screen.getByText('0 certificado(s) selecionado(s)')).toBeInTheDocument()
  })

  it('confirm calls linkToReport API then onConfirm callback', async () => {
    render(
      <CertificateSelectionModal
        isOpen={true}
        onClose={onClose}
        onConfirm={onConfirm}
        reportId={reportId}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('CAL-001')).toBeInTheDocument()
    })

    const user = userEvent.setup()

    // Select the first certificate
    await user.click(screen.getByText('CAL-001'))
    expect(screen.getByText('1 certificado(s) selecionado(s)')).toBeInTheDocument()

    // Click confirm button
    await user.click(screen.getByText('Concluir e Gerar PDF'))

    await waitFor(() => {
      expect(mockLinkToReport).toHaveBeenCalledWith('report-123', ['c1'])
    })

    await waitFor(() => {
      expect(onConfirm).toHaveBeenCalledTimes(1)
    })

    // onConfirm should receive the selected certificate objects
    const confirmedCerts = onConfirm.mock.calls[0][0]
    expect(confirmedCerts).toHaveLength(1)
    expect(confirmedCerts[0].id).toBe('c1')
  })

  it('renders nothing when isOpen is false', () => {
    const { container } = render(
      <CertificateSelectionModal
        isOpen={false}
        onClose={onClose}
        onConfirm={onConfirm}
        reportId={reportId}
      />
    )

    expect(container.innerHTML).toBe('')
  })

  it('renders search input with the correct placeholder', async () => {
    render(
      <CertificateSelectionModal
        isOpen={true}
        onClose={onClose}
        onConfirm={onConfirm}
        reportId={reportId}
      />
    )

    const searchInput = screen.getByPlaceholderText(
      'Buscar por equipamento, numero ou fabricante...'
    )
    expect(searchInput).toBeInTheDocument()
  })
})
