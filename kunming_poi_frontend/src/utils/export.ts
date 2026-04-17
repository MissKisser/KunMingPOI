/**
 * 数据导出工具函数
 * 支持 CSV 和 JSON 格式导出
 * @author Hackerdallas
 */

/**
 * 导出数据为 CSV 文件
 * @param data 数据数组
 * @param filename 文件名（不含扩展名）
 * @param columns 可选的列配置
 */
export function exportToCSV<T extends Record<string, any>>(
  data: T[],
  filename: string,
  columns?: { key: keyof T; label: string }[]
): void {
  if (!data.length) {
    console.warn('没有数据可导出')
    return
  }

  const keys: (keyof T)[] = columns?.map(c => c.key) ?? Object.keys(data[0] as object) as (keyof T)[]
  const headers: string[] = columns?.map(c => c.label) ?? (keys as string[])

  const csvContent = [
    headers.join(','),
    ...data.map(row =>
      keys.map(key => {
        const value = row[key]
        if (value === null || value === undefined) return ''
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`
        }
        return String(value)
      }).join(',')
    )
  ].join('\n')

  downloadFile(csvContent, `${filename}.csv`, 'text/csv;charset=utf-8')
}

/**
 * 导出数据为 JSON 文件
 * @param data 数据
 * @param filename 文件名（不含扩展名）
 */
export function exportToJSON<T>(data: T, filename: string): void {
  const jsonContent = JSON.stringify(data, null, 2)
  downloadFile(jsonContent, `${filename}.json`, 'application/json;charset=utf-8')
}

/**
 * 下载文件
 */
function downloadFile(content: string, filename: string, mimeType: string): void {
  const blob = new Blob(['\ufeff' + content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * 格式化日期时间用于文件名
 */
export function formatDateTimeForFilename(): string {
  const now = new Date()
  return `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}`
}
