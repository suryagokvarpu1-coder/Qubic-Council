# Task: Universal API Key & Provider Auto-Detection

## Phase 1: Planning & Design
- [ ] Analyze current API key storage (`settings.py`) and usage (`nodes/__init__.py`) <!-- id: 0 -->
- [ ] Design `ProviderAdapter` abstraction and Factory pattern <!-- id: 1 -->
- [ ] Define API key regex patterns for auto-detection <!-- id: 2 -->
- [ ] Create Implementation Plan <!-- id: 3 -->

## Phase 2: Backend Implementation
- [ ] Create `backend/app/engine/providers.py` for provider logic <!-- id: 4 -->
- [ ] Implement detection logic (Regex + Verification) <!-- id: 5 -->
- [ ] Refactor `backend/app/nodes/__init__.py` to use `ProviderFactory` <!-- id: 6 -->
- [ ] Update `/settings/keys` endpoint to handle raw key string and return detected provider <!-- id: 7 -->

## Phase 3: Frontend Implementation
- [ ] Add "Universal API Key" input to Sidebar in `mainpage.html` <!-- id: 8 -->
- [ ] Implement frontend logic to send key and display detected provider feedback <!-- id: 9 -->
- [ ] Handle validation errors and capability warnings <!-- id: 10 -->

## Phase 4: Verification
- [ ] Test with OpenAI key (mock/real) <!-- id: 11 -->
- [ ] Test with Anthropic key (mock/real) <!-- id: 12 -->
- [ ] Test with Groq key (mock/real) <!-- id: 13 -->
- [ ] Verify system auto-reconfiguration <!-- id: 14 -->
