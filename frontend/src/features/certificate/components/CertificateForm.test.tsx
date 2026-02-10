import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/test/utils'
import userEvent from '@testing-library/user-event'
import { CertificateForm } from './CertificateForm'
import type { Certificate } from '../api/certificateApi'

// ---- Mock the mutation hooks ----

const mockCreateMutateAsync = vi.fn()
const mockUpdateMutateAsync = vi.fn()

vi.mock('../hooks/useCertificates', () => ({
  useCreateCertificate: vi.fn(() => ({
    mutateAsync: mockCreateMutateAsync,
    isPending: false,
  })),
  useUpdateCertificate: vi.fn(() => ({
    mutateAsync: mockUpdateMutateAsync,
    isPending: false,
  })),
}))

// ---- Fixtures ----

const existingCert: Certificate = {
  id: 'cert-edit-1',
  tenant_id: 'tenant-1',
  equipment_name: 'Termopar Tipo K',
  certificate_number: 'CAL-2024-050',
  manufacturer: 'Omega',
  model: 'TK-200',
  serial_number: 'SN-OMEGA-99',
  laboratory: 'Lab Calibra',
  calibration_date: '2024-03-01',
  expiry_date: '2025-03-01',
  file_key: null,
  status: 'valid',
  is_active: true,
  created_at: '2024-03-01T10:00:00Z',
  updated_at: '2024-03-01T10:00:00Z',
}

describe('CertificateForm', () => {
  const onClose = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders all form fields when open in create mode', () => {
    render(<CertificateForm isOpen={true} onClose={onClose} />)

    expect(screen.getByLabelText(/Nome do Equipamento/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Numero do Certificado/)).toBeInTheDocument()
    expect(screen.getByLabelText('Fabricante')).toBeInTheDocument()
    expect(screen.getByLabelText('Modelo')).toBeInTheDocument()
    expect(screen.getByLabelText('Numero de Serie')).toBeInTheDocument()
    expect(screen.getByLabelText('Laboratorio')).toBeInTheDocument()
    expect(screen.getByLabelText(/Data de Calibracao/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Data de Validade/)).toBeInTheDocument()
    expect(screen.getByLabelText('Status')).toBeInTheDocument()
    expect(screen.getByText('Novo Certificado')).toBeInTheDocument()
    expect(screen.getByText('Criar Certificado')).toBeInTheDocument()
  })

  it('shows validation errors for required fields on empty submit', async () => {
    render(<CertificateForm isOpen={true} onClose={onClose} />)

    const user = userEvent.setup()
    const submitButton = screen.getByText('Criar Certificado')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Nome do equipamento e obrigatorio')).toBeInTheDocument()
    })
    expect(screen.getByText('Numero do certificado e obrigatorio')).toBeInTheDocument()
    expect(screen.getByText('Data de calibracao e obrigatoria')).toBeInTheDocument()
    expect(screen.getByText('Data de validade e obrigatoria')).toBeInTheDocument()
  })

  it('calls create API with correct data on valid submit', async () => {
    mockCreateMutateAsync.mockResolvedValue({})

    render(<CertificateForm isOpen={true} onClose={onClose} />)

    const user = userEvent.setup()

    await user.type(screen.getByLabelText(/Nome do Equipamento/), 'Multimetro Digital')
    await user.type(screen.getByLabelText(/Numero do Certificado/), 'CAL-2024-100')
    await user.type(screen.getByLabelText('Fabricante'), 'Fluke')
    await user.type(screen.getByLabelText('Modelo'), '87V')
    await user.type(screen.getByLabelText(/Data de Calibracao/), '2024-06-01')
    await user.type(screen.getByLabelText(/Data de Validade/), '2025-06-01')

    const submitButton = screen.getByText('Criar Certificado')
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockCreateMutateAsync).toHaveBeenCalledTimes(1)
    })

    const callArg = mockCreateMutateAsync.mock.calls[0][0]
    expect(callArg.equipment_name).toBe('Multimetro Digital')
    expect(callArg.certificate_number).toBe('CAL-2024-100')
    expect(callArg.manufacturer).toBe('Fluke')
    expect(callArg.model).toBe('87V')
    expect(callArg.calibration_date).toBe('2024-06-01')
    expect(callArg.expiry_date).toBe('2025-06-01')

    // Should close the form after successful create
    expect(onClose).toHaveBeenCalled()
  })

  it('populates form with existing data in edit mode', () => {
    render(
      <CertificateForm isOpen={true} onClose={onClose} certificate={existingCert} />
    )

    expect(screen.getByText('Editar Certificado')).toBeInTheDocument()
    expect(screen.getByText('Salvar Alteracoes')).toBeInTheDocument()

    expect(screen.getByLabelText(/Nome do Equipamento/)).toHaveValue('Termopar Tipo K')
    expect(screen.getByLabelText(/Numero do Certificado/)).toHaveValue('CAL-2024-050')
    expect(screen.getByLabelText('Fabricante')).toHaveValue('Omega')
    expect(screen.getByLabelText('Modelo')).toHaveValue('TK-200')
    expect(screen.getByLabelText('Numero de Serie')).toHaveValue('SN-OMEGA-99')
    expect(screen.getByLabelText('Laboratorio')).toHaveValue('Lab Calibra')
    expect(screen.getByLabelText(/Data de Calibracao/)).toHaveValue('2024-03-01')
    expect(screen.getByLabelText(/Data de Validade/)).toHaveValue('2025-03-01')
  })

  it('cancel button calls onClose', async () => {
    render(<CertificateForm isOpen={true} onClose={onClose} />)

    const user = userEvent.setup()
    await user.click(screen.getByText('Cancelar'))

    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('returns null when isOpen is false', () => {
    const { container } = render(
      <CertificateForm isOpen={false} onClose={onClose} />
    )

    expect(container.innerHTML).toBe('')
  })
})
