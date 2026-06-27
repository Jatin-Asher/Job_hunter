from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import logging
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models.models import Job

logger = logging.getLogger(__name__)

DEFAULT_ENTRY_LEVEL_KEYWORDS = [
    "entry level software developer",
    "junior software developer",
    "fresher software developer",
    "graduate software engineer",
    "intern software developer",
]

DEFAULT_LOCATIONS = ["Remote"]

ENTRY_LEVEL_POSITIVE_PATTERNS = [
    r"\b0\s*(?:-|–|to)\s*2\s*(?:years?|yrs?)\b",
    r"\b0\s*(?:-|–|to)\s*1\s*(?:years?|yrs?)\b",
    r"\b1\s*(?:-|–|to)\s*2\s*(?:years?|yrs?)\b",
    r"\b0\+?\s*(?:years?|yrs?)\b",
    r"\b1\+?\s*(?:years?|yrs?)\b",
    r"\b2\+?\s*(?:years?|yrs?)\b",
    r"\bentry[-\s]?level\b",
    r"\bjunior\b",
    r"\bfresher\b",
    r"\bgraduate\b",
    r"\bnew grad\b",
    r"\bintern(?:ship)?\b",
    r"\btrainee\b",
    r"\bassociate\b",
]

SENIOR_EXCLUSION_PATTERNS = [
    r"\bsenior\b",
    r"\bsr\.\b",
    r"\blead\b",
    r"\bstaff\b",
    r"\bprincipal\b",
    r"\bmanager\b",
    r"\barchitect\b",
    r"\b3\+\s*(?:years?|yrs?)\b",
    r"\b4\+\s*(?:years?|yrs?)\b",
    r"\b5\+\s*(?:years?|yrs?)\b",
    r"\b6\+\s*(?:years?|yrs?)\b",
    r"\b7\+\s*(?:years?|yrs?)\b",
    r"\b8\+\s*(?:years?|yrs?)\b",
    r"\b9\+\s*(?:years?|yrs?)\b",
    r"\b10\+\s*(?:years?|yrs?)\b",
    r"\b3\s*(?:-|–|to)\s*\d+\s*(?:years?|yrs?)\b",
]


class JobScraper:
    """Base class for job scrapers."""

    def __init__(self, source: str):
        self.source = source

    def scrape(self, filters: Dict) -> List[Dict]:
        """Scrape jobs based on filters."""
        raise NotImplementedError

    @staticmethod
    def create_job_hash(title: str, company: str, location: str) -> str:
        """Create a unique hash for duplicate detection."""
        key = f"{title.lower().strip()}|{company.lower().strip()}|{location.lower().strip()}"
        return hashlib.md5(key.encode()).hexdigest()

    @staticmethod
    def normalize_keywords(keywords: Optional[List[str]]) -> List[str]:
        cleaned = [keyword.strip() for keyword in (keywords or []) if keyword and keyword.strip()]
        return cleaned or DEFAULT_ENTRY_LEVEL_KEYWORDS

    @staticmethod
    def normalize_locations(locations: Optional[List[str]]) -> List[str]:
        cleaned = [location.strip() for location in (locations or []) if location and location.strip()]
        return cleaned or DEFAULT_LOCATIONS

    @staticmethod
    def is_entry_level_job(job_data: Dict) -> bool:
        searchable_text = " ".join(
            str(value or "")
            for value in [
                job_data.get("title"),
                job_data.get("company"),
                job_data.get("location"),
                job_data.get("description"),
                job_data.get("experience_level"),
                " ".join(job_data.get("skills_required") or []),
            ]
        ).lower()

        if any(re.search(pattern, searchable_text) for pattern in SENIOR_EXCLUSION_PATTERNS):
            return False

        return any(re.search(pattern, searchable_text) for pattern in ENTRY_LEVEL_POSITIVE_PATTERNS)


class LinkedInScraper(JobScraper):
    """Scrape public LinkedIn job search result cards."""

    SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    def __init__(self):
        super().__init__("LinkedIn")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

    @staticmethod
    def _text(card: BeautifulSoup, selector: str) -> str:
        element = card.select_one(selector)
        return element.get_text(" ", strip=True) if element else ""

    @staticmethod
    def _parse_date(date_string: str) -> Optional[datetime]:
        if not date_string:
            return None

        date_string = date_string.lower().strip()
        now = datetime.utcnow()

        if "today" in date_string or "just now" in date_string:
            return now

        match = re.search(r"(\d+)\s+(minute|hour|day|week|month)", date_string)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            if unit in {"minute", "hour"}:
                return now
            if unit == "day":
                return now - timedelta(days=amount)
            if unit == "week":
                return now - timedelta(weeks=amount)
            if unit == "month":
                return now - timedelta(days=amount * 30)

        return None

    @staticmethod
    def _normalize_url(url: str) -> str:
        if not url:
            return ""
        absolute_url = urljoin("https://www.linkedin.com", url)
        return absolute_url.split("?")[0]

    def _parse_card(self, card: BeautifulSoup) -> Optional[Dict]:
        title = self._text(card, ".base-search-card__title")
        company = self._text(card, ".base-search-card__subtitle")
        location = self._text(card, ".job-search-card__location")

        link = card.select_one("a.base-card__full-link")
        apply_url = self._normalize_url(link.get("href", "")) if link else ""

        posted_element = card.select_one("time")
        posted_text = posted_element.get_text(" ", strip=True) if posted_element else ""
        posted_date = self._parse_date(posted_text)

        logo = card.select_one("img")
        company_logo_url = logo.get("data-delayed-url") or logo.get("src") if logo else None

        if not title or not company or not apply_url:
            return None

        description_parts = [title, company, location]
        if posted_text:
            description_parts.append(f"Posted {posted_text}")

        return {
            "title": title,
            "company": company,
            "location": location,
            "description": " | ".join(part for part in description_parts if part),
            "apply_url": apply_url,
            "posted_date": posted_date,
            "work_mode": "Remote" if "remote" in location.lower() else None,
            "experience_level": None,
            "company_logo_url": company_logo_url,
            "source": self.source,
        }

    def scrape(
        self,
        keywords: List[str],
        locations: List[str],
        experience_level: Optional[List[str]] = None,
        limit_per_search: int = 25,
    ) -> List[Dict]:
        jobs: List[Dict] = []
        seen_urls = set()
        keywords = self.normalize_keywords(keywords)
        locations = self.normalize_locations(locations)

        for keyword in keywords:
            for location in locations:
                params = {
                    "keywords": keyword,
                    "location": location,
                    "start": 0,
                }

                try:
                    logger.info("Scraping LinkedIn jobs for keyword=%s location=%s", keyword, location)
                    response = self.session.get(self.SEARCH_URL, params=params, timeout=20)
                    response.raise_for_status()
                except requests.RequestException as exc:
                    logger.warning("LinkedIn request failed for %s in %s: %s", keyword, location, exc)
                    continue

                soup = BeautifulSoup(response.text, "lxml")
                cards = soup.select("li, .base-card")

                for card in cards:
                    job = self._parse_card(card)
                    if not job or job["apply_url"] in seen_urls:
                        continue

                    jobs.append(job)
                    seen_urls.add(job["apply_url"])

                    if len(jobs) >= limit_per_search * len(keywords) * len(locations):
                        return jobs

                time.sleep(1)

        logger.info("LinkedIn scraping completed. Total jobs collected: %s", len(jobs))
        return jobs


class RemotiveScraper(JobScraper):
    """Scraper for Remotive's public remote-jobs API.

    This provides a second platform without requiring API keys or browser
    automation. The source name is intentionally user-facing because it is
    stored and displayed in the frontend job list.
    """

    API_URL = "https://remotive.com/api/remote-jobs"

    def __init__(self):
        super().__init__("Remotive")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0 Safari/537.36"
                ),
                "Accept": "application/json,text/plain,*/*",
            }
        )

    @staticmethod
    def _parse_date(date_string: str) -> Optional[datetime]:
        if not date_string:
            return None
        try:
            return datetime.fromisoformat(date_string.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return None

    def scrape(
        self,
        keywords: List[str],
        locations: List[str],
        experience_level: Optional[List[str]] = None,
        limit_per_search: int = 25,
    ) -> List[Dict]:
        jobs: List[Dict] = []
        seen_urls = set()
        keywords = self.normalize_keywords(keywords)
        locations = self.normalize_locations(locations)
        normalized_locations = [location.lower().strip() for location in locations if location.strip()]

        for keyword in keywords:
            try:
                logger.info("Scraping Remotive jobs for keyword=%s", keyword)
                response = self.session.get(
                    self.API_URL,
                    params={"search": keyword, "limit": limit_per_search},
                    timeout=20,
                )
                response.raise_for_status()
                payload = response.json()
            except (requests.RequestException, ValueError) as exc:
                logger.warning("Remotive request failed for %s: %s", keyword, exc)
                continue

            for item in payload.get("jobs", []):
                apply_url = item.get("url") or ""
                title = item.get("title") or ""
                company = item.get("company_name") or ""
                location = item.get("candidate_required_location") or "Remote"

                if not title or not company or not apply_url or apply_url in seen_urls:
                    continue

                if normalized_locations and not any(
                    location_filter in location.lower() or location_filter == "remote"
                    for location_filter in normalized_locations
                ):
                    continue

                jobs.append(
                    {
                        "title": title,
                        "company": company,
                        "location": location,
                        "salary": item.get("salary") or None,
                        "description": BeautifulSoup(item.get("description") or "", "lxml").get_text(" ", strip=True),
                        "apply_url": apply_url,
                        "posted_date": self._parse_date(item.get("publication_date") or ""),
                        "work_mode": "Remote",
                        "experience_level": None,
                        "company_logo_url": item.get("company_logo") or None,
                        "source": self.source,
                        "skills_required": [tag for tag in item.get("tags", []) if tag],
                    }
                )
                seen_urls.add(apply_url)

                if len(jobs) >= limit_per_search * max(len(keywords), 1):
                    return jobs

            time.sleep(0.5)

        logger.info("Remotive scraping completed. Total jobs collected: %s", len(jobs))
        return jobs


class ArbeitnowScraper(JobScraper):
    """Scraper for Arbeitnow's public job board API."""

    API_URL = "https://www.arbeitnow.com/api/job-board-api"

    def __init__(self):
        super().__init__("Arbeitnow")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0 Safari/537.36"
                ),
                "Accept": "application/json,text/plain,*/*",
            }
        )

    @staticmethod
    def _parse_timestamp(timestamp) -> Optional[datetime]:
        if not timestamp:
            return None
        try:
            return datetime.utcfromtimestamp(int(timestamp))
        except (TypeError, ValueError, OSError):
            return None

    def scrape(
        self,
        keywords: List[str],
        locations: List[str],
        experience_level: Optional[List[str]] = None,
        limit_per_search: int = 25,
    ) -> List[Dict]:
        jobs: List[Dict] = []
        seen_urls = set()
        keywords = self.normalize_keywords(keywords)
        locations = self.normalize_locations(locations)
        normalized_keywords = [keyword.lower().strip() for keyword in keywords if keyword.strip()]
        normalized_locations = [location.lower().strip() for location in locations if location.strip()]

        try:
            logger.info("Scraping Arbeitnow jobs")
            response = self.session.get(self.API_URL, timeout=20)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            logger.warning("Arbeitnow request failed: %s", exc)
            return jobs

        max_jobs = limit_per_search * max(len(keywords), 1) * max(len(locations), 1)
        for item in payload.get("data", []):
            title = item.get("title") or ""
            company = item.get("company_name") or ""
            location = item.get("location") or "Remote"
            apply_url = item.get("url") or ""
            tags = [tag for tag in item.get("tags", []) if tag]
            searchable_text = " ".join([title, company, location, " ".join(tags)]).lower()

            if not title or not company or not apply_url or apply_url in seen_urls:
                continue

            if normalized_keywords and not any(keyword in searchable_text for keyword in normalized_keywords):
                continue

            if normalized_locations and not any(
                location_filter in location.lower()
                or (location_filter == "remote" and (item.get("remote") or "remote" in location.lower()))
                for location_filter in normalized_locations
            ):
                continue

            jobs.append(
                {
                    "title": title,
                    "company": company,
                    "location": location,
                    "description": BeautifulSoup(item.get("description") or "", "lxml").get_text(" ", strip=True),
                    "apply_url": apply_url,
                    "posted_date": self._parse_timestamp(item.get("created_at")),
                    "work_mode": "Remote" if item.get("remote") or "remote" in location.lower() else None,
                    "experience_level": None,
                    "company_logo_url": None,
                    "source": self.source,
                    "skills_required": tags,
                }
            )
            seen_urls.add(apply_url)

            if len(jobs) >= max_jobs:
                break

        logger.info("Arbeitnow scraping completed. Total jobs collected: %s", len(jobs))
        return jobs


class RemoteOKScraper(JobScraper):
    """Scraper for RemoteOK's public remote-jobs API."""

    API_URL = "https://remoteok.com/api"

    def __init__(self):
        super().__init__("RemoteOK")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0 Safari/537.36"
                ),
                "Accept": "application/json,text/plain,*/*",
            }
        )

    @staticmethod
    def _parse_date(date_string: str) -> Optional[datetime]:
        if not date_string:
            return None
        try:
            return datetime.fromisoformat(date_string.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return None

    def scrape(
        self,
        keywords: List[str],
        locations: List[str],
        experience_level: Optional[List[str]] = None,
        limit_per_search: int = 25,
    ) -> List[Dict]:
        jobs: List[Dict] = []
        seen_urls = set()
        keywords = self.normalize_keywords(keywords)
        normalized_keywords = [keyword.lower().strip() for keyword in keywords if keyword.strip()]

        try:
            logger.info("Scraping RemoteOK jobs")
            response = self.session.get(self.API_URL, timeout=20)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            logger.warning("RemoteOK request failed: %s", exc)
            return jobs

        max_jobs = limit_per_search * max(len(keywords), 1)
        for item in payload:
            if not isinstance(item, dict) or "position" not in item:
                continue

            title = item.get("position") or ""
            company = item.get("company") or ""
            apply_url = item.get("url") or item.get("apply_url") or ""
            tags = [str(tag) for tag in item.get("tags", []) if tag]
            searchable_text = " ".join([title, company, " ".join(tags), item.get("description") or ""]).lower()

            if not title or not company or not apply_url or apply_url in seen_urls:
                continue

            if normalized_keywords and not any(
                any(part in searchable_text for part in keyword.split())
                for keyword in normalized_keywords
            ):
                continue

            jobs.append(
                {
                    "title": title,
                    "company": company,
                    "location": item.get("location") or "Remote",
                    "salary": None,
                    "salary_min": item.get("salary_min"),
                    "salary_max": item.get("salary_max"),
                    "description": BeautifulSoup(item.get("description") or "", "lxml").get_text(" ", strip=True),
                    "apply_url": apply_url,
                    "posted_date": self._parse_date(item.get("date") or ""),
                    "work_mode": "Remote",
                    "experience_level": None,
                    "company_logo_url": item.get("company_logo") or None,
                    "source": self.source,
                    "skills_required": tags,
                }
            )
            seen_urls.add(apply_url)

            if len(jobs) >= max_jobs:
                break

        logger.info("RemoteOK scraping completed. Total jobs collected: %s", len(jobs))
        return jobs


class JobScrapingService:
    """Service to manage job scraping operations."""

    def __init__(self):
        self.linkedin_scraper = LinkedInScraper()
        self.scrapers = [
            self.linkedin_scraper,
            RemotiveScraper(),
            ArbeitnowScraper(),
            RemoteOKScraper(),
        ]

    def scrape_linkedin(
        self,
        keywords: List[str],
        locations: List[str],
        experience_level: Optional[List[str]] = None,
        db: Session = None,
    ) -> Dict:
        keywords = JobScraper.normalize_keywords(keywords)
        locations = JobScraper.normalize_locations(locations)
        results = {
            "source": "LinkedIn",
            "jobs_found": 0,
            "jobs_saved": 0,
            "duplicates_skipped": 0,
            "errors": [],
        }

        try:
            jobs = self.linkedin_scraper.scrape(keywords, locations, experience_level)
            jobs = self._filter_entry_level_jobs(jobs)
            results["jobs_found"] = len(jobs)

            if db and jobs:
                saved, skipped = self._save_jobs_to_db(jobs, db)
                results["jobs_saved"] = saved
                results["duplicates_skipped"] = skipped

        except Exception as exc:
            error_msg = f"LinkedIn scraping error: {exc}"
            logger.exception(error_msg)
            results["errors"].append(error_msg)

        return results

    def scrape_all_sources(
        self,
        keywords: List[str],
        locations: List[str],
        experience_level: Optional[List[str]] = None,
        db: Session = None,
    ) -> Dict:
        keywords = JobScraper.normalize_keywords(keywords)
        locations = JobScraper.normalize_locations(locations)
        all_results = {
            "total_jobs_found": 0,
            "total_jobs_saved": 0,
            "total_duplicates_skipped": 0,
            "sources": {},
        }

        for scraper in self.scrapers:
            source_results = self._scrape_source(scraper, keywords, locations, experience_level, db)
            all_results["sources"][scraper.source] = source_results
            all_results["total_jobs_found"] += source_results["jobs_found"]
            all_results["total_jobs_saved"] += source_results["jobs_saved"]
            all_results["total_duplicates_skipped"] += source_results["duplicates_skipped"]

        return all_results

    def _scrape_source(
        self,
        scraper: JobScraper,
        keywords: List[str],
        locations: List[str],
        experience_level: Optional[List[str]] = None,
        db: Session = None,
    ) -> Dict:
        results = {
            "source": scraper.source,
            "jobs_found": 0,
            "jobs_saved": 0,
            "duplicates_skipped": 0,
            "errors": [],
        }

        try:
            jobs = scraper.scrape(keywords, locations, experience_level)
            jobs = self._filter_entry_level_jobs(jobs)
            results["jobs_found"] = len(jobs)

            if db and jobs:
                saved, skipped = self._save_jobs_to_db(jobs, db)
                results["jobs_saved"] = saved
                results["duplicates_skipped"] = skipped

        except Exception as exc:
            error_msg = f"{scraper.source} scraping error: {exc}"
            logger.exception(error_msg)
            results["errors"].append(error_msg)

        return results

    @staticmethod
    def _filter_entry_level_jobs(jobs: List[Dict]) -> List[Dict]:
        filtered_jobs = [job for job in jobs if JobScraper.is_entry_level_job(job)]
        logger.info(
            "Entry-level filter kept %s of %s scraped jobs",
            len(filtered_jobs),
            len(jobs),
        )
        return filtered_jobs

    @staticmethod
    def _save_jobs_to_db(jobs: List[Dict], db: Session) -> Tuple[int, int]:
        saved = 0
        skipped = 0

        for job_data in jobs:
            try:
                job_hash = JobScraper.create_job_hash(
                    job_data.get("title", ""),
                    job_data.get("company", ""),
                    job_data.get("location", ""),
                )

                apply_url = job_data.get("apply_url", "")
                existing_job = db.query(Job).filter(
                    (Job.hash_value == job_hash) | (Job.apply_url == apply_url)
                ).first()
                if existing_job:
                    skipped += 1
                    continue

                new_job = Job(
                    title=job_data.get("title", ""),
                    company=job_data.get("company", ""),
                    location=job_data.get("location", ""),
                    salary=job_data.get("salary"),
                    salary_min=job_data.get("salary_min"),
                    salary_max=job_data.get("salary_max"),
                    experience_level=job_data.get("experience_level"),
                    work_mode=job_data.get("work_mode"),
                    company_size=job_data.get("company_size"),
                    description=job_data.get("description", ""),
                    skills_required=job_data.get("skills_required", []),
                    apply_url=job_data.get("apply_url", ""),
                    company_logo_url=job_data.get("company_logo_url"),
                    source=job_data.get("source", "Unknown"),
                    posted_date=job_data.get("posted_date"),
                    hash_value=job_hash,
                    is_active=True,
                )
                db.add(new_job)
                saved += 1

            except Exception as exc:
                logger.warning("Error preparing job %s: %s", job_data.get("title", "Unknown"), exc)

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        return saved, skipped