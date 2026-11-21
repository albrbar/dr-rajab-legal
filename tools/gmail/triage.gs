/**
 * Gmail triage — Google Apps Script (يعمل داخل حسابك، بلا توكن Claude).
 *
 * التثبيت: script.google.com ← New project ← الصق هذا الملف ← Save ← شغّل الدالة المطلوبة
 * (أول تشغيل يطلب إذن Gmail؛ الكود يعمل على حسابك أنت فقط).
 *
 * الترتيب الموصى به:
 *   1) classifyAll()     يصنّف الصندوق كله بدفعات من 100 محادثة (قراءة جماعية للمرسلين).
 *   2) previewTrash()    يعرض كم محادثة وأي مرسلين سيُحذفون، دون حذف.
 *   3) trashJunk()       ينقل Auto/1-Junk-ForDelete إلى Trash (قابل للاسترجاع 30 يومًا).
 *   4) installDailyTrigger()  تشغيل يومي تلقائي (يصنّف الجديد، ويحذف الإعلانات الأقدم من يومين).
 *
 * قواعد الأمان:
 *  - الحذف = نقل إلى Trash فقط (ليس حذفًا نهائيًا). Gmail يفرغه تلقائيًا بعد 30 يومًا.
 *  - لا يُحذف أبدًا ما عليه Accounts/Work/Private/Review أو ما فيه نجمة.
 *  - لا يُقرأ نص أي رسالة: المرسل والفئة فقط.
 *  - غير المحسوم يذهب إلى Auto/5-Review ولا يُحذف.
 */

const CFG = {
  LABELS: {
    junk: 'Auto/1-Junk-ForDelete',
    work: 'Auto/2-Work-Useful',
    priv: 'Auto/3-Private',
    acct: 'Auto/4-Accounts-Security',
    review: 'Auto/5-Review',
  },
  // مجلداتك المرتبة يدويًا: تُستثنى من التصنيف كليًا (بأسماء البحث).
  SKIP_USER_LABELS: ['work', 'personal', 'مخزن', 'gre', '2015-7', 'travel', 'usa-fellowship', 'english', 'receipts'],
  BATCH: 100,                   // أقصى حجم دفعة تقبله GmailApp
  MAX_RUNTIME_MS: 5 * 60 * 1000, // حد أمان قبل مهلة 6 دقائق
};

// الترتيب مهم: الحسابات أولًا، ثم العمل، ثم الإعلانات المعروفة.
const RULES = {
  acct: /security@|accounts\.google\.com|noreply-accounts|binance|paypal|stripe|billing|invoice|receipt|payments?@|\bbank\b|verify|verification|password/i,
  work: /businessprofile|calendar-notification|@github\.com|vercel\.com|notion\.(so|com)|metricool|slack\.com|zapier|canva|tiktok|windsor|supermetrics|hospital|clinic|مستشفى|عيادة/i,
  junk: /alibaba\.com|medi-jobs|medshr|beehiiv|jobalert|jobalerts|linkedin\.com|indeed\.com|redditmail|substack|mailchimp|newsletter|duolingo|coingecko|forbes|brizy|tm\.openai\.com|sider\.ai|n8n\.cloud|twin\.so|macaly|jam\.dev|tsboi|gitlab\.com|yahoogroups|marketing@|promo|deals?@|offers?@/i,
};

// ---------- أدوات مساعدة ----------

function searchName_(fullName) {
  return fullName.toLowerCase().replace(/[\s/]+/g, '-'); // يطابق صيغة label: في بحث Gmail
}

function exclusions_() {
  const mine = Object.values(CFG.LABELS).map((n) => '-label:' + searchName_(n));
  const user = CFG.SKIP_USER_LABELS.map((n) => '-label:' + n);
  return mine.concat(user).join(' ');
}

function label_(name) {
  return GmailApp.getUserLabelByName(name) || GmailApp.createLabel(name);
}

function bucketFor_(from, defaultBucket) {
  if (RULES.acct.test(from)) return 'acct';
  if (RULES.work.test(from)) return 'work';
  if (RULES.junk.test(from)) return 'junk';
  return defaultBucket;
}

/**
 * يصنّف كل ما يطابق الاستعلام. كل محادثة تأخذ label واحدًا فتخرج من الاستعلام،
 * فنكرر الدورة حتى لا تبقى نتائج. قراءة المرسلين جماعية: استدعاء واحد لكل 100 محادثة.
 */
function classifyQuery_(query, defaultBucket, started) {
  const counts = { junk: 0, work: 0, priv: 0, acct: 0, review: 0 };
  const labels = {};
  Object.keys(CFG.LABELS).forEach((k) => (labels[k] = label_(CFG.LABELS[k])));

  while (Date.now() - started < CFG.MAX_RUNTIME_MS) {
    const threads = GmailApp.search(query + ' ' + exclusions_(), 0, CFG.BATCH);
    if (!threads.length) return { counts: counts, done: true };

    const messages = GmailApp.getMessagesForThreads(threads); // قراءة جماعية
    const groups = { junk: [], work: [], priv: [], acct: [], review: [] };
    threads.forEach((t, i) => {
      const first = messages[i][0];
      const from = first ? first.getFrom() : '';
      groups[bucketFor_(from, defaultBucket)].push(t);
    });
    Object.keys(groups).forEach((k) => {
      if (groups[k].length) {
        labels[k].addToThreads(groups[k]); // وسم جماعي
        counts[k] += groups[k].length;
      }
    });
  }
  return { counts: counts, done: false };
}

function merge_(a, b) {
  Object.keys(b).forEach((k) => (a[k] = (a[k] || 0) + b[k]));
  return a;
}

// ---------- الدوال التي تشغّلها ----------

function classifyAll() {
  runClassify_('');
}

function runClassify_(extra) {
  const started = Date.now();
  const total = {};
  let finished = true;
  const sweeps = [
    ['in:inbox (category:promotions OR category:social) ' + extra, 'junk'],
    ['in:inbox category:updates ' + extra, 'review'],
    ['in:inbox ' + extra, 'review'], // الباقي (Primary وغيره): الأشخاص يذهبون للمراجعة
  ];
  for (const [q, def] of sweeps) {
    const r = classifyQuery_(q, def, started);
    merge_(total, r.counts);
    if (!r.done) { finished = false; break; }
  }
  Logger.log('classified: ' + JSON.stringify(total) + (finished ? ' | DONE' : ' | TIME LIMIT — شغّل الدالة مرة أخرى'));
}

function junkQuery_(minAgeDays) {
  const keep = ['work', 'priv', 'acct', 'review'].map((k) => '-label:' + searchName_(CFG.LABELS[k])).join(' ');
  const age = minAgeDays > 0 ? ' older_than:' + minAgeDays + 'd' : '';
  return 'label:' + searchName_(CFG.LABELS.junk) + ' ' + keep + ' -is:starred' + age;
}

function previewTrash() {
  const threads = GmailApp.search(junkQuery_(0), 0, 500);
  const bySender = {};
  GmailApp.getMessagesForThreads(threads).forEach((m) => {
    const f = (m[0] ? m[0].getFrom() : '?').replace(/.*<|>.*/g, '');
    bySender[f] = (bySender[f] || 0) + 1;
  });
  const top = Object.entries(bySender).sort((a, b) => b[1] - a[1]).slice(0, 25);
  Logger.log('سيُنقل إلى Trash (أول 500 فقط): ' + threads.length + '\n' + top.map((x) => x[1] + '  ' + x[0]).join('\n'));
}

function trashJunk(minAgeDays) {
  const started = Date.now();
  let n = 0;
  while (Date.now() - started < CFG.MAX_RUNTIME_MS) {
    const threads = GmailApp.search(junkQuery_(minAgeDays || 0), 0, CFG.BATCH);
    if (!threads.length) break;
    GmailApp.moveThreadsToTrash(threads); // 100 محادثة في استدعاء واحد
    n += threads.length;
  }
  Logger.log('moved to Trash: ' + n + ' (قابل للاسترجاع 30 يومًا)');
}

function dailyRun() {
  runClassify_('newer_than:3d');
  trashJunk(2); // الإعلانات الأقدم من يومين فقط، لتبقى نافذة للإنقاذ
}

function installDailyTrigger() {
  ScriptApp.getProjectTriggers().filter((t) => t.getHandlerFunction() === 'dailyRun').forEach(ScriptApp.deleteTrigger);
  ScriptApp.newTrigger('dailyRun').timeBased().everyDays(1).atHour(3).create();
  Logger.log('daily trigger installed (03:00)');
}
