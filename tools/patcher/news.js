/* MIDNIGHT RO - launcher news feed.
 *
 * The launcher pulls this file every time it opens and shows whatever is here,
 * so the news can change without sending anyone a new launcher_ui. Edit, upload,
 * done - players see it the next time they open the launcher.
 *
 * Publish with:
 *   gh release upload patches tools/patcher/news.js \
 *      --repo midnightro/patcher --clobber
 *
 * Rules, because this is loaded as a <script> into MSHTML (IE11 mode):
 *   * plain ES5 only - no let/const, no arrow functions, no trailing commas
 *   * save as UTF-8 (this file is fetched over HTTP, not read as CP874)
 *   * only the first three items are displayed; the rest are ignored
 *   * `tag` must be one of: update | event | patch  (it picks the pill colour)
 *   * a syntax error here means players silently keep the news bundled in their
 *     launcher_ui/config.js - it never breaks the launcher, but it also never
 *     tells you it failed, so check the file parses before uploading
 */
window.LAUNCHER_NEWS = {
    updated: '2026-08-20',
    items: [
        {
            tag: 'update',
            title: 'Episode 5.0 : Dawn of Morroc',
            body: 'เปิดโลกใบใหม่ พร้อมภารกิจและดันเจี้ยนสุดท้าทาย',
            date: '18/05/2024'
        },
        {
            tag: 'event',
            title: 'Morroc Login Event',
            body: 'ล็อกอินรับไอเทมพิเศษทุกวัน ตลอดเดือนพฤษภาคม!',
            date: '18/05/2024'
        },
        {
            tag: 'patch',
            title: 'Patch Update 5.0.1',
            body: 'แก้ไขปัญหา ปรับปรุงระบบ และอัปเดตเพิ่มเติม',
            date: '17/05/2024'
        }
    ]
};
