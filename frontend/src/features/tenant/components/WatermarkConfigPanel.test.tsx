import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/test/utils'
import userEvent from '@testing-library/user-event'
import { WatermarkConfigPanel } from './WatermarkConfigPanel'
import type { WatermarkConfig } from '../types'

// ---- Mock the tenant API ----

const mockMutateAsync = vi.fn()

vi.mock('../api', () => ({
  useUpdateBranding: vi.fn(() => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
    isError: false,
  })),
}))

// ---- Fixtures ----

const fullConfig: WatermarkConfig = {
  logo: true,
  gps: true,
  datetime: true,
  company_name: true,
  report_number: false,
  technician_name: true,
}

describe('WatermarkConfigPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockMutateAsync.mockResolvedValue({})
  })

  it('renders all toggle switches with correct default states', () => {
    render(<WatermarkConfigPanel currentConfig={fullConfig} />)

    // All 6 toggle fields should be visible
    expect(screen.getByText('Logo da Empresa')).toBeInTheDocument()
    expect(screen.getByText('Coordenadas GPS')).toBeInTheDocument()
    expect(screen.getByText('Data/Hora')).toBeInTheDocument()
    expect(screen.getByText('Nome da Empresa')).toBeInTheDocument()
    expect(screen.getByText('Numero do Relatorio')).toBeInTheDocument()
    expect(screen.getByText('Nome do Tecnico')).toBeInTheDocument()

    // Check the switch states via aria-checked
    const switches = screen.getAllByRole('switch')
    expect(switches).toHaveLength(6)

    // Verify specific switch states match the config
    expect(screen.getByRole('switch', { name: 'Logo da Empresa' })).toHaveAttribute('aria-checked', 'true')
    expect(screen.getByRole('switch', { name: 'Coordenadas GPS' })).toHaveAttribute('aria-checked', 'true')
    expect(screen.getByRole('switch', { name: 'Data/Hora' })).toHaveAttribute('aria-checked', 'true')
    expect(screen.getByRole('switch', { name: 'Nome da Empresa' })).toHaveAttribute('aria-checked', 'true')
    expect(screen.getByRole('switch', { name: 'Numero do Relatorio' })).toHaveAttribute('aria-checked', 'false')
    expect(screen.getByRole('switch', { name: 'Nome do Tecnico' })).toHaveAttribute('aria-checked', 'true')
  })

  it('toggle switches change state on click', async () => {
    render(<WatermarkConfigPanel currentConfig={fullConfig} />)

    const user = userEvent.setup()

    // GPS is initially ON (true)
    const gpsSwitch = screen.getByRole('switch', { name: 'Coordenadas GPS' })
    expect(gpsSwitch).toHaveAttribute('aria-checked', 'true')

    // Click to toggle it OFF
    await user.click(gpsSwitch)
    expect(gpsSwitch).toHaveAttribute('aria-checked', 'false')

    // Click again to toggle it back ON
    await user.click(gpsSwitch)
    expect(gpsSwitch).toHaveAttribute('aria-checked', 'true')

    // Toggle "Numero do Relatorio" from OFF to ON
    const reportSwitch = screen.getByRole('switch', { name: 'Numero do Relatorio' })
    expect(reportSwitch).toHaveAttribute('aria-checked', 'false')
    await user.click(reportSwitch)
    expect(reportSwitch).toHaveAttribute('aria-checked', 'true')
  })

  it('save button calls updateBranding API with the correct config', async () => {
    render(<WatermarkConfigPanel currentConfig={fullConfig} />)

    const user = userEvent.setup()

    // Toggle GPS off before saving
    await user.click(screen.getByRole('switch', { name: 'Coordenadas GPS' }))

    // Click save
    await user.click(screen.getByText('Salvar Configuracao'))

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalledTimes(1)
    })

    const savedConfig = mockMutateAsync.mock.calls[0][0]
    expect(savedConfig).toEqual({
      watermark_config: {
        logo: true,
        gps: false, // toggled off
        datetime: true,
        company_name: true,
        report_number: false,
        technician_name: true,
      },
    })
  })

  it('shows success message after save', async () => {
    render(<WatermarkConfigPanel currentConfig={fullConfig} />)

    const user = userEvent.setup()

    // Should not show success message initially
    expect(screen.queryByText('Configuracao salva com sucesso!')).not.toBeInTheDocument()

    // Click save
    await user.click(screen.getByText('Salvar Configuracao'))

    await waitFor(() => {
      expect(screen.getByText('Configuracao salva com sucesso!')).toBeInTheDocument()
    })
  })

  it('handles null currentConfig by using default values', () => {
    render(<WatermarkConfigPanel currentConfig={null} />)

    // With defaults: logo=true, gps=true, datetime=true, company_name=true,
    //   report_number=false, technician_name=true
    expect(screen.getByRole('switch', { name: 'Logo da Empresa' })).toHaveAttribute('aria-checked', 'true')
    expect(screen.getByRole('switch', { name: 'Coordenadas GPS' })).toHaveAttribute('aria-checked', 'true')
    expect(screen.getByRole('switch', { name: 'Data/Hora' })).toHaveAttribute('aria-checked', 'true')
    expect(screen.getByRole('switch', { name: 'Nome da Empresa' })).toHaveAttribute('aria-checked', 'true')
    expect(screen.getByRole('switch', { name: 'Numero do Relatorio' })).toHaveAttribute('aria-checked', 'false')
    expect(screen.getByRole('switch', { name: 'Nome do Tecnico' })).toHaveAttribute('aria-checked', 'true')
  })

  it('calls onSaved callback after successful save', async () => {
    const onSaved = vi.fn()
    render(<WatermarkConfigPanel currentConfig={fullConfig} onSaved={onSaved} />)

    const user = userEvent.setup()
    await user.click(screen.getByText('Salvar Configuracao'))

    await waitFor(() => {
      expect(onSaved).toHaveBeenCalledTimes(1)
    })
  })
})
