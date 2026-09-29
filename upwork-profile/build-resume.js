const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, BorderStyle, AlignmentType, LevelFormat, TabStopType,
} = require("docx");

const FONT = "Arial";
const NAVY = "1F3A5F";
const GRAY = "555555";
const CONTENT_W = 12240 - 2 * 1008; // Letter width minus 0.7" margins
const BODY = 19; // 9.5pt

const run = (text, opts = {}) => new TextRun({ text, font: FONT, size: BODY, ...opts });

const sectionHeading = (text) =>
  new Paragraph({
    spacing: { before: 200, after: 80 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: NAVY, space: 2 } },
    children: [run(text.toUpperCase(), { bold: true, size: 21, color: NAVY, characterSpacing: 30 })],
  });

// Left text with right-aligned text on the same line
const splitLine = (leftRuns, rightText, opts = {}) =>
  new Paragraph({
    tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }],
    spacing: { before: opts.before ?? 0, after: opts.after ?? 0 },
    keepNext: true,
    children: [...leftRuns, run("\t"), run(rightText, { color: GRAY, ...(opts.rightOpts || {}) })],
  });

const bullet = (label, text) =>
  new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 40, line: 264 },
    children: label ? [run(label + ": ", { bold: true }), run(text)] : [run(text)],
  });

const para = (children, opts = {}) =>
  new Paragraph({ spacing: { after: 60, line: 264, ...(opts.spacing || {}) }, alignment: opts.alignment, children });

const company = (name, location, before = 140) =>
  splitLine([run(name, { bold: true, size: 20, color: NAVY })], location, { before });

const role = (title, dates) =>
  splitLine([run(title, { bold: true, italics: true })], dates, { after: 20, rightOpts: { italics: false } });

const descriptor = (text) =>
  new Paragraph({ spacing: { after: 50 }, keepNext: true, children: [run(text, { italics: true, color: GRAY, size: 18 })] });

// Areas of expertise: borderless 3-column grid
const expertise = [
  "Japan Market Entry Strategy", "Healthcare Market Research", "Go-to-Market Strategy",
  "Physician & KOL Engagement", "Business Planning & KPI Design", "Partnership & Alliance Development",
  "Medical Congress & Event Marketing", "Salesforce / CRM Adoption", "Cross-border Coordination",
];
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const cellBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };
const colW = Math.floor(CONTENT_W / 3);
const colWidths = [colW, colW, CONTENT_W - 2 * colW];
const expertiseTable = new Table({
  width: { size: CONTENT_W, type: WidthType.DXA },
  columnWidths: colWidths,
  borders: { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder, insideHorizontal: noBorder, insideVertical: noBorder },
  rows: [0, 1, 2].map((r) =>
    new TableRow({
      children: [0, 1, 2].map((c) =>
        new TableCell({
          width: { size: colWidths[c], type: WidthType.DXA },
          borders: cellBorders,
          margins: { top: 20, bottom: 20, left: 0, right: 80 },
          children: [new Paragraph({ children: [run("▪ ", { color: NAVY }), run(expertise[r * 3 + c])] })],
        })
      ),
    })
  ),
});

const children = [
  // Header
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 40 },
    children: [run("MEGUMI KURAMITSU", { bold: true, size: 40, color: NAVY, characterSpacing: 60 })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 40 },
    children: [run("Japan Market Entry Advisor  |  Healthcare, Pharma & MedTech", { size: 21, color: GRAY })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 60 },
    children: [run("Tokyo, Japan   •   megumik0727@gmail.com   •   Japanese / English", { size: 18, color: GRAY })],
  }),

  sectionHeading("Professional Summary"),
  para([
    run(
      "Bilingual (Japanese/English) healthcare business professional with 15 years of experience across management consulting, " +
      "healthcare IT, pharmaceutical marketing, and global enterprise sales in Japan. Combines a working understanding of Japan's " +
      "healthcare stakeholders, including physicians, KOLs, hospitals, pharmaceutical companies, and medical device manufacturers, with " +
      "cross-border experience as the Japan-side counterpart to a leading US telehealth company. Available for project-based advisory " +
      "engagements on Japan market entry, market research, and go-to-market strategy."
    ),
  ], { alignment: AlignmentType.JUSTIFIED }),

  sectionHeading("Areas of Expertise"),
  expertiseTable,

  sectionHeading("Selected Achievements"),
  bullet(null, "Served as the Japan-side counterpart to Teladoc Health, Inc. (US) for its telehealth business in Japan, covering business planning, KPI design, and localization of clinical case materials."),
  bullet(null, "Led the PMO that replaced a 30-year-old legacy sales system with Salesforce at Kawasaki Heavy Industries' Robot Division."),
  bullet(null, "Won a global WAN RFP that contributed JPY 214 million in revenue and received the FY2012 Top Enterprise Sales Award at SoftBank."),
  bullet(null, "Conducted healthcare feasibility research at PwC, including analysis of local health systems and interviews with overseas medical institutions."),

  sectionHeading("Professional Experience"),

  company("Medii, Inc.", "Tokyo, Japan", 60),
  role("Project Manager, Pharma Excellence Division", "Feb 2025 – Present"),
  descriptor("Health-tech company operating Medii E-Consult, an online specialist consultation platform for physicians, and Medii Q, an AI search tool for clinical questions."),
  bullet(null, "Plan and manage disease-specific marketing programs in partnership with pharmaceutical companies."),
  bullet(null, "Extend specialist expertise to primary care physicians to support earlier diagnosis and treatment of rare and hard-to-diagnose diseases."),

  company("WeMex Co., Ltd.", "Tokyo, Japan"),
  role("Business Planning & Promotion, Healthcare IT Division", "Nov 2021 – Jan 2025"),
  descriptor("Healthcare IT division offering telehealth solutions to hospitals in Japan."),
  bullet("Business planning", "Developed the telehealth business plan, set KGIs and KPIs, and managed progress; defined Salesforce requirements for KPI data collection."),
  bullet("US partner management", "Served as the Japan-side counterpart to Teladoc Health, Inc., coordinating product and clinical case information and securing US physicians as speakers for Japanese seminars."),
  bullet("Alliances", "Established sales alliances with medical device manufacturers."),
  bullet("Marketing", "Led medical congress exhibitions from planning through lead conversion, along with product launches, media events, webinars, white papers, press releases, and website lead generation."),
  bullet("Hospital sales", "Designed a telehealth trial with a university hospital's medical DX department, defining evaluation criteria and target outcomes, analyzing outcome data, and supporting the process through institutional purchase approval."),
  bullet("Demand generation", "Generated sales opportunities through outbound campaigns and a nationwide physician survey conducted with key opinion leaders."),

  company("Kawasaki Heavy Industries, Ltd.", "Tokyo, Japan"),
  role("Sales Planning, Robot Division", "Jul 2017 – Oct 2021"),
  bullet("Salesforce PMO (2019–2020)", "Led the PMO and system administration for migrating the lead-to-order process from a 30-year-old in-house system to Salesforce. Simplified sales data entry and secured buy-in from a resistant sales organization through adoption design."),
  bullet("Marketing communications", "Managed the planning and production of the division website, product catalogs, exhibition brochures, and commemorative publications."),
  bullet("Corporate events", "Directed planning and on-site operations for press conferences, distributor meetings, and anniversary ceremonies."),

  company("PwC Aarata LLC", "Tokyo, Japan"),
  role("Associate, Sustainability Team", "Jan 2015 – Jun 2017"),
  bullet(null, "Supported the secretariat of a government-affiliated public-private program that helps Japanese companies launch base-of-the-pyramid (BOP) businesses in emerging markets, advising on program strategy and operations as an intermediary between the public and private sectors."),
  bullet(null, "Conducted research engagements in Bangladesh for the Ministry of Economy, Trade and Industry (METI) and the Cabinet Office of Japan."),
  bullet(null, "Performed healthcare feasibility research for a new business, including analysis of local health systems and interviews with overseas medical institutions."),

  company("SoftBank Corp. (formerly SoftBank Telecom Corp.)", "Tokyo, Japan"),
  role("Global Sales Representative", "Aug 2011 – Dec 2014"),
  role("Account Sales", "Apr 2011 – Aug 2011"),
  bullet(null, "Sold global data network services, including global MPLS, Internet VPN, and overseas data centers, to large Japanese and multinational corporations, split evenly between new business and account growth; delivered proposals in Japanese and English."),
  bullet(null, "Won a global WAN RFP that contributed JPY 214 million in revenue and received the FY2012 Top Enterprise Sales Award."),
  bullet(null, "Received the FY2012 Top Sales Award for Enterprise Sales Division 1 for a Cisco TelePresence implementation at client sites in the US and UK."),
  bullet(null, "Closed the department's fourth-largest global MPLS deal by revenue in 2012, and recorded the highest landline sales in the 2011 new-hire cohort."),

  sectionHeading("Education"),
  splitLine([run("State University of New York at Geneseo", { bold: true, size: 20, color: NAVY })], "Geneseo, NY, USA"),
  splitLine([run("B.S. in Business Administration; Minor in International Relations", { italics: true })], "Aug 2010", { after: 40 }),

  sectionHeading("Languages & Certifications"),
  para([run("Languages: ", { bold: true }), run("Japanese (native); English (fluent, TOEIC 975)")], { spacing: { after: 30 } }),
  para([run("Certifications: ", { bold: true }), run("CompTIA Network+ (2013)")]),

  sectionHeading("Additional"),
  bullet(null, "Founder of YOBO Chiebukuro, a Japanese media site on preventive healthcare (launched 2021)."),
  bullet(null, "Volunteer with a nonprofit organization promoting preventive healthcare (since 2019)."),
];

const doc = new Document({
  creator: "Megumi Kuramitsu",
  title: "Resume - Megumi Kuramitsu",
  styles: { default: { document: { run: { font: FONT, size: BODY } } } },
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 300, hanging: 220 } }, run: { color: NAVY } },
      }],
    }],
  },
  sections: [{
    properties: {
      page: { size: { width: 12240, height: 15840 }, margin: { top: 864, bottom: 864, left: 1008, right: 1008 } },
    },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(process.argv[2], buf);
  console.log("written", process.argv[2]);
});
