#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

function parseArgs(argv) {
  const values = {};
  for (let index = 2; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key || !key.startsWith("--") || value === undefined) {
      throw new Error(`invalid argument near ${key || "<end>"}`);
    }
    values[key.slice(2)] = value;
  }
  for (const required of ["base-url", "browser", "report", "screenshots"]) {
    if (!values[required]) throw new Error(`missing --${required}`);
  }
  return values;
}

function sha256(buffer) {
  return crypto.createHash("sha256").update(buffer).digest("hex");
}

function normalizedBase(value) {
  const url = new URL(value);
  if (url.protocol !== "https:" || url.username || url.password || url.search || url.hash) {
    throw new Error("base URL must be a credential-free HTTPS URL");
  }
  if (!url.pathname.endsWith("/")) url.pathname += "/";
  return url.toString();
}

async function inspectSurface(browser, baseUrl, outputDir, spec) {
  const context = await browser.newContext({
    viewport: { width: spec.width, height: spec.height },
    deviceScaleFactor: 1,
    isMobile: spec.mobile,
    hasTouch: spec.mobile,
    locale: "id-ID",
    colorScheme: "light",
  });
  const page = await context.newPage();
  const consoleErrors = [];
  const hostLevelObservations = [];
  const pageErrors = [];
  const failedRequests = [];
  const badResponses = [];
  page.on("console", (message) => {
    if (message.type() === "error") {
      const observation = { text: message.text(), location: message.location() };
      const hostFavicon = new URL("/favicon.ico", baseUrl).toString();
      if (observation.location.url === hostFavicon && observation.text.includes("404")) {
        hostLevelObservations.push({
          ...observation,
          disposition: "The browser requested the GitHub user-site favicon outside this repository's project path; it is not a reader resource or a deployable route in this lane.",
        });
      } else {
        consoleErrors.push(observation);
      }
    }
  });
  page.on("pageerror", (error) => pageErrors.push(String(error)));
  page.on("requestfailed", (request) => {
    failedRequests.push({ url: request.url(), error: request.failure()?.errorText || "unknown" });
  });
  page.on("response", (response) => {
    if (response.status() >= 400) badResponses.push({ url: response.url(), status: response.status() });
  });

  const requestedUrl = new URL(spec.path, baseUrl).toString();
  const response = await page.goto(requestedUrl, { waitUntil: "networkidle", timeout: 90000 });
  if (spec.finalPath) {
    const expectedUrl = new URL(spec.finalPath, baseUrl).toString();
    await page.waitForURL(expectedUrl, { waitUntil: "networkidle", timeout: 30000 });
  }

  const metrics = await page.evaluate(() => {
    const root = document.documentElement;
    const body = document.body;
    const main = document.querySelector("main");
    const math = Array.from(document.querySelectorAll("math"));
    const overflowingMath = math.filter((element) => {
      const box = element.getBoundingClientRect();
      return box.right > root.clientWidth + 1 || box.left < -1;
    });
    const containedOverflow = overflowingMath.filter((element) => {
      let ancestor = element.parentElement;
      while (ancestor && ancestor !== body) {
        const style = getComputedStyle(ancestor);
        if (["auto", "scroll"].includes(style.overflowX) && ancestor.scrollWidth > ancestor.clientWidth) {
          return true;
        }
        ancestor = ancestor.parentElement;
      }
      return false;
    });
    return {
      title: document.title,
      language: root.lang,
      h1: document.querySelector("h1")?.textContent?.trim() || null,
      client_width: root.clientWidth,
      document_width: root.scrollWidth,
      body_width: body ? body.scrollWidth : null,
      main_width: main ? Number(main.getBoundingClientRect().width.toFixed(3)) : null,
      page_horizontal_overflow: root.scrollWidth > root.clientWidth + 1,
      mathml_elements: math.length,
      svg_elements: document.querySelectorAll("svg").length,
      navigation_landmarks: document.querySelectorAll("nav").length,
      curriculum_links: document.querySelectorAll('a[href*="program-matematika-indonesia"]').length,
      original_source_links: document.querySelectorAll('a[href*="web.pdx.edu/~erdman/FAOA/"]').length,
      overflowing_math_elements: overflowingMath.length,
      locally_scroll_contained_math_elements: containedOverflow.length,
    };
  });

  if (spec.scrollSelector) {
    const target = page.locator(spec.scrollSelector).first();
    if (await target.count()) {
      await target.scrollIntoViewIfNeeded();
      await page.evaluate(() => window.scrollBy(0, -24));
    }
  }

  const screenshotName = `${spec.name}.png`;
  const screenshotPath = path.join(outputDir, screenshotName);
  await page.screenshot({ path: screenshotPath, fullPage: false });
  const screenshotBytes = fs.readFileSync(screenshotPath);
  const result = {
    name: spec.name,
    viewport: { width: spec.width, height: spec.height, mobile: spec.mobile },
    requested_url: requestedUrl,
    final_url: page.url(),
    initial_http_status: response ? response.status() : null,
    metrics,
    console_errors: consoleErrors,
    host_level_observations: hostLevelObservations,
    page_errors: pageErrors,
    failed_requests: failedRequests,
    bad_http_responses: badResponses,
    screenshot: {
      filename: screenshotName,
      bytes: screenshotBytes.length,
      sha256: sha256(screenshotBytes),
    },
  };
  result.status =
    result.initial_http_status === 200 &&
    consoleErrors.length === 0 &&
    pageErrors.length === 0 &&
    failedRequests.length === 0 &&
    badResponses.length === 0 &&
    !metrics.page_horizontal_overflow &&
    ["id", "id-ID"].includes(metrics.language) &&
    metrics.navigation_landmarks > 0 &&
    metrics.curriculum_links > 0 &&
    metrics.original_source_links > 0
      ? "pass"
      : "fail";
  await context.close();
  return result;
}

async function main() {
  const args = parseArgs(process.argv);
  const baseUrl = normalizedBase(args["base-url"]);
  const outputDir = path.resolve(args.screenshots);
  const reportPath = path.resolve(args.report);
  fs.mkdirSync(outputDir, { recursive: true });
  fs.mkdirSync(path.dirname(reportPath), { recursive: true });

  const specs = [
    {
      name: "desktop-root-reader",
      path: "",
      finalPath: "output/html/index.html",
      width: 1440,
      height: 900,
      mobile: false,
    },
    {
      name: "desktop-companion",
      path: "companion/",
      finalPath: "output/html-companion/index.html",
      width: 1440,
      height: 900,
      mobile: false,
    },
    {
      name: "mobile-source-chapter-06",
      path: "output/html/bab-06/index.html",
      width: 390,
      height: 844,
      mobile: true,
      scrollSelector: "main math",
    },
    {
      name: "mobile-companion-bridge",
      path: "output/html-companion/jembatan-spektral-kompak-svd/index.html",
      width: 390,
      height: 844,
      mobile: true,
      scrollSelector: "main h1",
    },
  ];

  const browser = await chromium.launch({ executablePath: path.resolve(args.browser), headless: true });
  let surfaces;
  try {
    surfaces = [];
    for (const spec of specs) surfaces.push(await inspectSurface(browser, baseUrl, outputDir, spec));
  } finally {
    await browser.close();
  }

  const aggregateConsoleErrors = surfaces.flatMap((surface) => surface.console_errors);
  const aggregateFailedRequests = surfaces.flatMap((surface) => surface.failed_requests);
  const report = {
    schema: "o008.github-pages.recovery-browser-qa.v1",
    status: surfaces.every((surface) => surface.status === "pass") ? "pass" : "fail",
    inspected_at_utc: new Date().toISOString(),
    anonymous_context: true,
    authentication_used: false,
    base_url: baseUrl,
    browser_engine: "Chromium via installed Microsoft Edge",
    console_errors: aggregateConsoleErrors,
    failed_requests: aggregateFailedRequests,
    inspected_urls: [...new Set(surfaces.flatMap((surface) => [surface.requested_url, surface.final_url]))].sort(),
    viewports: surfaces.map((surface) => ({
      name: surface.name,
      width: surface.viewport.width,
      height: surface.viewport.height,
      status: surface.status,
    })),
    surfaces,
  };
  fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  process.stdout.write(`${JSON.stringify(report)}\n`);
  if (report.status !== "pass") process.exitCode = 1;
}

main().catch((error) => {
  process.stderr.write(`${error.stack || error}\n`);
  process.exitCode = 1;
});
