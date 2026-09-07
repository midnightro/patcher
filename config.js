/* MIDNIGHT RO launcher - editable content.
   Plain ES5 assigned to a global: rpatchur renders the UI in MSHTML (IE11 mode),
   where fetch() does not exist and XHR on a file:// page is blocked, so the news
   cannot be loaded from JSON at runtime. Edit this file to change the news; it
   ships with the launcher and is hand-delivered like the rest of launcher_ui.

   `tag` picks the pill colour: update | event | patch. */
var LAUNCHER_CONFIG = {
    news: [
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
    ],

    /* Where the launcher looks for fresher news each time it opens.
       The list above is the offline fallback: whatever ships in this file is
       shown immediately, then replaced if the download succeeds. Set to '' to
       switch the feature off and always use the bundled list.

       It is loaded as a <script>, not fetched: this page runs from file:// in
       MSHTML, where fetch() does not exist and cross-origin XHR is blocked, but
       a script tag is not subject to either. The file must therefore be
       JavaScript that assigns window.LAUNCHER_NEWS - see tools/patcher/news.js. */
    newsUrl: 'https://github.com/midnightro/patcher/' +
        'releases/download/patches/news.js',
    newsTimeoutMs: 4000,

    /* Dynamic patch number shown after verification. This is a script rather
       than XHR/JSON because MSHTML blocks cross-origin XHR to release assets.
       The bundled values are only an offline fallback. */
    patchStatusUrl: 'https://github.com/midnightro/patcher/' +
        'releases/download/patches/patch_status.js',
    bundledPatchIndex: 35,
    bundledPatchFile: '0035_20260830_dynamic-launcher-patch-status.thor',

    /* Leave empty to keep the button showing "ยังไม่เปิดให้บริการ".
       rpatchur has no command for opening a browser, so a real URL here still
       needs the launcher to gain that ability first - see the note in
       changelog/03-client-grf-lua.md before filling these in. */
    websiteUrl: 'https://midnight-ro.divlab.co',
    registerUrl: 'https://midnight-ro.divlab.co'
};
