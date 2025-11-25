import httpx
import time
from typing import List, Dict, Optional
import json

class OpenAlexFetcher:
    """
    Fetcher untuk publikasi riset Indonesia dari berbagai institusi nasional
    IMPROVED VERSION: Better ROR handling, country filter fallback, quality checks
    """
    BASE_URL = "https://api.openalex.org"
    
    # Indonesian Research Institutions with VERIFIED ROR IDs
    INDONESIAN_INSTITUTIONS = {
        # Research Institutions
        'BRIN': 'https://ror.org/018a7sn25',
        
        # Top Universities - VERIFIED RORs
        'UI': 'https://ror.org/05v2pdr98',
        'ITB': 'https://ror.org/00tq7fx95',
        'UGM': 'https://ror.org/04q4f3q36',
        'IPB': 'https://ror.org/00te3t702',
        'ITS': 'https://ror.org/03v8tnc06',
        'UNAIR': 'https://ror.org/00xvgzh62',
        'UNDIP': 'https://ror.org/00xvgzh62',
        'UNPAD': 'https://ror.org/02jp35r79',
        'UNS': 'https://ror.org/05qj1jx13',
        'UNHAS': 'https://ror.org/052jqgt73',
        'USU': 'https://ror.org/042dyfs80',
        'UNAND': 'https://ror.org/01phqxe34',
        'UB': 'https://ror.org/0410hv376',
        'BINUS': 'https://ror.org/03skew617',
        'TELKOM_U': 'https://ror.org/03bg2mb49',
    }
    
    def __init__(self, email: str = "research@example.com"):
        self.email = email
        self.session = httpx.Client(timeout=60.0)
        self.stats = {
            'total_fetched': 0,
            'by_institution': {},
            'by_year': {},
            'errors': [],
            'indonesian_verified': 0
        }
    
    def _make_request(self, endpoint: str, params: dict, retry: int = 3) -> dict:
        """Make HTTP request with retry logic"""
        params['mailto'] = self.email
        url = f"{self.BASE_URL}/{endpoint}"
        
        for attempt in range(retry):
            try:
                response = self.session.get(url, params=params)
                
                if response.status_code == 429:
                    wait_time = 60
                    print(f"  ⚠️  Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                if response.status_code != 200:
                    if attempt < retry - 1:
                        time.sleep(2)
                        continue
                    print(f"  ❌ Error {response.status_code}")
                    response.raise_for_status()
                
                return response.json()
                
            except Exception as e:
                if attempt < retry - 1:
                    time.sleep(2)
                    continue
                print(f"  ❌ Request failed: {e}")
                raise
        
        return {}
    
    def fetch_indonesian_publications(
        self, 
        limit: int = 1000,
        year_from: int = 2020,
        year_to: Optional[int] = None,
        institutions: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        use_country_fallback: bool = True
    ) -> List[Dict]:
        """
        Fetch publikasi riset Indonesia
        IMPROVED: Uses country filter as primary + institution verification
        """
        print("=" * 70)
        print("🇮🇩 INDONESIAN NATIONAL RESEARCH PUBLICATIONS FETCHER")
        print("=" * 70)
        
        if year_to is None:
            from datetime import datetime
            year_to = datetime.now().year
        
        print(f"\n📊 Configuration:")
        print(f"  • Target: {limit} publications")
        print(f"  • Year range: {year_from} - {year_to}")
        print(f"  • Strategy: Country-wide + Institution verification")
        
        if fields:
            print(f"  • Research fields: {', '.join(fields)}")
        
        # Fetch using country filter (more reliable)
        all_publications = self._fetch_by_country_with_verification(
            limit=limit,
            year_from=year_from,
            year_to=year_to,
            fields=fields,
            target_institutions=institutions
        )
        
        # If not enough, try per-institution
        if len(all_publications) < limit * 0.3 and use_country_fallback:
            print(f"\n🔄 Country filter returned only {len(all_publications)}, trying per-institution...")
            
            selected_institutions = self.INDONESIAN_INSTITUTIONS
            if institutions:
                selected_institutions = {
                    k: v for k, v in self.INDONESIAN_INSTITUTIONS.items() 
                    if k in institutions
                }
            
            for inst_name, ror_id in selected_institutions.items():
                if len(all_publications) >= limit:
                    break
                
                print(f"\n📚 Trying {inst_name} directly...")
                pubs = self._fetch_by_ror_direct(
                    ror_id=ror_id,
                    institution_name=inst_name,
                    limit=50,
                    year_from=year_from,
                    year_to=year_to
                )
                
                # Merge with deduplication
                for pub in pubs:
                    if pub['title'] not in [p['title'] for p in all_publications]:
                        all_publications.append(pub)
                
                time.sleep(0.5)
        
        # Final stats
        self.stats['total_fetched'] = len(all_publications)
        for pub in all_publications:
            year = pub.get('year')
            if year:
                self.stats['by_year'][year] = self.stats['by_year'].get(year, 0) + 1
            
            inst = pub.get('primary_institution', 'Unknown')
            self.stats['by_institution'][inst] = self.stats['by_institution'].get(inst, 0) + 1
        
        self._print_summary()
        
        return all_publications[:limit]
    
    def _fetch_by_country_with_verification(
        self,
        limit: int,
        year_from: int,
        year_to: int,
        fields: Optional[List[str]] = None,
        target_institutions: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Fetch by country code (ID) and verify Indonesian affiliation
        This is more reliable than per-institution ROR
        """
        print(f"\n🌏 Fetching Indonesian publications (country-wide)...")
        
        publications = []
        per_page = 50
        cursor = "*"
        max_pages = (limit // per_page) + 5  # Add buffer
        page_count = 0
        
        # Build filter - Use country code as primary filter
        filters = [
            'institutions.country_code:ID',
            f'from_publication_date:{year_from}-01-01',
            f'to_publication_date:{year_to}-12-31',
            'has_abstract:true'  # Only with abstract for better quality
        ]
        
        # Add field filter if specified
        if fields:
            field_ids = self._map_fields_to_ids(fields)
            if field_ids:
                filters.append(f'primary_topic.field.id:{"|".join(field_ids)}')
        
        filter_str = ','.join(filters)
        
        try:
            while len(publications) < limit and cursor and page_count < max_pages:
                params = {
                    'filter': filter_str,
                    'per-page': per_page,
                    'cursor': cursor,
                }
                
                print(f"  Page {page_count + 1}: Fetching... (total: {len(publications)})")
                
                data = self._make_request('works', params)
                results = data.get('results', [])
                
                if not results:
                    print("  No more results")
                    break
                
                for work in results:
                    # Verify Indonesian affiliation
                    if self._has_indonesian_affiliation(work):
                        # Identify primary institution
                        inst = self._identify_primary_institution(work)
                        
                        # Filter by target institutions if specified
                        if target_institutions and inst not in target_institutions:
                            continue
                        
                        pub = self._parse_work(work, inst)
                        if pub and self._is_quality_publication(pub):
                            publications.append(pub)
                            self.stats['indonesian_verified'] += 1
                
                cursor = data.get('meta', {}).get('next_cursor')
                page_count += 1
                
                if not cursor:
                    break
                
                time.sleep(0.3)  # Be polite
                
        except Exception as e:
            print(f"❌ Fetch error: {e}")
        
        print(f"\n✅ Verified Indonesian publications: {len(publications)}")
        return publications
    
    def _fetch_by_ror_direct(
        self,
        ror_id: str,
        institution_name: str,
        limit: int,
        year_from: int,
        year_to: int
    ) -> List[Dict]:
        """Direct fetch by ROR ID"""
        publications = []
        
        filters = [
            f'authorships.institutions.ror:{ror_id}',
            f'from_publication_date:{year_from}-01-01',
            f'to_publication_date:{year_to}-12-31',
            'has_abstract:true'
        ]
        
        filter_str = ','.join(filters)
        
        try:
            params = {
                'filter': filter_str,
                'per-page': min(limit, 50)
            }
            
            data = self._make_request('works', params)
            results = data.get('results', [])
            
            print(f"  Found {len(results)} publications")
            
            for work in results:
                pub = self._parse_work(work, institution_name)
                if pub and self._is_quality_publication(pub):
                    publications.append(pub)
                    
        except Exception as e:
            print(f"  Error: {e}")
        
        return publications
    
    def _has_indonesian_affiliation(self, work: dict) -> bool:
        """Check if work has Indonesian affiliation"""
        indonesian_keywords = [
            'indonesia', 'indonesian', 'brin', 'lipi',
            'universitas', 'institut teknologi', 'university of indonesia',
            'gadjah mada', 'bandung', 'surabaya', 'yogyakarta'
        ]
        
        for authorship in work.get('authorships', []):
            for institution in authorship.get('institutions', []):
                # Check country code - FIXED: handle None
                country_code = institution.get('country_code')
                if country_code and country_code.upper() == 'ID':
                    return True
                
                
                # Check name
                name = institution.get('display_name', '')
                if name:
                    name_lower = name.lower()
                    if any(keyword in name_lower for keyword in indonesian_keywords):
                        return True
                
                # Check ROR
                ror = institution.get('ror', '')
                if ror:
                    ror_lower = ror.lower()
                    if any(known_ror.lower() in ror_lower for known_ror in self.INDONESIAN_INSTITUTIONS.values()):
                        return True
        
        return False
    
    def _identify_primary_institution(self, work: dict) -> str:
        """Identify primary Indonesian institution from work"""
        # Try to match with known institutions
        for authorship in work.get('authorships', []):
            for institution in authorship.get('institutions', []):
                ror = institution.get('ror', '')
                name = institution.get('display_name', '')
                
                # Match by ROR
                for inst_name, inst_ror in self.INDONESIAN_INSTITUTIONS.items():
                    if inst_ror.lower() in ror.lower():
                        return inst_name
                
                # Match by name keywords
                name_lower = name.lower()
                if 'brin' in name_lower or 'national research' in name_lower:
                    return 'BRIN'
                elif 'universitas indonesia' in name_lower or name.startswith('UI'):
                    return 'UI'
                elif 'bandung' in name_lower and 'institut' in name_lower:
                    return 'ITB'
                elif 'gadjah mada' in name_lower:
                    return 'UGM'
                elif 'bogor' in name_lower:
                    return 'IPB'
                elif 'sepuluh nopember' in name_lower or 'surabaya' in name_lower:
                    return 'ITS'
                elif 'airlangga' in name_lower:
                    return 'UNAIR'
                elif 'diponegoro' in name_lower:
                    return 'UNDIP'
                elif 'binus' in name_lower or 'bina nusantara' in name_lower:
                    return 'BINUS'
                elif 'telkom' in name_lower:
                    return 'TELKOM_U'
        
        return 'Other Indonesian Institution'
    
    def _is_quality_publication(self, pub: dict) -> bool:
        """Check if publication meets quality criteria"""
        # Must have title and abstract
        if not pub.get('title') or len(pub['title']) < 10:
            return False
        
        if not pub.get('abstract') or pub['abstract'] == 'No abstract available':
            return False
        
        if len(pub['abstract']) < 50:
            return False
        
        # Must have at least one author
        if not pub.get('authors'):
            return False
        
        # Year should be valid
        year = pub.get('year')
        if not year or year < 2000 or year > 2030:
            return False
        
        return True
    
    def _parse_work(self, work: dict, source_institution: str) -> Optional[Dict]:
        """Parse OpenAlex work object"""
        try:
            title = work.get('title', '').strip()
            if not title:
                return None
            
            # Abstract
            abstract = self._reconstruct_abstract(
                work.get('abstract_inverted_index', {})
            )
            
            # Authors - Only keep Indonesian authors or first 10
            authors = []
            affiliations = []
            
            for authorship in work.get('authorships', [])[:10]:
                author_info = authorship.get('author', {})
                author_name = author_info.get('display_name', '')
                
                if author_name:
                    authors.append(author_name)
                    
                    # Get first Indonesian institution or first institution
                    institutions = authorship.get('institutions', [])
                    found_indonesian = False
                    
                    for inst in institutions:
                        country_code = inst.get('country_code')
                        if country_code and country_code.upper() == 'ID':
                            affiliations.append(inst.get('display_name', 'Unknown'))
                            found_indonesian = True
                            break
                    
                    if not found_indonesian and institutions:
                        affiliations.append(institutions[0].get('display_name', 'Unknown'))
                    elif not found_indonesian:
                        affiliations.append('Unknown')
            
            # Source
            primary_location = work.get('primary_location', {}) or {}
            source = primary_location.get('source', {}) or {}
            source_name = source.get('display_name', 'Unknown')
            
            # Topics/Keywords
            topics = work.get('topics', [])
            keywords = [t.get('display_name', '') for t in topics[:5]]
            
            # Year
            year = work.get('publication_year')
            
            return {
                'title': title,
                'abstract': abstract or 'No abstract available',
                'year': year,
                'authors': authors,
                'affiliations': affiliations,
                'doi': work.get('doi', ''),
                'url': work.get('id', ''),
                'source': f"OpenAlex - {source_name}",
                'openalex_id': work.get('id', ''),
                'primary_institution': source_institution,
                'keywords': keywords
            }
            
        except Exception as e:
            return None
    
    def _reconstruct_abstract(self, inverted_index: dict) -> str:
        """Reconstruct abstract from inverted index"""
        if not inverted_index:
            return ""
        
        try:
            word_positions = []
            for word, positions in inverted_index.items():
                for pos in positions:
                    word_positions.append((pos, word))
            
            word_positions.sort(key=lambda x: x[0])
            abstract = ' '.join([word for _, word in word_positions])
            
            return abstract[:2000]
        except:
            return ""
    
    def _map_fields_to_ids(self, fields: List[str]) -> List[str]:
        """Map field names to OpenAlex field IDs"""
        field_mapping = {
            'Computer Science': 'https://openalex.org/fields/17',
            'Medicine': 'https://openalex.org/fields/27',
            'Engineering': 'https://openalex.org/fields/22',
            'Biology': 'https://openalex.org/fields/86',
            'Physics': 'https://openalex.org/fields/31',
            'Chemistry': 'https://openalex.org/fields/23',
            'Mathematics': 'https://openalex.org/fields/33',
            'Environmental Science': 'https://openalex.org/fields/23',
            'Agricultural Sciences': 'https://openalex.org/fields/7',
        }
        
        return [field_mapping.get(f, '') for f in fields if f in field_mapping]
    
    def _print_summary(self):
        """Print fetching summary"""
        print("\n" + "=" * 70)
        print("📊 FETCHING SUMMARY")
        print("=" * 70)
        
        print(f"\n✅ Total Publications: {self.stats['total_fetched']}")
        print(f"🇮🇩 Indonesian Verified: {self.stats['indonesian_verified']}")
        
        if self.stats['by_institution']:
            print("\n📚 By Institution:")
            sorted_inst = sorted(
                self.stats['by_institution'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            for inst, count in sorted_inst[:15]:  # Top 15
                bar = "█" * (count // 5) if count > 0 else ""
                print(f"  {inst:30} {count:4} {bar}")
        
        if self.stats['by_year']:
            print("\n📅 By Year:")
            for year in sorted(self.stats['by_year'].keys(), reverse=True):
                count = self.stats['by_year'][year]
                bar = "█" * (count // 10) if count > 0 else ""
                print(f"  {year}: {count:4} {bar}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors: {len(self.stats['errors'])}")
    
    def test_connection(self) -> bool:
        """Test OpenAlex API connection"""
        print("🔌 Testing OpenAlex API connection...")
        
        try:
            params = {
                'filter': 'institutions.country_code:ID',
                'per-page': 1
            }
            
            data = self._make_request('works', params)
            
            if data.get('results'):
                print("✅ API connection successful!")
                work = data['results'][0]
                print(f"  Sample: {work.get('title', 'N/A')[:60]}...")
                
                # Check institution
                for auth in work.get('authorships', []):
                    for inst in auth.get('institutions', []):
                        if inst.get('country_code') == 'ID':
                            print(f"  Institution: {inst.get('display_name', 'N/A')}")
                            break
                    break
                
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def close(self):
        """Close HTTP session"""
        self.session.close()