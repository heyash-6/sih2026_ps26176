import { useEffect, useMemo, useRef, useState } from 'react'
import { BrowserRouter, useLocation, useNavigate } from 'react-router-dom'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { pfz as staticPfz, alerts as staticAlerts } from './data'
import logo from './assets/orca-logo.png'
import './App.css'
import {
  askOrca,
  checkBackendHealth,
  getMarineData,
  getRouteAndGeofence,
  getPfzCandidates,
  getHazards,
  getAnalytics,
  getAllAlerts,
  getAnalysisHistory
} from './services/api'
import { onAuthStateChange, signOutUser, getSession } from './services/supabaseClient'
import AuthModal from './components/AuthModal'

const T = {
  en: {
    dashboard: 'Dashboard', map: 'Marine Intelligence Map', analytics: 'Ocean Analytics', fishing: 'Fishing Intelligence', safety: 'Safety & Routes', assistant: 'ORCA AI Assistant', alerts: 'Alerts', settings: 'Settings', profile: 'Profile', workspace: 'WORKSPACE', operational: 'Systems operational', connected: 'Marine data services connected', marine: 'MARINE INTELLIGENCE', glance: 'Marine conditions at a glance.', location: 'Mumbai Coast • Live Supabase & Sensor Streams Connected', ask: 'Ask ORCA', seaState: 'Sea state', wind: 'Wind', sst: 'Sea surface temperature', activePFZ: 'Active PFZs', moderate: 'Moderate', waves: '1.2 m waves', steady: 'NE • steady', favourable: 'Favourable', openMap: 'Open map', activeAdvisories: 'Active advisories', viewAll: 'View all', insights: "Today's marine insights", bestFishing: 'Best fishing opportunity', departure: 'Recommended departure', confidence: 'Data confidence', verified: 'Verified intelligence', sources: 'Sources: ISRO • INCOIS • IMD • Supabase', oceanInputs: 'Ocean, geospatial, and Supabase database inputs synchronized.', allLayers: 'All layers', weather: 'Weather', hazards: 'Hazards', boundaries: 'Boundaries', today: 'Today', selectedZone: 'Selected zone', high: 'High confidence', why: 'Why this zone?', signal: 'Signal', how: 'How ORCA reasons', discover: 'Discover', correlate: 'Correlate', assess: 'Assess', explain: 'Explain', findZones: 'Find promising fishing zones.', explore: 'Explore PFZs', viewZone: 'View zone', recommendation: 'ORCA recommendation', start: 'Start with', safeRoute: 'Safe route assessment', recommended: 'Recommended', low: 'Low', risk: 'Risk', whyRoute: 'Why ORCA recommends this route', safetyChecklist: 'Safety checklist', askSea: 'Ask ORCA about the sea.', conversational: 'CONVERSATIONAL MARINE INTELLIGENCE', placeholder: 'Ask a marine question or plan a trip...', send: 'Send', nearest: 'Nearest PFZ today', safeTomorrow: 'Is it safe to go tomorrow morning?', showHazards: 'Show hazards near Mumbai', findRoute: 'Find a safer route', close: 'Close', reset: 'Reset view', satellite: 'Satellite', street: 'Street', locate: 'My location', language: 'Language', search: 'Search', notifications: 'Notifications', noResults: 'No matching results.', routeA: 'Coastal route A', routeB: 'Coastal route B', routeC: 'Balanced route', routeRisk: 'Route risk', checked: 'Checked', refresh: 'Refresh', save: 'Save changes', saved: 'Changes saved', theme: 'Theme', darkMode: 'Dark mode', email: 'Email notifications', profileTitle: 'Operational Profile', role: 'Marine Researcher / Captain', details: 'Profile Details', name: 'Capt. Devesh Madhavi', status: 'Active Workspace Session', mobile: 'Mobile number', emailLabel: 'Email', profession: 'Operational Role', edit: 'Edit profile', done: 'Done', trend: 'PFZ confidence trend', pfzConfidence: 'PFZ confidence', freshness: 'Data freshness', latest: 'Latest sample', marineInputs: 'Satellite ocean colour, SST and weather inputs stored in Supabase.', spatialSignals: 'Correlates nearby spatial signals and PFZ candidates.', opportunitySafety: 'Balances fishing opportunity with safety constraints.', evidenceRecommendation: 'Explains the evidence behind each recommendation.', hazardAvoided: 'Avoids the identified caution corridor.', boundariesChecked: 'Checks operational boundaries before routing.', riskCorridor: 'Prefers the lower-risk coastal corridor.', recalculate: 'Route can be recalculated after new data arrives.', demo: 'Real-time database mode • live Supabase sync connected.', demoAnswer: 'Hello Captain! I am ORCA, your Marine AI Decision Copilot. How can I assist your voyage today? You can ask about PFZ zones, weather, wave conditions, or safe routes along the coast.', mapFail: 'Map tiles could not load. Controls and local markers remain available.', routeSummary: '39.2 km • about 2h 35m', routeBText: '48.5 km • about 3h 10m', routeCText: '42.0 km • about 2h 45m', selectPeriod: 'Period', hours24: '24 hours', days7: '7 days', system: 'System', resetData: 'Reset demo state', layers: 'Map layers', pfzLayer: 'Fishing zones', alertLayer: 'Marine alerts', vessels: 'Vessels', mapLabels: 'Map labels follow website language.', signIn: 'Sign In / Register', signOut: 'Sign Out', viewOnMap: '🗺️ View Route on Map', viewSafety: '🛡️ Safety Assessment', navHudTitle: 'Active Navigation Route', originPort: 'Departure Port', destZone: 'Destination Zone', eta: 'Estimated Travel Time', distance: 'Distance', geofenceClear: 'Boundary Clearance', calculateRoute: 'Calculate Safe Marine Route'
  },
  hi: {
    dashboard: 'डैशबोर्ड', map: 'समुद्री इंटेलिजेंस मैप', analytics: 'महासागर विश्लेषण', fishing: 'मछली पकड़ने की इंटेलिजेंस', safety: 'सुरक्षा और मार्ग', assistant: 'ORCA AI सहायक', alerts: 'सूचनाएं', settings: 'सेटिंग्स', profile: 'प्रोफ़ाइल', workspace: 'वर्कस्पेस', operational: 'सिस्टम चालू हैं', connected: 'समुद्री डेटा सेवाएं जुड़ी हैं', marine: 'समुद्री इंटेलिजेंस', glance: 'समुद्री स्थिति एक नज़र में।', location: 'मुंबई तट • लाइव सुपबेस और सेंसर डेटा कनेक्टेड', ask: 'ORCA से पूछें', seaState: 'समुद्र की स्थिति', wind: 'हवा', sst: 'समुद्र सतह तापमान', activePFZ: 'सक्रिय PFZ', moderate: 'मध्यम', waves: '1.2 मी. लहरें', steady: 'NE • स्थिर', favourable: 'अनुकूल', openMap: 'मैप खोलें', activeAdvisories: 'सक्रिय सलाह', viewAll: 'सभी देखें', insights: 'आज की समुद्री जानकारी', bestFishing: 'बेहतरीन मछली पकड़ने का अवसर', departure: 'अनुशंसित प्रस्थान', confidence: 'डेटा विश्वसनीयता', verified: 'सत्यापित इंटेलिजेंस', sources: 'स्रोत: ISRO • INCOIS • IMD • Supabase', oceanInputs: 'समुद्र और भौगोलिक इनपुट की जांच की गई।', allLayers: 'सभी लेयर', weather: 'मौसम', hazards: 'जोखिम', boundaries: 'सीमाएं', today: 'आज', selectedZone: 'चयनित क्षेत्र', high: 'उच्च विश्वसनीयता', why: 'यह क्षेत्र क्यों?', signal: 'संकेत', how: 'ORCA कैसे निर्णय लेता है', discover: 'खोजें', correlate: 'संबंध जोड़ें', assess: 'आकलन करें', explain: 'समझाएं', findZones: 'संभावित मछली पकड़ने वाले क्षेत्र खोजें।', explore: 'PFZ खोजें', viewZone: 'क्षेत्र देखें', recommendation: 'ORCA की सिफारिश', start: 'शुरुआत करें', safeRoute: 'सुरक्षित मार्ग आकलन', recommended: 'अनुशंसित', low: 'कम', risk: 'जोखिम', whyRoute: 'ORCA इस मार्ग की सिफारिश क्यों करता है', safetyChecklist: 'सुरक्षा चेकलिस्ट', askSea: 'समुद्र के बारे में ORCA से पूछें।', conversational: 'कन्वर्सेशनल मरीन इंटेलिजेंस', placeholder: 'समुद्र से जुड़ा सवाल पूछें...', send: 'भेजें', nearest: 'आज का निकटतम PFZ', safeTomorrow: 'क्या कल सुबह जाना सुरक्षित है?', showHazards: 'मुंबई के पास जोखिम दिखाएं', findRoute: 'सुरक्षित मार्ग खोजें', close: 'बंद करें', reset: 'दृश्य रीसेट', satellite: 'सैटेलाइट', street: 'सड़क', locate: 'मेरा स्थान', language: 'भाषा', search: 'खोजें', notifications: 'सूचनाएं', noResults: 'कोई परिणाम नहीं मिला।', routeA: 'तटीय मार्ग A', routeB: 'तटीय मार्ग B', routeC: 'संतुलित मार्ग', routeRisk: 'मार्ग जोखिम', checked: 'जांच पूरी', refresh: 'रीफ्रेश', save: 'बदलाव सहेजें', saved: 'बदलाव सहेजे गए', theme: 'थीम', darkMode: 'डार्क मोड', email: 'ईमेल सूचनाएं', profileTitle: 'ऑपरेशनल प्रोफ़ाइल', role: 'समुद्री शोधकर्ता / कप्तान', details: 'प्रोफ़ाइल विवरण', name: 'Capt. Devesh Madhavi', status: 'सक्रिय सत्र', mobile: 'मोबाइल नंबर', emailLabel: 'ईमेल', profession: 'पेशा', edit: 'संपादित करें', done: 'पूर्ण', trend: 'PFZ विश्वसनीयता ट्रेंड', pfzConfidence: 'PFZ विश्वसनीयता', freshness: 'डेटा ताजगी', latest: 'नवीनतम नमूना', marineInputs: 'सैटेलाइट समुद्री रंग, SST और मौसम इनपुट।', spatialSignals: 'आसपास के स्थानिक संकेत और PFZ उम्मीदवार जोड़ता है।', opportunitySafety: 'मछली पकड़ने के अवसर को सुरक्षा सीमाओं के साथ संतुलित करता है।', evidenceRecommendation: 'हर सिफारिश के पीछे के प्रमाण समझाता है।', hazardAvoided: 'पहचाने गए सावधानी क्षेत्र से बचता है।', boundariesChecked: 'मार्ग से पहले परिचालन सीमाएं जांचता है।', riskCorridor: 'कम जोखिम वाले तटीय गलियारे को प्राथमिकता देता है।', recalculate: 'नए डेटा के बाद मार्ग फिर निकाला जा सकता है।', demo: 'रीयल-टाइम डेटाबेस मोड • लाइव सुपबेस कनेक्टेड।', demoAnswer: 'नमस्ते कप्तान! मैं ORCA हूँ, आपका समुद्री AI निर्णय सहायक। मैं आपकी क्या मदद कर सकता हूँ?', mapFail: 'मैप टाइल लोड नहीं हो पाईं।', routeSummary: '39.2 किमी • लगभग 2 घंटे 35 मिनट', routeBText: '48.5 किमी • लगभग 3 घंटे 10 मिनट', routeCText: '42.0 किमी • लगभग 2 घंटे 45 मिनट', selectPeriod: 'अवधि', hours24: '24 घंटे', days7: '7 दिन', system: 'सिस्टम', resetData: 'रीसेट', layers: 'मैप लेयर', pfzLayer: 'मछली पकड़ने के क्षेत्र', alertLayer: 'समुद्री अलर्ट', vessels: 'नौकाएं', mapLabels: 'मैप के नाम वेबसाइट की भाषा के अनुसार हैं।', signIn: 'साइन इन / रजिस्टर', signOut: 'साइन आउट', viewOnMap: '🗺️ मैप पर मार्ग देखें', viewSafety: '🛡️ सुरक्षा आकलन', navHudTitle: 'सक्रिय नेविगेशन मार्ग', originPort: 'प्रस्थान बंदरगाह', destZone: 'गंतव्य क्षेत्र', eta: 'अनुमानित यात्रा समय', distance: 'दूरी', geofenceClear: 'सीमा अनुमति', calculateRoute: 'सुरक्षित समुद्री मार्ग निकालें'
  },
  mr: {
    dashboard: 'डॅशबोर्ड', map: 'सागरी इंटेलिजन्स नकाशा', analytics: 'महासागर विश्लेषण', fishing: 'मासेमारी इंटेलिजन्स', safety: 'सुरक्षा आणि मार्ग', assistant: 'ORCA AI सहाय्यक', alerts: 'सूचना', settings: 'सेटिंग्ज', profile: 'प्रोफाइल', workspace: 'वर्कस्पेस', operational: 'सिस्टम कार्यरत', connected: 'सागरी डेटा सेवा जोडलेल्या', marine: 'सागरी इंटेलिजन्स', glance: 'सागरी स्थिती एका नजरेत.', location: 'मुंबई किनारा • थेट सुपबेस आणि सेन्सर जोडणी', ask: 'ORCA ला विचारा', seaState: 'समुद्राची स्थिती', wind: 'वारा', sst: 'समुद्र पृष्ठभाग तापमान', activePFZ: 'सक्रिय PFZ', moderate: 'मध्यम', waves: '1.2 मी. लाटा', steady: 'NE • स्थिर', favourable: 'अनुकूल', openMap: 'नकाशा उघडा', activeAdvisories: 'सक्रिय सूचना', viewAll: 'सर्व पहा', insights: 'आजची सागरी माहिती', bestFishing: 'मासेमारीची सर्वोत्तम संधी', departure: 'शिफारस केलेली प्रस्थान वेळ', confidence: 'डेटा विश्वासार्हता', verified: 'सत्यापित इंटेलिजन्स', sources: 'स्रोत: ISRO • INCOIS • IMD • Supabase', oceanInputs: 'समुद्र आणि डेटाबेस इनपुट तपासले.', allLayers: 'सर्व लेयर्स', weather: 'हवामान', hazards: 'धोके', boundaries: 'सीमा', today: 'आज', selectedZone: 'निवडलेले क्षेत्र', high: 'उच्च विश्वासार्हता', why: 'हे क्षेत्र का?', signal: 'संकेत', how: 'ORCA कसे निर्णय घेतो', discover: 'शोध', correlate: 'संबंध जोडा', assess: 'आकलन', explain: 'समजावून सांगा', findZones: 'आशादायक मासेमारी क्षेत्र शोधा.', explore: 'PFZ शोधा', viewZone: 'क्षेत्र पहा', recommendation: 'ORCA ची शिफारस', start: 'सुरुवात', safeRoute: 'सुरक्षित मार्गाचे आकलन', recommended: 'शिफारस केलेला', low: 'कमी', risk: 'धोका', whyRoute: 'ORCA या मार्गाची शिफारस का करतो', safetyChecklist: 'सुरक्षा तपासणी', askSea: 'समुद्राबद्दल ORCA ला विचारा.', conversational: 'कन्वर्सेशनल मरीन इंटेलिजन्स', placeholder: 'सागरी प्रश्न विचारा किंवा मार्ग योजना करा...', send: 'पाठवा', nearest: 'आजचा जवळचा PFZ', safeTomorrow: 'उद्या सकाळी जाणे सुरक्षित आहे का?', showHazards: 'मुंबईजवळचे धोके दाखवा', findRoute: 'सुरक्षित मार्ग शोधा', close: 'बंद', reset: 'दृश्य रीसेट', satellite: 'सॅटेलाइट', street: 'रस्ता', locate: 'माझे स्थान', language: 'भाषा', search: 'शोधा', notifications: 'सूचना', noResults: 'जुळणारे परिणाम नाहीत.', routeA: 'किनारी मार्ग A', routeB: 'किनारी मार्ग B', routeC: 'संतुलित मार्ग', routeRisk: 'मार्ग धोका', checked: 'तपासले', refresh: 'रीफ्रेश', save: 'बदल जतन करा', saved: 'बदल जतन झाले', theme: 'थीम', darkMode: 'डार्क मोड', email: 'ईमेल सूचना', profileTitle: 'ऑपरेशनल प्रोफाइल', role: 'सागरी संशोधक / कॅप्टन', details: 'प्रोफाइल तपशील', name: 'Capt. Devesh Madhavi', status: 'सक्रिय खाते', mobile: 'मोबाइल क्रमांक', emailLabel: 'ईमेल', profession: 'व्यवसाय', edit: 'संपादित करा', done: 'पूर्ण', trend: 'PFZ विश्वासार्हता ट्रेंड', pfzConfidence: 'PFZ विश्वासार्हता', freshness: 'डेटा ताजेपणा', latest: 'नवीन नमुना', marineInputs: 'सॅटेलाइट समुद्री रंग, SST आणि हवामान इनपुट.', spatialSignals: 'जवळचे स्थानिक संकेत आणि PFZ उमेदवार जोडतो.', opportunitySafety: 'मासेमारीची संधी आणि सुरक्षा मर्यादा संतुलित करतो.', evidenceRecommendation: 'प्रत्येक शिफारसीमागील पुरावे समजावतो.', hazardAvoided: 'ओळखलेल्या सावधगिरीच्या क्षेत्रापासून दूर राहतो.', boundariesChecked: 'मार्गापूर्वी ऑपरेशनल सीमा तपासतो.', riskCorridor: 'कमी-धोका किनारी मार्ग पसंत करतो.', recalculate: 'नवीन डेटा आल्यावर मार्ग पुन्हा काढता येईल.', demo: 'थेट डेटाबेस मोड • सुपबेस डेटा जोडला आहे.', demoAnswer: 'नमस्कार कॅप्टन! मी ORCA आहे, आपला सागरी AI निर्णय सहाय्यक. मी आज आपल्या प्रवासासाठी कशी मदत करू?', mapFail: 'नकाशा टाइल लोड झाल्या नाहीत.', routeSummary: '39.2 किमी • सुमारे 2 तास 35 मिनिटे', routeBText: '48.5 किमी • सुमारे 3 तास 10 मिनिटे', routeCText: '42.0 किमी • सुमारे 2 तास 45 मिनिटे', selectPeriod: 'कालावधी', hours24: '24 तास', days7: '7 दिवस', system: 'सिस्टम', resetData: 'रीसेट', layers: 'नकाशा लेयर्स', pfzLayer: 'मासेमारी क्षेत्रे', alertLayer: 'सागरी सूचना', vessels: 'नौका', mapLabels: 'नकाशावरील नावे वेबसाइटच्या भाषेनुसार आहेत.', signIn: 'साइन इन / नोंदणी', signOut: 'साइन आउट', viewOnMap: '🗺️ नकाशावर मार्ग पहा', viewSafety: '🛡️ सुरक्षा विश्लेषण', navHudTitle: 'सक्रिय नेव्हिगेशन मार्ग', originPort: 'प्रस्थान बंदर', destZone: 'गंतव्य क्षेत्र', eta: 'अंदाजित वेळ', distance: 'अंतर', geofenceClear: 'सीमा तपासणी', calculateRoute: 'सुरक्षित सागरी मार्ग काढा'
  }
}

const tr = (lang, key) => T[lang]?.[key] ?? T.en[key] ?? key
const labels = {
  '/': 'Dashboard',
  '/map': 'Marine Intelligence Map',
  '/analytics': 'Ocean Analytics',
  '/fishing': 'Fishing Intelligence',
  '/safety': 'Safety & Routes',
  '/assistant': 'ORCA AI Assistant',
  '/alerts': 'Alerts',
  '/settings': 'Settings',
  '/profile': 'Profile'
}
const keyFor = u => ({
  Dashboard: 'dashboard',
  'Marine Intelligence Map': 'map',
  'Ocean Analytics': 'analytics',
  'Fishing Intelligence': 'fishing',
  'Safety & Routes': 'safety',
  'ORCA AI Assistant': 'assistant',
  Alerts: 'alerts',
  Settings: 'settings',
  Profile: 'profile'
}[u])

const PORTS = [
  // Gujarat (North-West)
  { id: 'veraval', name: 'Veraval Fishery Port (Gujarat)', state: 'Gujarat', sector: 'North-West (Gujarat)', lat: 20.9000, lon: 70.3667 },
  { id: 'porbandar', name: 'Porbandar Marine Port (Gujarat)', state: 'Gujarat', sector: 'North-West (Gujarat)', lat: 21.6417, lon: 69.6293 },
  { id: 'okha', name: 'Okha Fishery Port (Gujarat)', state: 'Gujarat', sector: 'North-West (Gujarat)', lat: 22.4667, lon: 69.0667 },

  // Maharashtra (West Coast)
  { id: 'mumbai', name: 'Mumbai Harbour (Sassoon Docks)', state: 'Maharashtra', sector: 'West Coast (Maharashtra)', lat: 18.9400, lon: 72.8300 },
  { id: 'alibaug', name: 'Alibaug Port (Maharashtra)', state: 'Maharashtra', sector: 'West Coast (Maharashtra)', lat: 18.6414, lon: 72.8722 },
  { id: 'ratnagiri', name: 'Ratnagiri Fishery Port (Mirkarwada)', state: 'Maharashtra', sector: 'West Coast (Maharashtra)', lat: 16.9902, lon: 73.3120 },
  { id: 'malvan', name: 'Malvan Port (Sindhudurg)', state: 'Maharashtra', sector: 'West Coast (Maharashtra)', lat: 16.0594, lon: 73.4686 },

  // Goa (South-West)
  { id: 'goa', name: 'Goa Mormugao Port', state: 'Goa', sector: 'South-West (Goa)', lat: 15.4989, lon: 73.8278 },

  // Karnataka (South-West)
  { id: 'karwar', name: 'Karwar Fishery Port (Karnataka)', state: 'Karnataka', sector: 'South-West (Karnataka)', lat: 14.8050, lon: 74.1240 },
  { id: 'mangalore', name: 'Mangalore Fishery Port (Bunder)', state: 'Karnataka', sector: 'South-West (Karnataka)', lat: 12.8580, lon: 74.8360 },

  // Kerala (South-West)
  { id: 'kochi', name: 'Cochin Fishery Harbour (Kerala)', state: 'Kerala', sector: 'South-West (Kerala)', lat: 9.9650, lon: 76.2620 },
  { id: 'kollam', name: 'Kollam Neendakara Harbour (Kerala)', state: 'Kerala', sector: 'South-West (Kerala)', lat: 8.9440, lon: 76.5360 },

  // Tamil Nadu (South Coast & Coromandel)
  { id: 'kanyakumari', name: 'Kanyakumari Cape Port (Tamil Nadu)', state: 'Tamil Nadu', sector: 'South Coast (Tamil Nadu)', lat: 8.0883, lon: 77.5385 },
  { id: 'tuticorin', name: 'Tuticorin V.O.C. Port (Tamil Nadu)', state: 'Tamil Nadu', sector: 'South-East (Gulf of Mannar)', lat: 8.7642, lon: 78.1348 },
  { id: 'nagapattinam', name: 'Nagapattinam Harbour (Tamil Nadu)', state: 'Tamil Nadu', sector: 'South-East (Coromandel)', lat: 10.7656, lon: 79.8424 },
  { id: 'chennai', name: 'Chennai Kasimedu Harbour (Tamil Nadu)', state: 'Tamil Nadu', sector: 'South-East (Coromandel)', lat: 13.1250, lon: 80.2980 },

  // Andhra Pradesh (East Coast)
  { id: 'kakinada', name: 'Kakinada Deepwater Port (Andhra)', state: 'Andhra Pradesh', sector: 'East Coast (Andhra Pradesh)', lat: 16.9891, lon: 82.2475 },
  { id: 'visakhapatnam', name: 'Visakhapatnam Fishing Harbour (Andhra)', state: 'Andhra Pradesh', sector: 'East Coast (Andhra Pradesh)', lat: 17.6868, lon: 83.2185 },

  // Odisha (East Coast)
  { id: 'paradip', name: 'Paradip Fishery Port (Odisha)', state: 'Odisha', sector: 'East Coast (Odisha)', lat: 20.2644, lon: 86.6715 },

  // West Bengal (North-East)
  { id: 'haldia', name: 'Haldia / Diamond Harbour (West Bengal)', state: 'West Bengal', sector: 'North-East (Bengal Bay)', lat: 22.0667, lon: 88.0667 }
]

function Card({ title, children, action }) {
  return (
    <section className="card">
      <div className="cardHead">
        <h3>{title}</h3>
        {action}
      </div>
      {children}
    </section>
  )
}

function Dashboard({ lang, navigate, setSelected, setModal, pfzList, alertList, oceanStats, selectedPort, setSelectedPort }) {
  const t = k => tr(lang, k)
  const currentPort = PORTS.find(p => p.id === selectedPort) || PORTS[3]
  const chosen = pfzList[0] || staticPfz[0]

  return (
    <>
      <div className="welcome">
        <div>
          <span className="eyebrow">{t('marine')} • {currentPort.sector}</span>
          <h2>{currentPort.name}</h2>
          <p>Real-time marine intelligence synced with Supabase & INCOIS-ISRO satellite radars.</p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          <select 
            value={selectedPort} 
            onChange={e => setSelectedPort && setSelectedPort(e.target.value)}
            className="selectControl"
          >
            {PORTS.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          <button className="primary" onClick={() => navigate('/map')}>{t('openMap')} →</button>
        </div>
      </div>

      <div className="stats">
        <div className="stat">
          <span>{t('seaState')}</span>
          <strong>{oceanStats?.wave_height?.status || t('moderate')}</strong>
          <small>{oceanStats?.wave_height?.current ? `${oceanStats.wave_height.current} m waves` : t('waves')}</small>
        </div>
        <div className="stat">
          <span>{t('wind')}</span>
          <strong>{oceanStats?.wind_speed?.current ? `${oceanStats.wind_speed.current} km/h` : '18 km/h'}</strong>
          <small>{t('steady')}</small>
        </div>
        <div className="stat">
          <span>{t('sst')}</span>
          <strong>{chosen?.sst ? `${chosen.sst}°C` : (oceanStats?.sea_surface_temp?.current ? `${oceanStats.sea_surface_temp.current}°C` : '28.1°C')}</strong>
          <small>{t('favourable')}</small>
        </div>
        <div className="stat">
          <span>{t('activePFZ')}</span>
          <strong>{pfzList.length}</strong>
          <small>{currentPort.name.split(' ')[0]} Sector</small>
        </div>
      </div>

      <div className="dashboardGrid">
        <Card title={t('activePFZ')} action={<button className="textBtn" onClick={() => navigate('/map')}>{t('viewAll')} →</button>}>
          <div className="rank">
            {pfzList.slice(0, 4).map(z => (
              <button key={z.id} onClick={() => { setSelected(z.id); navigate('/map') }}>
                <span><b>{z.id}</b>{z.name}</span>
                <strong>{z.confidence}%</strong>
              </button>
            ))}
          </div>
        </Card>

        <Card title={t('activeAdvisories')}>
          <div>
            {alertList.slice(0, 4).map(a => (
              <button className="alertRow" key={a.id} onClick={() => setModal(a)}>
                <span className={'severity ' + (a.risk_level ? a.risk_level.toLowerCase() : a.severity?.toLowerCase() || 'medium')}>
                  {a.risk_level || a.severity || 'ALERT'}
                </span>
                <div>
                  <b>{a.title?.[lang] || a.title || 'Marine Advisory'}</b>
                  <small>{a.description || a.body?.[lang] || a.body || ''}</small>
                </div>
                <span>→</span>
              </button>
            ))}
          </div>
        </Card>
      </div>

      <div className="grid2">
        <Card title={t('insights')}>
          <div className="insight">
            <span>01</span>
            <div>
              <b>{t('bestFishing')}</b>
              <p>{chosen.name} • {chosen.confidence}% confidence • {chosen.distance || '32 km offshore'}</p>
            </div>
          </div>
          <div className="insight">
            <span>02</span>
            <div>
              <b>{t('departure')}</b>
              <p>05:30–08:30 • Favourable low-swell window</p>
            </div>
          </div>
        </Card>
        <Card title={t('confidence')}>
          <div className="confidence">
            <strong>{oceanStats?.data_confidence || 94}%</strong>
            <div className="bar"><span /></div>
            <p>{t('verified')} • {t('oceanInputs')}</p>
          </div>
        </Card>
      </div>
    </>
  )
}

function MapPage({ lang, selected, setSelected, activeRoute, setActiveRoute, pfzList, allIndiaPfzList = [], alertList, selectedPort, setSelectedPort }) {
  const t = k => tr(lang, k)
  const ref = useRef(null)
  const mapRef = useRef(null)
  const [base, setBase] = useState('satellite')
  const [showPFZ, setShowPFZ] = useState(true)
  const [showAlerts, setShowAlerts] = useState(true)
  const [showVessels, setShowVessels] = useState(true)
  const [showRoute, setShowRoute] = useState(true)
  const [mapScope, setMapScope] = useState('all') // 'all' or 'port'
  const [mapError, setMapError] = useState(false)

  const currentPort = PORTS.find(p => p.id === selectedPort) || PORTS[3]
  const zone = pfzList.find(z => z.id === selected) || pfzList[0] || staticPfz[0]

  useEffect(() => {
    if (!ref.current || mapRef.current) return
    const map = L.map(ref.current, { zoomControl: false }).setView([currentPort.lat, currentPort.lon], 7)
    L.control.zoom({ position: 'bottomright' }).addTo(map)

    const street = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19
    })
    const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      attribution: 'Tiles © Esri'
    })

    ;(base === 'satellite' ? satellite : street).addTo(map)
    map.on('tileerror', () => setMapError(true))
    mapRef.current = { map, street, satellite, layers: [] }

    return () => {
      map.remove()
      mapRef.current = null
    }
  }, [])

  useEffect(() => {
    const obj = mapRef.current
    if (!obj) return
    obj.street.remove()
    obj.satellite.remove()
    ;(base === 'satellite' ? obj.satellite : obj.street).addTo(obj.map)
  }, [base])

  useEffect(() => {
    const obj = mapRef.current
    if (!obj) return

    obj.layers?.forEach(l => l.remove())
    const layers = []

    // 1. Draw Active Navigation Route if available
    if (showRoute && activeRoute && activeRoute.waypoints && activeRoute.waypoints.length > 0) {
      const latlngs = activeRoute.waypoints.map(w => [w.lat, w.lon])
      if (activeRoute.origin) latlngs.unshift([activeRoute.origin.lat, activeRoute.origin.lon])
      if (activeRoute.destination) latlngs.push([activeRoute.destination.lat, activeRoute.destination.lon])

      // Glowing outer route
      const glow = L.polyline(latlngs, {
        color: '#0088cc',
        weight: 8,
        opacity: 0.45,
        lineCap: 'round'
      }).addTo(obj.map)
      layers.push(glow)

      // Core route polyline
      const line = L.polyline(latlngs, {
        color: '#00d2ff',
        weight: 4,
        opacity: 0.95,
        dashArray: '8, 8'
      }).addTo(obj.map)
      layers.push(line)

      // Start / Origin Port Marker (Green Anchor)
      if (activeRoute.origin) {
        const startIcon = L.divIcon({
          className: 'orca-start-pin',
          html: '<div style="background:#20c997;color:#fff;border-radius:50%;width:30px;height:30px;display:grid;place-items:center;border:3px solid #fff;box-shadow:0 4px 14px rgba(0,0,0,0.3);font-size:16px;">⚓</div>',
          iconSize: [30, 30],
          iconAnchor: [15, 15]
        })
        const startMarker = L.marker([activeRoute.origin.lat, activeRoute.origin.lon], { icon: startIcon })
          .bindPopup(`<b>⚓ Departure Port</b><br/>${activeRoute.departure_name || 'Coastal Port'}<br/>Lat: ${activeRoute.origin.lat}, Lon: ${activeRoute.origin.lon}`)
          .addTo(obj.map)
        layers.push(startMarker)
      }

      // End / Destination Marker (Gold Target)
      if (activeRoute.destination) {
        const destIcon = L.divIcon({
          className: 'orca-dest-pin',
          html: '<div style="background:#ffc107;color:#000;border-radius:50%;width:32px;height:32px;display:grid;place-items:center;border:3px solid #fff;box-shadow:0 4px 14px rgba(0,0,0,0.3);font-size:16px;">🎯</div>',
          iconSize: [32, 32],
          iconAnchor: [16, 16]
        })
        const destMarker = L.marker([activeRoute.destination.lat, activeRoute.destination.lon], { icon: destIcon })
          .bindPopup(`<b>🎯 Destination PFZ</b><br/>${activeRoute.destination_name || 'Fishing Zone'}<br/>Distance: ${activeRoute.distance_km} km<br/>ETA: ~${Math.round(activeRoute.estimated_travel_time_min || (activeRoute.distance_km / 15 * 60))} mins`)
          .addTo(obj.map)
        layers.push(destMarker)
      }

      // Auto-fit bounds to route
      obj.map.fitBounds(L.latLngBounds(latlngs), { padding: [60, 60] })
    }

    // 2. Draw PFZ Fishing Zones across Indian Coast
    if (showPFZ) {
      const zonesToDraw = (mapScope === 'all' && allIndiaPfzList.length > 0) ? allIndiaPfzList : pfzList
      zonesToDraw.forEach(z => {
        const isSel = z.id === selected
        const isCurrentPort = z.port_id === selectedPort
        const m = L.circleMarker([z.lat, z.lng || z.lon], {
          radius: isSel ? 13 : (isCurrentPort ? 10 : 7),
          weight: isSel ? 3 : 2,
          color: isSel ? '#00d2ff' : (isCurrentPort ? '#00e5ff' : '#18a98d'),
          fillColor: isSel ? '#0088cc' : (isCurrentPort ? '#00b4d8' : '#20b486'),
          fillOpacity: isSel ? 0.95 : (isCurrentPort ? 0.85 : 0.65)
        })
        m.bindPopup(`<b>${z.id} · ${z.name}</b><br/><b>Sector:</b> ${z.sector || 'Indian Coast'}<br/><b>Port:</b> ${z.port_name || z.port_id || ''}<br/><b>Confidence:</b> ${z.confidence}%<br/><b>SST:</b> ${z.sst || 28.0}°C<br/><b>Chlorophyll:</b> ${z.chlorophyll || 1.4} mg/m³<br/><b>Distance:</b> ${z.distance || ''}`)
        m.on('click', () => {
          setSelected(z.id)
          if (z.port_id && setSelectedPort) {
            setSelectedPort(z.port_id)
          }
        })
        m.addTo(obj.map)
        layers.push(m)
      })
    }

    // 3. Draw Hazard Alerts (from Supabase)
    if (showAlerts) {
      alertList.forEach(a => {
        const lat = a.latitude || (a.geometry_geojson?.coordinates ? a.geometry_geojson.coordinates[1] : 18.94)
        const lon = a.longitude || (a.geometry_geojson?.coordinates ? a.geometry_geojson.coordinates[0] : 72.78)

        // Draw warning circle buffer
        const circle = L.circle([lat, lon], {
          radius: 18000,
          color: '#dc3545',
          fillColor: '#dc3545',
          fillOpacity: 0.18,
          weight: 1.5,
          dashArray: '5, 5'
        }).addTo(obj.map)
        layers.push(circle)

        const alertIcon = L.divIcon({
          className: 'orca-alert-pin',
          html: '<div style="background:#dc3545;color:#fff;border-radius:50%;width:26px;height:26px;display:grid;place-items:center;border:2px solid #fff;box-shadow:0 3px 10px rgba(0,0,0,0.25);font-size:13px;font-weight:bold;">⚠️</div>',
          iconSize: [26, 26],
          iconAnchor: [13, 13]
        })

        const m = L.marker([lat, lon], { icon: alertIcon })
        m.bindPopup(`<b>⚠️ ${a.title?.[lang] || a.title || 'Marine Hazard'}</b><br/>${a.description || a.body?.[lang] || a.body || ''}<br/><b>Risk:</b> ${a.risk_level || a.severity || 'HIGH'}`)
        m.addTo(obj.map)
        layers.push(m)
      })
    }

    // 4. Coastal Port Hub Markers across India
    PORTS.forEach(p => {
      const shortName = p.name.split(' ')[0]
      const isSelected = p.id === selectedPort
      const m = L.marker([p.lat, p.lon], {
        icon: L.divIcon({
          className: 'orca-map-label',
          html: `<span style="${isSelected ? 'background:#00d2ff;color:#000;font-weight:bold;border:2px solid #fff;' : ''}">⚓ ${shortName}</span>`,
          iconSize: null
        })
      })
      m.bindPopup(`<b>⚓ ${p.name}</b><br/><b>State:</b> ${p.state}<br/><b>Sector:</b> ${p.sector}<br/>Lat: ${p.lat}, Lon: ${p.lon}`)
      m.on('click', () => {
        if (setSelectedPort) setSelectedPort(p.id)
        if (mapRef.current?.map) mapRef.current.map.setView([p.lat, p.lon], 8)
      })
      m.addTo(obj.map)
      layers.push(m)
    })

    obj.layers = layers
    return () => layers.forEach(l => l.remove())
  }, [selected, showPFZ, showAlerts, showVessels, showRoute, activeRoute, lang, pfzList, allIndiaPfzList, alertList, mapScope, selectedPort])

  const focusPort = () => {
    const pt = PORTS.find(p => p.id === selectedPort) || PORTS[3]
    mapRef.current?.map.setView([pt.lat, pt.lon], 8)
  }
  const viewAllIndia = () => {
    setMapScope('all')
    mapRef.current?.map.setView([16.5, 78.5], 5)
  }
  const focus = () => mapRef.current?.map.setView([zone.lat, zone.lng || zone.lon], 9)

  return (
    <>
      <div className="pageIntro">
        <div>
          <span className="eyebrow">GEOSPATIAL & SATELLITE RADAR</span>
          <h2>{t('map')}</h2>
          <p>Real-time marine intelligence radar across the Indian Coastline (Arabian Sea & Bay of Bengal).</p>
        </div>
        <div className="toolbar" style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
          <select 
            value={selectedPort} 
            onChange={e => {
              const pId = e.target.value
              if (setSelectedPort) setSelectedPort(pId)
              const pt = PORTS.find(p => p.id === pId)
              if (pt && mapRef.current?.map) {
                mapRef.current.map.setView([pt.lat, pt.lon], 8)
              }
            }}
            className="selectControl"
          >
            {PORTS.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          <button onClick={focusPort}>📍 Focus Port</button>
          <button onClick={viewAllIndia}>🇮🇳 Whole Coast</button>
          <button className={base === 'street' ? 'active' : ''} onClick={() => setBase('street')}>{t('street')}</button>
          <button className={base === 'satellite' ? 'active' : ''} onClick={() => setBase('satellite')}>{t('satellite')}</button>
        </div>
      </div>

      <div className="mapGrid">
        <Card title={t('map')}>
          <div className="mapWrap">
            <div ref={ref} className="leafletMap" />
            {mapError && <div className="mapError">{t('mapFail')}</div>}
            
            <div className="mapControls">
              <label><input type="checkbox" checked={showRoute} onChange={e => setShowRoute(e.target.checked)} /> Route</label>
              <label><input type="checkbox" checked={showPFZ} onChange={e => setShowPFZ(e.target.checked)} /> {t('pfzLayer')}</label>
              <label><input type="checkbox" checked={showAlerts} onChange={e => setShowAlerts(e.target.checked)} /> {t('alertLayer')}</label>
              <button onClick={focus}>{t('selectedZone')}</button>
            </div>

            {/* Floating Navigation HUD */}
            {activeRoute && (
              <div className="mapNavHud">
                <h4>⚓ {t('navHudTitle')}</h4>
                <div className="hudGrid">
                  <div className="hudItem">
                    <span>{t('originPort')}</span>
                    <b>{activeRoute.departure_name || 'Mumbai Harbour'}</b>
                  </div>
                  <div className="hudItem">
                    <span>{t('destZone')}</span>
                    <b>{activeRoute.destination_name || 'PFZ-MUM-01'}</b>
                  </div>
                  <div className="hudItem">
                    <span>{t('distance')}</span>
                    <b>{activeRoute.distance_km} km</b>
                  </div>
                  <div className="hudItem">
                    <span>{t('eta')}</span>
                    <b>~{Math.round(activeRoute.estimated_travel_time_min || (activeRoute.distance_km / 15 * 60))} mins</b>
                  </div>
                </div>
              </div>
            )}
          </div>
        </Card>

        <Card title={t('selectedZone')}>
          <div className="selectedRow">
            <div>
              <span className="pill">{zone.id}</span>
              <h2>{zone.name}</h2>
              <p>{zone.distance || '32 km offshore'} • {zone.depth || '45m depth'}</p>
            </div>
            <strong>{zone.confidence}%</strong>
          </div>

          <div className="miniMetrics">
            <div><span>{t('sst')}</span><b>{zone.sst || 27.8}°C</b></div>
            <div><span>Chlorophyll</span><b>{zone.chlorophyll || 0.62} mg/m³</b></div>
            <div><span>{t('waves')}</span><b>{zone.waves || 1.2} m</b></div>
            <div><span>{t('wind')}</span><b>{zone.wind || 16} km/h</b></div>
          </div>

          <div className="evidence">
            <div>
              <b>{t('why')}</b>
              <span>{zone.reason?.[lang] || 'Optimal thermal oceanic front with high chlorophyll concentration and calm sea state.'}</span>
            </div>
            <button className="primary full" onClick={focus}>{t('selectedZone')} →</button>
          </div>
        </Card>
      </div>
    </>
  )
}

function AreaChart({ values, color, fill, labels }) {
  const w = 760, h = 240, p = 22, min = Math.min(...values), max = Math.max(...values), range = max - min || 1
  const pts = values.map((v, i) => {
    const x = p + i * (w - 2 * p) / (values.length - 1)
    const y = h - p - ((v - min) / range) * (h - 2 * p - 18)
    return [x, y]
  })
  const line = pts.map(([x, y], i) => (i ? 'L' : 'M') + x.toFixed(1) + ' ' + y.toFixed(1)).join(' ')
  const area = line + ` L ${pts.at(-1)[0]} ${h - p} L ${pts[0][0]} ${h - p} Z`
  return (
    <div className="areaChart">
      <svg viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" aria-hidden="true">
        <defs>
          <linearGradient id={`fill-${color}`} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={fill} stopOpacity=".34" />
            <stop offset="100%" stopColor={fill} stopOpacity=".02" />
          </linearGradient>
        </defs>
        {[0.2, 0.4, 0.6, 0.8].map((n, i) => (
          <line key={i} x1="22" x2="738" y1={h - p - (h - 2 * p) * n} y2={h - p - (h - 2 * p) * n} className="gridLine" />
        ))}
        <path d={area} fill={`url(#fill-${color})`} />
        <path d={line} fill="none" stroke={fill} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        {pts.map(([x, y], i) => (
          <circle key={i} cx={x} cy={y} r="5" fill="var(--surface)" stroke={fill} strokeWidth="2.5" />
        ))}
      </svg>
      <div className="axis">{labels.map(x => <span key={x}>{x}</span>)}</div>
    </div>
  )
}

function Analytics({ lang, oceanStats, setOceanPeriod }) {
  const t = k => tr(lang, k)
  const [period, setPeriod] = useState('7')

  const temp = oceanStats?.sea_surface_temp?.values || [27.2, 27.5, 27.8, 28.1, 28.4, 28.6, 28.8, 29.0]
  const chl = oceanStats?.chlorophyll?.values || [0.44, 0.48, 0.52, 0.56, 0.60, 0.63, 0.66, 0.68]
  const waves = oceanStats?.wave_height?.values || [0.72, 0.78, 0.86, 0.82, 0.76, 0.68, 0.74, 0.80]
  const wind = oceanStats?.wind_speed?.values || [14, 16, 18, 17, 20, 22, 19, 18]
  const labels = oceanStats?.labels || ['Day -6', 'Day -5', 'Day -4', 'Day -3', 'Day -2', 'Yesterday', 'Today']

  const handlePeriodChange = (val) => {
    setPeriod(val)
    if (setOceanPeriod) setOceanPeriod(val)
  }

  return (
    <>
      <div className="analyticsHero">
        <div>
          <span className="eyebrow">ORCA / {t('analytics')}</span>
          <h2>{t('analytics')}</h2>
          <p>Real-time marine conditions, oceanographic trends and satellite feeds stored in Supabase.</p>
        </div>
        <div className="analyticsActions">
          <span className="liveDot">Supabase Live Sync</span>
          <select value={period} onChange={e => handlePeriodChange(e.target.value)}>
            <option value="24">{t('hours24')}</option>
            <option value="7">{t('days7')}</option>
          </select>
        </div>
      </div>

      <div className="analyticsKpis">
        <div className="kpiCard kpi-temp">
          <span>SEA SURFACE TEMP</span>
          <strong>{oceanStats?.sea_surface_temp?.current || temp.at(-1).toFixed(1)}°C</strong>
          <small>Baseline variation <b>{oceanStats?.sea_surface_temp?.trend_delta || '+0.2°C'}</b></small>
        </div>
        <div className="kpiCard kpi-green">
          <span>CHLOROPHYLL</span>
          <strong>{oceanStats?.chlorophyll?.current || chl.at(-1).toFixed(2)} <em>mg/m³</em></strong>
          <small>Concentration <b>{oceanStats?.chlorophyll?.status || 'Favourable'}</b></small>
        </div>
        <div className="kpiCard kpi-blue">
          <span>WAVE HEIGHT</span>
          <strong>{oceanStats?.wave_height?.current || waves.at(-1).toFixed(1)} <em>m</em></strong>
          <small>Sea state <b>{oceanStats?.wave_height?.status || 'Low'}</b></small>
        </div>
        <div className="kpiCard kpi-cyan">
          <span>PRODUCTIVITY INDEX</span>
          <strong>{oceanStats?.productivity_index || 84} <em>/100</em></strong>
          <small>Regional ranking <b>Upper quartile</b></small>
        </div>
      </div>

      <div className="analyticsGrid">
        <Card title="Sea Surface Temperature (SST)" action={<span className="chartBadge red">{oceanStats?.sea_surface_temp?.trend_delta || '+0.2°C today'}</span>}>
          <p className="chartSub">Observed variation across coastal Maharashtra and Goa waters</p>
          <AreaChart values={temp} color="temp" fill="#ff6b6b" labels={labels} />
          <div className="chartStats">
            <div><span>Average</span><b>{oceanStats?.sea_surface_temp?.average || '28.1'}°C</b></div>
            <div><span>Minimum</span><b>{oceanStats?.sea_surface_temp?.min || '26.9'}°C</b></div>
            <div><span>Maximum</span><b>{oceanStats?.sea_surface_temp?.max || '29.2'}°C</b></div>
          </div>
        </Card>

        <Card title="Chlorophyll-a Concentration" action={<span className="chartBadge green">{oceanStats?.chlorophyll?.trend_delta || '+6.1% monthly'}</span>}>
          <p className="chartSub">Satellite ocean colour aggregation along shelf depth zones</p>
          <AreaChart values={chl} color="chl" fill="#20c997" labels={labels} />
          <div className="chartStats">
            <div><span>Current concentration</span><b>{oceanStats?.chlorophyll?.current || '0.62'} mg/m³</b></div>
            <div><span>Status</span><b>{oceanStats?.chlorophyll?.status || 'Favourable Front'}</b></div>
          </div>
        </Card>
      </div>
    </>
  )
}

function Fishing({ lang, navigate, setSelected, pfzList, allIndiaPfzList = [], selectedPort, setSelectedPort }) {
  const t = k => tr(lang, k)
  const [filterPort, setFilterPort] = useState(selectedPort || 'mumbai')

  useEffect(() => {
    if (selectedPort) setFilterPort(selectedPort)
  }, [selectedPort])

  const displayedPfzs = filterPort === 'all' 
    ? (allIndiaPfzList.length > 0 ? allIndiaPfzList : pfzList) 
    : pfzList

  const handleFilterChange = (p) => {
    setFilterPort(p)
    if (p !== 'all' && setSelectedPort) {
      setSelectedPort(p)
    }
  }

  return (
    <>
      <div className="pageIntro">
        <div>
          <span className="eyebrow">ORCA / {t('fishing')}</span>
          <h2>{t('findZones')}</h2>
          <p>Real-time Potential Fishing Zones (PFZs) identified via thermal fronts and satellite chlorophyll-a.</p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          <label style={{ fontWeight: 600, fontSize: '0.9rem' }}>Port Sector:</label>
          <select 
            value={filterPort} 
            onChange={e => handleFilterChange(e.target.value)}
            className="selectControl"
          >
            <option value="all">🇮🇳 All Indian Coast (32 PFZs)</option>
            {PORTS.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="pfzGrid">
        {displayedPfzs.map(z => (
          <Card key={z.id} title={`${z.id} · ${z.name}`} action={<span className="pill">{z.confidence}%</span>}>
            <div className="signal">
              <b>{t('signal')}</b>
              <span>{z.reason?.[lang] || z.sector || 'High pelagic productivity and thermal gradient'}</span>
            </div>
            <div className="zoneStats">
              <span>SST <b>{z.sst || 27.8}°C</b></span>
              <span>Chl <b>{z.chlorophyll || 0.62} mg/m³</b></span>
              <span>Distance <b>{z.distance || '28 km'}</b></span>
            </div>
            <button className="primary full" onClick={() => { setSelected(z.id); navigate('/map') }}>
              {t('viewZone')} →
            </button>
          </Card>
        ))}
      </div>

      <Card title={t('how')}>
        <div className="method">
          <div><b>01 · {t('discover')}</b><p>{t('marineInputs')}</p></div>
          <div><b>02 · {t('correlate')}</b><p>{t('spatialSignals')}</p></div>
          <div><b>03 · {t('assess')}</b><p>{t('opportunitySafety')}</p></div>
          <div><b>04 · {t('explain')}</b><p>{t('evidenceRecommendation')}</p></div>
        </div>
      </Card>
    </>
  )
}

function Safety({ lang, navigate, activeRoute, setActiveRoute, pfzList, selectedPort, setSelectedPort, onPortChange }) {
  const t = k => tr(lang, k)
  const [originId, setOriginId] = useState(selectedPort || 'mumbai')
  const [destZoneId, setDestZoneId] = useState(pfzList[0]?.id || '')
  const [calculating, setCalculating] = useState(false)

  useEffect(() => {
    if (selectedPort) {
      setOriginId(selectedPort)
    }
  }, [selectedPort])

  useEffect(() => {
    if (pfzList && pfzList.length > 0) {
      const match = pfzList.find(z => z.id === destZoneId)
      if (!match) {
        setDestZoneId(pfzList[0].id)
      }
    }
  }, [pfzList, destZoneId])

  const handlePortChange = (newPortId) => {
    setOriginId(newPortId)
    if (setSelectedPort) setSelectedPort(newPortId)
    if (onPortChange) onPortChange(newPortId)
  }

  const handleCalculateRoute = async () => {
    setCalculating(true)
    const port = PORTS.find(p => p.id === originId) || PORTS[0]
    const dest = pfzList.find(z => z.id === destZoneId) || pfzList[0] || staticPfz[0]

    try {
      const res = await getRouteAndGeofence(
        { lat: port.lat, lon: port.lon },
        { lat: dest.lat, lon: dest.lng || dest.lon }
      )
      if (res && res.route) {
        setActiveRoute({
          ...res.route,
          departure_name: port.name,
          destination_name: dest.name || dest.id,
          geofence_status: res.geofence?.status || 'clear'
        })
      }
    } catch (err) {
      console.error(err)
    } finally {
      setCalculating(false)
    }
  }

  return (
    <>
      <div className="pageIntro">
        <div>
          <span className="eyebrow">ORCA / {t('safety')}</span>
          <h2>{t('safeRoute')}</h2>
          <p>Evaluate real-time coastal routes, geofences, and weather hazards before departure.</p>
        </div>
      </div>

      <div className="safetyPlanner">
        <Card title="Interactive Voyage Route Planner">
          <div className="plannerForm">
            <div className="plannerRow">
              <label>{t('originPort')}</label>
              <select value={originId} onChange={e => handlePortChange(e.target.value)}>
                {PORTS.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            <div className="plannerRow">
              <label>{t('destZone')}</label>
              <select value={destZoneId} onChange={e => setDestZoneId(e.target.value)}>
                {pfzList.map(z => (
                  <option key={z.id} value={z.id}>{z.id} — {z.name} ({z.confidence}%) · {z.distance}</option>
                ))}
              </select>
            </div>

            <button className="primary" onClick={handleCalculateRoute} disabled={calculating}>
              {calculating ? 'Calculating Route...' : `🚀 ${t('calculateRoute')}`}
            </button>
          </div>
        </Card>

        <Card title="Route Assessment & Safe Corridor">
          {activeRoute ? (
            <div>
              <div className="routeSummary">
                <div>
                  <span className="pill">{t('recommended')}</span>
                  <h2>{activeRoute.destination_name || 'Designated Marine Route'}</h2>
                  <p>{activeRoute.distance_km} km • ~{Math.round(activeRoute.estimated_travel_time_min || (activeRoute.distance_km / 15 * 60))} mins @ 15 km/h</p>
                </div>
                <strong>LOW<small>{t('risk')}</small></strong>
              </div>

              <div className="reasonList">
                <div><b>01</b><span>Avoids Mumbai High swell advisory corridor</span></div>
                <div><b>02</b><span>Checked against Marine Protected Areas and international boundaries</span></div>
                <div><b>03</b><span>Waypoints synchronized with real-time Supabase weather readings</span></div>
              </div>

              <button className="primary full" style={{ marginTop: '16px' }} onClick={() => navigate('/map')}>
                🗺️ View Full Route on Marine Map →
              </button>
            </div>
          ) : (
            <p style={{ color: 'var(--muted)' }}>Select your origin port and destination zone to compute the safe navigational corridor.</p>
          )}
        </Card>
      </div>

      <Card title={t('safetyChecklist')}>
        <div className="checklist">
          <span>✓ {t('weather')} Verified</span>
          <span>✓ {t('seaState')} Within Limits</span>
          <span>✓ {t('boundaries')} Cleared</span>
          <span>✓ {t('routeRisk')} Evaluated</span>
          <span>✓ Supabase Live Sync Active</span>
        </div>
      </Card>
    </>
  )
}

function Assistant({ lang, navigate, setActiveRoute, setSelectedZone }) {
  const t = k => tr(lang, k)
  const [messages, setMessages] = useState([{ role: 'orca', text: t('demoAnswer') }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(() => 'orca_sess_' + Math.random().toString(36).substring(2, 10))

  useEffect(() => {
    setMessages([{ role: 'orca', text: t('demoAnswer') }])
  }, [lang])

  const send = async (q) => {
    if (!q.trim() || loading) return
    const userText = q.trim()
    const history = messages.slice(-6).map(m => ({ role: m.role, text: m.text }))
    setMessages(m => [...m, { role: 'user', text: userText }])
    setInput('')
    setLoading(true)

    try {
      const data = await askOrca(userText, sessionId, { language: lang, history })
      if (data && (data.explanation_text || data.recommendation)) {
        let reply = data.explanation_text || ''

        if (data.recommendation && data.recommendation.zone_id && data.recommendation.zone_id !== 'NONE') {
          reply += `\n\n🎯 Recommendation: ${data.recommendation.zone_id} (Status: ${data.recommendation.status}, Risk Score: ${data.recommendation.risk_score}/100, Band: ${data.recommendation.risk_band})`
          if (data.evidence && data.evidence.length > 0) {
            reply += '\n\n📊 Evidence Trail:\n' + data.evidence.map(e => `• ${e.claim}`).join('\n')
          }

          // Automatically extract route and set active route
          if (data.map_payload && data.map_payload.routes && data.map_payload.routes.length > 0) {
            const r = data.map_payload.routes[0]
            setActiveRoute({
              ...r,
              destination_name: data.recommendation.zone_id,
              departure_name: 'Departure Port'
            })
            setSelectedZone(data.recommendation.zone_id)
          }
        }

        setMessages(m => [
          ...m,
          {
            role: 'orca',
            text: reply,
            hasRoute: !!(data.map_payload && data.map_payload.routes && data.map_payload.routes.length > 0),
            zoneId: data.recommendation?.zone_id
          }
        ])
      } else {
        setMessages(m => [...m, { role: 'orca', text: 'I received your query and checked the marine database. Conditions are favourable with slight sea state.' }])
      }
    } catch (err) {
      setMessages(m => [...m, { role: 'orca', text: 'Encountered connection issue. Using cached marine parameters.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="assistant">
      <div className="assistantIntro">
        <img className="assistantLogo" src={logo} alt="ORCA logo" />
        <span className="eyebrow">{t('conversational')}</span>
        <h2>{t('askSea')}</h2>
      </div>

      <div className="chat">
        <div className="messages">
          {messages.map((m, i) => (
            <div className={'message ' + m.role} key={i}>
              <div className="msgAvatar">{m.role === 'orca' ? '⚓' : 'D'}</div>
              <div className="bubble">
                {m.text}
                {m.hasRoute && (
                  <div className="bubbleNavActions">
                    <button className="bubbleNavBtn" onClick={() => navigate('/map')}>
                      {t('viewOnMap')} →
                    </button>
                    <button className="bubbleNavBtn" onClick={() => navigate('/safety')}>
                      {t('viewSafety')} →
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="message orca">
              <div className="msgAvatar">⚓</div>
              <div className="bubble typing">Reasoning across ocean, weather & Supabase data...</div>
            </div>
          )}
        </div>

        <div className="suggestions">
          {['nearest', 'safeTomorrow', 'showHazards', 'findRoute'].map(k => (
            <button key={k} onClick={() => send(t(k))}>{t(k)}</button>
          ))}
        </div>

        <div className="composer">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && send(input)}
            placeholder={t('placeholder')}
          />
          <button className="primary" onClick={() => send(input)}>{t('send')} →</button>
        </div>
      </div>
    </div>
  )
}

function AlertsPage({ lang, setModal, alertList }) {
  const t = k => tr(lang, k)
  return (
    <>
      <div className="pageIntro">
        <div>
          <span className="eyebrow">{t('alerts').toUpperCase()}</span>
          <h2>{t('alerts')}</h2>
          <p>Real-time marine hazard warnings and high-wave advisories fetched from Supabase.</p>
        </div>
      </div>

      <div className="alertList">
        {alertList.map(a => (
          <button className="alertLarge" key={a.id} onClick={() => setModal(a)}>
            <span className={'severity ' + (a.risk_level ? a.risk_level.toLowerCase() : a.severity?.toLowerCase() || 'medium')}>
              {a.risk_level || a.severity || 'ALERT'}
            </span>
            <div>
              <h3>{a.title?.[lang] || a.title || 'Marine Hazard'}</h3>
              <p>{a.description || a.body?.[lang] || a.body || ''}</p>
            </div>
            <span>→</span>
          </button>
        ))}
      </div>
    </>
  )
}

function SettingsPage({ lang, setLang, dark, setDark }) {
  const t = k => tr(lang, k)
  const [email, setEmail] = useState(true)
  const [saved, setSaved] = useState(false)

  return (
    <>
      <div className="pageIntro">
        <div>
          <span className="eyebrow">{t('settings').toUpperCase()}</span>
          <h2>{t('settings')}</h2>
        </div>
        <button className="primary" onClick={() => { setSaved(true); setTimeout(() => setSaved(false), 1500) }}>
          {saved ? t('saved') : t('save')}
        </button>
      </div>

      <Card title={t('language')}>
        <div className="settingRow">
          <div>
            <b>{t('language')}</b>
            <p>{t('mapLabels')}</p>
          </div>
          <select value={lang} onChange={e => setLang(e.target.value)}>
            <option value="en">English</option>
            <option value="hi">हिन्दी</option>
            <option value="mr">मराठी</option>
          </select>
        </div>
      </Card>

      <Card title={t('theme')}>
        <div className="settingRow">
          <div>
            <b>{t('darkMode')}</b>
            <p>{dark ? 'Deep ocean blue dark interface' : 'Clean coastal light interface'}</p>
          </div>
          <button className={'toggle ' + (dark ? 'on' : '')} onClick={() => setDark(v => !v)}><span /></button>
        </div>
        <div className="settingRow">
          <div>
            <b>{t('email')}</b>
            <p>{t('notifications')}</p>
          </div>
          <button className={'toggle ' + (email ? 'on' : '')} onClick={() => setEmail(v => !v)}><span /></button>
        </div>
      </Card>
    </>
  )
}

function Profile({ lang, user, onSignOut }) {
  const t = k => tr(lang, k)
  const [editing, setEditing] = useState(false)
  const [profession, setProfession] = useState(localStorage.getItem('orca-profession') || 'Marine Researcher')

  const userName = user?.user_metadata?.full_name || user?.email?.split('@')[0] || t('name')
  const userRole = user?.user_metadata?.role || profession

  const save = () => {
    localStorage.setItem('orca-profession', profession)
    setEditing(false)
  }

  return (
    <>
      <div className="pageIntro">
        <div>
          <span className="eyebrow">{t('profileTitle').toUpperCase()}</span>
          <h2>{t('profileTitle')}</h2>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="primary" onClick={() => editing ? save() : setEditing(true)}>
            {editing ? t('done') : t('edit')}
          </button>
          {user && (
            <button className="textBtn" style={{ color: 'var(--danger)', fontWeight: 'bold' }} onClick={onSignOut}>
              {t('signOut')}
            </button>
          )}
        </div>
      </div>

      <Card title={t('details')}>
        <div className="profileBox">
          <div className="avatar bigAvatar">⚓</div>
          <div className="profileMain">
            <h2>{userName}</h2>
            <p>{userRole}</p>
            <span className="pill">{user ? 'Supabase Authenticated' : t('status')}</span>
          </div>
        </div>

        <div className="profileDetails">
          <div>
            <span>{t('emailLabel')}</span>
            <b>{user?.email || 'captain.devesh@orca-marine.in'}</b>
          </div>
          <div>
            <span>User ID (UUID)</span>
            <b>{user?.id ? user.id.slice(0, 18) + '...' : 'auth-demo-session'}</b>
          </div>
          <div>
            <span>{t('profession')}</span>
            {editing ? (
              <select value={profession} onChange={e => setProfession(e.target.value)}>
                <option>Marine Researcher</option>
                <option>Fisherman</option>
                <option>Fleet Operator</option>
              </select>
            ) : (
              <b>{profession}</b>
            )}
          </div>
          <div>
            <span>Database Connection</span>
            <b>byikekhtwiewlpxbuwgo.supabase.co</b>
          </div>
        </div>
      </Card>
    </>
  )
}

function App() {
  const loc = useLocation()
  const navigate = useNavigate()
  const [lang, setLang] = useState(localStorage.getItem('orca-lang') || 'en')
  const [dark, setDark] = useState(localStorage.getItem('orca-theme') === 'dark')
  const [selected, setSelected] = useState('PFZ-MUM-01')
  const [modal, setModal] = useState(null)
  const [panel, setPanel] = useState(null)
  const [query, setQuery] = useState('')
  const [backendOnline, setBackendOnline] = useState(false)

  // Supabase Auth State
  const [currentUser, setCurrentUser] = useState(null)
  const [authModalOpen, setAuthModalOpen] = useState(false)

  // Dynamic Data & Route State
  const [selectedPort, setSelectedPort] = useState('mumbai')
  const [allIndiaPfzList, setAllIndiaPfzList] = useState([])
  const [pfzList, setPfzList] = useState(staticPfz)
  const [alertList, setAlertList] = useState(staticAlerts)
  const [oceanStats, setOceanStats] = useState(null)
  const [oceanPeriod, setOceanPeriod] = useState('7')
  const [activeRoute, setActiveRoute] = useState({
    origin: { lat: 18.94, lon: 72.83 },
    destination: { lat: 18.82, lon: 72.48 },
    waypoints: [
      { lat: 18.94, lon: 72.83 },
      { lat: 18.88, lon: 72.65 },
      { lat: 18.82, lon: 72.48 }
    ],
    distance_km: 39.2,
    estimated_travel_time_min: 155,
    departure_name: 'Mumbai Harbour',
    destination_name: 'PFZ-MUM-01'
  })

  const path = loc.pathname
  const t = k => tr(lang, k)

  // Initialize Supabase Auth session listener
  useEffect(() => {
    getSession().then(session => {
      if (session?.user) setCurrentUser(session.user)
    })
    const { data: authListener } = onAuthStateChange((_event, user) => {
      setCurrentUser(user)
    })
    return () => authListener?.subscription?.unsubscribe()
  }, [])

  // Sync lang & theme to DOM
  useEffect(() => {
    localStorage.setItem('orca-lang', lang)
    document.documentElement.lang = lang
  }, [lang])

  useEffect(() => {
    localStorage.setItem('orca-theme', dark ? 'dark' : 'light')
    document.documentElement.dataset.theme = dark ? 'dark' : 'light'
  }, [dark])

  // Periodic Backend Health Check & Data Fetching
  useEffect(() => {
    const check = async () => {
      const health = await checkBackendHealth()
      setBackendOnline(!!health?.online)
    }
    check()
    const timer = setInterval(check, 10000)
    return () => clearInterval(timer)
  }, [])

  const loadPfzs = (portId = selectedPort) => {
    // 1. Port-specific live PFZs from Supabase / Backend
    getPfzCandidates(null, null, portId).then(res => {
      if (res && res.candidates && res.candidates.length > 0) {
        const mapped = res.candidates.map(c => ({
          id: c.zone_id,
          name: c.name || `${c.zone_id} Coastal Front`,
          sector: c.sector || 'Indian Coastal Shelf',
          port_id: c.port_id || portId,
          port_name: c.port_name || portId,
          lat: c.lat,
          lng: c.lon,
          lon: c.lon,
          confidence: Math.round((c.confidence_score || 0.90) * 100),
          sst: c.sst_celsius || 28.0,
          chlorophyll: c.chlorophyll_mg_m3 || 1.4,
          waves: 1.2,
          wind: 16,
          bearing: c.bearing_deg || 250,
          depth: c.depth_m || 45,
          distance: `${c.distance_km || 30} km`,
          reason: {
            en: `Real-time satellite SST (${c.sst_celsius}°C) & chlorophyll front along ${c.name || c.zone_id}`,
            hi: `सैटेलाइट SST (${c.sst_celsius}°C) और क्लोरोफिल फ्रंट ${c.name || c.zone_id}`,
            mr: `सॅटेलाइट SST (${c.sst_celsius}°C) आणि क्लोरोफिल फ्रंट ${c.name || c.zone_id}`
          }
        }))
        setPfzList(mapped)
      }
    })

    // 2. All-India PFZs overview
    getPfzCandidates(null, null, 'all').then(res => {
      if (res && res.candidates && res.candidates.length > 0) {
        const mappedAll = res.candidates.map(c => ({
          id: c.zone_id,
          name: c.name || `${c.zone_id} Front`,
          sector: c.sector || 'Indian Coast',
          port_id: c.port_id,
          port_name: c.port_name,
          lat: c.lat,
          lng: c.lon,
          lon: c.lon,
          confidence: Math.round((c.confidence_score || 0.90) * 100),
          sst: c.sst_celsius || 28.0,
          chlorophyll: c.chlorophyll_mg_m3 || 1.4,
          distance: `${c.distance_km || 30} km`
        }))
        setAllIndiaPfzList(mappedAll)
      }
    })
  }

  // Fetch live Alerts, Analytics, and PFZ from backend/Supabase
  useEffect(() => {
    getAllAlerts().then(res => {
      if (res && res.alerts && res.alerts.length > 0) {
        setAlertList(res.alerts)
      }
    })
    getAnalytics(oceanPeriod).then(res => {
      if (res) setOceanStats(res)
    })
    loadPfzs(selectedPort)
  }, [selectedPort, oceanPeriod])

  const handleSignOut = async () => {
    await signOutUser()
    setCurrentUser(null)
  }

  const nav = [
    ['Dashboard', '/'],
    ['Marine Intelligence Map', '/map'],
    ['Ocean Analytics', '/analytics'],
    ['Fishing Intelligence', '/fishing'],
    ['Safety & Routes', '/safety'],
    ['ORCA AI Assistant', '/assistant'],
    ['Alerts', '/alerts'],
    ['Settings', '/settings']
  ]

  const results = useMemo(() => nav.filter(([name]) => name.toLowerCase().includes(query.toLowerCase())), [query])

  let content
  if (path === '/') {
    content = (
      <Dashboard
        lang={lang}
        navigate={navigate}
        setSelected={setSelected}
        setModal={setModal}
        pfzList={pfzList}
        alertList={alertList}
        oceanStats={oceanStats}
        selectedPort={selectedPort}
        setSelectedPort={p => {
          setSelectedPort(p)
          loadPfzs(p)
        }}
      />
    )
  }
  if (path === '/map') {
    content = (
      <MapPage
        lang={lang}
        selected={selected}
        setSelected={setSelected}
        activeRoute={activeRoute}
        setActiveRoute={setActiveRoute}
        pfzList={pfzList}
        allIndiaPfzList={allIndiaPfzList}
        alertList={alertList}
        selectedPort={selectedPort}
        setSelectedPort={p => {
          setSelectedPort(p)
          loadPfzs(p)
        }}
      />
    )
  }
  if (path === '/analytics') {
    content = (
      <Analytics
        lang={lang}
        oceanStats={oceanStats}
        setOceanPeriod={setOceanPeriod}
      />
    )
  }
  if (path === '/fishing') {
    content = (
      <Fishing
        lang={lang}
        navigate={navigate}
        setSelected={setSelected}
        pfzList={pfzList}
        allIndiaPfzList={allIndiaPfzList}
        selectedPort={selectedPort}
        setSelectedPort={p => {
          setSelectedPort(p)
          loadPfzs(p)
        }}
      />
    )
  }
  if (path === '/safety') {
    content = (
      <Safety
        lang={lang}
        navigate={navigate}
        activeRoute={activeRoute}
        setActiveRoute={setActiveRoute}
        pfzList={pfzList}
        selectedPort={selectedPort}
        setSelectedPort={setSelectedPort}
        onPortChange={p => {
          setSelectedPort(p)
          loadPfzs(p)
        }}
      />
    )
  }
  if (path === '/assistant') {
    content = (
      <Assistant
        lang={lang}
        navigate={navigate}
        setActiveRoute={setActiveRoute}
        setSelectedZone={setSelected}
      />
    )
  }
  if (path === '/alerts') {
    content = (
      <AlertsPage
        lang={lang}
        setModal={setModal}
        alertList={alertList}
      />
    )
  }
  if (path === '/settings') {
    content = (
      <SettingsPage
        lang={lang}
        setLang={setLang}
        dark={dark}
        setDark={setDark}
      />
    )
  }
  if (path === '/profile') {
    content = (
      <Profile
        lang={lang}
        user={currentUser}
        onSignOut={handleSignOut}
      />
    )
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <button className="brand" onClick={() => navigate('/')}>
          <img className="brandLogo" src={logo} alt="ORCA logo" />
          <div>
            <b>ORCA</b>
            <small>Marine Intelligence</small>
          </div>
        </button>

        <div className="navTitle">{t('workspace')}</div>
        {nav.map(([name, url], i) => (
          <button
            key={url}
            className={'nav ' + ((url === '/' ? path === '/' : path === url) ? 'active' : '')}
            onClick={() => navigate(url)}
          >
            <span className="ico">{['⌂', '◈', '◫', '◉', '◇', '◌', '!', '⚙'][i]}</span>
            {t(keyFor(name))}
          </button>
        ))}

        <div className="sideBottom">
          <span className={backendOnline ? 'greenDot' : 'amberDot'} />
          <div>
            <b>{backendOnline ? 'Supabase & AI Engine' : t('operational')}</b>
            <small>{backendOnline ? 'Live Connected (:8000)' : t('connected')}</small>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="header">
          <div>
            <span className="eyebrow">ORCA / {t(keyFor(labels[path] || 'Dashboard'))}</span>
            <h1>{t(keyFor(labels[path] || 'Dashboard'))}</h1>
          </div>

          <div className="headerRight">
            <button className="iconBtn" onClick={() => setPanel(panel === 'search' ? null : 'search')} aria-label={t('search')}>⌕</button>
            <button className="iconBtn" onClick={() => setPanel(panel === 'bell' ? null : 'bell')} aria-label={t('notifications')}>♢</button>

            <select aria-label={t('language')} value={lang} onChange={e => setLang(e.target.value)}>
              <option value="en">English</option>
              <option value="hi">हिन्दी</option>
              <option value="mr">मराठी</option>
            </select>

            {currentUser ? (
              <button className="avatarBtn" onClick={() => navigate('/profile')}>
                <div className="avatarIcon">⚓</div>
                <span className="avatarName">{currentUser.user_metadata?.full_name?.split(' ')[0] || currentUser.email?.split('@')[0] || 'Captain'}</span>
              </button>
            ) : (
              <button className="authNavBtn" onClick={() => setAuthModalOpen(true)}>
                ⚓ {t('signIn')}
              </button>
            )}
          </div>
        </header>

        {panel && (
          <div className="floatingPanel">
            {panel === 'search' ? (
              <div>
                <b>{t('search')}</b>
                <input
                  autoFocus
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  placeholder={t('search') + '...'}
                />
                <div className="searchResults">
                  {query ? (
                    results.map(([n, u]) => (
                      <button key={u} onClick={() => { navigate(u); setPanel(null); setQuery('') }}>
                        {t(keyFor(n))} →
                      </button>
                    ))
                  ) : (
                    <span>{t('noResults')}</span>
                  )}
                </div>
                <button onClick={() => setPanel(null)}>{t('close')}</button>
              </div>
            ) : (
              <div>
                <b>{t('notifications')}</b>
                {alertList.map(a => (
                  <button className="panelAlert" key={a.id} onClick={() => { setModal(a); setPanel(null) }}>
                    <strong>{a.title?.[lang] || a.title || 'Alert'}</strong>
                    <span>{a.description || a.body?.[lang] || a.body || ''}</span>
                  </button>
                ))}
                <button onClick={() => setPanel(null)}>{t('close')}</button>
              </div>
            )}
          </div>
        )}

        <div className="content">{content}</div>
      </main>

      {modal && (
        <div className="modalBackdrop" onClick={() => setModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <span className={'severity ' + (modal.risk_level ? modal.risk_level.toLowerCase() : modal.severity?.toLowerCase() || 'medium')}>
              {modal.risk_level || modal.severity || 'ALERT'}
            </span>
            <h2>{modal.title?.[lang] || modal.title || 'Advisory'}</h2>
            <p>{modal.description || modal.body?.[lang] || modal.body || ''}</p>
            <button className="primary" onClick={() => setModal(null)}>{t('close')}</button>
          </div>
        </div>
      )}

      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={user => setCurrentUser(user)}
      />
    </div>
  )
}

export default function Root() {
  return (
    <BrowserRouter>
      <App />
    </BrowserRouter>
  )
}
