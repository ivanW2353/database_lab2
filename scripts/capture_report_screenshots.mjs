import { mkdir } from 'node:fs/promises'
import { resolve } from 'node:path'

const playwrightPath = `${process.env.TEMP.replaceAll('\\', '/')}/database_lab2_capture/node_modules/playwright-core/index.mjs`
const { chromium } = await import(`file:///${playwrightPath}`)

const baseUrl = 'http://127.0.0.1:5173'
const outputDir = resolve('docs/screenshots')
const edgePath = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'

await mkdir(outputDir, { recursive: true })

const browser = await chromium.launch({
  executablePath: edgePath,
  headless: true,
  args: ['--disable-gpu']
})

async function shot(page, name) {
  await page.waitForTimeout(800)
  await page.waitForLoadState('networkidle')
  await page.screenshot({ path: resolve(outputDir, name), fullPage: true })
}

async function login(page, role, login) {
  await page.goto(baseUrl)
  await page.locator('select').selectOption(role)
  await page.locator('input').nth(0).fill(login)
  await page.locator('input').nth(1).fill('123456')
  await page.getByRole('button', { name: '登录', exact: true }).click()
  await page.waitForLoadState('networkidle')
}

async function go(page, label) {
  await page.getByRole('button', { name: label, exact: true }).click()
  await page.waitForTimeout(800)
  await page.waitForLoadState('networkidle')
}

const loginContext = await browser.newContext({ viewport: { width: 1440, height: 1000 } })
const loginPage = await loginContext.newPage()
await loginPage.goto(baseUrl)
await shot(loginPage, '01-login.png')
await loginContext.close()

const studentContext = await browser.newContext({ viewport: { width: 1440, height: 1000 } })
const studentPage = await studentContext.newPage()
await login(studentPage, 'student', 'pb22000001')
await shot(studentPage, '02-student-dashboard.png')

await go(studentPage, '图书检索')
await shot(studentPage, '04-book-search.png')

await go(studentPage, '我的借阅')
await shot(studentPage, '06-student-borrows.png')

await go(studentPage, '我的预约')
await shot(studentPage, '07-student-reservations.png')

await go(studentPage, '违期记录')
await shot(studentPage, '08-student-overdue.png')
await studentContext.close()

const adminContext = await browser.newContext({ viewport: { width: 1440, height: 1000 } })
const adminPage = await adminContext.newPage()
await login(adminPage, 'librarian', 'admin')
await shot(adminPage, '03-admin-dashboard.png')

await go(adminPage, '图书管理')
const firstBookDetail = adminPage.getByRole('button', { name: '详情', exact: true }).first()
if (await firstBookDetail.count()) await firstBookDetail.click()
await adminPage.waitForTimeout(500)
await shot(adminPage, '05-admin-book-detail.png')
if (await adminPage.getByRole('button', { name: '关闭', exact: true }).count()) {
  await adminPage.getByRole('button', { name: '关闭', exact: true }).click()
}

await go(adminPage, '学生管理')
const firstStudentDetail = adminPage.getByRole('button', { name: '详情', exact: true }).first()
if (await firstStudentDetail.count()) await firstStudentDetail.click()
await adminPage.waitForTimeout(500)
await shot(adminPage, '09-admin-students.png')
if (await adminPage.getByRole('button', { name: '关闭', exact: true }).count()) {
  await adminPage.getByRole('button', { name: '关闭', exact: true }).click()
}

await go(adminPage, '管理员管理')
await shot(adminPage, '10-admin-librarians.png')

await go(adminPage, '还书')
await shot(adminPage, '11-admin-return.png')

await go(adminPage, '预约')
await shot(adminPage, '12-admin-reservations.png')

await go(adminPage, '违期')
await shot(adminPage, '13-admin-overdue.png')

await adminContext.close()
await browser.close()
