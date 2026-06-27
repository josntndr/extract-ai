import { describe, it, expect } from 'vitest'
import { formatBytes, formatConfidence, humanize } from './utils'

describe('formatBytes', () => {
  it('formats zero and bytes', () => {
    expect(formatBytes(0)).toBe('0 B')
    expect(formatBytes(512)).toBe('512 B')
  })

  it('scales to KB / MB', () => {
    expect(formatBytes(1024)).toBe('1 KB')
    expect(formatBytes(1_500_000)).toBe('1.4 MB')
  })
})

describe('formatConfidence', () => {
  it('renders a dash for null/undefined', () => {
    expect(formatConfidence(null)).toBe('—')
    expect(formatConfidence(undefined)).toBe('—')
  })

  it('renders a rounded percentage', () => {
    expect(formatConfidence(0.873)).toBe('87%')
    expect(formatConfidence(1)).toBe('100%')
  })
})

describe('humanize', () => {
  it('title-cases snake_case tokens', () => {
    expect(humanize('business_report')).toBe('Business Report')
  })

  it('upper-cases PDF and OCR', () => {
    expect(humanize('native_pdf')).toBe('Native PDF')
    expect(humanize('scanned_ocr')).toBe('Scanned OCR')
  })
})
