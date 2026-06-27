import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { InvoiceExtraction } from './InvoiceExtraction'
import type { Extraction } from '@/types'

function makeExtraction(data: Record<string, unknown>): Extraction {
  return {
    id: 'e1',
    document_id: 'd1',
    data,
    missing_fields: [],
    model: 'mock',
    confidence: 0.9,
    created_at: '2026-01-01T00:00:00Z',
  }
}

describe('InvoiceExtraction', () => {
  it('renders vendor, number, line items and totals for invoice data', () => {
    const extraction = makeExtraction({
      invoice_number: 'INV-2024-0042',
      issue_date: '2024-05-01',
      due_date: null,
      vendor_name: 'Acme Supplies Ltd',
      vendor_address: null,
      bill_to: 'Globex Corp',
      currency: 'USD',
      subtotal: 1000,
      tax: 250,
      total: 1250,
      line_items: [
        { description: 'Widget', quantity: 3, unit_price: 10, amount: 30 },
      ],
    })

    render(<InvoiceExtraction extraction={extraction} />)

    expect(screen.getByText('Acme Supplies Ltd')).toBeInTheDocument()
    expect(screen.getByText('#INV-2024-0042')).toBeInTheDocument()
    expect(screen.getByText('Globex Corp')).toBeInTheDocument()
    expect(screen.getByText('Widget')).toBeInTheDocument()
    // Grand total is formatted with currency + 2 decimals.
    expect(screen.getByText('USD 1,250.00')).toBeInTheDocument()
  })

  it('falls back to a JSON view when the shape is not an invoice', () => {
    const extraction = makeExtraction({ something_else: 'value' })
    render(<InvoiceExtraction extraction={extraction} />)
    expect(screen.getByText(/something_else/)).toBeInTheDocument()
  })
})
